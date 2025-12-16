import os
import discord
import asyncio
from discord.ext import commands

BOT_TOKEN = os.getenv('DISCORD_TOKEN')
try:
    MY_USER_ID = int(os.getenv('MY_USER_ID'))
except (TypeError, ValueError):
    print("Lỗi: Vui lòng kiểm tra lại MY_USER_ID trong file .env")
    exit()

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

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.guild is None:
        return

    await bot.process_commands(message)

    target_user = message.guild.get_member(MY_USER_ID)

    if target_user is None:
        return 

    current_status = str(target_user.status)
    
    if current_status == 'offline':
        is_mentioned = message.mentions
        if is_mentioned:
            try:
                target_emoji_id = 1446417289829285959
                emoji = bot.get_emoji(target_emoji_id)

                if emoji:
                    await message.add_reaction(emoji)
                else:
                    await message.add_reaction('👀') 
            except discord.HTTPException:
                pass

            await message.reply(
                f"Chắc **Mashiro** hiện đang ngủ trương dái lên rồi. "
                "Bạn nhắn tin sau nhé!",
               mention_author=True
            )

if BOT_TOKEN:
    bot.run(BOT_TOKEN)
else:
    print("Lỗi: Không tìm thấy DISCORD_TOKEN trong file .env")