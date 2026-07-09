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
    def generate_random_stk():
        """Tạo STK random (16-19 số)"""
        return ''.join(random.choices(string.digits, k=16))
    
    @staticmethod
    def generate_random_name():
        """Tạo tên ngẫu nhiên"""
        first_names = ["NGUYỄN", "TRẦN", "PHẠM", "HOÀNG", "VŨ", "ĐỖ", "CÂU", "ĐẶNG", "BÙI", "DƯ"]
        middle_names = ["VĂN", "QUỐC", "THANH", "MINH", "ĐỨC", "HỮU", "VIỆt", "TRỊ"]
        last_names = ["AN", "ANH", "BÌNH", "CHI", "DŨNG", "DỰC", "GIANG", "HÒA", "HƯƠNG", "KỲ"]
        
        return f"{random.choice(first_names)} {random.choice(middle_names)} {random.choice(last_names)}"
    
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
        if name[0].isdigit():  # Không được bắt đầu bằng số
            return False
        return True
    
    @staticmethod
    def format_bank_data_display(data_list):
        """Format hiển thị kho data cho dễ nhập hàng loạt"""
        formatted = "STK | TÊN | NGÂN HÀNG\n"
        formatted += "=" * 50 + "\n"
        for idx, (stk, name, bank_name) in enumerate(data_list, 1):
            formatted += f"{idx}. {stk} | {name} | {bank_name}\n"
        return formatted
    
    @staticmethod
    def parse_bank_data_input(input_text):
        """Parse input hàng loạt dạng STK|Tên|Ngân hàng"""
        lines = input_text.strip().split('\n')
        data_list = []
        errors = []
        
        for idx, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split('|')
            if len(parts) != 3:
                errors.append(f"Dòng {idx}: Sai định dạng (phải là STK|Tên|Ngân hàng)")
                continue
            
            stk = parts[0].strip()
            name = parts[1].strip()
            bank_name = parts[2].strip()
            
            if not Base64Handler.validate_stk(stk):
                errors.append(f"Dòng {idx}: STK '{stk}' không hợp lệ")
                continue
            
            if not Base64Handler.validate_name(name):
                errors.append(f"Dòng {idx}: Tên '{name}' không hợp lệ")
                continue
            
            data_list.append((stk, name, bank_name))
        
        return data_list, errors
    
    @staticmethod
    def create_base64_from_phone_and_data(user_id, phone):
        """Tạo Base64 bằng cách lấy SĐT + random data từ kho"""
        # Lấy data bank từ kho
        bank_data = db.get_bank_data(user_id)
        
        if not bank_data:
            return None, "Kho data trống, vui lòng thêm dữ liệu"
        
        # Random 1 data
        selected_data = random.choice(bank_data)
        stk, name, bank_name = selected_data[1], selected_data[2], selected_data[3]
        
        # Validate phone
        if not Base64Handler.validate_phone(phone):
            return None, "Số điện thoại không hợp lệ"
        
        # Tạo thông tin
        username = Base64Handler.generate_random_username()
        password = Base64Handler.generate_random_password()
        withdraw_pw = Base64Handler.generate_random_password()
        
        # Tạo Base64
        base64_code = Base64Handler.create_base64(
            username, password, withdraw_pw, name, phone, stk, bank_name
        )
        
        # Log
        db.add_base64_log(user_id, username, password, withdraw_pw, name, phone, stk, bank_name, base64_code)
        
        # Xóa data đã dùng
        db.delete_bank_data(selected_data[0])
        
        return base64_code, None
