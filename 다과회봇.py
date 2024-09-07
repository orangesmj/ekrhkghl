import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import Button, View, Modal, TextInput
from datetime import datetime
import json
import os
import re
access_token = os.environ["BOT_TOKEN"]

Nick_Log = "nickname_history.json"  # 닉네임 변경 기록을 저장할 파일 이름

# 봇의 인텐트를 설정합니다. 모든 필요한 인텐트를 활성화합니다.
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# 닉네임 변경 기록을 저장할 딕셔너리 (사용자 ID를 키로 하고 닉네임과 날짜의 목록을 값으로 저장)
nickname_history = {}

# 역할 및 채널 ID 변수 설정
Ch_1 = 1264567815340298281  # 입장가이드 채널 변수
Me_1 = 1281651525529374760  # 내 ID 메세지 변수
Emoji_1 = "✅"  # 입장가이드 이모지 변수
Role_1 = 1281601086142021772  # 입장가이드 역할 변수

Ch_2 = 1267706085763190818  # 가입양식 채널 변수
Role_2 = 1281606443551686676  # 가입양식 완료 후 부여되는 역할 변수
move_ch = 1264567865227346004  # 가입양식 > 가입보관소로 이동되는 변수
MS_1 = 1281606690952708216  # 내 글을 제외한 모든 글 삭제를 1시간 주기의 특정 ID

Ch_3 = 1263829979398017159  # 닉네임변경 채널 변수
Man = 1043194155515519048  # 남 역할 이모지
Woman = 1043891312384024576  # 여 역할 이모지
Sex = ['💙', '❤️']  # 역할 부여에 사용되는 이모지들
MS_2 = 1281654298500927635  # 닉네임 변경 양식에 내 고정글
Role_4 = 1264571068874756149  # 닉변완료 부여 역할

Ch_4 = 1264567815340298281  # 라소소 채널 변수
Me_2 = 1281667957076000769  # 라소소 클로잇 ID 메세지 변수
Emoji_2 = "✅"  # 라소소 이모지 변수
Role_5 = 1264571068874756149  # 라소소 역할 변수

Nick_ch = 1281830606476410920  # 닉네임 변경 로그 채널 ID
ad1 = 1264012076997808308  # 운영자 역할ID 변수
open_channel_id = 1281629317402460161  # 서버 켜지면 알람 뜰 채널

# 삭제된 메시지를 기록할 로그 채널 ID
Rec = 1267642384108486656  

# 가입 양식 메시지를 검증하기 위한 정규 표현식 정의
REQUIRED_REGEX = re.compile(
    r"동의여부\s*:\s*.*\n동의일자\s*:\s*.*", re.MULTILINE
)

# JSON 파일에서 닉네임 변경 기록 불러오기
def load_nickname_history():
    global nickname_history
    if os.path.exists(Nick_Log):
        with open(Nick_Log, 'r', encoding='utf-8') as file:
            nickname_history = json.load(file)
            # JSON 파일에서 날짜 형식을 문자열로 저장하기 때문에 튜플 형식으로 변환
            nickname_history = {int(k): [(n, d) for n, d in v] for k, v in nickname_history.items()}

# 닉네임 변경 기록을 JSON 파일에 저장하기
def save_nickname_history():
    with open(Nick_Log, 'w', encoding='utf-8') as file:
        json.dump(nickname_history, file, ensure_ascii=False, indent=4)

# 현재 서버에서 중복된 닉네임을 찾는 함수 (대소문자 구별 없이 검사)
def is_duplicate_nickname(new_nickname, guild):
    for member in guild.members:
        if member.display_name.lower() == new_nickname.lower():
            return True
    return False

# 봇이 준비되었을 때 실행되는 이벤트
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    load_nickname_history()  # 닉네임 변경 기록 불러오기
    
    # 슬래시 명령어를 Discord 서버에 동기화합니다.
    try:
        await bot.tree.sync()
        print("슬래시 명령어가 동기화되었습니다.")
    except Exception as e:
        print(f"명령어 동기화 중 오류 발생: {e}")

    # 주기적인 메시지 삭제 작업 시작
    delete_messages.start()
    delete_messages_2.start()
    channel = bot.get_channel(open_channel_id)
    if channel:
        await channel.send('봇이 활성화되었습니다!')

    # 닉네임 변경 및 가입 양식 작성 버튼 항상 활성화
    await send_nickname_button(bot.get_channel(Ch_3))
    await send_join_form_button(bot.get_channel(Ch_2))

# 주기적으로 메시지 삭제
@tasks.loop(hours=1)
async def delete_messages():
    channel = bot.get_channel(Ch_2)  # 메시지를 삭제할 채널
    if channel:
        async for message in channel.history(limit=100):  # 최근 100개의 메시지를 가져옵니다
            if message.id != MS_1:  # 특정 메시지를 제외하고
                await message.delete()  # 메시지를 삭제합니다
                print(f'Deleted message from {message.author.display_name} with content: {message.content}')

@tasks.loop(minutes=5)
async def delete_messages_2():
    channel = bot.get_channel(Ch_3)  # 메시지를 삭제할 채널
    if channel:
        async for message in channel.history(limit=100):  # 최근 100개의 메시지를 가져옵니다
            if message.id != MS_2:  # 특정 메시지를 제외하고
                await message.delete()  # 메시지를 삭제합니다
                print(f'Deleted message from {message.author.display_name} with content: {message.content}')

# 역할 부여 및 제거 처리 함수
async def handle_reaction(payload, add_role: bool, channel_id, message_id, emoji, role_id):
    # 이모지가 특정 메시지에서 눌렸는지 확인
    if payload.channel_id != channel_id or payload.message_id != message_id:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    if member is None or member.bot:
        return

    # 이모지가 Emoji_1과 일치하는지 확인
    if str(payload.emoji) == emoji:
        role = guild.get_role(role_id)
        if role:
            try:
                if add_role:
                    await member.add_roles(role)
                    await member.send(f"{role.name} 역할이 부여되었습니다!")

                    # 리액션 제거 (리액션 카운트를 유지하기 위해)
                    channel = bot.get_channel(channel_id)
                    message = await channel.fetch_message(message_id)
                    await message.remove_reaction(emoji, member)

            except Exception as e:
                await member.send(f"역할 부여 중 오류 발생: {e}")

# 리액션 추가 시 이벤트 처리
@bot.event
async def on_raw_reaction_add(payload):
    # 입장 가이드 역할 추가
    await handle_reaction(payload, True, Ch_1, Me_1, Emoji_1, Role_1)
    
    # 라소소 역할 추가
    if payload.channel_id == Ch_4 and payload.message_id == Me_2 and str(payload.emoji) == Emoji_2:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member:
            role = guild.get_role(Role_5)
            if role:
                try:
                    await member.add_roles(role)
                    await member.send(f"{role.name} 역할이 부여되었습니다!")
                    print(f'{role.name} 역할이 {member.display_name}에게 부여되었습니다.')

                    # 리액션 카운트를 유지하기 위해 리액션 제거
                    channel = bot.get_channel(payload.channel_id)
                    message = await channel.fetch_message(payload.message_id)
                    await message.remove_reaction(payload.emoji, member)

                except discord.Forbidden:
                    await member.send("권한이 없어 역할을 부여할 수 없습니다.")
                except discord.HTTPException as e:
                    await member.send(f"역할 부여 중 오류 발생: {e}")

    # 닉네임 변경 및 역할 부여 처리
    if payload.channel_id == Ch_3 and str(payload.emoji) in Sex:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member:
            # 현재 누른 이모지에 따른 역할 부여 및 반대 역할 제거
            selected_role = guild.get_role(Man if str(payload.emoji) == '💙' else Woman)
            opposite_role = guild.get_role(Woman if str(payload.emoji) == '💙' else Man)
            if selected_role:
                try:
                    await member.add_roles(selected_role)
                    await member.send(f'{selected_role.name} 역할이 부여되었습니다.')

                    # 반대 역할 제거
                    if opposite_role in member.roles:
                        await member.remove_roles(opposite_role)
                        await member.send(f'{opposite_role.name} 역할이 제거되었습니다.')

                    # 리액션 카운트를 유지하기 위해 리액션 제거
                    channel = bot.get_channel(payload.channel_id)
                    message = await channel.fetch_message(payload.message_id)
                    await message.remove_reaction(payload.emoji, member)

                except Exception as e:
                    await member.send(f"역할 부여 오류: {e}")

# 메시지 삭제 시 로그 기록
@bot.event
async def on_message_delete(message):
    # 제외된 채널이거나, 메시지가 봇의 메시지인 경우 로그 기록하지 않음
    if message.channel.id in [Ch_2, Ch_3] or message.author.bot:
        return

    # 기록 채널 가져오기
    log_channel = bot.get_channel(Rec)
    if log_channel:
        try:
            # 삭제된 메시지의 내용을 로그 채널로 전송
            deleted_message = (
                f"**삭제된 메시지**\n"
                f"채널: {message.channel.mention}\n"
                f"작성자: {message.author.mention}\n"
                f"내용: {message.content}"
            )
            # 작성자의 프로필 이미지 URL 가져오기
            embed = discord.Embed(description=deleted_message, color=discord.Color.red())
            embed.set_author(name=str(message.author), icon_url=message.author.avatar.url if message.author.avatar else None)
            await log_channel.send(embed=embed)
            print(f"로그 채널에 삭제된 메시지가 전송되었습니다: {message.content}")
        except discord.HTTPException as e:
            print(f"메시지 삭제 기록 중 오류 발생: {e}")
    else:
        print("로그 채널을 찾을 수 없습니다.")

# 가입 양식 작성 모달 창
class JoinFormModal(Modal):
    def __init__(self, member):
        super().__init__(title="가입 양식 작성", timeout=None)
        self.member = member
        # 가입 양식의 각 항목을 추가
        self.agreement = TextInput(label="동의여부", placeholder="동의함 또는 동의하지 않음", required=True)
        self.agreement_date = TextInput(label="동의일자", placeholder="YYYY-MM-DD", required=True)
        self.nickname = TextInput(label="인게임 내 닉네임", placeholder="예: 라테일유저", required=True)
        self.guild_name = TextInput(label="인게임 내 길드", placeholder="예: 다과회", required=True)

        self.add_item(self.agreement)
        self.add_item(self.agreement_date)
        self.add_item(self.nickname)
        self.add_item(self.guild_name)

    async def on_submit(self, interaction: discord.Interaction):
        # 입력된 내용을 사용하여 양식 제출 완료
        agreement_text = self.agreement.value
        agreement_date = self.agreement_date.value
        nickname = self.nickname.value
        guild_name = self.guild_name.value
        
        # 동의여부에 "동의"가 포함되지 않는지 확인
        if "동의" not in agreement_text:
            await interaction.response.send_message(
                "양식이 틀렸습니다. 동의여부에 동의, 동의일자에 오늘 날짜로 기재해주셔야 정상 이용 가능합니다. "
                "팝업을 종료 후 다시 버튼을 눌러 다시 작성해주세요.",
                ephemeral=True
            )
            return

        # 양식 내용 작성할 채널 가져오기
        move_channel = bot.get_channel(move_ch)
        if move_channel:
            # 입력된 내용을 포함하는 임베드 메시지 생성
            embed = discord.Embed(
                title="가입 양식 제출",
                description=(
                    f"개인의 언쟁에 길드에 피해가는 것을 방지하기 위한 동의서입니다.\n"
                    f"확인 후 동의 부탁드립니다.\n\n"
                    f"[라테일 다과회] 내에서 개인 언쟁에 휘말릴 경우 본인의 길드의 도움을 받지 않으며 "
                    f"상대방 길드를 언급하지 않음에 동의하십니까?\n\n"
                    f"동의여부 : {agreement_text}\n"
                    f"동의일자 : {agreement_date}\n"
                    f"인게임 내 닉네임 : {nickname}\n"
                    f"인게임 내 길드 : {guild_name}"
                ),
                color=discord.Color.blue()
            )
            embed.set_author(name=self.member.display_name, icon_url=self.member.avatar.url if self.member.avatar else None)
            await move_channel.send(embed=embed)

        # Role_2 역할 부여
        role = interaction.guild.get_role(Role_2)
        if role:
            try:
                await self.member.add_roles(role)
                await interaction.user.send(f"{role.name} 역할이 부여되었습니다!")
            except discord.Forbidden:
                await interaction.user.send("권한이 없어 역할을 부여할 수 없습니다.")
            except discord.HTTPException as e:
                await interaction.user.send(f"역할 부여 중 오류가 발생했습니다: {e}")

        # 양식이 정상적으로 제출되었음을 DM으로 알림
        await interaction.user.send("가입 양식이 성공적으로 제출되었습니다!")
        await interaction.response.send_message("가입 양식이 성공적으로 제출되었습니다.", ephemeral=True)

# 가입 양식 작성 버튼 관련 처리
async def send_join_form_button(channel):
    # 가입 양식 작성 버튼 생성
    button = Button(label="가입 양식 작성", style=discord.ButtonStyle.primary)

    # 버튼 클릭 시 모달 창을 띄우는 콜백 함수
    async def button_callback(interaction):
        await interaction.response.send_modal(JoinFormModal(interaction.user))

    button.callback = button_callback
    view = View()
    view.add_item(button)

    # 가입 양식 작성 버튼을 채널에 전송 (버튼이 사라지지 않도록 유지)
    await channel.send("가입 양식 작성 버튼이 활성화되었습니다.", view=view, delete_after=None)

# 닉네임 변경 모달 창
class NicknameChangeModal(Modal):
    def __init__(self, member):
        super().__init__(title="닉네임 변경", timeout=None)
        self.member = member
        self.new_nickname = TextInput(label="변경할 닉네임을 입력하세요", placeholder="새로운 닉네임", required=True)
        self.add_item(self.new_nickname)

    async def on_submit(self, interaction: discord.Interaction):
        new_nickname = self.new_nickname.value
        old_nick = self.member.display_name
        
        # 중복 닉네임 검사 (대소문자 구별 없음)
        if is_duplicate_nickname(new_nickname, interaction.guild):
            await interaction.response.send_message(
                "중복된 닉네임입니다. 팝업창을 닫고 다시 닉네임 변경을 눌러 다른 닉네임으로 변경해주세요.",
                ephemeral=True
            )
            # 관리자에게 중복 시도 알림 전송
            admin_role = interaction.guild.get_role(ad1)
            if admin_role:
                for admin in admin_role.members:
                    await admin.send(
                        f"{interaction.user.mention} 님이 이미 사용 중인 닉네임으로 변경하려고 시도했습니다.\n"
                        f"현재 닉네임: {old_nick}\n변경 시도 닉네임: {new_nickname}"
                    )
            return
        
        # 닉네임 변경
        try:
            await self.member.edit(nick=new_nickname)
            await interaction.response.send_message(f"닉네임이 '{new_nickname}'로 변경되었습니다.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(
                "닉네임을 변경할 권한이 없습니다. 서버 관리자에게 문의하세요.",
                ephemeral=True
            )
            return
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"닉네임 변경 중 오류가 발생했습니다: {e}",
                ephemeral=True
            )
            return
        
        # 닉네임 변경 기록 저장
        change_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.member.id not in nickname_history:
            nickname_history[self.member.id] = []
        nickname_history[self.member.id].append((old_nick, change_date))
        save_nickname_history()  # 닉네임 변경 기록을 파일에 저장

        # Role_4 역할 부여
        role = interaction.guild.get_role(Role_4)
        if role:
            try:
                await self.member.add_roles(role)
                await interaction.user.send(f"{role.name} 역할이 부여되었습니다!")
            except discord.Forbidden:
                await interaction.user.send("권한이 없어 역할을 부여할 수 없습니다.")
            except discord.HTTPException as e:
                await interaction.user.send(f"역할 부여 중 오류가 발생했습니다: {e}")

        # 닉네임 변경 로그 전송
        nick_log_channel = bot.get_channel(Nick_ch)
        if nick_log_channel:
            embed = discord.Embed(
                title="닉네임 변경 로그",
                description=f"{self.member.mention} 닉네임이 변경되었습니다.",
                color=discord.Color.green()
            )
            embed.set_author(name=self.member.name, icon_url=self.member.avatar.url if self.member.avatar else None)
            embed.add_field(name="이전 닉네임", value=old_nick, inline=False)
            embed.add_field(name="변경된 닉네임", value=new_nickname, inline=False)
            await nick_log_channel.send(embed=embed)

# 닉네임 변경 버튼 관련 처리
async def send_nickname_button(channel):
    # 닉네임 변경 버튼 생성
    button = Button(label="닉네임 변경", style=discord.ButtonStyle.primary)

    # 버튼 클릭 시 모달 창을 띄우는 콜백 함수
    async def button_callback(interaction):
        await interaction.response.send_modal(NicknameChangeModal(interaction.user))

    button.callback = button_callback
    view = View()
    view.add_item(button)

    # 닉네임 변경 버튼을 채널에 전송 (버튼이 사라지지 않도록 유지)
    await channel.send("닉네임 변경 버튼이 활성화되었습니다.", view=view, delete_after=None)

# /조회 슬래시 커맨드
@bot.tree.command(name="조회", description="조회할 유저를 선택하여 닉네임 변경 전 닉네임들과 변경 날짜를 확인합니다.")
@app_commands.describe(user="조회할 유저를 선택하세요.")
async def check_nickname(interaction: discord.Interaction, user: discord.Member):
    # 조회 명령어 사용자가 ad1 역할을 가지고 있는지 확인
    admin_role = interaction.guild.get_role(ad1)
    if admin_role not in interaction.user.roles:
        await interaction.response.send_message("이 명령어를 사용할 권한이 없습니다.", ephemeral=True)
        return
    
    # 선택된 유저의 닉네임 변경 기록을 확인합니다.
    nicknames = nickname_history.get(user.id)
    if nicknames:
        # 닉네임과 날짜를 함께 출력
        nickname_list = "\n".join([f"{nick} (변경일: {date})" for nick, date in nicknames])
        await interaction.response.send_message(f"{user.mention}의 이전 닉네임 목록:\n{nickname_list}", ephemeral=True)
    else:
        await interaction.response.send_message(f"{user.mention}의 닉네임 변경 기록이 없습니다.", ephemeral=True)

# 봇 실행
bot.run(access_token)
