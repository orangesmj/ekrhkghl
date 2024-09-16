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

# 사용할 데이터베이스와 컬렉션 설정
db = client["DiscordBotDatabase"]  # 데이터베이스 이름 설정
nickname_collection = db["nickname_history"]  # 닉네임 변경 기록 컬렉션
ban_collection = db["ban_list"]  # 차단된 사용자 정보를 저장할 컬렉션
entry_collection = db["entry_list"]  # 입장 정보를 저장할 컬렉션
exit_collection = db["exit_list"]  # 퇴장 정보를 저장할 컬렉션
inventory_collection = db["inventory"]  # 유저의 재화(쿠키, 커피 등) 인벤토리
attendance_collection = db["attendance"]  # 출석 기록을 저장할 컬렉션
coffee_usage_collection = db["coffee_usage"]  # 커피 사용 기록을 저장할 컬렉션
bundle_open_count_collection = db["bundle_open_count"]  # 꾸러미 오픈 횟수 기록
raffle_collection = db["raffle_participants"]  # 추첨 참여자 기록
ticket_collection = db["tickets"]  # 티켓 기록 컬렉션

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

# 사용할 데이터베이스와 컬렉션 설정
db = client["DiscordBotDatabase"]  # 데이터베이스 이름 설정
nickname_collection = db["nickname_history"]  # 닉네임 변경 기록 컬렉션
ban_collection = db["ban_list"]  # 차단된 사용자 정보를 저장할 컬렉션
entry_collection = db["entry_list"]  # 입장 정보를 저장할 컬렉션
exit_collection = db["exit_list"]  # 퇴장 정보를 저장할 컬렉션
inventory_collection = db["inventory"]  # 유저의 재화(쿠키, 커피 등) 인벤토리
attendance_collection = db["attendance"]  # 출석 기록을 저장할 컬렉션
coffee_usage_collection = db["coffee_usage"]  # 커피 사용 기록을 저장할 컬렉션
bundle_open_count_collection = db["bundle_open_count"]  # 꾸러미 오픈 횟수 기록
raffle_collection = db["raffle_participants"]  # 추첨 참여자 기록
ticket_collection = db["tickets"]  # 티켓 기록 컬렉션

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

# 새로운 변수 추가
cnftjr = 1264398760499220570  # 출석 체크 메시지 채널 ID
cncja_result = 1285220422819774486  # 추첨 결과 채널 ID
rkdnlqkdnlqh = 1285220522422173727  # 가위바위보 이벤트 채널 ID
rkdnlqkdnlqh_result = 1285220550511431761  # 가위바위보 결과 채널 ID

# 삭제된 메시지를 기록할 로그 채널 ID
Rec = 1267642384108486656  # 전체 삭제 로그 채널 ID 변수

# 역할 변수 설정
Boost = 1264071791404650567  # 설정한 역할 ID (서버 부스트 역할)

# 재화(쿠키, 커피 등)과 관련된 설정
Cookie = "<:cookie_blue:1270270603135549482>"          # 쿠키 이모지 변수값
Cookie_S = "<:cookie_bundle_S:1270270702599016541>"    # 쿠키꾸러미(소) 이모지 변수값
Cookie_M = "<:cookie_bundle_M:1270270764884688938>"    # 쿠키꾸러미(중) 이모지 변수값
Cookie_L = "<:cookie_bundle_L:1270270801970462805>"    # 쿠키꾸러미(대) 이모지 변수값
Coffee = "<:Coffee:1271072742581600377>"                # 커피 이모지 변수값
Ticket = "<:Premium_Ticket:1271017996864979026>"        # 티켓 이모지 변수값

# 가위바위보 이벤트 관련 이모지 설정
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

# 티켓을 로드하는 함수
def load_tickets():
    """MongoDB에서 모든 티켓을 불러옵니다."""
    return {int(doc["_id"]): doc["tickets"] for doc in ticket_collection.find()}

# 티켓을 저장하는 함수
def save_tickets(tickets):
    """MongoDB에 티켓 정보를 저장합니다."""
    for user_id, count in tickets.items():
        ticket_collection.update_one(
            {"_id": user_id},
            {"$set": {"tickets": count}},
            upsert=True
        )
    print(f"[DEBUG] 티켓 정보 저장됨: {tickets}")

# 보너스 적용 및 최대 획득량 제한 함수
def apply_bonus(amount, max_amount, bonus_active):
    """보너스를 적용하고 최대 획득량을 제한하는 함수입니다."""
    if bonus_active:
        amount = int(amount * 1.5)
        if amount > max_amount:
            amount = max_amount
    return amount
# 봇이 준비되었을 때 실행되는 이벤트
@bot.event
async def on_ready():
    """봇이 준비되었을 때 실행되는 함수입니다."""
    print(f'Logged in as {bot.user}')
    load_nickname_history()  # 닉네임 기록을 불러옵니다.
    load_ban_list()          # 차단 목록을 불러옵니다.
    load_entry_list()        # 입장 기록을 불러옵니다.
    load_exit_list()         # 퇴장 기록을 불러옵니다.
    bot.tickets = load_tickets()  # 티켓 정보를 불러옵니다.
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

    # 티켓 지급 및 소멸 태스크 초기화
    if not give_tickets_task.is_running():
        give_tickets_task.start()
    if not remove_tickets_task.is_running():
        remove_tickets_task.start()
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
# 리액션을 통한 역할 부여 및 제거를 처리하는 함수
async def handle_reaction(payload, add_role: bool, channel_id, message_id, emoji, role_id, use_ticket=False):
    """리액션을 통해 역할을 부여하거나 제거합니다."""
    if payload.channel_id != channel_id or (message_id and payload.message_id != message_id):
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    if member is None or member.bot:
        return

    if str(payload.emoji) == emoji:
        role = guild.get_role(role_id)
        if role:
            try:
                # Ticket 사용 여부 확인
                if use_ticket:
                    user_id = str(payload.user_id)
                    tickets = bot.tickets.get(int(user_id), 0)
                    if tickets < 1:
                        await member.send("참여하기 위해서는 티켓이 1개 이상 필요합니다.")
                        return
                    # 티켓 소모
                    bot.tickets[int(user_id)] = tickets - 1
                    save_tickets(bot.tickets)

                if add_role:
                    await member.add_roles(role)
                    await member.send(f"{role.name} 역할이 부여되었습니다!")
                    channel = bot.get_channel(channel_id)
                    if message_id:
                        message = await channel.fetch_message(message_id)
                        await message.remove_reaction(emoji, member)
            except Exception as e:
                await member.send(f"역할 부여 중 오류 발생: {e}")
# 리액션 추가 시 호출되는 이벤트
@bot.event
async def on_raw_reaction_add(payload):
    """리액션 추가 시 호출되는 함수입니다."""
    # 입장 가이드 역할 부여
    await handle_reaction(payload, True, Ch_1, Me_1, Emoji_1, Role_1)

    # 라소소 역할 부여
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

    # 성별 역할 부여
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

    # 가위바위보 참여 시 티켓 소모
    if payload.channel_id == rkdnlqkdnlqh and str(payload.emoji) in [rkdnl, qkdnl, qh]:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member:
            # 티켓 소모 및 참여 처리
            await handle_reaction(payload, False, rkdnlqkdnlqh, None, str(payload.emoji), None, use_ticket=True)

    # 추첨 참여 시 티켓 소모
    if payload.channel_id == cncja_result and str(payload.emoji) == Cookie:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member:
            # 티켓 소모 및 참여 기록
            await handle_reaction(payload, False, cncja_result, None, str(payload.emoji), None, use_ticket=True)

            # 추첨 참여 기록
            raffle_collection.update_one(
                {"_id": "current_raffle"},
                {"$addToSet": {"participants": payload.user_id}}
            )

            # 참여 메시지 전송
            cncja_channel = bot.get_channel(cncja_result)
            if cncja_channel:
                user = guild.get_member(payload.user_id)
                if user:
                    await cncja_channel.send(f"{user.display_name}님이 추첨에 응모하였습니다. 티켓이 1개 소모되었습니다.")
# 메시지 삭제 시 로그를 기록하는 이벤트
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
# 가입 양식 작성 모달 창 클래스 정의
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
        """모달이 제출되었을 때 호출되는 함수입니다."""
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
# 닉네임 변경 모달 창 클래스 정의
class NicknameChangeModal(Modal):
    """닉네임을 변경하는 모달 창입니다."""
    def __init__(self, member):
        super().__init__(title="닉네임 변경", timeout=None)
        self.member = member
        self.new_nickname = TextInput(label="변경할 닉네임을 입력하세요", placeholder="새로운 닉네임", required=True)
        self.add_item(self.new_nickname)

    async def on_submit(self, interaction: discord.Interaction):
        """모달이 제출되었을 때 호출되는 함수입니다."""
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
# 모달 및 버튼을 처리하는 함수들
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
# 닉네임 중복 여부를 확인하는 함수
def is_duplicate_nickname(nickname, guild):
    """닉네임 중복 여부를 확인합니다."""
    normalized_nickname = nickname.lower()
    for member in guild.members:
        if member.display_name.lower() == normalized_nickname:
            return True
    return False
# 슬래시 명령어: 차단된 사용자 목록을 보여주는 함수
@bot.tree.command(name="차단목록", description="차단된 사용자 목록을 확인합니다.")
async def ban_list_command(interaction: discord.Interaction):
    """차단된 사용자의 목록을 보여주는 슬래시 명령어입니다."""
    admin_role = interaction.guild.get_role(ad1)
    if admin_role not in interaction.user.roles:
        await interaction.response.send_message("이 명령어를 사용할 권한이 없습니다.", ephemeral=True)
        return

    if ban_list:
        ban_info = "\n".join(
            [f"ID: {user_id}, 닉네임: {info.get('nickname', '알 수 없음')}, 마지막 닉네임: {info.get('last_nickname', '기록 없음')}, 사유: {info['reason']}"
             for user_id, info in ban_list.items()]
        )
        await interaction.response.send_message(f"차단된 사용자 목록:\n{ban_info}", ephemeral=True)
    else:
        await interaction.response.send_message("현재 차단된 사용자가 없습니다.", ephemeral=True)
# 슬래시 명령어: 차단된 사용자를 해제하는 함수
@bot.tree.command(name="차단해제", description="차단된 사용자의 차단을 해제합니다.")
@app_commands.describe(nickname="차단 해제할 사용자의 별명을 입력하세요.")
async def unban_user(interaction: discord.Interaction, nickname: str):
    """차단된 사용자를 해제하는 슬래시 명령어입니다."""
    admin_role = interaction.guild.get_role(ad1)
    if admin_role not in interaction.user.roles:
        await interaction.response.send_message("이 명령어를 사용할 권한이 없습니다.", ephemeral=True)
        return

    # 사용자 찾기: nickname과 last_nickname 모두 확인
    user_id = next(
        (uid for uid, info in ban_list.items() if info.get('nickname') == nickname or info.get('last_nickname') == nickname),
        None
    )

    if not user_id:
        await interaction.response.send_message("해당 별명을 가진 차단된 사용자를 찾을 수 없습니다.", ephemeral=True)
        await ban_list_command(interaction)
        return

    guild = interaction.guild
    try:
        user = await bot.fetch_user(int(user_id))
        await guild.unban(user)
        del ban_list[int(user_id)]
        save_ban_list()  # 차단 목록을 MongoDB에 저장
        await interaction.response.send_message(f"사용자 {nickname}의 차단이 해제되었습니다.")
        await ban_list_command(interaction)
    except discord.NotFound:
        await interaction.response.send_message("해당 ID를 가진 사용자를 찾을 수 없습니다.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("차단 해제할 권한이 없습니다.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"차단 해제 중 오류가 발생했습니다: {e}", ephemeral=True)
# 관리자 전용 아이템 지급 명령어
@bot.tree.command(name="지급", description="특정 유저에게 재화를 지급합니다.")
@app_commands.describe(user="재화를 지급할 사용자를 선택하세요.", item="지급할 아이템", amount="지급할 개수")
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

    # 최대 획득량 설정 (예: 쿠키 최대 100개)
    max_amounts = {
        "쿠키": 100,
        "커피": 10,
        "티켓": 5,
        "쿠키꾸러미(소)": 50,
        "쿠키꾸러미(중)": 30,
        "쿠키꾸러미(대)": 20
    }
    max_amount = max_amounts.get(item, amount)

    # 최대 획득량 제한
    final_amount = min(amount, max_amount)

    items[item] += final_amount
    save_inventory(user_id, items)
    await interaction.response.send_message(f"{user.display_name}에게 {item} {final_amount}개를 지급했습니다.", ephemeral=True)
    await user.send(f"{item} {final_amount}개가 지급되었습니다.")
# 쿠키 랭킹 명령어
@bot.tree.command(name="랭킹", description="쿠키 랭킹을 확인합니다.")
async def show_ranking(interaction: discord.Interaction):
    """쿠키 랭킹을 보여주는 명령어입니다."""
    all_inventories = inventory_collection.find()
    rankings = sorted(
        ((inv["_id"], inv["items"].get("쿠키", 0)) for inv in all_inventories),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    if not rankings:
        await interaction.response.send_message("랭킹을 조회할 데이터가 없습니다.", ephemeral=True)
        return

    ranking_message = "\n".join([
        f"{idx + 1}. {interaction.guild.get_member(int(user_id)).display_name}: {cookies} {Cookie}"
        for idx, (user_id, cookies) in enumerate(rankings)
    ])
    await interaction.response.send_message(f"쿠키 랭킹:\n{ranking_message}", ephemeral=True)
# 인벤토리 확인 명령어
@bot.tree.command(name="인벤토리", description="자신의 인벤토리를 확인합니다.")
async def show_inventory(interaction: discord.Interaction):
    """유저가 자신의 인벤토리를 확인하는 명령어입니다."""
    user_id = str(interaction.user.id)
    items = load_inventory(user_id)
    inventory_message = f"**{interaction.user.display_name}님의 인벤토리**\n"
    inventory_message += f"{Cookie}: {items.get('쿠키', 0)}개\n"
    inventory_message += f"{Coffee}: {items.get('커피', 0)}개\n"
    inventory_message += f"{Cookie_S}: {items.get('쿠키꾸러미(소)', 0)}개\n"
    inventory_message += f"{Cookie_M}: {items.get('쿠키꾸러미(중)', 0)}개\n"
    inventory_message += f"{Cookie_L}: {items.get('쿠키꾸러미(대)', 0)}개\n"
    inventory_message += f"{Ticket}: {items.get('티켓', 0)}개\n"
    await interaction.response.send_message(inventory_message, ephemeral=True)
# 쿠키 꾸러미를 오픈하여 쿠키를 받는 명령어
@bot.tree.command(name="오픈", description="쿠키 꾸러미를 오픈하여 쿠키를 받습니다.")
@app_commands.describe(size="오픈할 쿠키 꾸러미의 크기 (소, 중, 대)")
async def open_bundle(interaction: discord.Interaction, size: str):
    """쿠키 꾸러미를 오픈하여 쿠키를 받는 기능입니다."""
    user_id = str(interaction.user.id)
    items = load_inventory(user_id)

    # 입력된 크기를 검증하고 이모지와 이름 매칭
    bundle_sizes = {
        "소": {"name": "쿠키꾸러미(소)", "emoji": Cookie_S, "min": 2, "max": 5},
        "중": {"name": "쿠키꾸러미(중)", "emoji": Cookie_M, "min": 5, "max": 10},
        "대": {"name": "쿠키꾸러미(대)", "emoji": Cookie_L, "min": 10, "max": 30}
    }

    if size not in bundle_sizes:
        await interaction.response.send_message("잘못된 크기입니다. 소, 중, 대 중에서 선택해주세요.", ephemeral=True)
        return

    bundle_info = bundle_sizes[size]
    bundle_name = bundle_info["name"]
    bundle_emoji = bundle_info["emoji"]

    if items.get(bundle_name, 0) < 1:
        await interaction.response.send_message(f"보유한 {bundle_name}이 없습니다.", ephemeral=True)
        return

    # 꾸러미 1개 소비
    items[bundle_name] -= 1

    # 오늘 오픈한 꾸러미 수 확인
    current_date = get_kst_time().split()[0]
    bundle_open_record = bundle_open_count_collection.find_one({"_id": user_id})
    if bundle_open_record and bundle_open_record.get("date") == current_date:
        open_count = bundle_open_record.get("count", 0) + 1
    else:
        open_count = 1

    # 쿠키 수량 계산 및 최대 획득량 제한
    base_cookies = random.randint(bundle_info["min"], bundle_info["max"])
    cookies_received = base_cookies  # 보너스 적용 없음

    # 인벤토리에 쿠키 추가
    items["쿠키"] = items.get("쿠키", 0) + cookies_received
    save_inventory(user_id, items)

    # 꾸러미 오픈 횟수 업데이트
    bundle_open_count_collection.update_one(
        {"_id": user_id},
        {"$set": {"date": current_date, "count": open_count}},
        upsert=True
    )

    await interaction.response.send_message(
        f"{bundle_emoji} {bundle_name}을 오픈하여 쿠키 {cookies_received}개를 획득했습니다! {Cookie}",
        ephemeral=True
    )
# 가위바위보 이벤트 클래스 정의
class RockPaperScissorsView(View):
    def __init__(self):
        super().__init__(timeout=120)  # 2분 동안 반응 대기
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

        # 티켓 사용 여부 확인
        tickets = bot.tickets.get(user_id, 0)
        if tickets < 1:
            await interaction.response.send_message("참여하기 위해서는 티켓이 1개 이상 필요합니다.", ephemeral=True)
            return

        # 티켓 소모
        bot.tickets[user_id] = tickets - 1
        save_tickets(bot.tickets)

        self.participants[user_id] = choice
        await interaction.response.send_message(f"'{choice}'을(를) 선택하셨습니다! 티켓 1개가 소모되었습니다.", ephemeral=True)

    async def on_timeout(self):
        # 이벤트 종료 후 결과 처리
        if not self.participants:
            return  # 참여자가 없을 경우 종료

        # 랜덤으로 봇의 선택
        bot_choice = random.choice(['가위', '바위', '보'])

        # 결과 채널 가져오기
        result_channel = bot.get_channel(rkdnlqkdnlqh_result)
        if not result_channel:
            result_channel = bot.get_channel(cncja_result)  # 대체 채널

        winners = []
        for user_id, choice in self.participants.items():
            outcome = determine_rps_outcome(choice, bot_choice)
            if outcome == "win":
                user = bot.get_user(user_id)
                if user:
                    # 쿠키꾸러미(소) 4개 지급
                    items = load_inventory(str(user_id))
                    items["쿠키꾸러미(소)"] += 4
                    save_inventory(str(user_id), items)
                    winners.append(user.display_name)

        # 결과 메시지 작성
        if winners:
            winners_list = "\n".join(winners)
            result_message = (
                "축하합니다. 가위바위보에 승리하여 쿠키꾸러미(소)가 4개 지급되었습니다.\n"
                "승리자 :\n" + winners_list
            )
            await result_channel.send(result_message)
        else:
            await result_channel.send(f"가위바위보 이벤트가 종료되었습니다. 봇의 선택: {bot_choice}\n승리자가 없습니다.")

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

# 매일 오후 9시에 가위바위보 이벤트를 시작하는 태스크
@tasks.loop(hours=24)
async def rps_event():
    """매일 오후 9시에 가위바위보 이벤트를 시작합니다."""
    now = datetime.now(timezone('Asia/Seoul'))
    target_time = now.replace(hour=21, minute=0, second=0, microsecond=0)
    if now > target_time:
        target_time += timedelta(days=1)
    wait_seconds = (target_time - now).total_seconds()
    await asyncio.sleep(wait_seconds)

    # 이벤트 채널 가져오기
    event_channel = bot.get_channel(rkdnlqkdnlqh)
    if not event_channel:
        event_channel = bot.get_channel(cncja_result)  # 대체 채널

    # 이벤트 메시지 전송
    embed = discord.Embed(
        title="가위바위보 이벤트",
        description=(
            "가위바위보 이벤트가 시작되었습니다!\n"
            "가위바위보 시 티켓이 1개 소진됩니다.\n"
            "가위바위보는 아래 이모지를 눌러 자동 참여됩니다. (중복 참여 불가입니다.)"
        ),
        color=discord.Color.green()
    )
    message = await event_channel.send(embed=embed)

    # 이모지 추가
    await message.add_reaction(rkdnl)
    await message.add_reaction(qkdnl)
    await message.add_reaction(qh)

    # 가위바위보 뷰 생성 및 전송
    view = RockPaperScissorsView()
    await event_channel.send("가위바위보에 참여하려면 아래 이모지를 클릭하세요!", view=view)
# 매일 오전 12시 1분에 티켓 지급
@tasks.loop(hours=24)
async def give_tickets_task():
    """매일 오전 12시 1분에 Boost 역할을 가진 사용자에게 티켓을 지급합니다."""
    now = datetime.now(timezone('Asia/Seoul'))
    target_time = now.replace(hour=0, minute=1, second=0, microsecond=0)
    if now > target_time:
        target_time += timedelta(days=1)
    wait_seconds = (target_time - now).total_seconds()
    await asyncio.sleep(wait_seconds)

    guild = bot.get_guild(YOUR_GUILD_ID)  # YOUR_GUILD_ID를 실제 서버 ID로 변경하세요
    boost_role = guild.get_role(Boost)
    if boost_role:
        for member in boost_role.members:
            user_id = member.id
            current_tickets = bot.tickets.get(user_id, 0)
            bot.tickets[user_id] = current_tickets + 2
            save_tickets(bot.tickets)
            try:
                await member.send(f"매일 2개의 티켓이 지급되었습니다! 현재 티켓 수: {bot.tickets[user_id]}개")
            except discord.Forbidden:
                print(f"DM을 보낼 수 없습니다: {member.display_name}")
        print("[DEBUG] Boost 역할을 가진 사용자에게 티켓이 지급되었습니다.")

# 매일 오후 11시 59분에 티켓 소멸
@tasks.loop(hours=24)
async def remove_tickets_task():
    """매일 오후 11시 59분에 티켓을 소멸시킵니다."""
    now = datetime.now(timezone('Asia/Seoul'))
    target_time = now.replace(hour=23, minute=59, second=0, microsecond=0)
    if now > target_time:
        target_time += timedelta(days=1)
    wait_seconds = (target_time - now).total_seconds()
    await asyncio.sleep(wait_seconds)

    # 모든 사용자의 티켓 초기화
    bot.tickets = {user_id: 0 for user_id in bot.tickets}
    save_tickets(bot.tickets)
    print("[DEBUG] 모든 사용자의 티켓이 초기화되었습니다.")
# 슬래시 명령어: 추첨
@bot.tree.command(name="추첨", description="지급품목을 설정하고 추첨 이벤트를 시작합니다.")
@app_commands.describe(item="지급할 아이템을 선택하세요.", consume_ticket="소모할 티켓 개수를 입력하세요.")
async def raffle(interaction: discord.Interaction, item: str, consume_ticket: int):
    """추첨 명령어를 통해 지급품목을 설정하고 참여할 수 있도록 합니다."""
    admin_role = interaction.guild.get_role(ad1)
    if admin_role not in interaction.user.roles:
        await interaction.response.send_message("이 명령어를 사용할 권한이 없습니다.", ephemeral=True)
        return

    # 지급품목과 소모 티켓 개수 검증
    valid_items = ["Cookie", "Cookie_S", "Cookie_M", "Cookie_L", "Coffee"]
    if item not in valid_items:
        await interaction.response.send_message(f"지급할 수 없는 아이템입니다: {item}", ephemeral=True)
        return

    if consume_ticket < 1:
        await interaction.response.send_message("소모할 티켓 개수는 1개 이상이어야 합니다.", ephemeral=True)
        return

    # 추첨 정보 저장
    raffle_collection.update_one(
        {"_id": "current_raffle"},
        {"$set": {"item": item, "consume_ticket": consume_ticket, "participants": []}},
        upsert=True
    )

    # 추첨 결과 채널에 메시지 전송
    raffle_channel = bot.get_channel(cncja_result)
    if not raffle_channel:
        await interaction.response.send_message("추첨 결과 채널을 찾을 수 없습니다.", ephemeral=True)
        return

    embed = discord.Embed(
        title="추첨 이벤트",
        description=(
            f"추첨 이벤트가 시작되었습니다!\n"
            f"지급품목: {item}\n"
            f"참여 시 {consume_ticket}개의 티켓이 소모됩니다.\n"
            f"참여하려면 아래 이모지를 클릭하세요."
        ),
        color=discord.Color.purple()
    )
    raffle_message = await raffle_channel.send(embed=embed)
    await raffle_message.add_reaction(Cookie)

    await interaction.response.send_message("추첨 이벤트가 시작되었습니다.", ephemeral=True)
# 추첨 참여 시 티켓 소모 및 참여 기록
@bot.event
async def on_raw_reaction_add(payload):
    """리액션 추가 시 호출되는 함수입니다."""
    # 입장 가이드 역할 부여
    await handle_reaction(payload, True, Ch_1, Me_1, Emoji_1, Role_1)

    # 라소소 역할 부여
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

    # 성별 역할 부여
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

    # 가위바위보 참여 시 티켓 소모
    if payload.channel_id == rkdnlqkdnlqh and str(payload.emoji) in [rkdnl, qkdnl, qh]:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member:
            # 티켓 소모 및 참여 처리
            await handle_reaction(payload, False, rkdnlqkdnlqh, None, str(payload.emoji), None, use_ticket=True)

    # 추첨 참여 시 티켓 소모
    if payload.channel_id == cncja_result and str(payload.emoji) == Cookie:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member:
            # 티켓 소모 및 참여 기록
            await handle_reaction(payload, False, cncja_result, None, str(payload.emoji), None, use_ticket=True)

            # 추첨 참여 기록
            raffle_collection.update_one(
                {"_id": "current_raffle"},
                {"$addToSet": {"participants": payload.user_id}}
            )

            # 참여 메시지 전송
            cncja_channel = bot.get_channel(cncja_result)
            if cncja_channel:
                user = guild.get_member(payload.user_id)
                if user:
                    await cncja_channel.send(f"{user.display_name}님이 추첨에 응모하였습니다. 티켓이 1개 소모되었습니다.")
# 가위바위보 이벤트 종료 후 결과 발표
class RockPaperScissorsView(View):
    def __init__(self):
        super().__init__(timeout=120)  # 2분 동안 반응 대기
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

        # 티켓 사용 여부 확인
        tickets = bot.tickets.get(user_id, 0)
        if tickets < 1:
            await interaction.response.send_message("참여하기 위해서는 티켓이 1개 이상 필요합니다.", ephemeral=True)
            return

        # 티켓 소모
        bot.tickets[user_id] = tickets - 1
        save_tickets(bot.tickets)

        self.participants[user_id] = choice
        await interaction.response.send_message(f"'{choice}'을(를) 선택하셨습니다! 티켓 1개가 소모되었습니다.", ephemeral=True)

    async def on_timeout(self):
        # 이벤트 종료 후 결과 처리
        if not self.participants:
            return  # 참여자가 없을 경우 종료

        # 랜덤으로 봇의 선택
        bot_choice = random.choice(['가위', '바위', '보'])

        # 결과 채널 가져오기
        result_channel = bot.get_channel(rkdnlqkdnlqh_result)
        if not result_channel:
            result_channel = bot.get_channel(cncja_result)  # 대체 채널

        winners = []
        for user_id, choice in self.participants.items():
            outcome = determine_rps_outcome(choice, bot_choice)
            if outcome == "win":
                user = bot.get_user(user_id)
                if user:
                    # 쿠키꾸러미(소) 4개 지급
                    items = load_inventory(str(user_id))
                    items["쿠키꾸러미(소)"] += 4
                    save_inventory(str(user_id), items)
                    winners.append(user.display_name)

        # 결과 메시지 작성
        if winners:
            winners_list = "\n".join(winners)
            result_message = (
                "축하합니다. 가위바위보에 승리하여 쿠키꾸러미(소)가 4개 지급되었습니다.\n"
                "승리자 :\n" + winners_list
            )
            await result_channel.send(result_message)
        else:
            await result_channel.send(f"가위바위보 이벤트가 종료되었습니다. 봇의 선택: {bot_choice}\n승리자가 없습니다.")

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

# 매일 오후 9시에 가위바위보 이벤트를 시작하는 태스크
@tasks.loop(hours=24)
async def rps_event():
    """매일 오후 9시에 가위바위보 이벤트를 시작합니다."""
    now = datetime.now(timezone('Asia/Seoul'))
    target_time = now.replace(hour=21, minute=0, second=0, microsecond=0)
    if now > target_time:
        target_time += timedelta(days=1)
    wait_seconds = (target_time - now).total_seconds()
    await asyncio.sleep(wait_seconds)

    # 이벤트 채널 가져오기
    event_channel = bot.get_channel(rkdnlqkdnlqh)
    if not event_channel:
        event_channel = bot.get_channel(cncja_result)  # 대체 채널

    # 이벤트 메시지 전송
    embed = discord.Embed(
        title="가위바위보 이벤트",
        description=(
            "가위바위보 이벤트가 시작되었습니다!\n"
            "가위바위보 시 티켓이 1개 소진됩니다.\n"
            "가위바위보는 아래 이모지를 눌러 자동 참여됩니다. (중복 참여 불가입니다.)"
        ),
        color=discord.Color.green()
    )
    message = await event_channel.send(embed=embed)

    # 이모지 추가
    await message.add_reaction(rkdnl)
    await message.add_reaction(qkdnl)
    await message.add_reaction(qh)

    # 가위바위보 뷰 생성 및 전송
    view = RockPaperScissorsView()
    await event_channel.send("가위바위보에 참여하려면 아래 이모지를 클릭하세요!", view=view)
# 매일 오후 11시 1분에 추첨 결과 발표
@tasks.loop(hours=24)
async def raffle_result_task():
    """매일 오후 11시 1분에 추첨 결과를 발표합니다."""
    now = datetime.now(timezone('Asia/Seoul'))
    target_time = now.replace(hour=23, minute=1, second=0, microsecond=0)
    if now > target_time:
        target_time += timedelta(days=1)
    wait_seconds = (target_time - now).total_seconds()
    await asyncio.sleep(wait_seconds)

    # 현재 추첨 정보 가져오기
    raffle_info = raffle_collection.find_one({"_id": "current_raffle"})
    if not raffle_info:
        return  # 현재 추첨 정보가 없을 경우 종료

    item = raffle_info.get("item")
    consume_ticket = raffle_info.get("consume_ticket", 1)
    participants = raffle_info.get("participants", [])

    if not participants:
        return  # 참여자가 없을 경우 종료

    # 추첨 참여자 중 랜덤으로 당첨자 선정
    winner_id = random.choice(participants)
    guild = bot.get_guild(YOUR_GUILD_ID)  # YOUR_GUILD_ID를 실제 서버 ID로 변경하세요
    winner = guild.get_member(winner_id)
    if not winner:
        return  # 당첨자를 찾을 수 없을 경우 종료

    # 인벤토리에 아이템 추가
    items = load_inventory(str(winner_id))
    items[item] = items.get(item, 0) + 1
    save_inventory(str(winner_id), items)

    # 결과 발표 채널에 메시지 전송
    result_channel = bot.get_channel(cncja_result)
    if result_channel:
        await result_channel.send(
            f"축하합니다! {winner.display_name}님이 추첨에서 당첨되어 {item} 1개가 지급되었습니다!"
        )

    # 현재 추첨 정보 초기화
    raffle_collection.delete_one({"_id": "current_raffle"})
# 티켓 지급 및 소멸 태스크 수정
@tasks.loop(hours=24)
async def give_tickets_task():
    """매일 오전 12시 1분에 Boost 역할을 가진 사용자에게 티켓을 지급합니다."""
    now = datetime.now(timezone('Asia/Seoul'))
    target_time = now.replace(hour=0, minute=1, second=0, microsecond=0)
    if now > target_time:
        target_time += timedelta(days=1)
    wait_seconds = (target_time - now).total_seconds()
    await asyncio.sleep(wait_seconds)

    guild = bot.get_guild(YOUR_GUILD_ID)  # YOUR_GUILD_ID를 실제 서버 ID로 변경하세요
    boost_role = guild.get_role(Boost)
    if boost_role:
        for member in boost_role.members:
            user_id = member.id
            current_tickets = bot.tickets.get(user_id, 0)
            bot.tickets[user_id] = current_tickets + 2
            save_tickets(bot.tickets)
            try:
                await member.send(f"매일 2개의 티켓이 지급되었습니다! 현재 티켓 수: {bot.tickets[user_id]}개")
            except discord.Forbidden:
                print(f"DM을 보낼 수 없습니다: {member.display_name}")
        print("[DEBUG] Boost 역할을 가진 사용자에게 티켓이 지급되었습니다.")

@tasks.loop(hours=24)
async def remove_tickets_task():
    """매일 오후 11시 59분에 티켓을 소멸시킵니다."""
    now = datetime.now(timezone('Asia/Seoul'))
    target_time = now.replace(hour=23, minute=59, second=0, microsecond=0)
    if now > target_time:
        target_time += timedelta(days=1)
    wait_seconds = (target_time - now).total_seconds()
    await asyncio.sleep(wait_seconds)

    # 모든 사용자의 티켓 초기화
    bot.tickets = {user_id: 0 for user_id in bot.tickets}
    save_tickets(bot.tickets)
    print("[DEBUG] 모든 사용자의 티켓이 초기화되었습니다.")
# 매일 오후 11시 1분에 추첨 결과 발표 태스크 시작
@tasks.loop(count=1)
async def initialize_tasks():
    """봇 시작 시 티켓 지급 및 소멸 태스크를 초기화합니다."""
    give_tickets_task.start()
    remove_tickets_task.start()
    raffle_result_task.start()

initialize_tasks.start()
# 봇 실행
bot.run(TOKEN)  # 봇 실행 코드
