import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# 1. Tải các biến môi trường từ file .env
load_dotenv()

# 2. Lấy dữ liệu từ biến môi trường
BOT_TOKEN = os.getenv('DISCORD_TOKEN')
try:
    MY_USER_ID = int(os.getenv('MY_USER_ID'))
except (TypeError, ValueError):
    print("Lỗi: Vui lòng kiểm tra lại MY_USER_ID trong file .env")
    exit()

# --- CẤU HÌNH QUYỀN ---
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

    target_user = message.guild.get_member(MY_USER_ID)

    if target_user is None:
        return 

    current_status = str(target_user.status)
    
    if current_status == 'offline':
        content_lower = message.content.lower()
        is_mentioned = message.mentions and target_user in message.mentions
        is_name_called = "mashiro" in content_lower

        if is_name_called or is_mentioned:
            # --- CẬP NHẬT: Dùng Emoji ID ---
            try:
                # Thay dãy số bên dưới bằng ID emoji của bạn
                target_emoji_id = 1413875601722445997
                
                # Lấy object emoji từ ID
                emoji = client.get_emoji(target_emoji_id)

                if emoji:
                    await message.add_reaction(emoji)
                else:
                    # Nếu bot không tìm thấy emoji (do bot không ở trong server chứa emoji đó)
                    # thì dùng tạm emoji mặc định
                    print(f"Không tìm thấy emoji có ID: {target_emoji_id}")
                    await message.add_reaction('👀') 
            except discord.HTTPException as e:
                print(f"Lỗi khi thả emoji: {e}")
            # -------------------------------

            await message.reply(
                f"Chắc **Mashiro** hiện đang ngủ trương dái lên rồi. "
                "Bạn nhắn tin sau nhé!",
               mention_author=True
            )

if BOT_TOKEN:
    client.run(BOT_TOKEN)
else:
    print("Lỗi: Không tìm thấy DISCORD_TOKEN trong file .env")
