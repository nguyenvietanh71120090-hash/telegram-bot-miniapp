import sqlite3
import json
from datetime import datetime
import os

DATABASE_FILE = "bot_data.db"

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Tạo toàn bộ bảng"""
        
        # Bảng User
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                full_name TEXT,
                balance REAL DEFAULT 0,
                va_deposit REAL DEFAULT 0,
                is_admin BOOLEAN DEFAULT 0,
                is_banned BOOLEAN DEFAULT 0,
                ban_until TIMESTAMP,
                approved BOOLEAN DEFAULT 0,
                referrer_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bảng Kho Data (STK | Tên | Ngân hàng)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_bank_data (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                stk TEXT,
                name TEXT,
                bank_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Bảng Kho SĐT
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_phone_data (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Bảng Base64 Log
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS base64_log (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                username TEXT,
                password TEXT,
                withdraw_pw TEXT,
                full_name TEXT,
                phone TEXT,
                stk TEXT,
                bank_name TEXT,
                base64_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Bảng KienLongBank VA
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS kienlong_va (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                full_name TEXT,
                account_number TEXT,
                bank_name TEXT DEFAULT 'KienLongBank',
                ctv_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Bảng Proxy
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS proxies (
                id INTEGER PRIMARY KEY,
                ip TEXT,
                port INTEGER,
                username TEXT,
                password TEXT,
                proxy_type TEXT,
                added_by_admin INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bảng Voucher MBBank
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vouchers (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                phone TEXT,
                quantity INTEGER,
                note TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Bảng Giao dịch nạp tiền
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                amount REAL,
                type TEXT,
                status TEXT DEFAULT 'pending',
                transaction_code TEXT,
                approved_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Bảng Cấu hình Admin
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Bảng Mã khuyến mãi
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS promo_codes (
                id INTEGER PRIMARY KEY,
                code TEXT UNIQUE,
                amount REAL,
                uses_left INTEGER,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bảng Telethon Session
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS telethon_session (
                id INTEGER PRIMARY KEY,
                admin_id INTEGER,
                phone_number TEXT,
                api_id TEXT,
                api_hash TEXT,
                session_string TEXT,
                is_active BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users(id)
            )
        ''')
        
        # Bảng Rate Limit (chống spam)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_limit (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                action TEXT,
                count INTEGER DEFAULT 1,
                reset_at TIMESTAMP,
                UNIQUE(user_id, action)
            )
        ''')
        
        self.conn.commit()
    
    def add_user(self, telegram_id, username, full_name):
        """Thêm user mới"""
        try:
            self.cursor.execute('''
                INSERT INTO users (telegram_id, username, full_name)
                VALUES (?, ?, ?)
            ''', (telegram_id, username, full_name))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_user(self, telegram_id):
        """Lấy info user"""
        self.cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        return self.cursor.fetchone()
    
    def get_user_by_id(self, user_id):
        """Lấy user theo ID"""
        self.cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()
    
    def update_balance(self, telegram_id, amount, balance_type='balance'):
        """Cộng/trừ tiền"""
        self.cursor.execute(f'UPDATE users SET {balance_type} = {balance_type} + ? WHERE telegram_id = ?', 
                           (amount, telegram_id))
        self.conn.commit()
    
    def set_balance(self, telegram_id, amount, balance_type='balance'):
        """Set tiền (không cộng)"""
        self.cursor.execute(f'UPDATE users SET {balance_type} = ? WHERE telegram_id = ?', 
                           (amount, telegram_id))
        self.conn.commit()
    
    def add_bank_data(self, user_id, stk, name, bank_name):
        """Thêm vào kho data"""
        self.cursor.execute('''
            INSERT INTO user_bank_data (user_id, stk, name, bank_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, stk, name, bank_name))
        self.conn.commit()
    
    def get_bank_data(self, user_id):
        """Lấy toàn bộ kho data của user"""
        self.cursor.execute('''
            SELECT id, stk, name, bank_name FROM user_bank_data WHERE user_id = ?
        ''', (user_id,))
        return self.cursor.fetchall()
    
    def delete_bank_data(self, data_id):
        """Xóa 1 dòng data"""
        self.cursor.execute('DELETE FROM user_bank_data WHERE id = ?', (data_id,))
        self.conn.commit()
    
    def add_phone_data(self, user_id, phone):
        """Thêm SĐT vào kho"""
        self.cursor.execute('''
            INSERT INTO user_phone_data (user_id, phone)
            VALUES (?, ?)
        ''', (user_id, phone))
        self.conn.commit()
    
    def get_phone_data(self, user_id):
        """Lấy toàn bộ kho SĐT"""
        self.cursor.execute('''
            SELECT id, phone FROM user_phone_data WHERE user_id = ?
        ''', (user_id,))
        return self.cursor.fetchall()
    
    def delete_phone_data(self, phone_id):
        """Xóa 1 SĐT"""
        self.cursor.execute('DELETE FROM user_phone_data WHERE id = ?', (phone_id,))
        self.conn.commit()
    
    def set_config(self, key, value):
        """Set giá trong admin panel"""
        self.cursor.execute('''
            INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)
        ''', (key, str(value)))
        self.conn.commit()
    
    def get_config(self, key, default=None):
        """Lấy giá cấu hình"""
        self.cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
        result = self.cursor.fetchone()
        return result[0] if result else default
    
    def add_va(self, user_id, full_name, account_number):
        """Lưu VA tạo được"""
        self.cursor.execute('''
            INSERT INTO kienlong_va (user_id, full_name, account_number)
            VALUES (?, ?, ?)
        ''', (user_id, full_name, account_number))
        self.conn.commit()
    
    def get_va_list(self, user_id):
        """Lấy danh sách VA của user"""
        self.cursor.execute('''
            SELECT id, full_name, account_number, created_at FROM kienlong_va WHERE user_id = ?
        ''', (user_id,))
        return self.cursor.fetchall()
    
    def add_base64_log(self, user_id, username, password, withdraw_pw, full_name, phone, stk, bank_name, base64_code):
        """Log Base64 đã tạo"""
        self.cursor.execute('''
            INSERT INTO base64_log (user_id, username, password, withdraw_pw, full_name, phone, stk, bank_name, base64_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, password, withdraw_pw, full_name, phone, stk, bank_name, base64_code))
        self.conn.commit()
    
    def add_proxy(self, ip, port, username, password, proxy_type):
        """Thêm proxy"""
        self.cursor.execute('''
            INSERT INTO proxies (ip, port, username, password, proxy_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (ip, port, username, password, proxy_type))
        self.conn.commit()
    
    def get_proxies(self, proxy_type=None):
        """Lấy danh sách proxy"""
        if proxy_type:
            self.cursor.execute('SELECT * FROM proxies WHERE proxy_type = ?', (proxy_type,))
        else:
            self.cursor.execute('SELECT * FROM proxies')
        return self.cursor.fetchall()
    
    def add_transaction(self, user_id, amount, trans_type, trans_code):
        """Thêm giao dịch"""
        self.cursor.execute('''
            INSERT INTO transactions (user_id, amount, type, transaction_code)
            VALUES (?, ?, ?, ?)
        ''', (user_id, amount, trans_type, trans_code))
        self.conn.commit()
        
        # Lấy ID giao dịch vừa tạo
        self.cursor.execute('SELECT last_insert_rowid()')
        return self.cursor.fetchone()[0]
    
    def approve_transaction(self, trans_id, admin_id):
        """Duyệt giao dịch"""
        self.cursor.execute('''
            UPDATE transactions SET status = 'approved', approved_by = ?, approved_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (admin_id, trans_id))
        self.conn.commit()
    
    def get_pending_transactions(self):
        """Lấy giao dịch chưa duyệt"""
        self.cursor.execute('SELECT * FROM transactions WHERE status = "pending"')
        return self.cursor.fetchall()
    
    def add_promo_code(self, code, amount, uses):
        """Tạo mã khuyến mãi"""
        self.cursor.execute('''
            INSERT INTO promo_codes (code, amount, uses_left)
            VALUES (?, ?, ?)
        ''', (code, amount, uses))
        self.conn.commit()
    
    def use_promo_code(self, code):
        """Sử dụng mã khuyến mãi"""
        self.cursor.execute('''
            UPDATE promo_codes SET uses_left = uses_left - 1 WHERE code = ? AND uses_left > 0
        ''', (code,))
        self.conn.commit()
        
        self.cursor.execute('SELECT amount FROM promo_codes WHERE code = ?', (code,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def ban_user(self, telegram_id, ban_until=None):
        """Khóa user"""
        self.cursor.execute('''
            UPDATE users SET is_banned = 1, ban_until = ? WHERE telegram_id = ?
        ''', (ban_until, telegram_id))
        self.conn.commit()
    
    def unban_user(self, telegram_id):
        """Mở khóa user"""
        self.cursor.execute('''
            UPDATE users SET is_banned = 0, ban_until = NULL WHERE telegram_id = ?
        ''', (telegram_id,))
        self.conn.commit()
    
    def approve_user(self, telegram_id):
        """Duyệt quyền user"""
        self.cursor.execute('''
            UPDATE users SET approved = 1 WHERE telegram_id = ?
        ''', (telegram_id,))
        self.conn.commit()
    
    def get_all_users(self):
        """Lấy tất cả user (cho export Excel)"""
        self.cursor.execute('SELECT telegram_id, username, full_name, balance, va_deposit, created_at FROM users')
        return self.cursor.fetchall()
    
    def check_rate_limit(self, user_id, action, limit=5, window=60):
        """Kiểm tra rate limit (chống spam)"""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        reset_time = now + timedelta(seconds=window)
        
        self.cursor.execute('''
            SELECT count, reset_at FROM rate_limit WHERE user_id = ? AND action = ?
        ''', (user_id, action))
        
        result = self.cursor.fetchone()
        
        if not result:
            self.cursor.execute('''
                INSERT INTO rate_limit (user_id, action, count, reset_at) VALUES (?, ?, 1, ?)
            ''', (user_id, action, reset_time))
            self.conn.commit()
            return True
        
        count, reset_at = result
        reset_dt = datetime.fromisoformat(reset_at)
        
        if now > reset_dt:
            self.cursor.execute('''
                UPDATE rate_limit SET count = 1, reset_at = ? WHERE user_id = ? AND action = ?
            ''', (reset_time, user_id, action))
            self.conn.commit()
            return True
        
        if count < limit:
            self.cursor.execute('''
                UPDATE rate_limit SET count = count + 1 WHERE user_id = ? AND action = ?
            ''', (user_id, action))
            self.conn.commit()
            return True
        
        return False
    
    def close(self):
        self.conn.close()

# Khởi tạo database
db = Database()
