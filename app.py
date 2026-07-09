import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from backend.database import db
from backend.base64_handler import Base64Handler
from backend.telethon_auto import telethon_client
import asyncio
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

ADMIN_ID = int(os.getenv('ADMIN_ID'))
FLASK_SECRET = os.getenv('FLASK_SECRET_KEY', 'secret')

# ========== FRONTEND ROUTES ==========

@app.route('/')
def index():
    """Serve mini app"""
    return send_from_directory('frontend', 'index.html')

@app.route('/admin')
def admin():
    """Serve admin panel"""
    return send_from_directory('frontend', 'admin_panel.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('frontend', filename)

# ========== API ROUTES ==========

@app.route('/api/user/info', methods=['POST'])
def get_user_info():
    """Lấy thông tin user"""
    data = request.json
    telegram_id = data.get('telegram_id')
    
    user = db.get_user(telegram_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user[0],
        'telegram_id': user[1],
        'username': user[2],
        'full_name': user[3],
        'balance': user[4],
        'va_deposit': user[5],
        'is_admin': user[6],
        'approved': user[9]
    })

@app.route('/api/base64/create', methods=['POST'])
def create_base64():
    """Tạo Base64"""
    data = request.json
    telegram_id = data.get('telegram_id')
    
    user = db.get_user(telegram_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    username = data.get('username')
    password = data.get('password')
    withdraw_pw = data.get('withdraw_pw')
    full_name = data.get('full_name')
    phone = data.get('phone')
    stk = data.get('stk')
    bank_name = data.get('bank_name')
    
    # Validate
    if not Base64Handler.validate_phone(phone) or not Base64Handler.validate_stk(stk):
        return jsonify({'error': 'Invalid phone or STK'}), 400
    
    base64_code = Base64Handler.create_base64(
        username, password, withdraw_pw, full_name, phone, stk, bank_name
    )
    
    # Log
    db.add_base64_log(user[0], username, password, withdraw_pw, full_name, phone, stk, bank_name, base64_code)
    
    return jsonify({
        'base64': base64_code,
        'created_at': datetime.now().isoformat()
    })

@app.route('/api/bankdata/add', methods=['POST'])
def add_bank_data():
    """Thêm data vào kho"""
    data = request.json
    telegram_id = data.get('telegram_id')
    
    user = db.get_user(telegram_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user_id = user[0]
    bank_data_list = data.get('data', [])
    
    count = 0
    for item in bank_data_list:
        stk = item.get('stk')
        name = item.get('name')
        bank_name = item.get('bank_name')
        
        if Base64Handler.validate_stk(stk) and Base64Handler.validate_name(name):
            db.add_bank_data(user_id, stk, name, bank_name)
            count += 1
    
    return jsonify({'added': count})

@app.route('/api/bankdata/list', methods=['POST'])
def list_bank_data():
    """Lấy danh sách data"""
    data = request.json
    telegram_id = data.get('telegram_id')
    
    user = db.get_user(telegram_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user_id = user[0]
    bank_data = db.get_bank_data(user_id)
    
    return jsonify({
        'data': [
            {'id': d[0], 'stk': d[1], 'name': d[2], 'bank_name': d[3]}
            for d in bank_data
        ]
    })

@app.route('/api/bankdata/delete', methods=['POST'])
def delete_bank_data():
    """Xóa data"""
    data = request.json
    data_id = data.get('data_id')
    
    db.delete_bank_data(data_id)
    return jsonify({'success': True})

@app.route('/api/phone/add', methods=['POST'])
def add_phone():
    """Thêm SĐT"""
    data = request.json
    telegram_id = data.get('telegram_id')
    phones = data.get('phones', [])
    
    user = db.get_user(telegram_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user_id = user[0]
    count = 0
    
    for phone in phones:
        if Base64Handler.validate_phone(phone):
            db.add_phone_data(user_id, phone)
            count += 1
    
    return jsonify({'added': count})

@app.route('/api/phone/list', methods=['POST'])
def list_phone():
    """Lấy danh sách SĐT"""
    data = request.json
    telegram_id = data.get('telegram_id')
    
    user = db.get_user(telegram_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user_id = user[0]
    phones = db.get_phone_data(user_id)
    
    return jsonify({
        'phones': [
            {'id': p[0], 'phone': p[1]}
            for p in phones
        ]
    })

@app.route('/api/phone/delete', methods=['POST'])
def delete_phone():
    """Xóa SĐT"""
    data = request.json
    phone_id = data.get('phone_id')
    
    db.delete_phone_data(phone_id)
    return jsonify({'success': True})

@app.route('/api/va/create', methods=['POST'])
def create_va():
    """Tạo VA"""
    data = request.json
    telegram_id = data.get('telegram_id')
    full_name = data.get('full_name')
    
    user = db.get_user(telegram_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Gọi Telethon async
    try:
        loop = asyncio.new_event_loop()
        result, error = loop.run_until_complete(
            telethon_client.create_va_kienlong(full_name)
        )
        loop.close()
        
        if error:
            return jsonify({'error': error}), 400
        
        # Lưu vào DB
        db.add_va(user[0], result['name'], result['account_number'])
        
        return jsonify({
            'name': result['name'],
            'account_number': result['account_number'],
            'bank': 'KienLongBank'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/va/list', methods=['POST'])
def list_va():
    """Lấy danh sách VA"""
    data = request.json
    telegram_id = data.get('telegram_id')
    
    user = db.get_user(telegram_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user_id = user[0]
    vas = db.get_va_list(user_id)
    
    return jsonify({
        'vas': [
            {
                'id': v[0],
                'name': v[1],
                'account_number': v[2],
                'created_at': v[3]
            }
            for v in vas
        ]
    })

# ========== ADMIN ROUTES ==========

@app.route('/api/admin/config/get', methods=['POST'])
def admin_get_config():
    """Lấy config"""
    data = request.json
    if data.get('admin_id') != ADMIN_ID:
        return jsonify({'error': 'Unauthorized'}), 401
    
    key = data.get('key')
    value = db.get_config(key)
    
    return jsonify({'key': key, 'value': value})

@app.route('/api/admin/config/set', methods=['POST'])
def admin_set_config():
    """Set config"""
    data = request.json
    if data.get('admin_id') != ADMIN_ID:
        return jsonify({'error': 'Unauthorized'}), 401
    
    key = data.get('key')
    value = data.get('value')
    
    db.set_config(key, value)
    return jsonify({'success': True})

@app.route('/api/admin/users/list', methods=['POST'])
def admin_list_users():
    """Lấy danh sách users"""
    data = request.json
    if data.get('admin_id') != ADMIN_ID:
        return jsonify({'error': 'Unauthorized'}), 401
    
    users = db.get_all_users()
    
    return jsonify({
        'users': [
            {
                'telegram_id': u[0],
                'username': u[1],
                'full_name': u[2],
                'balance': u[3],
                'va_deposit': u[4],
                'created_at': u[5]
            }
            for u in users
        ]
    })

@app.route('/api/admin/user/ban', methods=['POST'])
def admin_ban_user():
    """Khóa user"""
    data = request.json
    if data.get('admin_id') != ADMIN_ID:
        return jsonify({'error': 'Unauthorized'}), 401
    
    telegram_id = data.get('telegram_id')
    ban_until = data.get('ban_until')
    
    db.ban_user(telegram_id, ban_until)
    return jsonify({'success': True})

@app.route('/api/admin/user/approve', methods=['POST'])
def admin_approve_user():
    """Duyệt user"""
    data = request.json
    if data.get('admin_id') != ADMIN_ID:
        return jsonify({'error': 'Unauthorized'}), 401
    
    telegram_id = data.get('telegram_id')
    db.approve_user(telegram_id)
    
    return jsonify({'success': True})

@app.route('/api/admin/transactions/pending', methods=['POST'])
def admin_pending_transactions():
    """Lấy giao dịch chưa duyệt"""
    data = request.json
    if data.get('admin_id') != ADMIN_ID:
        return jsonify({'error': 'Unauthorized'}), 401
    
    transactions = db.get_pending_transactions()
    
    return jsonify({
        'transactions': [
            {
                'id': t[0],
                'user_id': t[1],
                'amount': t[2],
                'type': t[3],
                'transaction_code': t[5],
                'created_at': t[7]
            }
            for t in transactions
        ]
    })

@app.route('/api/admin/transaction/approve', methods=['POST'])
def admin_approve_transaction():
    """Duyệt giao dịch"""
    data = request.json
    if data.get('admin_id') != ADMIN_ID:
        return jsonify({'error': 'Unauthorized'}), 401
    
    trans_id = data.get('trans_id')
    db.approve_transaction(trans_id, ADMIN_ID)
    
    return jsonify({'success': True})

# ========== ERROR HANDLERS ==========

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
