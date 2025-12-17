import discord
import os
from pymongo import MongoClient
from discord.ext import commands
from discord.ui import View, Select, Button

VERIFY_CHANNEL_ID = 1450100315327168642
VERIFY_ROLE_ID = 1450138002121556049
TARGET_GUILD_ID = 1450079520756465758
MONGO_URI = os.getenv("MONGO_URI")

if MONGO_URI:
    try:
        cluster = MongoClient(MONGO_URI)
        db = cluster["auto_reply_bot"]    
        attempts_col = db["verify_attempts"] 
        print("Đã kết nối thành công tới MongoDB!")
    except Exception as e:
        print(f"Lỗi kết nối MongoDB: {e}")
        attempts_col = None
else:
    print("CẢNH BÁO: Chưa cấu hình MONGO_URI trong biến môi trường!")
    attempts_col = None

QUESTIONS_DATA = [
    {
        "question": "Câu 1: Chisa hiện tại bao nhiêu tuổi? (Câu này khó hãy xuy nghĩ kĩ)",
        "options": [
            {"label": "17 tuổi", "value": "wrong_1"},
            {"label": "18 tuổi", "value": "wrong_2"},
            {"label": "37 tuổi", "value": "correct"}
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

def has_attempted(user_id):
    if attempts_col is None: return False
    return attempts_col.find_one({"user_id": user_id}) is not None

def save_attempt(user_id):
    if attempts_col is not None:
        attempts_col.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id, "status": "attempted"}},
            upsert=True
        )

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
                save_attempt(interaction.user.id)
                
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
                        print(f"Lỗi quyền hạn: Bot không thể cấp role {role.name} cho {interaction.user.name}.")
                        await interaction.response.edit_message(content="Lỗi: Bot không có quyền cấp Role này (Role Bot thấp hơn Role cần cấp hoặc thiếu quyền Manage Roles). Vui lòng liên hệ Admin.", view=None)
                    except Exception as e:
                        print(f"Lỗi không xác định khi cấp role: {e}")
                        await interaction.response.edit_message(content=f"Đã xảy ra lỗi hệ thống: {e}", view=None)
                else:
                    await interaction.response.edit_message(content="Bạn đã trả lời đúng hết nhưng không tìm thấy Role ID trên Server. Vui lòng liên hệ Admin.", view=None)
        else:
            save_attempt(interaction.user.id) 
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
        if has_attempted(interaction.user.id):
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

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(StartVerifyView())

async def setup(bot):
    await bot.add_cog(VerifySystem(bot))
