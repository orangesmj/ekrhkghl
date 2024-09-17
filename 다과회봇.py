# 첫 번째 부분: 라이브러리 임포트 및 초기 설정

import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import Button, View, Modal, TextInput
from datetime import datetime, timedelta, timezone
import os
from pymongo import MongoClient  # MongoDB 연결을 위한 패키지
from pytz import timezone
import random
import asyncio  # 비동기 처리를 위한 패키지

# 커피 사용 시 확률 테이블 수정
coffee_probabilities = {
    '쿠키꾸러미(소)': [(2, 30), (3, 25), (4, 25), (5, 20)],  # 기존 유지

    # 쿠키꾸러미(중): 예시로 설정한 기존 확률 사용
    '쿠키꾸러미(중)': [
        (5, 20),  # 확률: 20%
        (6, 25),  # 확률: 25%
        (7, 30),  # 확률: 30%
        (8, 15),  # 확률: 15%
        (9, 6),   # 확률: 6%
        (10, 4)   # 확률: 4%
    ],

    # 쿠키꾸러미(대): 설정된 확률 (총합 100%)
    '쿠키꾸러미(대)': [
        (10, 5), (11, 5), (12, 4), (13, 3), (14, 2), (15, 1),   # 10~15 총합 20%
        (16, 9), (17, 8), (18, 7), (19, 6), (20, 5),            # 16~20 총합 35%
        (21, 7), (22, 6), (23, 5), (24, 4), (25, 3),            # 21~25 총합 25%
        (26, 5), (27, 5), (28, 4), (29, 3), (30, 3)             # 26~30 총합 20%
    ]
}

# 환경 변수에서 Discord 봇 토큰과 MongoDB URL을 가져옵니다.
TOKEN = os.environ.get("BOT_TOKEN")  # Discord 봇 토큰을 환경 변수에서 가져옵니다.
mongo_url = os.environ.get("MONGO_URL")

# 환경 변수 검증
if not TOKEN:
    raise ValueError("환경 변수 BOT_TOKEN이 설정되지 않았습니다.")

if not mongo_url:
    raise ValueError("MongoDB URL이 설정되지 않았습니다.")

# MongoDB 연결 설정
client = MongoClient(mongo_url)

# 사용할 데이터베이스와 컬렉션 설정
db = client["DiscordBotDatabase"]  # 데이터베이스 이름 설정
nickname_collection = db["nickname_history"]  # 닉네임 변경 기록 컬렉션
ban_collection = db["ban_list"]  # 차단된 사용자 정보를 저장할 컬렉션
entry_collection = db["entry_list"]  # 입장 정보를 저장할 컬렉션
exit_collection = db["exit_list"]  # 퇴장 정보를 저장할 컬렉션
inventory_collection = db["inventory"]  # 유저의 재화(쿠키, 커피 등) 인벤토리
attendance_collection = db["attendance"]  # 출석 기록을 저장할 컬렉션
coffee_usage_collection = db["coffee_usage"]  # 커피 사용 기록을 저장할 컬렉션
active_raffles_collection = db["active_raffles"]  # 활성화된 추첨 이벤트를 저장할 컬렉션

# 봇의 인텐트를 설정합니다. 모든 필요한 인텐트를 활성화합니다.
intents = discord.Intents.default()
intents.members = True  # 멤버 관련 이벤트 허용
intents.message_content = True  # 메시지 콘텐츠 접근 허용
intents.messages = True  # 메시지 관련 이벤트 허용
intents.guilds = True  # 서버 관련 이벤트 허용
bot = commands.Bot(command_prefix='!', intents=intents)

# 닉네임 변경 기록 및 입장/퇴장 기록을 저장할 딕셔너리
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
MS_1 = 1281606690952708216  # 특정 메시지 ID 변수 (가입양식 관련)

Ch_3 = 1263829979398017159  # 닉네임 변경 채널 변수
Man = 1043194155515519048  # 남자 역할 ID
Woman = 1043891312384024576  # 여자 역할 ID
Sex = ['💙', '❤️']  # 역할 부여에 사용되는 이모지들
MS_2 = 1281654298500927635  # 닉네임 변경 양식에 대한 특정 메시지 ID
Role_4 = 1264571068874756149  # 특정 역할 ID 변수 (예: 닉네임 변경 완료 후 부여되는 역할)
Boost = 1234567890123456789  # Boost 역할 ID (예시, 실제 ID로 대체 필요)

# MongoDB와의 상호작용을 위한 함수들

def load_inventory(user_id):
    """유저의 인벤토리를 MongoDB에서 불러옵니다."""
    user_data = inventory_collection.find_one({"_id": user_id})
    if user_data:
        return user_data.get("items", {})
    else:
        # 인벤토리가 없을 경우 초기화
        inventory_collection.insert_one({"_id": user_id, "items": {"쿠키": 0, "커피": 0, "티켓": 0, "쿠키꾸러미(소)": 0, "쿠키꾸러미(중)": 0, "쿠키꾸러미(대)": 0}})
        return {"쿠키": 0, "커피": 0, "티켓": 0, "쿠키꾸러미(소)": 0, "쿠키꾸러미(중)": 0, "쿠키꾸러미(대)": 0}

def save_inventory(user_id, items):
    """유저의 인벤토리를 MongoDB에 저장합니다."""
    inventory_collection.update_one({"_id": user_id}, {"$set": {"items": items}}, upsert=True)

def load_nickname_history():
    """닉네임 변경 기록을 MongoDB에서 불러옵니다."""
    global nickname_history
    nickname_history = {int(k): v for k, v in nickname_collection.find()}
    print("닉네임 기록을 불러왔습니다.")

def save_nickname_history():
    """닉네임 변경 기록을 MongoDB에 저장합니다."""
    nickname_collection.delete_many({})  # 기존 기록 삭제
    for user_id, history in nickname_history.items():
        nickname_collection.insert_one({"_id": user_id, "history": history})

def load_ban_list():
    """차단 목록을 MongoDB에서 불러옵니다."""
    global ban_list
    ban_list = {int(k): v for k, v in ban_collection.find()}
    print("차단 목록을 불러왔습니다.")

def save_ban_list():
    """차단 목록을 MongoDB에 저장합니다."""
    ban_collection.delete_many({})  # 기존 목록 삭제
    for user_id, info in ban_list.items():
        ban_collection.insert_one({"_id": user_id, "nickname": info.get('nickname'), "last_nickname": info.get('last_nickname'), "reason": info.get('reason')})

def load_entry_list():
    """입장 기록을 MongoDB에서 불러옵니다."""
    global entry_list
    entry_list = {int(k): v for k, v in entry_collection.find()}
    print("입장 기록을 불러왔습니다.")

def save_entry_list():
    """입장 기록을 MongoDB에 저장합니다."""
    entry_collection.delete_many({})  # 기존 기록 삭제
    for user_id, info in entry_list.items():
        entry_collection.insert_one({"_id": user_id, "joined_at": info.get('joined_at')})

def load_exit_list():
    """퇴장 기록을 MongoDB에서 불러옵니다."""
    global exit_list
    exit_list = {int(k): v for k, v in exit_collection.find()}
    print("퇴장 기록을 불러왔습니다.")

def save_exit_list():
    """퇴장 기록을 MongoDB에 저장합니다."""
    exit_collection.delete_many({})  # 기존 기록 삭제
    for user_id, info in exit_list.items():
        exit_collection.insert_one({"_id": user_id, "left_at": info.get('left_at')})

# 리액션을 통한 역할 부여 처리
@bot.event
async def on_reaction_add(reaction, user):
    """특정 이모지에 반응하면 역할을 부여합니다."""
    if user.bot:
        return  # 봇의 반응은 무시
    
    if reaction.message.channel.id == Ch_1 and str(reaction.emoji) == Emoji_1:
        role = user.guild.get_role(Role_1)
        if role:
            await user.add_roles(role)
            await user.send(f"{role.name} 역할이 부여되었습니다.")
            # 반응을 제거하여 중복 반응 방지
            await reaction.remove(user)

@bot.event
async def on_reaction_remove(reaction, user):
    """특정 이모지의 반응을 제거하면 역할을 제거합니다."""
    if user.bot:
        return  # 봇의 반응은 무시
    
    if reaction.message.channel.id == Ch_1 and str(reaction.emoji) == Emoji_1:
        role = user.guild.get_role(Role_1)
        if role:
            await user.remove_roles(role)
            await user.send(f"{role.name} 역할이 제거되었습니다.")

# 가입 양식 및 닉네임 변경 모달 창 관련 코드

# 가입 양식 모달 창 정의
class JoinFormModal(Modal):
    """가입 양식을 작성할 수 있는 모달 창입니다."""
    def __init__(self, user):
        super().__init__(title="가입 양식")
        self.user = user

        # 모달 창에 텍스트 입력 필드 추가
        self.name = TextInput(label="이름", placeholder="이름을 입력하세요.", required=True)
        self.age = TextInput(label="나이", placeholder="나이를 입력하세요.", required=True)
        self.gender = TextInput(label="성별", placeholder="성별을 입력하세요.", required=True)
        
        self.add_item(self.name)
        self.add_item(self.age)
        self.add_item(self.gender)

    async def on_submit(self, interaction: discord.Interaction):
        """모달 창 제출 시 호출되는 함수입니다."""
        # 입력된 데이터 저장 (예시로 인벤토리에 저장)
        user_id = str(self.user.id)
        items = load_inventory(user_id)
        # 예시: 가입 양식 데이터를 인벤토리에 추가 (실제 구현 시 별도의 컬렉션 사용 권장)
        items["이름"] = self.name.value
        items["나이"] = self.age.value
        items["성별"] = self.gender.value
        save_inventory(user_id, items)
        
        # 가입 완료 메시지 전송 및 역할 부여
        await interaction.response.send_message(f"{self.user.mention}님, 가입이 완료되었습니다!", ephemeral=True)
        role = interaction.guild.get_role(Role_2)
        if role:
            await self.user.add_roles(role)
            await self.user.send(f"{role.name} 역할이 부여되었습니다.")

# 닉네임 변경 모달 창 정의
class NicknameChangeModal(Modal):
    """닉네임을 변경할 수 있는 모달 창입니다."""
    def __init__(self, user):
        super().__init__(title="닉네임 변경")
        self.user = user

        # 모달 창에 텍스트 입력 필드 추가
        self.new_nickname = TextInput(label="새 닉네임", placeholder="새 닉네임을 입력하세요.", required=True)
        
        self.add_item(self.new_nickname)

    async def on_submit(self, interaction: discord.Interaction):
        """모달 창 제출 시 호출되는 함수입니다."""
        new_nickname = self.new_nickname.value
        if is_duplicate_nickname(new_nickname, interaction.guild):
            await interaction.response.send_message("이미 사용 중인 닉네임입니다. 다른 닉네임을 선택해주세요.", ephemeral=True)
            return
        
        # 닉네임 변경
        old_nickname = self.user.display_name
        await self.user.edit(nick=new_nickname)
        
        # 닉네임 기록 업데이트
        user_id = self.user.id
        if user_id not in nickname_history:
            nickname_history[user_id] = []
        nickname_history[user_id].append({
            "nickname": new_nickname,
            "changed_at": get_kst_time()
        })
        save_nickname_history()
        
        await interaction.response.send_message(f"닉네임이 `{new_nickname}`(으)로 변경되었습니다!", ephemeral=True)

# 유저의 닉네임 중복 여부를 확인하는 함수
def is_duplicate_nickname(nickname, guild):
    """닉네임 중복 여부를 확인합니다."""
    normalized_nickname = nickname.lower()
    for member in guild.members:
        if member.display_name.lower() == normalized_nickname:
            return True
    return False

# 가입 양식 버튼 전송 함수
async def send_join_form_button(channel):
    """가입 양식 작성 버튼을 전송하는 함수입니다."""
    button = Button(label="가입 양식 작성", style=discord.ButtonStyle.primary)
    async def button_callback(interaction):
        await interaction.response.send_modal(JoinFormModal(interaction.user))
    button.callback = button_callback
    view = View()
    view.add_item(button)
    await channel.send("가입 양식 작성 버튼이 활성화되었습니다.", view=view, delete_after=None)

# 닉네임 변경 버튼 전송 함수
async def send_nickname_button(channel):
    """닉네임 변경 버튼을 전송하는 함수입니다."""
    button = Button(label="닉네임 변경", style=discord.ButtonStyle.primary)
    async def button_callback(interaction):
        await interaction.response.send_modal(NicknameChangeModal(interaction.user))
    button.callback = button_callback
    view = View()
    view.add_item(button)
    await channel.send("닉네임 변경 버튼이 활성화되었습니다.", view=view, delete_after=None)

# 세 번째 부분: 차단 목록 관리, 지급 및 회수 명령어, 인벤토리 확인, 쿠키 랭킹, 추첨 이벤트, 출석 체크, 가위바위보 이벤트 등

# (이전 대화에서 제공된 세 번째 부분의 코드가 이곳에 위치하게 됩니다.)

# 지급 명령어 예시 (/지급 명령어에 확률 적용 추가)
@bot.tree.command(name="지급", description="특정 유저에게 재화를 지급합니다.")
@app_commands.describe(user="재화를 지급할 사용자를 선택하세요.", item="지급할 아이템", amount="지급할 개수")
@app_commands.choices(
    item=[
        app_commands.Choice(name="쿠키", value="쿠키"),
        app_commands.Choice(name="커피", value="커피"),
        app_commands.Choice(name="티켓", value="티켓"),
        app_commands.Choice(name="쿠키꾸러미(소)", value="쿠키꾸러미(소)"),
        app_commands.Choice(name="쿠키꾸러미(중)", value="쿠키꾸러미(중)"),
        app_commands.Choice(name="쿠키꾸러미(대)", value="쿠키꾸러미(대)"),
    ]
)
async def give_item(interaction: discord.Interaction, user: discord.User, item: str, amount: int):
    """지급 명령어를 통해 특정 유저에게 아이템을 지급합니다."""
    admin_role = interaction.guild.get_role(ad1)
    if admin_role not in interaction.user.roles:
        await interaction.response.send_message("이 명령어를 사용할 권한이 없습니다.", ephemeral=True)
        return

    # 인벤토리에 아이템 추가
    user_id = str(user.id)
    items = load_inventory(user_id)
    valid_items = ["쿠키", "커피", "티켓", "쿠키꾸러미(소)", "쿠키꾸러미(중)", "쿠키꾸러미(대)"]
    if item not in valid_items:
        await interaction.response.send_message(f"지급할 수 없는 아이템입니다: {item}", ephemeral=True)
        return

    # 최대 획득량 설정
    max_amount = 9999  # 모든 아이템의 최대 획득량을 9999로 설정
    final_amount = min(amount, max_amount)

    # 확률 적용 (예: 쿠키꾸러미에 대한 확률 적용)
    if item in coffee_probabilities:
        probabilities = coffee_probabilities[item]
        choices, weights = zip(*probabilities)
        selected_cookies = random.choices(choices, weights=weights, k=final_amount)
        total_cookies = sum(selected_cookies)
        items["쿠키"] += total_cookies
        message = f"{user.display_name}에게 {item} {final_amount}개를 지급했습니다. 총 쿠키: {total_cookies}개"
    else:
        items[item] += final_amount
        message = f"{user.display_name}에게 {item} {final_amount}개를 지급했습니다."

    save_inventory(user_id, items)

    # 지급 완료 메시지
    await interaction.response.send_message(message, ephemeral=True)
    try:
        await user.send(message)
    except discord.Forbidden:
        await interaction.response.send_message(f"{user.display_name}님에게 DM을 보낼 수 없습니다.", ephemeral=True)

# 출석 체크 명령어
@bot.command(name="출석체크", description="출석 체크를 통해 보상을 받습니다.")
async def attendance_check(ctx):
    """출석 체크를 통해 보상을 받는 명령어입니다."""
    # 유저 ID와 현재 날짜
    user_id = str(ctx.author.id)
    today_date = datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')

    # 오늘 출석 체크 여부 확인
    attendance_record = attendance_collection.find_one({"_id": user_id, "last_date": today_date})
    if attendance_record:
        await ctx.send(f"{ctx.author.mention}, 오늘 이미 출석체크를 하셨습니다!", delete_after=5)
        return

    # 인벤토리 가져오기
    items = load_inventory(user_id)

    # 출석 기록 불러오기
    user_attendance = attendance_collection.find_one({"_id": user_id}) or {"streak": 0, "last_date": None}
    last_date = user_attendance.get("last_date")
    streak = user_attendance.get("streak", 0)

    # 연속 출석 처리: 어제와의 차이가 1일이면 연속 출석 증가
    if last_date and (datetime.strptime(today_date, '%Y-%m-%d') - datetime.strptime(last_date, '%Y-%m-%d')).days == 1:
        streak += 1
    else:
        streak = 1  # 연속 출석이 끊겼을 경우 초기화

    # 7일 연속 출석 시 커피 1개 지급
    if streak == 7:
        items["커피"] = items.get("커피", 0) + 1
        await ctx.send(f"감사합니다. {ctx.author.mention}님! 7일 연속 출석하여 {Coffee} 1개를 증정해 드렸습니다. 인벤토리를 확인해주세요!")
        streak = 0  # 7일 달성 시 초기화

    # 기본 보상 지급
    items["쿠키꾸러미(소)"] += 2  # 기본 보상 Cookie_S 2개 지급
    # Boost 역할이 있을 경우 추가 보상
    boost_role = ctx.guild.get_role(Boost)
    if boost_role in ctx.author.roles:
        items["쿠키꾸러미(중)"] += 1  # Boost 역할이 있을 경우 Cookie_M 1개 추가 지급

    # 인벤토리 저장
    save_inventory(user_id, items)

    # 출석 기록 저장
    attendance_collection.update_one(
        {"_id": user_id},
        {"$set": {"last_date": today_date, "streak": streak}},
        upsert=True
    )

    # 보상 지급 완료 메시지
    if boost_role in ctx.author.roles:
        await ctx.send(f"{ctx.author.mention}님! 오늘도 와주셔서 감사합니다. {Cookie_S} 2개와 {Cookie_M} 1개를 증정해 드렸습니다. 인벤토리를 확인해주세요!")
    else:
        await ctx.send(f"{ctx.author.mention}님! 오늘도 와주셔서 감사합니다. {Cookie_S} 2개를 증정해 드렸습니다. 인벤토리를 확인해주세요!")

# 가위바위보 이벤트 클래스 정의
class RockPaperScissorsView(View):
    """가위바위보 이벤트를 처리하는 뷰 클래스입니다."""
    def __init__(self):
        super().__init__(timeout=3600)  # 1시간 동안 반응 대기
        self.participants = {}  # 참여자 딕셔너리: user_id -> choice

    @discord.ui.button(label="가위", style=discord.ButtonStyle.primary, emoji='✂️')  # rkdnl 이모지 대체
    async def scissors(self, interaction: discord.Interaction, button: Button):
        """가위를 선택했을 때 호출되는 함수입니다."""
        await self.process_choice(interaction, '가위')

    @discord.ui.button(label="바위", style=discord.ButtonStyle.primary, emoji='🪨')  # qkdnl 이모지 대체
    async def rock(self, interaction: discord.Interaction, button: Button):
        """바위를 선택했을 때 호출되는 함수입니다."""
        await self.process_choice(interaction, '바위')

    @discord.ui.button(label="보", style=discord.ButtonStyle.primary, emoji='📄')  # qh 이모지 대체
    async def paper(self, interaction: discord.Interaction, button: Button):
        """보를 선택했을 때 호출되는 함수입니다."""
        await self.process_choice(interaction, '보')

    async def process_choice(self, interaction: discord.Interaction, choice):
        """사용자의 선택을 처리하는 함수입니다."""
        user_id = interaction.user.id
        if user_id in self.participants:
            await interaction.response.send_message("이미 참여하셨습니다.", ephemeral=True)
            return

        # 인벤토리에서 쿠키 5개 소진
        items = load_inventory(str(user_id))
        if items.get("쿠키", 0) < 5:
            await interaction.response.send_message("보유한 쿠키가 5개 이상 필요합니다.", ephemeral=True)
            return

        # 쿠키 소진 및 참여 등록
        items["쿠키"] -= 5
        save_inventory(str(user_id), items)

        self.participants[user_id] = choice
        await interaction.response.send_message(f"'{choice}'을(를) 선택하셨습니다!", ephemeral=True)

    async def on_timeout(self):
        """뷰가 타임아웃되었을 때 호출되는 함수입니다."""
        # 이벤트 종료 후 결과 처리
        if not self.participants:
            return  # 참여자가 없을 경우 종료

        # 랜덤으로 봇의 선택
        bot_choice = random.choice(['가위', '바위', '보'])

        # 결과 채널 가져오기
        result_channel = bot.get_channel(123456789012345678)  # rkdnlqkdnlqh_result 대체
        if not result_channel:
            result_channel = bot.get_channel(123456789012345679)  # cncja_result 대체

        results = []
        for user_id, choice in self.participants.items():
            outcome = determine_rps_outcome(choice, bot_choice)
            user = bot.get_user(user_id)
            if user:
                if outcome == "win":
                    # 쿠키꾸러미(소) 4개 지급
                    items = load_inventory(str(user_id))
                    items["쿠키꾸러미(소)"] += 4
                    save_inventory(str(user_id), items)
                    results.append(f"{user.display_name}님이 이겼습니다! 쿠키꾸러미(소) 4개가 지급되었습니다.")
                elif outcome == "lose":
                    results.append(f"{user.display_name}님이 졌습니다!")
                else:
                    results.append(f"{user.display_name}님이 비겼습니다!")

        # 봇의 선택과 함께 결과 메시지 전송
        embed = discord.Embed(title="가위바위보 결과", description=f"봇의 선택: {bot_choice}", color=discord.Color.blue())
        embed.add_field(name="결과", value="\n".join(results), inline=False)
        await result_channel.send(embed=embed)

# 승리 로직 결정 함수
def determine_rps_outcome(user_choice, bot_choice):
    """사용자의 선택과 봇의 선택을 비교하여 승패를 결정합니다."""
    rules = {
        '가위': '보',    # 가위는 보를 이김
        '바위': '가위',  # 바위는 가위를 이김
        '보': '바위'     # 보는 바위를 이김
    }

    if user_choice == bot_choice:
        return "draw"
    elif rules[user_choice] == bot_choice:
        return "win"
    else:
        return "lose"

# 매일 오후 9시에 가위바위보 이벤트를 시작하는 태스크
@tasks.loop(hours=24)
async def rps_event():
    """매일 오후 9시에 가위바위보 이벤트를 시작합니다."""
    # 현재 시간을 한국 표준 시간으로 가져오기
    now = datetime.now(timezone('Asia/Seoul'))
    # 오늘 오후 9시 설정
    target_time = now.replace(hour=21, minute=0, second=0, microsecond=0)
    if now > target_time:
        # 이미 오후 9시를 지나갔으면 다음 날 오후 9시로 설정
        target_time += timedelta(days=1)
    # 대기 시간 계산
    wait_seconds = (target_time - now).total_seconds()
    await asyncio.sleep(wait_seconds)

    # 이벤트 채널 가져오기
    event_channel = bot.get_channel(123456789012345678)  # rkdnlqkdnlqh 대체
    if not event_channel:
        event_channel = bot.get_channel(123456789012345679)  # cncja_result 대체

    # 이벤트 메시지 전송
    embed = discord.Embed(
        title="가위바위보 이벤트",
        description=(
            "가위바위보 이벤트가 시작되었습니다!\n"
            "가위바위보 시 쿠키가 5개 소진됩니다.\n"
            "가위바위보 승리 시, 쿠키꾸러미(소)가 4개 지급됩니다.\n"
            "가위바위보는 아래 버튼을 눌러 자동 참여됩니다. (중복 참여 불가입니다.)"
        ),
        color=discord.Color.green()
    )
    message = await event_channel.send(embed=embed)

    # 버튼 추가 및 이벤트 시작
    view = RockPaperScissorsView()
    await event_channel.send("가위바위보에 참여하려면 아래 버튼을 클릭하세요!", view=view)

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

    # 주기적인 태스크 시작
    delete_messages_2.start()  # 주기적인 메시지 삭제 태스크 시작
    rps_event.start()          # 가위바위보 이벤트 태스크 시작

    # 봇이 활성화되었음을 알림
    channel = bot.get_channel(123456789012345678)  # open_channel_id 대체
    if channel:
        await channel.send('봇이 활성화되었습니다!')

    # 활성화된 추첨 이벤트 재개
    await resume_active_raffles()

# 봇 재부팅 시 활성화된 추첨 이벤트 재개
async def resume_active_raffles():
    """봇이 재부팅되었을 때 활성화된 추첨을 다시 시작합니다."""
    active_raffles = list(active_raffles_collection.find())
    for raffle in active_raffles:
        raffle_id = raffle["raffle_id"]
        item = raffle["item"]
        consume_cookies = raffle["consume_cookies"]
        duration = (raffle["end_time"] - datetime.now(timezone('Asia/Seoul'))).total_seconds()
        prize_amount = raffle["prize_amount"]
        participants = raffle.get("participants", [])

        if duration <= 0:
            # 추첨 시간이 이미 지났다면 결과 발표
            if participants:
                winners = random.sample(participants, min(prize_amount, len(participants)))
                cncja_channel = bot.get_channel(123456789012345678)  # cncja 대체
                if cncja_channel:
                    for winner_id in winners:
                        winner = bot.get_user(winner_id)
                        if winner:
                            items = load_inventory(str(winner.id))
                            items[item] += prize_amount
                            save_inventory(str(winner.id), items)
                            try:
                                await cncja_channel.send(f"축하합니다! {winner.display_name}님이 {item} {prize_amount}개를 획득하셨습니다!")
                            except discord.HTTPException:
                                pass  # 메시지 전송 실패 시 무시
            else:
                cncja_channel = bot.get_channel(123456789012345678)  # cncja 대체
                if cncja_channel:
                    await cncja_channel.send("참여자가 없어 추첨이 취소되었습니다.", delete_after=5)
            # MongoDB에서 추첨 상태 삭제
            active_raffles_collection.delete_one({"raffle_id": raffle_id})
            continue

        # 추첨 메시지 재생성
        cncja_channel = bot.get_channel(123456789012345678)  # cncja 대체
        if not cncja_channel:
            continue  # 추첨 채널을 찾을 수 없으면 건너뜀

        embed = discord.Embed(
            title="추첨 이벤트 진행 중!",
            description=(
                f"{item} {prize_amount}개가 걸려 있습니다!\n"
                f"참여 시 쿠키 {consume_cookies}개가 소모됩니다.\n"
                f"종료 시간: {raffle['end_time']}\n"
                f"🟢 이모지를 눌러 참여하세요!"
            ),
            color=discord.Color.gold()
        )
        message = await cncja_channel.send(embed=embed)
        await message.add_reaction("🟢")  # 추첨 참여 이모지 추가

        # 남은 시간 동안 참여자 수집
        async def collect_participants_resume():
            try:
                while datetime.now(timezone('Asia/Seoul')) < raffle["end_time"]:
                    reaction, user = await bot.wait_for(
                        'reaction_add',
                        timeout=(raffle["end_time"] - datetime.now(timezone('Asia/Seoul'))).total_seconds(),
                        check=lambda r, u: str(r.emoji) == "🟢" and r.message.id == message.id and not u.bot
                    )
                    # 인벤토리에서 쿠키 소모
                    items = load_inventory(str(user.id))
                    if items.get("쿠키", 0) < consume_cookies:
                        await cncja_channel.send(f"{user.display_name}님, 쿠키가 부족하여 참여할 수 없습니다.", delete_after=5)
                        continue

                    # 쿠키 소진 및 참여 등록
                    items["쿠키"] -= consume_cookies
                    save_inventory(str(user.id), items)
                    if user.id not in raffle["participants"]:
                        raffle["participants"].append(user.id)
                        # MongoDB에 참여자 업데이트
                        active_raffles_collection.update_one(
                            {"raffle_id": raffle_id},
                            {"$addToSet": {"participants": user.id}},
                            upsert=True
                        )
                        await cncja_channel.send(f"{user.display_name}님이 추첨에 참여했습니다. 쿠키 {consume_cookies}개가 소진됩니다.", delete_after=5)
            except asyncio.TimeoutError:
                pass  # 추첨 시간이 종료됨

        await collect_participants_resume()

        # 추첨 종료 후 결과 발표
        if raffle["participants"]:
            winners = random.sample(raffle["participants"], min(prize_amount, len(raffle["participants"])))
            for winner_id in winners:
                winner = bot.get_user(winner_id)
                if winner:
                    items = load_inventory(str(winner.id))
                    items[item] += prize_amount
                    save_inventory(str(winner.id), items)
                    try:
                        await cncja_channel.send(f"축하합니다! {winner.display_name}님이 {item} {prize_amount}개를 획득하셨습니다!")
                    except discord.HTTPException:
                        pass  # 메시지 전송 실패 시 무시
        else:
            if cncja_channel:
                await cncja_channel.send("참여자가 없어 추첨이 취소되었습니다.", delete_after=5)

        # MongoDB에서 추첨 상태 삭제
        active_raffles_collection.delete_one({"raffle_id": raffle_id})

        # 추첨 메시지 자동 삭제
        await asyncio.sleep(5)  # 5초 대기 후 삭제
        try:
            await message.delete()  # 추첨 이벤트 메시지 삭제
        except discord.HTTPException:
            pass  # 메시지 삭제 실패 시 무시

# 지급 명령어 예시 (/지급 명령어에 확률 적용 추가)
@bot.tree.command(name="지급", description="특정 유저에게 재화를 지급합니다.")
@app_commands.describe(user="재화를 지급할 사용자를 선택하세요.", item="지급할 아이템", amount="지급할 개수")
@app_commands.choices(
    item=[
        app_commands.Choice(name="쿠키", value="쿠키"),
        app_commands.Choice(name="커피", value="커피"),
        app_commands.Choice(name="티켓", value="티켓"),
        app_commands.Choice(name="쿠키꾸러미(소)", value="쿠키꾸러미(소)"),
        app_commands.Choice(name="쿠키꾸러미(중)", value="쿠키꾸러미(중)"),
        app_commands.Choice(name="쿠키꾸러미(대)", value="쿠키꾸러미(대)"),
    ]
)
async def give_item(interaction: discord.Interaction, user: discord.User, item: str, amount: int):
    """지급 명령어를 통해 특정 유저에게 아이템을 지급합니다."""
    admin_role = interaction.guild.get_role(ad1)
    if admin_role not in interaction.user.roles:
        await interaction.response.send_message("이 명령어를 사용할 권한이 없습니다.", ephemeral=True)
        return

    # 인벤토리에 아이템 추가
    user_id = str(user.id)
    items = load_inventory(user_id)
    valid_items = ["쿠키", "커피", "티켓", "쿠키꾸러미(소)", "쿠키꾸러미(중)", "쿠키꾸러미(대)"]
    if item not in valid_items:
        await interaction.response.send_message(f"지급할 수 없는 아이템입니다: {item}", ephemeral=True)
        return

    # 최대 획득량 설정
    max_amount = 9999  # 모든 아이템의 최대 획득량을 9999로 설정
    final_amount = min(amount, max_amount)

    # 확률 적용 (예: 쿠키꾸러미에 대한 확률 적용)
    if item in coffee_probabilities:
        probabilities = coffee_probabilities[item]
        choices, weights = zip(*probabilities)
        selected_cookies = random.choices(choices, weights=weights, k=final_amount)
        total_cookies = sum(selected_cookies)
        items["쿠키"] += total_cookies
        message = f"{user.display_name}에게 {item} {final_amount}개를 지급했습니다. 총 쿠키: {total_cookies}개"
    else:
        items[item] += final_amount
        message = f"{user.display_name}에게 {item} {final_amount}개를 지급했습니다."

    save_inventory(user_id, items)

    # 지급 완료 메시지
    await interaction.response.send_message(message, ephemeral=True)
    try:
        await user.send(message)
    except discord.Forbidden:
        await interaction.response.send_message(f"{user.display_name}님에게 DM을 보낼 수 없습니다.", ephemeral=True)

# 출석 체크 명령어
@bot.command(name="출석체크", description="출석 체크를 통해 보상을 받습니다.")
async def attendance_check(ctx):
    """출석 체크를 통해 보상을 받는 명령어입니다."""
    # 유저 ID와 현재 날짜
    user_id = str(ctx.author.id)
    today_date = datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')

    # 오늘 출석 체크 여부 확인
    attendance_record = attendance_collection.find_one({"_id": user_id, "last_date": today_date})
    if attendance_record:
        await ctx.send(f"{ctx.author.mention}, 오늘 이미 출석체크를 하셨습니다!", delete_after=5)
        return

    # 인벤토리 가져오기
    items = load_inventory(user_id)

    # 출석 기록 불러오기
    user_attendance = attendance_collection.find_one({"_id": user_id}) or {"streak": 0, "last_date": None}
    last_date = user_attendance.get("last_date")
    streak = user_attendance.get("streak", 0)

    # 연속 출석 처리: 어제와의 차이가 1일이면 연속 출석 증가
    if last_date and (datetime.strptime(today_date, '%Y-%m-%d') - datetime.strptime(last_date, '%Y-%m-%d')).days == 1:
        streak += 1
    else:
        streak = 1  # 연속 출석이 끊겼을 경우 초기화

    # 7일 연속 출석 시 커피 1개 지급
    if streak == 7:
        items["커피"] = items.get("커피", 0) + 1
        await ctx.send(f"감사합니다. {ctx.author.mention}님! 7일 연속 출석하여 커피 1개를 증정해 드렸습니다. 인벤토리를 확인해주세요!")
        streak = 0  # 7일 달성 시 초기화

    # 기본 보상 지급
    items["쿠키꾸러미(소)"] += 2  # 기본 보상 쿠키꾸러미(소) 2개 지급
    # Boost 역할이 있을 경우 추가 보상
    boost_role = ctx.guild.get_role(Boost)
    if boost_role in ctx.author.roles:
        items["쿠키꾸러미(중)"] += 1  # Boost 역할이 있을 경우 쿠키꾸러미(중) 1개 추가 지급

    # 인벤토리 저장
    save_inventory(user_id, items)

    # 출석 기록 저장
    attendance_collection.update_one(
        {"_id": user_id},
        {"$set": {"last_date": today_date, "streak": streak}},
        upsert=True
    )

    # 보상 지급 완료 메시지
    if boost_role in ctx.author.roles:
        await ctx.send(f"{ctx.author.mention}님! 오늘도 와주셔서 감사합니다. 쿠키꾸러미(소) 2개와 쿠키꾸러미(중) 1개를 증정해 드렸습니다. 인벤토리를 확인해주세요!")
    else:
        await ctx.send(f"{ctx.author.mention}님! 오늘도 와주셔서 감사합니다. 쿠키꾸러미(소) 2개를 증정해 드렸습니다. 인벤토리를 확인해주세요!")

# 가위바위보 이벤트 클래스 정의
class RockPaperScissorsView(View):
    """가위바위보 이벤트를 처리하는 뷰 클래스입니다."""
    def __init__(self):
        super().__init__(timeout=3600)  # 1시간 동안 반응 대기
        self.participants = {}  # 참여자 딕셔너리: user_id -> choice

    @discord.ui.button(label="가위", style=discord.ButtonStyle.primary, emoji='✂️')  # 가위 이모지
    async def scissors(self, interaction: discord.Interaction, button: Button):
        """가위를 선택했을 때 호출되는 함수입니다."""
        await self.process_choice(interaction, '가위')

    @discord.ui.button(label="바위", style=discord.ButtonStyle.primary, emoji='🪨')  # 바위 이모지
    async def rock(self, interaction: discord.Interaction, button: Button):
        """바위를 선택했을 때 호출되는 함수입니다."""
        await self.process_choice(interaction, '바위')

        @discord.ui.button(label="보", style=discord.ButtonStyle.primary, emoji='📄')  # 보 이모지
        async def paper(self, interaction: discord.Interaction, button: Button):
            """보를 선택했을 때 호출되는 함수입니다."""
            await self.process_choice(interaction, '보')
    
        async def process_choice(self, interaction: discord.Interaction, choice):
            """사용자의 선택을 처리하는 함수입니다."""
            user_id = interaction.user.id
            if user_id in self.participants:
                await interaction.response.send_message("이미 참여하셨습니다.", ephemeral=True)
                return
    
            # 인벤토리에서 쿠키 5개 소진
            items = load_inventory(str(user_id))
            if items.get("쿠키", 0) < 5:
                await interaction.response.send_message("보유한 쿠키가 5개 이상 필요합니다.", ephemeral=True)
                return
    
            # 쿠키 소진 및 참여 등록
            items["쿠키"] -= 5
            save_inventory(str(user_id), items)
    
            self.participants[user_id] = choice
            await interaction.response.send_message(f"'{choice}'을(를) 선택하셨습니다!", ephemeral=True)
    
        async def on_timeout(self):
            """뷰가 타임아웃되었을 때 호출되는 함수입니다."""
            # 이벤트 종료 후 결과 처리
            if not self.participants:
                return  # 참여자가 없을 경우 종료
    
            # 랜덤으로 봇의 선택
            bot_choice = random.choice(['가위', '바위', '보'])
    
            # 결과 채널 가져오기 (채널 ID를 실제로 사용할 채널 ID로 대체하세요)
            result_channel = bot.get_channel(123456789012345678)  # rkdnlqkdnlqh_result 대체
            if not result_channel:
                result_channel = bot.get_channel(123456789012345679)  # cncja_result 대체
    
            results = []
            for user_id, choice in self.participants.items():
                outcome = determine_rps_outcome(choice, bot_choice)
                user = bot.get_user(user_id)
                if user:
                    if outcome == "win":
                        # 쿠키꾸러미(소) 4개 지급
                        items = load_inventory(str(user_id))
                        items["쿠키꾸러미(소)"] += 4
                        save_inventory(str(user_id), items)
                        results.append(f"{user.display_name}님이 이겼습니다! 쿠키꾸러미(소) 4개가 지급되었습니다.")
                    elif outcome == "lose":
                        results.append(f"{user.display_name}님이 졌습니다!")
                    else:
                        results.append(f"{user.display_name}님이 비겼습니다!")
    
            # 봇의 선택과 함께 결과 메시지 전송
            embed = discord.Embed(title="가위바위보 결과", description=f"봇의 선택: {bot_choice}", color=discord.Color.blue())
            embed.add_field(name="결과", value="\n".join(results), inline=False)
            await result_channel.send(embed=embed)
    
    # 승리 로직 결정 함수
    def determine_rps_outcome(user_choice, bot_choice):
        """사용자의 선택과 봇의 선택을 비교하여 승패를 결정합니다."""
        rules = {
            '가위': '보',    # 가위는 보를 이김
            '바위': '가위',  # 바위는 가위를 이김
            '보': '바위'     # 보는 바위를 이김
        }
    
        if user_choice == bot_choice:
            return "draw"
        elif rules[user_choice] == bot_choice:
            return "win"
        else:
            return "lose"
    
    # 매일 오후 9시에 가위바위보 이벤트를 시작하는 태스크
    @tasks.loop(hours=24)
    async def rps_event():
        """매일 오후 9시에 가위바위보 이벤트를 시작합니다."""
        # 현재 시간을 한국 표준 시간으로 가져오기
        now = datetime.now(timezone('Asia/Seoul'))
        # 오늘 오후 9시 설정
        target_time = now.replace(hour=21, minute=0, second=0, microsecond=0)
        if now > target_time:
            # 이미 오후 9시를 지나갔으면 다음 날 오후 9시로 설정
            target_time += timedelta(days=1)
        # 대기 시간 계산
        wait_seconds = (target_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)
    
        # 이벤트 채널 가져오기 (채널 ID를 실제로 사용할 채널 ID로 대체하세요)
        event_channel = bot.get_channel(123456789012345678)  # rkdnlqkdnlqh 대체
        if not event_channel:
            event_channel = bot.get_channel(123456789012345679)  # cncja_result 대체
    
        # 이벤트 메시지 전송
        embed = discord.Embed(
            title="가위바위보 이벤트",
            description=(
                "가위바위보 이벤트가 시작되었습니다!\n"
                "가위바위보 시 쿠키가 5개 소진됩니다.\n"
                "가위바위보 승리 시, 쿠키꾸러미(소)가 4개 지급됩니다.\n"
                "가위바위보는 아래 버튼을 눌러 자동 참여됩니다. (중복 참여 불가입니다.)"
            ),
            color=discord.Color.green()
        )
        message = await event_channel.send(embed=embed)
    
        # 버튼 추가 및 이벤트 시작
        view = RockPaperScissorsView()
        await event_channel.send("가위바위보에 참여하려면 아래 버튼을 클릭하세요!", view=view)
    
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
    
        # 주기적인 태스크 시작
        # delete_messages_2.start()  # 주기적인 메시지 삭제 태스크 시작 (이 함수가 정의되지 않았습니다. 필요 시 추가하세요)
        rps_event.start()          # 가위바위보 이벤트 태스크 시작
    
        # 봇이 활성화되었음을 알림 (채널 ID를 실제로 사용할 채널 ID로 대체하세요)
        channel = bot.get_channel(123456789012345678)  # open_channel_id 대체
        if channel:
            await channel.send('봇이 활성화되었습니다!')
    
        # 활성화된 추첨 이벤트 재개
        # await resume_active_raffles()  # 이 함수가 정의되어 있어야 합니다. 필요 시 추가하세요
    
    # 봇 재부팅 시 활성화된 추첨 이벤트 재개
    async def resume_active_raffles():
        """봇이 재부팅되었을 때 활성화된 추첨을 다시 시작합니다."""
        active_raffles = list(active_raffles_collection.find())
        for raffle in active_raffles:
            raffle_id = raffle["raffle_id"]
            item = raffle["item"]
            consume_cookies = raffle["consume_cookies"]
            duration = (raffle["end_time"] - datetime.now(timezone('Asia/Seoul'))).total_seconds()
            prize_amount = raffle["prize_amount"]
            participants = raffle.get("participants", [])
    
            if duration <= 0:
                # 추첨 시간이 이미 지났다면 결과 발표
                if participants:
                    winners = random.sample(participants, min(prize_amount, len(participants)))
                    cncja_channel = bot.get_channel(123456789012345678)  # cncja 대체
                    if cncja_channel:
                        for winner_id in winners:
                            winner = bot.get_user(winner_id)
                            if winner:
                                items = load_inventory(str(winner.id))
                                items[item] += prize_amount
                                save_inventory(str(winner.id), items)
                                try:
                                    await cncja_channel.send(f"축하합니다! {winner.display_name}님이 {item} {prize_amount}개를 획득하셨습니다!")
                                except discord.HTTPException:
                                    pass  # 메시지 전송 실패 시 무시
                else:
                    cncja_channel = bot.get_channel(123456789012345678)  # cncja 대체
                    if cncja_channel:
                        await cncja_channel.send("참여자가 없어 추첨이 취소되었습니다.", delete_after=5)
                # MongoDB에서 추첨 상태 삭제
                active_raffles_collection.delete_one({"raffle_id": raffle_id})
                continue
    
            # 추첨 메시지 재생성
            cncja_channel = bot.get_channel(123456789012345678)  # cncja 대체
            if not cncja_channel:
                continue  # 추첨 채널을 찾을 수 없으면 건너뜀
    
            embed = discord.Embed(
                title="추첨 이벤트 진행 중!",
                description=(
                    f"{item} {prize_amount}개가 걸려 있습니다!\n"
                    f"참여 시 쿠키 {consume_cookies}개가 소모됩니다.\n"
                    f"종료 시간: {raffle['end_time']}\n"
                    f"🟢 이모지를 눌러 참여하세요!"
                ),
                color=discord.Color.gold()
            )
            message = await cncja_channel.send(embed=embed)
            await message.add_reaction("🟢")  # 추첨 참여 이모지 추가
    
            # 남은 시간 동안 참여자 수집
            async def collect_participants_resume():
                try:
                    while datetime.now(timezone('Asia/Seoul')) < raffle["end_time"]:
                        reaction, user = await bot.wait_for(
                            'reaction_add',
                            timeout=(raffle["end_time"] - datetime.now(timezone('Asia/Seoul'))).total_seconds(),
                            check=lambda r, u: str(r.emoji) == "🟢" and r.message.id == message.id and not u.bot
                        )
                        # 인벤토리에서 쿠키 소모
                        items = load_inventory(str(user.id))
                        if items.get("쿠키", 0) < consume_cookies:
                            await cncja_channel.send(f"{user.display_name}님, 쿠키가 부족하여 참여할 수 없습니다.", delete_after=5)
                            continue
    
                        # 쿠키 소진 및 참여 등록
                        items["쿠키"] -= consume_cookies
                        save_inventory(str(user.id), items)
                        if user.id not in raffle["participants"]:
                            raffle["participants"].append(user.id)
                            # MongoDB에 참여자 업데이트
                            active_raffles_collection.update_one(
                                {"raffle_id": raffle_id},
                                {"$addToSet": {"participants": user.id}},
                                upsert=True
                            )
                            await cncja_channel.send(f"{user.display_name}님이 추첨에 참여했습니다. 쿠키 {consume_cookies}개가 소진됩니다.", delete_after=5)
                except asyncio.TimeoutError:
                    pass  # 추첨 시간이 종료됨
    
            await collect_participants_resume()
    
            # 추첨 종료 후 결과 발표
            if raffle["participants"]:
                winners = random.sample(raffle["participants"], min(prize_amount, len(raffle["participants"])))
                for winner_id in winners:
                    winner = bot.get_user(winner_id)
                    if winner:
                        items = load_inventory(str(winner.id))
                        items[item] += prize_amount
                        save_inventory(str(winner.id), items)
                        try:
                            await cncja_channel.send(f"축하합니다! {winner.display_name}님이 {item} {prize_amount}개를 획득하셨습니다!")
                        except discord.HTTPException:
                            pass  # 메시지 전송 실패 시 무시
            else:
                if cncja_channel:
                    await cncja_channel.send("참여자가 없어 추첨이 취소되었습니다.", delete_after=5)
    
            # MongoDB에서 추첨 상태 삭제
            active_raffles_collection.delete_one({"raffle_id": raffle_id})
    
            # 추첨 메시지 자동 삭제
            await asyncio.sleep(5)  # 5초 대기 후 삭제
            try:
                await message.delete()  # 추첨 이벤트 메시지 삭제
            except discord.HTTPException:
                pass  # 메시지 삭제 실패 시 무시
    
    # 지급 명령어 예시 (/지급 명령어에 확률 적용 추가)
    @bot.tree.command(name="지급", description="특정 유저에게 재화를 지급합니다.")
    @app_commands.describe(user="재화를 지급할 사용자를 선택하세요.", item="지급할 아이템", amount="지급할 개수")
    @app_commands.choices(
        item=[
            app_commands.Choice(name="쿠키", value="쿠키"),
            app_commands.Choice(name="커피", value="커피"),
            app_commands.Choice(name="티켓", value="티켓"),
            app_commands.Choice(name="쿠키꾸러미(소)", value="쿠키꾸러미(소)"),
            app_commands.Choice(name="쿠키꾸러미(중)", value="쿠키꾸러미(중)"),
            app_commands.Choice(name="쿠키꾸러미(대)", value="쿠키꾸러미(대)"),
        ]
    )
    async def give_item(interaction: discord.Interaction, user: discord.User, item: str, amount: int):
        """지급 명령어를 통해 특정 유저에게 아이템을 지급합니다."""
        admin_role = interaction.guild.get_role(ad1)
        if admin_role not in interaction.user.roles:
            await interaction.response.send_message("이 명령어를 사용할 권한이 없습니다.", ephemeral=True)
            return
    
        # 인벤토리에 아이템 추가
        user_id = str(user.id)
        items = load_inventory(user_id)
        valid_items = ["쿠키", "커피", "티켓", "쿠키꾸러미(소)", "쿠키꾸러미(중)", "쿠키꾸러미(대)"]
        if item not in valid_items:
            await interaction.response.send_message(f"지급할 수 없는 아이템입니다: {item}", ephemeral=True)
            return
    
        # 최대 획득량 설정
        max_amount = 9999  # 모든 아이템의 최대 획득량을 9999로 설정
        final_amount = min(amount, max_amount)
    
        # 확률 적용 (예: 쿠키꾸러미에 대한 확률 적용)
        if item in coffee_probabilities:
            probabilities = coffee_probabilities[item]
            choices, weights = zip(*probabilities)
            selected_cookies = random.choices(choices, weights=weights, k=final_amount)
            total_cookies = sum(selected_cookies)
            items["쿠키"] += total_cookies
            message = f"{user.display_name}에게 {item} {final_amount}개를 지급했습니다. 총 쿠키: {total_cookies}개"
        else:
            items[item] += final_amount
            message = f"{user.display_name}에게 {item} {final_amount}개를 지급했습니다."
    
        save_inventory(user_id, items)
    
        # 지급 완료 메시지
        await interaction.response.send_message(message, ephemeral=True)
        try:
            await user.send(message)
        except discord.Forbidden:
            await interaction.response.send_message(f"{user.display_name}님에게 DM을 보낼 수 없습니다.", ephemeral=True)
    
    # 출석 체크 명령어
    @bot.command(name="출석체크", description="출석 체크를 통해 보상을 받습니다.")
    async def attendance_check(ctx):
        """출석 체크를 통해 보상을 받는 명령어입니다."""
        # 유저 ID와 현재 날짜
        user_id = str(ctx.author.id)
        today_date = datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
    
        # 오늘 출석 체크 여부 확인
        attendance_record = attendance_collection.find_one({"_id": user_id, "last_date": today_date})
        if attendance_record:
            await ctx.send(f"{ctx.author.mention}, 오늘 이미 출석체크를 하셨습니다!", delete_after=5)
            return
    
        # 인벤토리 가져오기
        items = load_inventory(user_id)
    
        # 출석 기록 불러오기
        user_attendance = attendance_collection.find_one({"_id": user_id}) or {"streak": 0, "last_date": None}
        last_date = user_attendance.get("last_date")
        streak = user_attendance.get("streak", 0)
    
        # 연속 출석 처리: 어제와의 차이가 1일이면 연속 출석 증가
        if last_date and (datetime.strptime(today_date, '%Y-%m-%d') - datetime.strptime(last_date, '%Y-%m-%d')).days == 1:
            streak += 1
        else:
            streak = 1  # 연속 출석이 끊겼을 경우 초기화
    
        # 7일 연속 출석 시 커피 1개 지급
        if streak == 7:
            items["커피"] = items.get("커피", 0) + 1
            await ctx.send(f"감사합니다. {ctx.author.mention}님! 7일 연속 출석하여 커피 1개를 증정해 드렸습니다. 인벤토리를 확인해주세요!")
            streak = 0  # 7일 달성 시 초기화
    
        # 기본 보상 지급
        items["쿠키꾸러미(소)"] += 2  # 기본 보상 쿠키꾸러미(소) 2개 지급
        # Boost 역할이 있을 경우 추가 보상
        boost_role = ctx.guild.get_role(Boost)
        if boost_role in ctx.author.roles:
            items["쿠키꾸러미(중)"] += 1  # Boost 역할이 있을 경우 쿠키꾸러미(중) 1개 추가 지급
    
        # 인벤토리 저장
        save_inventory(user_id, items)
    
        # 출석 기록 저장
        attendance_collection.update_one(
            {"_id": user_id},
            {"$set": {"last_date": today_date, "streak": streak}},
            upsert=True
        )
    
        # 보상 지급 완료 메시지
        if boost_role in ctx.author.roles:
            await ctx.send(f"{ctx.author.mention}님! 오늘도 와주셔서 감사합니다. 쿠키꾸러미(소) 2개와 쿠키꾸러미(중) 1개를 증정해 드렸습니다. 인벤토리를 확인해주세요!")
        else:
            await ctx.send(f"{ctx.author.mention}님! 오늘도 와주셔서 감사합니다. 쿠키꾸러미(소) 2개를 증정해 드렸습니다. 인벤토리를 확인해주세요!")
    
    # 승리 로직 결정 함수
    def determine_rps_outcome(user_choice, bot_choice):
        """사용자의 선택과 봇의 선택을 비교하여 승패를 결정합니다."""
        rules = {
            '가위': '보',    # 가위는 보를 이김
            '바위': '가위',  # 바위는 가위를 이김
            '보': '바위'     # 보는 바위를 이김
        }
    
        if user_choice == bot_choice:
            return "draw"
        elif rules[user_choice] == bot_choice:
            return "win"
        else:
            return "lose"
    
    # 봇 실행
    bot.run(TOKEN)
