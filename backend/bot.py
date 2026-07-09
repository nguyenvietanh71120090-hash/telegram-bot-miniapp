import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from backend.database import db
from backend.base64_handler import Base64Handler
from datetime import datetime, timedelta

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Thiết lập các handler"""
        # Commands
        self.app.add_handler(CommandHandler('start', self.start))
        self.app.add_handler(CommandHandler('themsdt', self.add_phone))
        self.app.add_handler(CommandHandler('themdata', self.add_data))
        self.app.add_handler(CommandHandler('checkkhodata', self.check_kho_data))
        self.app.add_handler(CommandHandler('base64', self.create_base64_menu))
        self.app.add_handler(CommandHandler('admin', self.admin_panel))
        
        # Callback
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /start"""
        user = update.effective_user
        telegram_id = user.id
        
        # Kiểm tra user tồn tại
        user_data = db.get_user(telegram_id)
        if not user_data:
            db.add_user(telegram_id, user.username or "unknown", user.first_name or "User")
        
        # Kiểm tra admin
        if telegram_id == ADMIN_ID:
            keyboard = [
                [InlineKeyboardButton("📊 Admin Panel", callback_data='admin_panel')],
                [InlineKeyboardButton("💰 Mini App", callback_data='miniapp')]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("💰 Mở Mini App", callback_data='miniapp')]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"🌸 Chào mừng {user.first_name}!\n\nBot hỗ trợ tạo Base64, Kho data, và VA KienLongBank.",
            reply_markup=reply_markup
        )
    
    async def add_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Thêm SĐT"""
        await update.message.reply_text(
            "📱 Nhập số điện thoại (định dạng: 0xxxxxxxxxx):"
        )
        context.user_data['waiting_for'] = 'phone'
    
    async def add_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Thêm data"""
        await update.message.reply_text(
            "📋 Nhập data (định dạng: STK|Tên|Ngân hàng)\n\nVí dụ:\n1234567890123456|NGUYEN VAN A|MB Bank\n9876543210987654|TRAN THI B|Vietcombank"
        )
        context.user_data['waiting_for'] = 'data'
    
    async def check_kho_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Kiểm tra kho data"""
        user = update.effective_user
        telegram_id = user.id
        user_data = db.get_user(telegram_id)
        
        if not user_data:
            await update.message.reply_text("❌ User không tồn tại")
            return
        
        user_id = user_data[0]
        bank_data = db.get_bank_data(user_id)
        
        if not bank_data:
            await update.message.reply_text("🗑️ Kho data trống")
            return
        
        text = "STK | TÊN | NGÂN HÀNG\n" + "="*50 + "\n"
        for idx, d in enumerate(bank_data, 1):
            text += f"{idx}. {d[1]} | {d[2]} | {d[3]}\n"
        
        await update.message.reply_text(f"<pre>{text}</pre>", parse_mode='HTML')
    
    async def create_base64_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Menu tạo Base64"""
        keyboard = [
            [InlineKeyboardButton("✏️ Nhập thủ công", callback_data='base64_manual')],
            [InlineKeyboardButton("🎲 Random toàn bộ", callback_data='base64_random')],
            [InlineKeyboardButton("📚 Từ kho data", callback_data='base64_from_kho')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Chọn cách tạo Base64:", reply_markup=reply_markup)
    
    async def admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Panel admin"""
        user = update.effective_user
        if user.id != ADMIN_ID:
            await update.message.reply_text("❌ Chỉ admin mới có quyền")
            return
        
        await update.message.reply_text("👑 Admin Panel - Mở Mini App")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý nút bấm"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'miniapp':
            await query.edit_message_text(
                text="🌸 Mini App\n\nMở Mini App để sử dụng tất cả tính năng.\n\n[Mini App sẽ được cấu hình sau]"
            )
        elif query.data == 'admin_panel':
            await query.edit_message_text(
                text="👑 Admin Panel\n\n[Admin Panel sẽ được cấu hình sau]"
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý tin nhắn"""
        user = update.effective_user
        telegram_id = user.id
        text = update.message.text
        
        if 'waiting_for' not in context.user_data:
            return
        
        waiting = context.user_data['waiting_for']
        user_data = db.get_user(telegram_id)
        user_id = user_data[0]
        
        if waiting == 'phone':
            if not Base64Handler.validate_phone(text):
                await update.message.reply_text("❌ SĐT không hợp lệ")
                return
            
            db.add_phone_data(user_id, text)
            await update.message.reply_text("✅ Thêm SĐT thành công")
            del context.user_data['waiting_for']
        
        elif waiting == 'data':
            lines = text.strip().split('\n')
            data_list = []
            errors = []
            
            for idx, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split('|')
                if len(parts) != 3:
                    errors.append(f"Dòng {idx}: Sai định dạng")
                    continue
                
                stk, name, bank_name = parts[0].strip(), parts[1].strip(), parts[2].strip()
                
                if not Base64Handler.validate_stk(stk) or not Base64Handler.validate_name(name):
                    errors.append(f"Dòng {idx}: Dữ liệu không hợp lệ")
                    continue
                
                db.add_bank_data(user_id, stk, name, bank_name)
                data_list.append((stk, name, bank_name))
            
            if errors:
                error_text = "\n".join(errors)
                await update.message.reply_text(f"❌ Lỗi:\n{error_text}")
            
            await update.message.reply_text(f"✅ Thêm {len(data_list)} data thành công")
            del context.user_data['waiting_for']
    
    def run(self):
        """Chạy bot"""
        self.app.run_polling()

# Tạo instance
bot = TelegramBot()
