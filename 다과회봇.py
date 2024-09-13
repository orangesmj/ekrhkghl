import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import Button, View, Modal, TextInput
from datetime import datetime
import os
import re
from pymongo import MongoClient  # MongoDB 연결을 위한 패키지
from pytz import timezone

# 한국 표준 시간(KST)으로 현재 시간을 반환하는 함수
def get_kst_time():
    kst = timezone('Asia/Seoul')
    return datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')

# 환경 변수에서 Discord 봇 토큰을 가져옵니다.
TOKEN = os.environ.get("BOT_TOKEN")  # Discord 봇 토큰을 환경 변수에서 가져옵니다.

# MongoDB 연결 설정
# MongoDB 클라이언트를 설정하여 데이터베이스와 연결합니다.
mongo_url = "mongodb+srv://ab01085156927:33iLGd96gUvlL7Jw@ekrhkghl.kv5wj.mongodb.net/?retryWrites=true&w=majority&appName=ekrhkghl"
client = MongoClient(mongo_url)

# 사용할 데이터베이스와 컬렉션 설정
# 각 데이터를 저장할 컬렉션을 지정합니다.
db = client["DiscordBotDatabase"]  # 데이터베이스 이름 설정
nickname_collection = db["nickname_history"]  # 닉네임 변경 기록 컬렉션
ban_collection = db["ban_list"]  # 차단된 사용자 정보를 저장할 컬렉션
entry_collection = db["entry_list"]  # 입장 정보를 저장할 컬렉션
exit_collection = db["exit_list"]  # 퇴장 정보를 저장할 컬렉션

# 봇의 인텐트를 설정합니다. 모든 필요한 인텐트를 활성화합니다.
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # 메시지 콘텐츠 접근 허용
intents.messages = True  # 메시지 관련 이벤트 허용
intents.guilds = True  # 서버 관련 이벤트 허용
bot = commands.Bot(command_prefix='!', intents=intents)

# 닉네임 변경 기록 및 입장/퇴장 기록을 저장할 딕셔너리
# 데이터를 임시로 저장하는 변수입니다. MongoDB와 동기화하여 사용됩니다.
nickname_history = {}
ban_list = {}
entry_list = {}
exit_list = {}

# 관리자 역할 ID 설정
ad1 = 1264012076997808308  # 운영자 역할 ID 변수

# 역할 및 채널 ID 변수 설정
Ch_1 = 1264567815340298281  # 입장가이드 채널 변수

Me_1 = 1281651525529374760  # 내 ID 메시지 변수
Emoji_1 = "✅"  # 입장가이드 이모지 변수
Role_1 = 1281601086142021772  # 입장가이드 역할 변수

Ch_2 = 1267706085763190818  # 가입양식 채널 변수
Role_2 = 1281606443551686676  # 가입양식 완료 후 부여되는 역할 변수
move_ch = 1264567865227346004  # 가입양식에서 가입보관소로 이동되는 채널 변수
MS_1 = 1281606690952708216  # 내 글을 제외한 모든 글 삭제를 1시간 주기로 실행할 특정 메시지 ID

Ch_3 = 1263829979398017159  # 닉네임 변경 채널 변수
Man = 1043194155515519048  # 남자 역할 ID
Woman = 1043891312384024576  # 여자 역할 ID
Sex = ['💙', '❤️']  # 역할 부여에 사용되는 이모지들
MS_2 = 1281654298500927635  # 닉네임 변경 양식에 대한 내 고정 메시지 ID
Role_4 = 1264571068874756149  # 닉변 완료 후 부여되는 역할 ID

Ch_4 = 1264567815340298281  # 라소소 채널 변수
Me_2 = 1281667957076000769  # 라소소 클로잇 ID 메시지 변수
Emoji_2 = "✅"  # 라소소 이모지 변수
Role_5 = 1264571068874756149  # 라소소 역할 변수

Nick_ch = 1281830606476410920  # 닉네임 변경 로그 채널 ID 변수
open_channel_id = 1281629317402460161  # 서버가 켜지면 알람이 뜰 채널 변수

# 삭제된 메시지를 기록할 로그 채널 ID
Rec = 1267642384108486656  # 전체 삭제 로그 채널 ID 변수

# 역할 변수 설정
Boost = 1264071791404650567  # 설정한 역할 ID (서버 부스트 역할)

# JSON 파일에서 데이터를 불러오는 대신, MongoDB에서 데이터를 불러오는 함수로 수정합니다.
def load_nickname_history():
    """MongoDB에서 닉네임 변경 기록을 불러옵니다."""
    global nickname_history
    nickname_history = {
        doc["_id"]: [(item["nickname"], item["date"]) for item in doc["history"]]
        for doc in nickname_collection.find()
    }
    print(f"[DEBUG] 닉네임 변경 기록 불러옴: {nickname_history}")

def save_nickname_history():
    """MongoDB에 닉네임 변경 기록을 저장합니다."""
    for user_id, history in nickname_history.items():
        last_nickname = history[-1][0]  # 마지막 닉네임
        current_nickname = history[-1][0] if len(history) == 1 else history[-2][0]  # 현재 닉네임 (변경 전 닉네임)
        nickname_collection.update_one(
            {"_id": user_id},
            {"$set": {
                "history": [{"nickname": n, "date": d} for n, d in history],
                "last_nickname": last_nickname,
                "current_nickname": current_nickname
            }},
            upsert=True,
        )
    print(f"[DEBUG] 닉네임 변경 기록 저장됨: {nickname_history}")

def load_ban_list():
    """MongoDB에서 차단 목록을 불러옵니다."""
    global ban_list
    ban_list = {doc["_id"]: doc["data"] for doc in ban_collection.find()}
    print(f"[DEBUG] 차단 목록 불러옴: {ban_list}")

def save_ban_list():
    """MongoDB에 차단 목록을 저장합니다."""
    for user_id, data in ban_list.items():
        ban_collection.update_one(
            {"_id": user_id},
            {"$set": {"data": data, "last_nickname": data.get('last_nickname', '기록 없음')}},
            upsert=True
        )
    print(f"[DEBUG] 차단 목록 저장됨: {ban_list}")

def load_entry_list():
    """MongoDB에서 입장 기록을 불러옵니다."""
    global entry_list
    entry_list = {doc["_id"]: doc["data"] for doc in entry_collection.find()}
    print(f"[DEBUG] 입장 기록 불러옴: {entry_list}")

def save_entry_list():
    """MongoDB에 입장 기록을 저장합니다."""
    for user_id, data in entry_list.items():
        entry_collection.update_one(
            {"_id": user_id},
            {"$set": {"data": data, "last_nickname": data["nickname"]}},
            upsert=True
        )
    print(f"[DEBUG] 입장 기록 저장됨: {entry_list}")

def load_exit_list():
    """MongoDB에서 퇴장 기록을 불러옵니다."""
    global exit_list
    exit_list = {doc["_id"]: doc["data"] for doc in exit_collection.find()}
    print(f"[DEBUG] 퇴장 기록 불러옴: {exit_list}")

def save_exit_list():
    """MongoDB에 퇴장 기록을 저장합니다."""
    for user_id, data in exit_list.items():
        exit_collection.update_one(
            {"_id": user_id},
            {"$set": {"data": data, "last_nickname": data["nickname"]}},
            upsert=True
        )
    print(f"[DEBUG] 퇴장 기록 저장됨: {exit_list}")

# 봇이 준비되었을 때 실행되는 이벤트
@bot.event
async def on_ready():
    """봇이 준비되었을 때 실행되는 함수입니다."""
    print(f'Logged in as {bot.user}')
    load_nickname_history()  # 닉네임 기록을 불러옵니다.
    load_ban_list()          # 차단 목록을 불러옵니다.
    load_entry_list()        # 입장 기록을 불러옵니다.
    load_exit_list()         # 퇴장 기록을 불러옵니다.
    try:
        await bot.tree.sync()  # 슬래시 명령어를 동기화합니다.
        print("슬래시 명령어가 동기화되었습니다.")
    except Exception as e:
        print(f"명령어 동기화 중 오류 발생: {e}")

    delete_messages.start()   # 주기적인 메시지 삭제 태스크 시작
    delete_messages_2.start() # 주기적인 메시지 삭제 태스크 시작
    channel = bot.get_channel(open_channel_id)
    if channel:
        await channel.send('봇이 활성화되었습니다!')  # 봇이 활성화되었음을 알림

# 입장 및 퇴장 이벤트 처리
@bot.event
async def on_member_join(member):
    """사용자가 서버에 입장할 때 호출되는 함수입니다."""
    user_id = str(member.id)
    current_time = get_kst_time()
    entry_list[user_id] = {
        "nickname": member.display_name,
        "last_join": current_time,
        "join_count": entry_list.get(user_id, {}).get("join_count", 0) + 1
    }
    save_entry_list()  # 입장 기록을 MongoDB에 저장

    # 입장 횟수가 1회 이상인 경우 관리자에게 알림
    if entry_list[user_id]["join_count"] > 1:
        last_nickname, last_date = nickname_history.get(int(user_id), [(member.display_name, '기록 없음')])[-1]
        for guild_member in member.guild.members:
            if ad1 in [role.id for role in guild_member.roles]:
                try:
                    await guild_member.send(
                        f"ID: {member.id}가 다시 입장했습니다. "
                        f"퇴장 전 마지막 별명: '{last_nickname}' (변경일: {last_date})"
                    )
                except discord.Forbidden:
                    print(f"DM을 보낼 수 없습니다: {guild_member.display_name}")

@bot.event
async def on_member_remove(member):
    """사용자가 서버에서 퇴장할 때 호출되는 함수입니다."""
    user_id = str(member.id)
    current_time = get_kst_time()
    exit_list[user_id] = {
        "nickname": member.display_name,
        "last_leave": current_time,
        "leave_count": exit_list.get(user_id, {}).get("leave_count", 0) + 1
    }
    save_exit_list()  # 퇴장 기록을 MongoDB에 저장

    # 사용자가 차단된 목록에 있는 경우 업데이트
    if member.id in ban_list:
        ban_list[member.id]['last_nickname'] = member.display_name
        save_ban_list()

# 서버 부스트 시, 역할 자동 활성화
@bot.event
async def on_member_update(before, after):
    """사용자의 업데이트(역할 추가 등)를 처리합니다."""
    # Nitro Boost 여부를 감지
    if not before.premium_since and after.premium_since:
        boost_role = after.guild.get_role(Boost)
        if boost_role:
            await after.add_roles(boost_role)
            await after.send(f'서버 부스트 감사합니다! {boost_role.name} 역할이 부여되었습니다.')

    # 닉네임 변경 기록
    if before.display_name != after.display_name:
        change_date = get_kst_time()  # 한국 시간으로 변경된 시간 설정
        if after.id not in nickname_history:
            nickname_history[after.id] = []

        # 변경 전 닉네임을 current_nickname으로 설정하고 변경 후 닉네임을 저장
        nickname_history[after.id].append((before.display_name, change_date))
        save_nickname_history()

# 주기적으로 메시지 삭제
@tasks.loop(minutes=3)
async def delete_messages():
    """특정 채널의 메시지를 주기적으로 삭제합니다."""
    channel = bot.get_channel(Ch_2)
    if channel:
        async for message in channel.history(limit=100):
            if message.id != MS_1:
                await message.delete()
                print(f'Deleted message from {message.author.display_name} with content: {message.content}')

@tasks.loop(minutes=3)
async def delete_messages_2():
    """닉네임 변경 및 가입 양식 채널의 메시지를 주기적으로 삭제하고 버튼을 다시 활성화합니다."""
    nickname_channel = bot.get_channel(Ch_3)
    if nickname_channel:
        async for message in nickname_channel.history(limit=100):
            if message.id != MS_2 and message.author == bot.user:
                await message.delete()
                print(f"Deleted old nickname change button message from {message.author.display_name}")
        await send_nickname_button(nickname_channel)

    join_form_channel = bot.get_channel(Ch_2)
    if join_form_channel:
        async for message in join_form_channel.history(limit=100):
            if message.id != MS_1 and message.author == bot.user:
                await message.delete()
                print(f"Deleted old join form button message from {message.author.display_name}")
        await send_join_form_button(join_form_channel)

# 리액션을 통한 역할 부여 및 제거
async def handle_reaction(payload, add_role: bool, channel_id, message_id, emoji, role_id):
    """리액션을 통해 역할을 부여하거나 제거합니다."""
    if payload.channel_id != channel_id or payload.message_id != message_id:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    if member is None or member.bot:
        return

    if str(payload.emoji) == emoji:
        role = guild.get_role(role_id)
        if role:
            try:
                if add_role:
                    await member.add_roles(role)
                    await member.send(f"{role.name} 역할이 부여되었습니다!")
                    channel = bot.get_channel(channel_id)
                    message = await channel.fetch_message(message_id)
                    await message.remove_reaction(emoji, member)
            except Exception as e:
                await member.send(f"역할 부여 중 오류 발생: {e}")

@bot.event
async def on_raw_reaction_add(payload):
    """리액션 추가 시 호출되는 함수입니다."""
    await handle_reaction(payload, True, Ch_1, Me_1, Emoji_1, Role_1)

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
                    channel = bot.get_channel(payload.channel_id)
                    message = await channel.fetch_message(payload.message_id)
                    await message.remove_reaction(payload.emoji, member)
                except discord.Forbidden:
                    await member.send("권한이 없어 역할을 부여할 수 없습니다.")
                except discord.HTTPException as e:
                    await member.send(f"역할 부여 중 오류 발생: {e}")

    if payload.channel_id == Ch_3 and str(payload.emoji) in Sex:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member:
            selected_role = guild.get_role(Man if str(payload.emoji) == '💙' else Woman)
            opposite_role = guild.get_role(Woman if str(payload.emoji) == '💙' else Man)
            if selected_role:
                try:
                    await member.add_roles(selected_role)
                    await member.send(f'{selected_role.name} 역할이 부여되었습니다.')
                    if opposite_role in member.roles:
                        await member.remove_roles(opposite_role)
                        await member.send(f'{opposite_role.name} 역할이 제거되었습니다.')
                    channel = bot.get_channel(payload.channel_id)
                    message = await channel.fetch_message(payload.message_id)
                    await message.remove_reaction(payload.emoji, member)
                except Exception as e:
                    await member.send(f"역할 부여 오류: {e}")

# 메시지 삭제 시 로그 기록
@bot.event
async def on_message_delete(message):
    """메시지 삭제 시 로그를 기록합니다."""
    # 메시지가 봇이 작성한 것이거나, 특정 예외 채널에서 삭제된 경우 기록하지 않음
    if message.author.bot or message.channel.id in [Ch_2, Ch_3]:
        return

    # 로그 채널 가져오기
    log_channel = bot.get_channel(Rec)
    if log_channel is None:
        print("로그 채널을 찾을 수 없습니다.")
        return

    try:
        # 삭제된 메시지의 기본 정보
        deleted_message = (
            f"**삭제된 메시지**\n"
            f"**채널**: {message.channel.mention}\n"
            f"**작성자**: {message.author.mention}\n"
        )

        # 메시지 내용 추가
        if message.content:
            deleted_message += f"**내용**: {message.content}\n"
        else:
            # 추가 콘텐츠를 검사
            additional_content = []
            if message.attachments:
                attachment_urls = "\n".join([attachment.url for attachment in message.attachments])
                additional_content.append(f"**첨부 파일**:\n{attachment_urls}")

            if message.embeds:
                for index, embed in enumerate(message.embeds, start=1):
                    embed_details = embed.to_dict()
                    additional_content.append(f"**임베드 #{index}**: {embed_details}")

            if message.stickers:
                sticker_names = ", ".join([sticker.name for sticker in message.stickers])
                additional_content.append(f"**스티커**: {sticker_names}")

            if additional_content:
                deleted_message += "\n".join(additional_content)
            else:
                deleted_message += "**내용**: 메시지 내용이 없습니다.\n"

        # 삭제된 메시지 정보를 임베드로 전송
        embed = discord.Embed(description=deleted_message, color=discord.Color.red())
        embed.set_author(name=str(message.author), icon_url=message.author.avatar.url if message.author.avatar else None)
        await log_channel.send(embed=embed)
        print("로그 채널에 삭제된 메시지가 전송되었습니다.")
    except discord.HTTPException as e:
        print(f"메시지 삭제 기록 중 오류 발생: {e}")

# 가입 양식 작성 모달 창
class JoinFormModal(Modal):
    """가입 양식을 작성하는 모달 창입니다."""
    def __init__(self, member):
        super().__init__(title="가입 양식 작성", timeout=None)
        self.member = member
        self.agreement = TextInput(label="동의여부", placeholder="동의함 또는 동의하지 않음", required=True)
        self.agreement_date = TextInput(label="동의일자", placeholder="YYYY-MM-DD", required=True)
        self.nickname = TextInput(label="인게임 내 닉네임", placeholder="예: 라테일유저", required=True)
        self.guild_name = TextInput(label="인게임 내 길드", placeholder="예: 다과회", required=True)
        self.add_item(self.agreement)
        self.add_item(self.agreement_date)
        self.add_item(self.nickname)
        self.add_item(self.guild_name)

    async def on_submit(self, interaction: discord.Interaction):
        agreement_text = self.agreement.value
        agreement_date = self.agreement_date.value
        
        # 현재 날짜를 'YYYY-MM-DD' 형식으로 한국 시간 기준으로 얻습니다.
        today_date = datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
        nickname = self.nickname.value
        guild_name = self.guild_name.value

        # 동의 여부와 날짜가 올바른지 검사
        if "동의" not in agreement_text or agreement_date != today_date:
            await interaction.response.send_message(
                f"양식이 올바르지 않습니다. 동의여부와 동의일자는 오늘 날짜({today_date})로 입력해주세요.",
                ephemeral=True
            )
            return

        move_channel = bot.get_channel(move_ch)
        if move_channel:
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

        role = interaction.guild.get_role(Role_2)
        if role:
            try:
                await self.member.add_roles(role)
                await interaction.user.send(f"{role.name} 역할이 부여되었습니다!")
            except discord.Forbidden:
                await interaction.user.send("권한이 없어 역할을 부여할 수 없습니다.")
            except discord.HTTPException as e:
                await interaction.user.send(f"역할 부여 중 오류가 발생했습니다: {e}")

        await interaction.user.send("가입 양식이 성공적으로 제출되었습니다!")
        await interaction.response.send_message("가입 양식이 성공적으로 제출되었습니다.", ephemeral=True)

# 닉네임 변경 모달 창
class NicknameChangeModal(Modal):
    """닉네임을 변경하는 모달 창입니다."""
    def __init__(self, member):
        super().__init__(title="닉네임 변경", timeout=None)
        self.member = member
        self.new_nickname = TextInput(label="변경할 닉네임을 입력하세요", placeholder="새로운 닉네임", required=True)
        self.add_item(self.new_nickname)

    async def on_submit(self, interaction: discord.Interaction):
        new_nickname = self.new_nickname.value
        old_nick = self.member.display_name

        if is_duplicate_nickname(new_nickname, interaction.guild):
            await interaction.response.send_message(
                "중복된 닉네임입니다. 팝업창을 닫고 다시 닉네임 변경을 눌러 다른 닉네임으로 변경해주세요.",
                ephemeral=True
            )
            admin_role = interaction.guild.get_role(ad1)
            if admin_role:
                for admin in admin_role.members:
                    await admin.send(
                        f"{interaction.user.mention} 님이 이미 사용 중인 닉네임으로 변경하려고 시도했습니다.\n"
                        f"현재 닉네임: {old_nick}\n변경 시도 닉네임: {new_nickname}"
                    )
            return

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

        change_date = get_kst_time()
        if self.member.id not in nickname_history:
            nickname_history[self.member.id] = []
        nickname_history[self.member.id].append((old_nick, change_date))
        save_nickname_history()

        role = interaction.guild.get_role(Role_4)
        if role:
            try:
                await self.member.add_roles(role)
                await interaction.user.send(f"{role.name} 역할이 부여되었습니다!")
            except discord.Forbidden:
                await interaction.user.send("권한이 없어 역할을 부여할 수 없습니다.")
            except discord.HTTPException as e:
                await interaction.user.send(f"역할 부여 중 오류가 발생했습니다: {e}")

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

# 모달 및 버튼 처리 함수
async def send_join_form_button(channel):
    """가입 양식 작성 버튼을 전송하는 함수입니다."""
    button = Button(label="가입 양식 작성", style=discord.ButtonStyle.primary)
    async def button_callback(interaction):
        await interaction.response.send_modal(JoinFormModal(interaction.user))
    button.callback = button_callback
    view = View()
    view.add_item(button)
    await channel.send("가입 양식 작성 버튼이 활성화되었습니다.", view=view, delete_after=None)

async def send_nickname_button(channel):
    """닉네임 변경 버튼을 전송하는 함수입니다."""
    button = Button(label="닉네임 변경", style=discord.ButtonStyle.primary)
    async def button_callback(interaction):
        await interaction.response.send_modal(NicknameChangeModal(interaction.user))
    button.callback = button_callback
    view = View()
    view.add_item(button)
    await channel.send("닉네임 변경 버튼이 활성화되었습니다.", view=view, delete_after=None)

# /차단, /차단목록, /차단해제 슬래시 명령어 정의
@bot.tree.command(name="차단", description="서버에서 사용자를 차단합니다.")
@app_commands.describe(user="차단할 사용자를 선택하세요.", reason="차단 사유를 입력하세요.")
async def ban_user(interaction: discord.Interaction, user: discord.User, reason: str = "사유 없음"):
    """사용자를 차단하는 슬래시 명령어입니다."""
    admin_role = interaction.guild.get_role(ad1)
    if admin_role not in interaction.user.roles:
        await interaction.response.send_message("이 명령어를 사용할 권한이 없습니다.", ephemeral=True)
        return

    guild = interaction.guild
    try:
        await guild.ban(user, reason=reason)
        ban_list[user.id] = {"nickname": user.name, "reason": reason}
        save_ban_list()  # 차단 목록을 MongoDB에 저장
        await interaction.response.send_message(f"사용자 {user.mention}가 차단되었습니다. 사유: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("차단할 권한이 없습니다.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"차단 중 오류가 발생했습니다: {e}", ephemeral=True)

@bot.tree.command(name="차단목록", description="차단된 사용자 목록을 확인합니다.")
async def ban_list_command(interaction: discord.Interaction):
    """차단된 사용자의 목록을 보여주는 슬래시 명령어입니다."""
    admin_role = interaction.guild.get_role(ad1)
    if admin_role not in interaction.user.roles:
        await interaction.response.send_message("이 명령어를 사용할 권한이 없습니다.", ephemeral=True)
        return

    if ban_list:
        ban_info = "\n".join(
            [f"ID: {user_id}, 마지막 별명: {info.get('last_nickname', '기록 없음')}, 사유: {info['reason']}"
             for user_id, info in ban_list.items()]
        )
        await interaction.response.send_message(f"차단된 사용자 목록:\n{ban_info}", ephemeral=True)
    else:
        await interaction.response.send_message("현재 차단된 사용자가 없습니다.", ephemeral=True)

@bot.tree.command(name="차단해제", description="차단된 사용자의 차단을 해제합니다.")
@app_commands.describe(nickname="차단 해제할 사용자의 마지막 별명을 입력하세요.")
async def unban_user(interaction: discord.Interaction, nickname: str):
    """차단된 사용자를 해제하는 슬래시 명령어입니다."""
    admin_role = interaction.guild.get_role(ad1)
    if admin_role not in interaction.user.roles:
        await interaction.response.send_message("이 명령어를 사용할 권한이 없습니다.", ephemeral=True)
        return

    user_id = next((uid for uid, info in ban_list.items() if info.get('last_nickname') == nickname), None)

    if not user_id:
        await interaction.response.send_message("해당 별명을 가진 차단된 사용자를 찾을 수 없습니다.", ephemeral=True)
        await show_ban_list(interaction)
        return

    guild = interaction.guild
    try:
        user = await bot.fetch_user(int(user_id))
        await guild.unban(user)
        del ban_list[int(user_id)]
        save_ban_list()  # 차단 목록을 MongoDB에 저장
        await interaction.response.send_message(f"사용자 {nickname}의 차단이 해제되었습니다.")
        await show_ban_list(interaction)
    except discord.NotFound:
        await interaction.response.send_message("해당 ID를 가진 사용자를 찾을 수 없습니다.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("차단 해제할 권한이 없습니다.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"차단 해제 중 오류가 발생했습니다: {e}", ephemeral=True)

# 차단 목록 표시 함수
async def show_ban_list(interaction: discord.Interaction):
    """현재 차단된 사용자의 목록을 보여줍니다."""
    if ban_list:
        ban_info = "\n".join(
            [f"ID: {user_id}, 마지막 별명: {info.get('last_nickname', '기록 없음')}, 사유: {info['reason']}"
             for user_id, info in ban_list.items()]
        )
        await interaction.followup.send(f"현재 차단된 사용자 목록:\n{ban_info}", ephemeral=True)
    else:
        await interaction.followup.send("현재 차단된 사용자가 없습니다.", ephemeral=True)

# 닉네임 중복 확인 함수
def is_duplicate_nickname(nickname, guild):
    """닉네임 중복 여부를 확인합니다."""
    normalized_nickname = nickname.lower()
    for member in guild.members:
        if member.display_name.lower() == normalized_nickname:
            return True
    return False

# 봇 실행
bot.run(TOKEN)  # 봇 실행 코드
