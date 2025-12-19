import os
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('DISCORD_TOKEN')


intents = discord.Intents.default()
intents.message_content = True 
intents.presences = True       
intents.members = True         

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Đã đăng nhập thành công: {bot.user}')
    print('Đang theo dõi trạng thái AFK...')
    try:
        await bot.load_extension('verify')
        print("Đã tải module verify thành công.")
    except Exception as e:
        print(f"Không thể tải module verify: {e}")
if BOT_TOKEN:
    bot.run(BOT_TOKEN)
else:
    print("Lỗi: Không tìm thấy DISCORD_TOKEN trong file .env")
