# 🌸 Telegram Bot Mini App - KienLongBank VA Tool

**Bot tự động tạo Virtual Account (VA) KienLongBank, quản lý Base64, Kho Data & Kho Số Điện Thoại**

## 🚀 Tính Năng

### 📱 Mini App (Frontend)
- ✅ Tạo Base64 (3 cách: Manual, Random, Từ kho data)
- ✅ Quản lý Kho Data (STK | Tên | Ngân hàng)
- ✅ Quản lý Kho Số Điện Thoại
- ✅ Tạo Virtual Account KienLongBank tự động
- ✨ Giao diện đẹp với animation & depth
- 📱 Responsive (Mobile first)

### 🤖 Bot Telegram
- /start - Menu chính
- /themsdt - Thêm số điện thoại
- /themdata - Thêm data vào kho
- /checkkhodata - Kiểm tra kho data
- /base64 - Menu tạo Base64
- /admin - Panel admin (chỉ admin)

### 🔧 Admin Panel
- 📊 Quản lý users
- 🚫 Khóa/Mở khóa users
- ✅ Duyệt users
- 💰 Quản lý giao dịch
- ⚙️ Cấu hình hệ thống
- 📋 Export dữ liệu

### 💾 Backend
- 🗄️ SQLite Database (Users, Data, Transactions, ...)
- 🔐 Base64 Encoding/Decoding
- 📲 Telethon Auto VA (Tự động tạo VA)
- 🌐 Flask API

---

## 📦 Cài Đặt

### 1. Clone Repository
```bash
git clone <repo-url>
cd telegram-bot-miniapp
```

### 2. Cài Dependencies
```bash
pip install -r requirements.txt
```

### 3. Cấu Hình .env
```bash
cp .env.example .env
```

Sửa file `.env`:
```
BOT_TOKEN=8868689120:AAFYIrYN7TVJjGO-224cYHLgsn6K4igclMs
ADMIN_ID=7598327240
API_ID=30909656
API_HASH=89f4892151c8205335ad0726b4727577
CTV_CODE=TAM881_Vanhcai01
TARGET_BOT=msystem999bot
FLASK_SECRET_KEY=telegram_miniapp_secret_key_2024
FLASK_PORT=5000
```

### 4. Chạy Ứng Dụng

**Chạy Bot + API:**
```bash
python run.py
```

**Hoặc chạy riêng:**
```bash
# Bot
python -m backend.bot

# API
python app.py
```

---

## 📁 Cấu Trúc Thư Mục

```
project/
├── .env                 # Config
├── requirements.txt     # Dependencies
├── run.py              # File chạy chính
├── app.py              # Flask API
├── bot_data.db         # SQLite Database (tự tạo)
│
├── backend/
│   ├── __init__.py
│   ├── database.py     # Database models
│   ├── base64_handler.py # Base64 utils
│   ├── telethon_auto.py  # Auto VA
│   └── bot.py          # Bot Telegram
│
├── frontend/
│   ├── index.html      # Mini App UI
│   ├── style.css       # Styling + Animation
│   ├── app.js          # Frontend Logic
│   └── admin_panel.html # Admin Dashboard
│
└── README.md
```

---

## 🔌 API Endpoints

### User Routes
- `POST /api/user/info` - Lấy thông tin user
- `POST /api/base64/create` - Tạo Base64
- `POST /api/bankdata/add` - Thêm data
- `POST /api/bankdata/list` - Lấy danh sách data
- `POST /api/bankdata/delete` - Xóa data
- `POST /api/phone/add` - Thêm SĐT
- `POST /api/phone/list` - Lấy danh sách SĐT
- `POST /api/va/create` - Tạo VA
- `POST /api/va/list` - Lấy danh sách VA

### Admin Routes
- `POST /api/admin/config/get` - Lấy config
- `POST /api/admin/config/set` - Set config
- `POST /api/admin/users/list` - Lấy danh sách users
- `POST /api/admin/user/ban` - Khóa user
- `POST /api/admin/user/approve` - Duyệt user
- `POST /api/admin/transactions/pending` - Lấy giao dịch chưa duyệt
- `POST /api/admin/transaction/approve` - Duyệt giao dịch

---

## 🎨 Giao Diện

### Mini App
- 📱 Gradient background (Purple - Pink)
- ✨ Smooth animations
- 🎯 Responsive design
- 🌙 Dark mode support
- 💫 Hover effects

### Colors
- Primary: `#667eea` → `#764ba2`
- Accent: `#f5576c`
- Background: `#f5f7fa`

---

## 🔐 Bảo Mật

- ✅ Admin ID verification cho tất cả admin routes
- ✅ Input validation (STK, Phone, Name)
- ✅ Database encryption (optional)
- ✅ Rate limiting (anti-spam)
- ✅ CORS enabled

---

## 📝 Hướng Dẫn Sử Dụng

### Tạo Base64
1. Mở Mini App
2. Chọn "🔓 Tạo Base64"
3. Chọn một trong 3 cách:
   - **Manual**: Nhập thủ công từng field
   - **Random**: Tạo ngẫu nhiên X mã
   - **Từ kho data**: Lấy data từ kho + SĐT
4. Copy Base64

### Quản Lý Data
1. Chọn "🗄️ Kho Data"
2. Tab "Thêm": Paste data (STK|Tên|Ngân hàng)
3. Tab "Xem": Xem & xóa dữ liệu

### Tạo VA
1. Chọn "🏦 VA KienLong"
2. Nhập tên người dùng
3. Click "🚀 Tạo VA"
4. Nhận kết quả (Tên + STK)

---

## 🐛 Troubleshooting

### Bot không response
- Check BOT_TOKEN có hợp lệ
- Restart bot: `python run.py`

### Telethon error
- Check API_ID, API_HASH
- OTP hết hạn? Gửi lại: `/start`

### Database error
- Xóa `bot_data.db` nếu bị corrupt
- Sẽ tự tạo mới

---

## 📞 Support

**Admin Telegram**: @yourusername

---

## 📄 License

MIT License

---

**Made with ❤️ by Developer**
