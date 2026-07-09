import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import asyncio
from backend.database import db
import re

load_dotenv()

API_ID = int(os.getenv('API_ID', '30909656'))
API_HASH = os.getenv('API_HASH', '89f4892151c8205335ad0726b4727577')
TARGET_BOT = os.getenv('TARGET_BOT', 'msystem999bot')
CTV_CODE = os.getenv('CTV_CODE', 'TAM881_Vanhcai01')

class TelethonAutoVA:
    def __init__(self):
        self.client = None
        self.session_file = 'backend/telethon_sessions/admin_session'
        os.makedirs('backend/telethon_sessions', exist_ok=True)
    
    async def setup_session(self, phone_number):
        """Thiết lập Telethon session"""
        self.client = TelegramClient(self.session_file, API_ID, API_HASH)
        await self.client.connect()
        
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(phone_number)
            print(f"[Telethon] Mã OTP đã gửi tới {phone_number}")
            return True
        return False
    
    async def verify_otp(self, otp_code):
        """Xác thực OTP"""
        try:
            await self.client.sign_in(code=otp_code)
            print("[Telethon] Đăng nhập thành công!")
            return True
        except SessionPasswordNeededError:
            print("[Telethon] Cần mật khẩu 2FA")
            return False
        except Exception as e:
            print(f"[Telethon] Lỗi: {e}")
            return False
    
    async def verify_2fa_password(self, password):
        """Xác thực mật khẩu 2FA"""
        try:
            await self.client.sign_in(password=password)
            print("[Telethon] Đăng nhập 2FA thành công!")
            return True
        except Exception as e:
            print(f"[Telethon] Lỗi 2FA: {e}")
            return False
    
    async def create_va_kienlong(self, full_name):
        """Tự động tạo VA KienLongBank"""
        if not self.client or not await self.client.is_user_authorized():
            return None, "Session chưa được thiết lập"
        
        try:
            # Gửi /newva
            await self.client.send_message(TARGET_BOT, '/newva')
            await asyncio.sleep(1)
            
            # Chọn ngân hàng KLB
            await self.client.send_message(TARGET_BOT, 'KLB')
            await asyncio.sleep(1)
            
            # Gửi tên
            await self.client.send_message(TARGET_BOT, full_name)
            await asyncio.sleep(1)
            
            # Gửi mã CTV
            await self.client.send_message(TARGET_BOT, CTV_CODE)
            await asyncio.sleep(2)
            
            # Lấy tin nhắn cuối cùng từ bot
            async for message in self.client.iter_messages(TARGET_BOT, limit=1):
                response = message.text
                if 'Tạo Virtual Account' in response or 'Account' in response:
                    # Parse response
                    result = self.parse_va_response(response)
                    if result:
                        return result, None
            
            return None, "Không nhận được phản hồi từ bot"
        
        except Exception as e:
            return None, f"Lỗi: {str(e)}"
    
    @staticmethod
    def parse_va_response(response):
        """Parse phản hồi từ bot (ẩn CTV)"""
        # Tìm tên tài khoản
        name_match = re.search(r'Tên[\s:]+([^\n|]+)', response, re.IGNORECASE)
        # Tìm số tài khoản
        stk_match = re.search(r'(Số tài khoản|STK)[\s:]+([0-9]{10,})', response, re.IGNORECASE)
        
        if name_match and stk_match:
            return {
                "name": name_match.group(1).strip(),
                "account_number": stk_match.group(2)
            }
        return None
    
    async def close(self):
        """Đóng kết nối"""
        if self.client:
            await self.client.disconnect()

# Instance
telethon_client = TelethonAutoVA()
