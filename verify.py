import discord
from discord.ext import commands
from discord.ui import View, Select, Button

VERIFY_CHANNEL_ID = 1446129455440466066
VERIFY_ROLE_ID = 1446527733256552620
TARGET_GUILD_ID = 1446129454005883024

QUESTIONS_DATA = [
    {
        "question": "Câu 1: Chisa hiện tại bao nhiêu tuổi?",
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
            {"label": "Namipon", "value": "correct"},
            {"label": "Naponmi", "value": "wrong_1"},
            {"label": "Miponna", "value": "wrong_2"}
        ],
        "correct_value": "correct"
    },
    {
        "question": "Câu 3: Chisa gây hiệu ứng xấu gì lên địch?",
        "options": [
            {"label": "Havoc Bane", "value": "correct"},
            {"label": "Spectro Frazzle", "value": "wrong_1"},
            {"label": "Electro Flare", "value": "wrong_2"}
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
                guild = interaction.guild
                member = interaction.user
                role = guild.get_role(VERIFY_ROLE_ID)
                
                if role:
                    try:
                        await member.add_roles(role)
                        await interaction.response.edit_message(content="Chúc mừng bạn là một Chíacon chân chính.", view=None)
                    except discord.Forbidden:
                        await interaction.response.edit_message(content="Tôi không có quyền cấp role này. Vui lòng liên hệ Admin.", view=None)
                else:
                    await interaction.response.edit_message(content="Không tìm thấy Role ID. Vui lòng liên hệ Admin.", view=None)
        else:
            await interaction.response.edit_message(content="Sai rồi! Vui lòng thử lại từ đầu.", view=None)

class QuizView(View):
    def __init__(self, question_index=0):
        super().__init__(timeout=180)
        self.add_item(QuestionSelect(question_index, self))

class StartVerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Khảo sát Chíacon", style=discord.ButtonStyle.green, custom_id="verify_start_btn")
    async def start_button(self, interaction: discord.Interaction, button: Button):
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
        
        await ctx.send("Nhấn vào nút bên dưới để bắt đầu xác thực", view=StartVerifyView())

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(StartVerifyView())

async def setup(bot):
    await bot.add_cog(VerifySystem(bot))