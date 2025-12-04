import discord
import os
from dotenv import load_dotenv

# 1. Tải các biến môi trường từ file .env
load_dotenv()

# 2. Lấy dữ liệu từ biến môi trường
BOT_TOKEN = os.getenv('DISCORD_TOKEN')
try:
    MY_USER_ID = int(os.getenv('MY_USER_ID')) # Chuyển ID sang số nguyên (int)
except (TypeError, ValueError):
    print("Lỗi: Vui lòng kiểm tra lại MY_USER_ID trong file .env")
    exit()

# --- CẤU HÌNH QUYỀN (GIỮ NGUYÊN) ---
intents = discord.Intents.default()
intents.message_content = True 
intents.presences = True       
intents.members = True         

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Đã đăng nhập thành công: {client.user}')
    print('Đang theo dõi trạng thái AFK...')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.guild is None:
        return

    # Lấy thông tin người dùng mục tiêu từ ID đã lấy trong .env
    target_user = message.guild.get_member(MY_USER_ID)

    if target_user is None:
        return 

    # Logic kiểm tra trạng thái
    current_status = str(target_user.status)
    
    # Chỉ trả lời khi bạn Offline (hoặc Invisible)
    if current_status == 'offline':
        content_lower = message.content.lower()
        is_mentioned = message.mentions and target_user in message.mentions
        is_name_called = "mashiro" in content_lower

        if is_name_called or is_mentioned:
            await message.channel.send(
                f"Bạn {message.author.mention} thân mến, **Mashiro** hiện đang ngủ trương dái lên rồi. "
                "Bạn nhắn tin sau nhé!"
            )

# Chạy bot bằng Token lấy từ môi trường
if BOT_TOKEN:
    client.run(BOT_TOKEN)
else:
    print("Lỗi: Không tìm thấy DISCORD_TOKEN trong file .env")
