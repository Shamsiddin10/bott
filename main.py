import telebot
from telebot import types

TOKEN = ("8264391860:AAH1Xrg_l2jmFBwV3yxbmysipeL5zNl4L94")
ADMIN_ID = 7384088509 
bot = telebot.TeleBot(TOKEN)

# 🍕 Mahsulotlar bazasi
MENU = {
    "lavash": {"name": "🌯 Lavash Standart", "price": 30000, "image": "https://images.unsplash.com/photo-1628191140046-8dd396d13693", "desc": "Mol go'shti, chips, pomidor, bodring va mayonez."},
    "shaurma": {"name": "🥙 Shaurma", "price": 26000, "image": "https://images.unsplash.com/photo-1529006557810-274b9b2fc783", "desc": "Maxsus non ichida go'sht va sousli sabzavotlar."},
    "pizza": {"name": "🍕 Pizza Pepperoni", "price": 65000, "image": "https://images.unsplash.com/photo-1534308983496-4fabb1a015ee", "desc": "Pishloq, pepperoni va maxsus tomat sousi."},
    "burger": {"name": "🍔 Burger", "price": 25000, "image": "https://images.unsplash.com/photo-1571091718767-18b5b1457add", "desc": "Mol go'shti, pishloq, maxsus sous."},
    "hotdog": {"name": "🌭 Hot-dog", "price": 20000, "image": "https://images.unsplash.com/photo-1541234406184-297f66a297e5", "desc": "Sosiska, xantal va ketchup."},
    "fri": {"name": "🍟 Fri", "price": 15000, "image": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877", "desc": "Qarsildoq kartoshka fri."},
    "cola": {"name": "🥤 Cola 0.5L", "price": 10000, "image": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97", "desc": "Muzdek Coca-Cola."},
    "choy": {"name": "🍵 Ko'k choy", "price": 5000, "image": "https://images.unsplash.com/photo-1576092768241-dec231879fc3", "desc": "Limonli issiq ko'k choy."}
}

user_orders = {}

# --- Klaviaturalar ---
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📋 Menyu", "🛒 Savatcha")
    markup.add("📞 Aloqa", "⚙️ Admin")
    return markup

def menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for item in MENU.values():
        markup.add(types.KeyboardButton(item['name']))
    markup.add(types.KeyboardButton("⬅️ Orqaga"))
    return markup

# --- Bot mantiqi ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Xush kelibsiz! Marhamat, tanlang:", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: any(m['name'] == message.text for m in MENU.values()))
def product_detail(message):
    product_key = next((k for k, v in MENU.items() if v['name'] == message.text), None)
    if product_key:
        item = MENU[product_key]
        caption = f"✨ **{item['name']}**\n\n📖 {item['desc']}\n💰 Narxi: {item['price']} so'm"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ Savatga qo'shish", callback_data=f"add_{product_key}"))
        bot.send_photo(message.chat.id, item['image'], caption=caption, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_'))
def callback_add(call):
    key = call.data.replace('add_', '')
    user_id = call.message.chat.id
    user_orders.setdefault(user_id, []).append(key)
    bot.answer_callback_query(call.id, f"{MENU[key]['name']} qo'shildi! ✅")

@bot.message_handler(func=lambda message: message.text == "🛒 Savatcha")
def show_cart(message):
    user_id = message.chat.id
    orders = user_orders.get(user_id, [])
    if not orders:
        bot.send_message(user_id, "Savatchangiz bo'sh! 🛒")
        return
    res = "🛒 **Sizning savatchangiz:**\n\n"
    total = 0
    for x in set(orders):
        count = orders.count(x)
        price = MENU[x]['price'] * count
        total += price
        res += f"🔸 {MENU[x]['name']} x {count} = {price} so'm\n"
    res += f"\n💰 **Jami: {total} so'm**"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✅ Buyurtmani tasdiqlash", "🗑 Tozalash", "⬅️ Orqaga")
    bot.send_message(user_id, res, reply_markup=markup, parse_mode="Markdown")

# --- BUYURTMANI TASDIQLASH (ID olib tashlangan) ---
@bot.message_handler(func=lambda message: message.text == "✅ Buyurtmani tasdiqlash")
def confirm_order(message):
    user_id = message.chat.id
    orders = user_orders.get(user_id, [])
    
    if not orders:
        bot.send_message(user_id, "Savat bo'sh!")
        return

    # Foydalanuvchiga javob
    bot.send_message(user_id, "✅ Buyurtmangiz qabul qilindi!\n\nBizni tanlaganingizdan xursandmiz! 😊", reply_markup=main_keyboard())

    # Adminga xabar (ID olib tashlandi, faqat Ism va Username qoldi)
    user_name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "Developer"
    
    admin_msg = f"🆕 **Yangi buyurtma!**\n\n👤 Mijoz: {user_name}\n📱 Telegram: {username}\n\n"
    total = 0
    for x in set(orders):
        count = orders.count(x)
        price = MENU[x]['price'] * count
        total += price
        admin_msg += f"• {MENU[x]['name']} x {count}\n"
    admin_msg += f"\n💰 Jami: {total} so'm"
    
    bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    
    # Savatni tozalash
    user_orders[user_id] = []

@bot.message_handler(func=lambda message: message.text == "🗑 Tozalash")
def clear_cart(message):
    user_orders[message.chat.id] = []
    bot.send_message(message.chat.id, "Savat tozalandi!", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "⬅️ Orqaga")
def back(message):
    bot.send_message(message.chat.id, "Asosiy menyu", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "📋 Menyu")
def menu_list(message):
    bot.send_message(message.chat.id, "Taomni tanlang:", reply_markup=menu_keyboard())

@bot.message_handler(func=lambda message: message.text == "📞 Aloqa")
def contact(message):
    bot.send_message(message.chat.id, "📞 Tel: +998 94 128 30 84\n📍 Manzil: Asaka")

@bot.message_handler(func=lambda message: message.text == "⚙️ Admin")
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "Xush kelibsiz, Admin!")
    else:
        bot.send_message(message.chat.id, "Faqat adminlar uchun! 🛑")

bot.polling(none_stop=True)