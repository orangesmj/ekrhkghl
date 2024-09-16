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


# 쿠키 변수
cnftjr = 1264398760499220570  # 출석 체크 메시지 채널 ID
cncja_result = 1285220422819774486  # 추첨 결과 채널 ID
rkdnlqkdnlqh = 1285220522422173727  # 가위바위보 이벤트 채널 ID
rkdnlqkdnlqh_result = 1285220550511431761  # 가위바위보 결과 채널 ID

# 역할 변수 설정
Boost = 1264071791404650567  # 부스트 역할 ID

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
            tickets = bot.tickets.get(payload.user_id, 0)
            if tickets >= 1:
                # Ticket이 있으면 1개 소모
                bot.tickets[payload.user_id] = tickets - 1
                save_tickets(bot.tickets)
                consumed = "Ticket 1개"
            else:
                # Ticket이 없으면 기본 소모
                consume_cookie = 1  # 기본 소모 쿠키 개수 설정 (필요 시 변경)
                items = load_inventory(str(payload.user_id))
                if items.get("쿠키", 0) < consume_cookie:
                    await member.send("쿠키가 부족하여 추첨에 참여할 수 없습니다.")
                    return
                items["쿠키"] -= consume_cookie
                save_inventory(str(payload.user_id), items)
                consumed = f"쿠키 {consume_cookie}개"

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
                    await cncja_channel.send(f"{user.display_name}님이 추첨에 응모하였습니다. {consumed}가 소모되었습니다.")
# 슬래시 명령어: 추첨
@bot.tree.command(name="추첨", description="지급품목을 설정하고 추첨 이벤트를 시작합니다.")
@app_commands.describe(
    item="지급할 아이템을 선택하세요. (Cookie, Cookie_S, Cookie_M, Cookie_L, Coffee)",
    consume_cookie="소모할 쿠키 개수를 입력하세요."
)
async def raffle(interaction: discord.Interaction, item: str, consume_cookie: int):
    """추첨 명령어를 통해 지급품목을 설정하고 참여할 수 있도록 합니다."""
    MS_3 = 1264940881417470034  # MS_3 역할 ID
    admin_role = interaction.guild.get_role(MS_3)
    
    # 역할 제한 확인
    if admin_role not in interaction.user.roles:
        await interaction.response.send_message("이 명령어를 사용할 권한이 없습니다.", ephemeral=True)
        return

    # 지급품목과 소모 쿠키 개수 검증
    valid_items = ["Cookie", "Cookie_S", "Cookie_M", "Cookie_L", "Coffee"]
    if item not in valid_items:
        await interaction.response.send_message(f"지급할 수 없는 아이템입니다: {item}", ephemeral=True)
        return

    if consume_cookie < 1:
        await interaction.response.send_message("소모할 쿠키 개수는 1개 이상이어야 합니다.", ephemeral=True)
        return

    user_id = str(interaction.user.id)
    tickets = bot.tickets.get(int(user_id), 0)

    if tickets >= 1:
        # Ticket이 있으면 1개 소모
        bot.tickets[int(user_id)] = tickets - 1
        save_tickets(bot.tickets)
        consumed = "Ticket 1개"
    else:
        # Ticket이 없으면 지정한 개수의 Cookie 소모
        items = load_inventory(user_id)
        if items.get("쿠키", 0) < consume_cookie:
            await interaction.response.send_message("쿠키가 부족합니다.", ephemeral=True)
            return
        items["쿠키"] -= consume_cookie
        save_inventory(user_id, items)
        consumed = f"쿠키 {consume_cookie}개"

    # 추첨 참여 기록
    raffle_collection.update_one(
        {"_id": "current_raffle"},
        {"$addToSet": {"participants": interaction.user.id}},
        upsert=True
    )

    # 추첨 이벤트 메시지 전송
    raffle_channel = bot.get_channel(cncja_result)  # cncja_result는 추첨 결과 채널 ID
    if raffle_channel:
        await raffle_channel.send(f"{interaction.user.display_name}님이 추첨에 참여하였습니다. {consumed}가 소모되었습니다.")

    await interaction.response.send_message("추첨에 참여하였습니다.", ephemeral=True)
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
    participants = raffle_info.get("participants", [])

    if not participants:
        return  # 참여자가 없을 경우 종료

    # 당첨자 선정
    winner_id = random.choice(participants)
    guild = bot.get_guild(1043189119603453982)
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


#봇 시작 명령어
bot.run(TOKEN)
