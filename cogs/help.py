import discord
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("HelpCog đã được khởi tạo!")

    @discord.app_commands.command(name='bothelp', description='Hiển thị thông tin về các lệnh của bot')
    async def bothelp(self, interaction: discord.Interaction):
        help_text = """
**Danh sách các lệnh của bot:**

- **`/join`**: Tham gia kênh voice hiện tại của người dùng.
- **`/leave`**: Rời khỏi kênh voice.
- **`/play <URL>`**: Phát nhạc từ YouTube bằng URL.
- **`/pause`**: Tạm dừng phát nhạc.
- **`/resume`**: Tiếp tục phát nhạc.
- **`/bothelp`**: Hiển thị thông tin về các lệnh.
- **`/claim`**: Nhận 30 tiền miễn phí mỗi ngày.
- **`/taixiu`**: Chơi Tài Xỉu.
  - **`bet`**: Số tiền muốn cược.
  - **`choice`**: Lựa chọn giữa 'Tài' hoặc 'Xỉu'.
  - **VD:** Muốn chọn Tài, sử dụng lệnh `/taixiu bet 10 choice tài`.
  - **VD:** Muốn chọn Xỉu, sử dụng lệnh `/taixiu bet 10 choice xỉu`.
        """
        await interaction.response.send_message(help_text)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
