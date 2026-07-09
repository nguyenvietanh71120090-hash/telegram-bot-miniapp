import base64
import json
import random
import string
from backend.database import db

class Base64Handler:
    @staticmethod
    def create_base64(username, password, withdraw_pw, full_name, phone, stk, bank_name):
        """Tạo mã Base64 từ dữ liệu"""
        data = {
            "username": username,
            "pw": password,
            "wd": withdraw_pw,
            "name": full_name,
            "phone": phone,
            "stk": stk,
            "bankname": bank_name
        }
        json_str = json.dumps(data, ensure_ascii=False)
        base64_code = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        return base64_code
    
    @staticmethod
    def decode_base64(base64_code):
        """Decode mã Base64"""
        try:
            json_str = base64.b64decode(base64_code).decode('utf-8')
            return json.loads(json_str)
        except:
            return None
    
    @staticmethod
    def generate_random_username():
        """Tạo username random"""
        prefix = "user_"
        random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return prefix + random_part
    
    @staticmethod
    def generate_random_password():
        """Tạo password random (10 ký tự)"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    
    @staticmethod
    def validate_phone(phone):
        """Kiểm tra SĐT hợp lệ"""
        phone = phone.strip()
        if len(phone) < 10 or len(phone) > 11:
            return False
        if not phone.isdigit():
            return False
        if not phone.startswith('0'):
            return False
        return True
    
    @staticmethod
    def validate_stk(stk):
        """Kiểm tra STK hợp lệ"""
        stk = stk.strip()
        if len(stk) < 10 or len(stk) > 20:
            return False
        if not stk.isdigit():
            return False
        return True
    
    @staticmethod
    def validate_name(name):
        """Kiểm tra tên hợp lệ"""
        name = name.strip()
        if len(name) < 3 or len(name) > 50:
            return False
        if name[0].isdigit():
            return False
        return True
