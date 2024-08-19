import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import sqlite3
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)

class TaiXiu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('user_money.db', timeout=10)
        self.cursor = self.conn.cursor()
        
        # Tạo bảng nếu chưa tồn tại
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS money (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER,
            last_claim TEXT
        )
        ''')
        self.conn.commit()

    def get_balance(self, user_id):
        try:
            self.cursor.execute('SELECT balance FROM money WHERE user_id = ?', (user_id,))
            result = self.cursor.fetchone()
            if result and result[0] is not None:
                return result[0]
            return 100  # Trả về số dư mặc định là 100 nếu không có kết quả
        except Exception as e:
            logging.error(f'Error getting balance: {e}')
            return 100

    def update_balance(self, user_id, amount):
        try:
            self.cursor.execute('INSERT OR REPLACE INTO money (user_id, balance) VALUES (?, ?)', (user_id, amount))
            self.conn.commit()
        except Exception as e:
            logging.error(f'Error updating balance: {e}')

    def get_last_claim(self, user_id):
        try:
            self.cursor.execute('SELECT last_claim FROM money WHERE user_id = ?', (user_id,))
            result = self.cursor.fetchone()
            if result and result[0]:
                return datetime.fromisoformat(result[0])
            return None
        except Exception as e:
            logging.error(f'Error getting last claim: {e}')
            return None

    def update_last_claim(self, user_id):
        try:
            now = datetime.utcnow().isoformat()
            self.cursor.execute('INSERT OR REPLACE INTO money (user_id, last_claim) VALUES (?, ?)', (user_id, now))
            self.conn.commit()
        except Exception as e:
            logging.error(f'Error updating last claim: {e}')

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info('Cog TaiXiu đã sẵn sàng!')

    @app_commands.command(name='taixiu', description='Chơi Tài Xỉu và cá cược.')
    async def taixiu(self, interaction: discord.Interaction, bet: int, choice: str):
        user_id = interaction.user.id
        balance = self.get_balance(user_id)

        if balance <= 0:
            await interaction.response.send_message('Bạn không có đủ tiền để chơi. Vui lòng nạp thêm tiền trước khi chơi.', ephemeral=False)
            return

        if bet > balance:
            await interaction.response.send_message('Bạn không có đủ tiền để cược số tiền này.', ephemeral=False)
            return

        self.update_balance(user_id, balance - bet)
        await interaction.response.send_message(f'Bạn đã cược {bet} tiền vào {choice}. Kết quả sẽ được thông báo sau 15 giây...')
        await asyncio.sleep(15)

        result = random.choice(['Tài', 'Xỉu'])
        new_balance = self.get_balance(user_id)
        
        if choice.lower() == result.lower():
            self.update_balance(user_id, new_balance + bet *2 )
            await interaction.followup.send(f'Chúc mừng! Kết quả là {result}. Bạn đã thắng và nhận được {bet * 2} tiền. Số dư hiện tại của bạn là {new_balance + bet * 2} tiền.', ephemeral=False)
        else:
            await interaction.followup.send(f'Rất tiếc! Kết quả là {result}. Bạn đã thua và mất {bet * 2 } tiền. Số dư hiện tại của bạn là {new_balance} tiền.', ephemeral=False)

    @app_commands.command(name='claim', description='Nhận 30 tiền miễn phí mỗi 24 giờ.')
    async def claim(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        now = datetime.utcnow()
        last_claim = self.get_last_claim(user_id)

        if last_claim:
            time_since_last_claim = now - last_claim
            if time_since_last_claim < timedelta(hours=24):
                wait_time = timedelta(hours=24) - time_since_last_claim
                wait_time_str = str(wait_time).split('.')[0]
                logging.info(f'Người dùng {user_id} cần chờ thêm thời gian: {wait_time_str}')
                await interaction.response.send_message(f'Bạn đã nhận tiền gần đây. Vui lòng quay lại sau {wait_time_str}.', ephemeral=False)
                return

        balance = self.get_balance(user_id)
        if balance is None:
            balance = 100  # Cấp số dư mặc định nếu balance là None

        self.update_balance(user_id, balance + 30)
        self.update_last_claim(user_id)

        logging.info(f'Người dùng {user_id} nhận thêm 30 tiền.')
        await interaction.response.send_message('Bạn đã nhận 30 tiền miễn phí! Số dư hiện tại của bạn là {balance + 30} tiền.', ephemeral=False)

async def setup(bot):
    await bot.add_cog(TaiXiu(bot))
