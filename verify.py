import discord
import os
import aiosqlite
from discord.ext import commands
from discord.ui import View, Select, Button

VERIFY_CHANNEL_ID = 1450100315327168642
VERIFY_ROLE_ID = 1450138002121556049
TARGET_GUILD_ID = 1450079520756465758

# Cấu hình đường dẫn DB
DB_PATH = "/data/verify.db"
if not os.path.exists("/data"):
    DB_PATH = "verify.db"

# Hàm đảm bảo bảng tồn tại (Chạy mỗi khi cần truy vấn)
async def ensure_table_exists():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS attempts (
                user_id INTEGER PRIMARY KEY,
                status TEXT
            )
        """)
        await db.commit()

QUESTIONS_DATA = [
    {
        "question": "Câu 1: Tacet Mark của Chisa nằm ở đâu?",
        "options": [
            {"label": "Lưỡi", "value": "wrong_1"},
            {"label": "Tay phải", "value": "correct"},
            {"label": "Bàn chân", "value": "wrong_2"}
        ],
        "correct_value": "correct"
    },
    {
        "question": "Câu 2: Tên của con Capybara là gì?",
        "options": [
            {"label": "Naponmi", "value": "wrong_1"},
            {"label": "Namipon", "value": "correct"},
            {"label": "Miponna", "value": "wrong_2"}
        ],
        "correct_value": "correct"
    },
    {
        "question": "Câu 3: Chisa gây hiệu ứng xấu gì lên địch?",
        "options": [
            {"label": "Spectro Frazzle", "value": "wrong_1"},
            {"label": "Electro Flare", "value": "wrong_2"},
            {"label": "Havoc Bane", "value": "correct"}
        ],
        "correct_value": "correct"
    },
    {
        "question": "Câu 4: Trấn Chisa substat là gì?",
        "options": [
            {"label": "Crit Rate", "value": "correct"},
            {"label": "Crit Damage", "value": "wrong_1"},
            {"label": "ATK", "value": "wrong_2"}
        ],
        "correct_value": "correct"
    },
    {
        "question": "Câu 5: Chisa là vợ đúng ko??",
        "options": [
            {"label": "Đúng", "value": "correct"},
            {"label": "Không", "value": "wrong_1"},
        ],
        "correct_value": "correct"
    }
]

async def has_attempted(user_id):
    await ensure_table_exists()
    
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM attempts WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone() is not None

async def save_attempt(user_id):
    await ensure_table_exists()
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO attempts (user_id, status) VALUES (?, ?)", (user_id, "attempted"))
        await db.commit()

class QuestionSelect(Select):
    def __init__(self, question_index, current_view):
        self.question_index = question_index
        self.current_view = current_view
        q_data = QUESTIONS_DATA[question_index]
        
        options = []
        for opt in q_data["options"]:
            options.append(discord.SelectOption(label=opt["label"], value=opt["value"]))

        super().__init__(placeholder="Chọn đáp án...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0]
        correct_value = QUESTIONS_DATA[self.question_index]["correct_value"]

        if selected_value == correct_value:
            if self.question_index + 1 < len(QUESTIONS_DATA):
                next_view = QuizView(self.question_index + 1)
                await interaction.response.edit_message(content=QUESTIONS_DATA[self.question_index + 1]["question"], view=next_view)
            else:
                await save_attempt(interaction.user.id)
                
                guild = interaction.guild
                if not guild:
                    await interaction.response.edit_message(content="Lỗi: Không tìm thấy Server context.", view=None)
                    return

                role = guild.get_role(VERIFY_ROLE_ID)
                
                if role:
                    try:
                        member = guild.get_member(interaction.user.id)
                        if member is None:
                            member = await guild.fetch_member(interaction.user.id)

                        await member.add_roles(role)
                        await interaction.response.edit_message(content=f"Chúc mừng bạn là một Chíacon chân chính. Hãy truy cập <#{1450232000584618057}> bọn mình có món quà nho nhỏ cho bạn.", view=None)
                    
                    except discord.Forbidden:
                        await interaction.response.edit_message(content="Lỗi: Bot không có quyền cấp Role này.", view=None)
                    except Exception as e:
                        await interaction.response.edit_message(content=f"Đã xảy ra lỗi hệ thống: {e}", view=None)
                else:
                    await interaction.response.edit_message(content="Bạn đã trả lời đúng hết nhưng không tìm thấy Role ID.", view=None)
        else:
            await save_attempt(interaction.user.id) 
            await interaction.response.edit_message(content="Sai rồi! Rất tiếc, bạn méo phải Chíacon.", view=None)

class QuizView(View):
    def __init__(self, question_index=0):
        super().__init__(timeout=180)
        self.add_item(QuestionSelect(question_index, self))

class StartVerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Khảo sát Chíacon", style=discord.ButtonStyle.green, custom_id="verify_start_btn")
    async def start_button(self, interaction: discord.Interaction, button: Button):
        if await has_attempted(interaction.user.id):
            await interaction.response.send_message("Bạn đã tham gia khảo sát rồi, không thể thực hiện lại.", ephemeral=True)
            return

        await interaction.response.send_message(
            content=QUESTIONS_DATA[0]["question"],
            view=QuizView(0),
            ephemeral=True
        )

class VerifySystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setup_verify(self, ctx):
        if ctx.channel.id != VERIFY_CHANNEL_ID:
            return
        await ctx.send("Nhấn vào nút bên dưới để bắt đầu xác thực. Lưu ý: Bạn chỉ được phép làm 1 lần duy nhất.", view=StartVerifyView())

async def setup(bot):
    try:
        await ensure_table_exists()
        print(f"Đã khởi tạo SQLite thành công tại {DB_PATH}")
    except Exception as e:
        print(f"Lỗi khởi tạo DB: {e}")

    # Đăng ký View và Cog
    bot.add_view(StartVerifyView())
    await bot.add_cog(VerifySystem(bot))