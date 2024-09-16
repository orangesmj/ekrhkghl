import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import Button, View, Modal, TextInput
from datetime import datetime, timedelta
import os
from pymongo import MongoClient  # MongoDB 연결을 위한 패키지
from pytz import timezone
import random
import asyncio  # 비동기 처리를 위한 패키지

# 한국 표준 시간(KST)으로 현재 시간을 반환하는 함수
def get_kst_time():
    """한국 표준 시간대로 현재 시간을 반환합니다."""
    kst = timezone('Asia/Seoul')
    return datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')

# 환경 변수에서 Discord 봇 토큰과 MongoDB URL을 가져옵니다.
TOKEN = os.environ.get("BOT_TOKEN")  # Discord 봇 토큰을 환경 변수에서 가져옵니다.
mongo_url = os.environ.get("MONGO_URL")  # MongoDB 연결 URL을 환경 변수에서 가져옵니다.

# 환경 변수 검증
if not TOKEN:
    raise ValueError("환경 변수 BOT_TOKEN이 설정되지 않았습니다.")
if not mongo_url:
    raise ValueError("환경 변수 MONGO_URL이 설정되지 않았습니다.")

# MongoDB 연결 설정
client = MongoClient(mongo_url)
db = client["DiscordBotDatabase"]  # 데이터베이스 이름 설정
nickname_collection = db["nickname_history"]  # 닉네임 변경 기록 컬렉션
ban_collection = db["ban_list"]  # 차단된 사용자 정보를 저장할 컬렉션
entry_collection = db["entry_list"]  # 입장 정보를 저장할 컬렉션
exit_collection = db["exit_list"]  # 퇴장 정보를 저장할 컬렉션
inventory_collection = db["inventory"]  # 유저의 재화(쿠키, 커피 등) 인벤토리
attendance_collection = db["attendance"]  # 출석 기록을 저장할 컬렉션
bundle_open_count_collection = db["bundle_open_count"]  # 꾸러미 오픈 횟수 기록

# 봇의 인텐트를 설정합니다. 모든 필요한 인텐트를 활성화합니다.
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True
intents.guilds = True
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
cnftjr = 1264398760499220570  # 출석 체크 메시지 채널 ID
cncja_result = 1285220422819774486  # 추첨 결과 채널 ID
rkdnlqkdnlqh = 1285220522422173727  # 가위바위보 이벤트 채널 ID
rkdnlqkdnlqh_result = 1285220550511431761  # 가위바위보 결과 채널 ID
Rec = 1267642384108486656  # 전체 삭제 로그 채널 ID 변수
Boost = 1264071791404650567  # 설정한 역할 ID (서버 부스트 역할)

# 재화(쿠키, 커피 등)과 관련된 설정
Cookie = "<:cookie_blue:1270270603135549482>"          # 쿠키 이모지 변수값
Cookie_S = "<:cookie_bundle_S:1270270702599016541>"    # 쿠키꾸러미(소) 이모지 변수값
Cookie_M = "<:cookie_bundle_M:1270270764884688938>"    # 쿠키꾸러미(중) 이모지 변수값
Cookie_L = "<:cookie_bundle_L:1270270801970462805>"    # 쿠키꾸러미(대) 이모지 변수값
Coffee = "<:Coffee:1271072742581600377>"                # 커피 이모지 변수값
Ticket = "<:Premium_Ticket:1271017996864979026>"        # 티켓 이모지 변수값
rkdnl = "<:event_scissor:1270902821365223525>"        # 가위 이모지 변수값
qkdnl = "<:event_rock:1270902812246675499>"           # 바위 이모지 변수값
qh = "<:event_paper:1270902801945464862>"             # 보 이모지 변수값

# 닉네임 변경 기록을 MongoDB에서 불러오는 함수
def load_nickname_history():
    """MongoDB에서 닉네임 변경 기록을 불러옵니다."""
    global nickname_history
    nickname_history = {
        int(doc["_id"]): [(item["nickname"], item["date"]) for item in doc["history"]]
        for doc in nickname_collection.find()
    }
    print(f"[DEBUG] 닉네임 변경 기록 불러옴: {nickname_history}")

# 닉네임 변경 기록을 MongoDB에 저장하는 함수
def save_nickname_history():
    """MongoDB에 닉네임 변경 기록을 저장합니다."""
    for user_id, history in nickname_history.items():
        last_nickname = history[-1][0] if len(history) > 0 else '기록 없음'  # 변경된 마지막 닉네임
        current_nickname_doc = nickname_collection.find_one({"_id": user_id})
        current_nickname = current_nickname_doc.get("current_nickname", "기록 없음") if current_nickname_doc else "기록 없음"
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

# 차단 목록을 MongoDB에서 불러오는 함수
def load_ban_list():
    """MongoDB에서 차단 목록을 불러옵니다."""
    global ban_list
    ban_list = {int(doc["_id"]): doc["data"] for doc in ban_collection.find()}
    print(f"[DEBUG] 차단 목록 불러옴: {ban_list}")

# 차단 목록을 MongoDB에 저장하는 함수
def save_ban_list():
    """MongoDB에 차단 목록을 저장합니다."""
    for user_id, data in ban_list.items():
        ban_collection.update_one(
            {"_id": user_id},
            {"$set": {"data": data, "last_nickname": data.get('last_nickname', '기록 없음')}},
            upsert=True
        )
    print(f"[DEBUG] 차단 목록 저장됨: {ban_list}")

# 입장 기록을 MongoDB에서 불러오는 함수
def load_entry_list():
    """MongoDB에서 입장 기록을 불러옵니다."""
    global entry_list
    entry_list = {int(doc["_id"]): doc["data"] for doc in entry_collection.find()}
    print(f"[DEBUG] 입장 기록 불러옴: {entry_list}")

# 입장 기록을 MongoDB에 저장하는 함수
def save_entry_list():
    """MongoDB에 입장 기록을 저장합니다."""
    for user_id, data in entry_list.items():
        entry_collection.update_one(
            {"_id": user_id},
            {"$set": {"data": data, "last_nickname": data["nickname"]}},
            upsert=True
        )
    print(f"[DEBUG] 입장 기록 저장됨: {entry_list}")

# 퇴장 기록을 MongoDB에서 불러오는 함수
def load_exit_list():
    """MongoDB에서 퇴장 기록을 불러옵니다."""
    global exit_list
    exit_list = {int(doc["_id"]): doc["data"] for doc in exit_collection.find()}
    print(f"[DEBUG] 퇴장 기록 불러옴: {exit_list}")

# 퇴장 기록을 MongoDB에 저장하는 함수
def save_exit_list():
    """MongoDB에 퇴장 기록을 저장합니다."""
    for user_id, data in exit_list.items():
        exit_collection.update_one(
            {"_id": user_id},
            {"$set": {"data": data, "last_nickname": data["nickname"]}},
            upsert=True
        )
    print(f"[DEBUG] 퇴장 기록 저장됨: {exit_list}")

# 특정 유저의 인벤토리를 MongoDB에서 불러오는 함수
def load_inventory(user_id):
    """MongoDB에서 특정 유저의 인벤토리를 불러옵니다."""
    user_inventory = inventory_collection.find_one({"_id": user_id})
    if not user_inventory:
        # 기본값 설정
        return {
            "쿠키": 0,
            "커피": 0,
            "티켓": 0,
            "쿠키꾸러미(소)": 0,
            "쿠키꾸러미(중)": 0,
            "쿠키꾸러미(대)": 0
        }
    return user_inventory.get("items", {
        "쿠키": 0,
        "커피": 0,
        "티켓": 0,
        "쿠키꾸러미(소)": 0,
        "쿠키꾸러미(중)": 0,
        "쿠키꾸러미(대)": 0
    })

# 특정 유저의 인벤토리를 MongoDB에 저장하는 함수
def save_inventory(user_id, items):
    """MongoDB에 특정 유저의 인벤토리를 저장합니다."""
    inventory_collection.update_one(
        {"_id": user_id},
        {"$set": {"items": items}},
        upsert=True
    )
    print(f"[DEBUG] {user_id}의 인벤토리가 저장되었습니다: {items}")

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

    delete_messages.start()    # 주기적인 메시지 삭제 태스크 시작
    delete_messages_2.start()  # 주기적인 메시지 삭제 태스크 시작
    channel = bot.get_channel(open_channel_id)
    if channel:
        await channel.send('봇이 활성화되었습니다!')  # 봇이 활성화되었음을 알림

    # 출석 체크 메시지를 보낼 채널 가져오기
    attendance_channel = bot.get_channel(cnftjr)
    if attendance_channel:
        print(f"출석 체크 메시지를 {attendance_channel.name} 채널에 보낼 준비가 되었습니다.")

    # 매일 오후 9시에 가위바위보 이벤트 시작
    if not rps_event.is_running():
        rps_event.start()

# 출석 체크 명령어 수정
@bot.tree.command(name="출석", description="출석 체크하여 보상을 받습니다.")
async def attendance(interaction: discord.Interaction):
    """사용자의 출석을 체크하고 보상을 지급합니다."""
    user_id = str(interaction.user.id)
    current_date = get_kst_time().split()[0]  # 현재 날짜 (연-월-일)

    # 출석 여부 확인
    attendance_record = attendance_collection.find_one({"_id": user_id})
    if attendance_record and attendance_record.get("last_attendance_date") == current_date:
        await interaction.response.send_message("이미 출석하셨습니다. 내일 다시 시도해주세요!", ephemeral=True)
        return

    # 기본 출석 보상 설정
    reward = 2  # 쿠키꾸러미(소) 2개

    # 인벤토리에 쿠키꾸러미(소) 추가
    items = load_inventory(user_id)
    items["쿠키꾸러미(소)"] += reward

    # Boost 역할 확인
    guild = interaction.guild
    member = guild.get_member(interaction.user.id)
    if member and guild.get_role(Boost) in member.roles:
        items["쿠키꾸러미(소)"] += 2  # 추가로 2개 지급
        items["쿠키꾸러미(중)"] += 1  # 쿠키꾸러미(중) 1개 지급

    save_inventory(user_id, items)

    # 출석 기록 업데이트
    attendance_collection.update_one(
        {"_id": user_id},
        {"$set": {"last_attendance_date": current_date}},
        upsert=True
    )

    # 출석 체크 메시지를 cnftjr 채널에 전송
    attendance_channel = bot.get_channel(cnftjr)
    if attendance_channel:
        message = "출석체크 되었습니다. 쿠키꾸러미가 지급되었습니다!"
        await attendance_channel.send(message)
    else:
        await interaction.response.send_message("출석 체크가 완료되었습니다!", ephemeral=True)

    await interaction.response.send_message(f"출석 체크 완료! {Cookie_S} 2개를 받았습니다.", ephemeral=True)

# 매일 오후 9시에 가위바위보 이벤트를 시작하고 밤 11시에 종료하는 태스크
@tasks.loop(hours=24)
async def rps_event():
    """매일 오후 9시에 가위바위보 이벤트를 시작하고 밤 11시에 종료합니다."""
    now = datetime.now(timezone('Asia/Seoul'))
    start_time = now.replace(hour=21, minute=0, second=0, microsecond=0)  # 오후 9시 시작
    end_time = now.replace(hour=23, minute=0, second=0, microsecond=0)    # 오후 11시 종료
    result_time = end_time + timedelta(minutes=1)                         # 오후 11시 1분 결과 발표

    if now > start_time:
        start_time += timedelta(days=1)
        end_time += timedelta(days=1)
        result_time += timedelta(days=1)

    # 이벤트 시작까지 대기
    wait_seconds = (start_time - now).total_seconds()
    await asyncio.sleep(wait_seconds)

    # 가위바위보 이벤트 시작
    await clear_rps_event_messages()
    event_channel = bot.get_channel(rkdnlqkdnlqh)
    if event_channel:
        # 이벤트 메시지 전송
        embed = discord.Embed(
            title="가위바위보 이벤트",
            description=(
                "가위바위보 이벤트가 시작되었습니다!\n"
                "가위바위보 시 쿠키가 5개 소진됩니다.\n"
                "가위바위보 승리 시, 쿠키꾸러미(소)가 4개 지급됩니다.\n"
                "가위바위보는 아래 이모지를 누르면 자동 참여됩니다. (중복 참여 불가입니다.)"
            ),
            color=discord.Color.green()
        )
        message = await event_channel.send(embed=embed)

        # 이모지 추가
        await message.add_reaction(rkdnl)
        await message.add_reaction(qkdnl)
        await message.add_reaction(qh)

        # 가위바위보 뷰 생성
        view = RockPaperScissorsView()
        await event_channel.send("가위바위보에 참여하려면 아래 이모지를 클릭하세요!", view=view)

        # 이벤트 종료 시간까지 대기
        await asyncio.sleep((end_time - start_time).total_seconds())
        await view.on_timeout()

        # 이벤트 메시지 삭제
        await clear_rps_event_messages()

    # 결과 발표까지 대기
    await asyncio.sleep((result_time - end_time).total_seconds())
    await announce_rps_results(view.participants)

# 가위바위보 결과 발표 함수
async def announce_rps_results(participants):
    """가위바위보 결과를 발표합니다."""
    bot_choice = random.choice(['가위', '바위', '보'])  # 봇의 랜덤 선택

    # 결과 채널 가져오기
    result_channel = bot.get_channel(rkdnlqkdnlqh_result)
    if not result_channel:
        return

    # 승리자 목록 생성
    winners = []
    for user_id, choice in participants.items():
        outcome = determine_rps_outcome(choice, bot_choice)
        user = bot.get_user(user_id)
        if user and outcome == "win":
            # 승리 시 쿠키꾸러미(소) 4개 지급
            items = load_inventory(str(user_id))
            items["쿠키꾸러미(소)"] += 4
            save_inventory(str(user_id), items)
            winners.append(user.display_name)

    # 결과 메시지 생성
    if winners:
        winner_list = ", ".join(winners)
        embed = discord.Embed(
            title="가위바위보 결과 발표",
            description=(
                "축하합니다! 가위바위보에 승리하여 쿠키꾸러미(소)가 4개 지급되었습니다.\n"
                f"승리자: {winner_list}"
            ),
            color=discord.Color.blue()
        )
    else:
        embed = discord.Embed(
            title="가위바위보 결과 발표",
            description="아쉽게도 승리자가 없습니다.",
            color=discord.Color.red()
        )

    await result_channel.send(embed=embed)

# 승리 로직 결정 함수
def determine_rps_outcome(user_choice, bot_choice):
    """사용자의 선택과 봇의 선택을 비교하여 승패를 결정합니다."""
    rules = {
        '가위': '보',  # 가위는 보를 이김
        '바위': '가위',  # 바위는 가위를 이김
        '보': '바위'   # 보는 바위를 이김
    }

    if user_choice == bot_choice:
        return "draw"
    elif rules[user_choice] == bot_choice:
        return "win"
    else:
        return "lose"

# 이벤트 채널에서 기존 메시지 삭제
async def clear_rps_event_messages():
    """이벤트 채널에서 가위바위보 관련 메시지를 삭제합니다."""
    event_channel = bot.get_channel(rkdnlqkdnlqh)
    if event_channel:
        async for message in event_channel.history(limit=100):
            if message.author == bot.user:
                await message.delete()

# 가위바위보 이벤트 클래스 정의
class RockPaperScissorsView(View):
    def __init__(self):
        super().__init__(timeout=60)  # 1분 동안 반응 대기
        self.participants = {}  # 참여자 딕셔너리: user_id -> choice

    @discord.ui.button(label="가위", style=discord.ButtonStyle.primary, emoji=rkdnl)
    async def scissors(self, interaction: discord.Interaction, button: Button):
        await self.process_choice(interaction, '가위')

    @discord.ui.button(label="바위", style=discord.ButtonStyle.primary, emoji=qkdnl)
    async def rock(self, interaction: discord.Interaction, button: Button):
        await self.process_choice(interaction, '바위')

    @discord.ui.button(label="보", style=discord.ButtonStyle.primary, emoji=qh)
    async def paper(self, interaction: discord.Interaction, button: Button):
        await self.process_choice(interaction, '보')

    async def process_choice(self, interaction: discord.Interaction, choice):
        user_id = interaction.user.id
        if user_id in self.participants:
            await interaction.response.send_message("이미 참여하셨습니다.", ephemeral=True)
            return

        # 인벤토리에서 쿠키 5개 소진
        items = load_inventory(str(user_id))
        if items.get("쿠키", 0) < 5:
            await interaction.response.send_message("보유한 쿠키가 5개 이상 필요합니다.", ephemeral=True)
            return

        items["쿠키"] -= 5
        save_inventory(str(user_id), items)

        self.participants[user_id] = choice
        await interaction.response.send_message(f"'{choice}'을(를) 선택하셨습니다!", ephemeral=True)

    async def on_timeout(self):
        """이벤트 종료 시 호출되는 함수입니다."""
        if not self.participants:
            return  # 참여자가 없을 경우 종료
        # 이 함수는 rps_event()에서 결과 발표를 처리하므로 여기서 별도의 처리를 하지 않습니다.

# 봇 실행
bot.run(TOKEN)  # 봇 실행 코드
