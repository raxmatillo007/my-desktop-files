# pizza_bot_full_fixed.py
# Talab: pip install pyTelegramBotAPI

import telebot
from telebot import types
import json
import os
from datetime import datetime
import random
import re
import traceback

# ====== SOZLASH ======
BOT_TOKEN = "8250278777:AAH48QXVN7ipKQNZLwnkBJqp42L6eO2p1BI"   # Tokening
ADMIN_ID = 7165482615  # admin chat id
ORDERS_FILE = "orders.json"
IMG_FOLDER = "img"     # rasm papkasi (relativ yo'l)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

# ====== MENYU ======
MENU = [
    {"id":1, "name":"Margherita", "desc":"Tomat sous, mozzarella, basil", "base_price":45000, "img": os.path.join(IMG_FOLDER, "margherita.jpg")},
    {"id":2, "name":"Pepperoni",  "desc":"Pepperoni, mozzarella, tomat sous", "base_price":55000, "img": os.path.join(IMG_FOLDER, "pepperoni.jpg")},
    {"id":3, "name":"Chicken BBQ","desc":"Tovuq, BBQ sous, pishloq", "base_price":60000, "img": os.path.join(IMG_FOLDER, "chicken_bbq.jpg")},
    {"id":4, "name":"Vegetarian","desc":"Sabzavotlar, mozzarella, pomidor", "base_price":50000, "img": os.path.join(IMG_FOLDER, "vegetarian.jpg")}
]

EXTRAS = {
    "Qo'shimcha pishloq":8000,
    "Qo'shimcha kolbasa":10000,
    "Qo'ziqorin":7000,
    "Achchiq sous":3000
}

DRINKS = {
    "Coca-Cola 1L":12000,
    "Fanta 1L":12000,
    "Sprite 1L":12000,
    "Pepsi 1L":12000,
    "Suv 1L":5000
}

DRINK_IMAGES = {
    "Coca-Cola 1L": os.path.join(IMG_FOLDER, "coca.jpg"),
    "Fanta 1L": os.path.join(IMG_FOLDER, "fanta.jpg"),
    "Sprite 1L": os.path.join(IMG_FOLDER, "sprite.jpg"),
    "Pepsi 1L": os.path.join(IMG_FOLDER, "pepsi.jpg"),
    "Suv 1L": os.path.join(IMG_FOLDER, "suv.jpg"),
}

SIZE_MULTIPLIERS = {"25":1.0, "30":1.25, "35":1.5}

# USER SESSION: chat_id -> session dict
USER_SESSION = {}

# ====== Helper functions ======
def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_orders(orders):
    try:
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Save orders error:", e)

def new_order_id():
    orders = load_orders()
    if not orders:
        return 1
    return max(o.get("id", 0) for o in orders) + 1

def format_order_short(o):
    return f"🆔{o['id']}  🍕{o['pizza_name']} ({o['size']} sm) x{o.get('quantity',1)}  💵{o['total']} so'm  [{o['status']}]"

def format_order_full(o):
    return (
        f"🆔 Buyurtma ID: {o['id']}\n"
        f"📅 {o.get('created_at')}\n"
        f"👤 {o.get('customer_name')}\n"
        f"📞 {o.get('phone')}\n"
        f"📍 {o.get('address')}\n"
        f"🍕 {o.get('pizza_name')} ({o.get('size')} sm) x{o.get('quantity',1)}\n"
        f"➕ Qo'shimchalar: {', '.join(o.get('extras') or ['yoq'])}\n"
        f"🥤 Ichimliklar: {', '.join(o.get('drinks') or ['yoq'])}\n"
        f"💳 To'lov: {o.get('payment_type')}\n"
        f"💰 Jami: {o.get('total')} so'm\n"
        f"🚚 Kuryer: {o.get('courier','-')}\n"
        f"📌 Holat: {o.get('status')}\n"
        f"ETA: {o.get('eta','-')}"
    )

def try_send_photo(chat_id, img_path, caption=None):
    """Rasmni yuborish: agar lokal fayl mavjud bo'lsa ochamiz; aks holda URL sifatida urinadi."""
    if not img_path:
        return False
    try:
        if os.path.exists(img_path):
            with open(img_path, "rb") as ph:
                bot.send_photo(chat_id, ph, caption=caption)
        else:
            bot.send_photo(chat_id, img_path, caption=caption)
        return True
    except Exception as e:
        print("send_photo error:", e)
        try:
            if caption:
                bot.send_message(chat_id, caption)
        except:
            pass
        return False

# ====== /start ======
@bot.message_handler(commands=["start"])
def cmd_start(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🍕 Menyu", "📦 Buyurtmalarim")
    kb.row("📍 Manzil yuborish", "📞 Biz bilan bog'lanish")
    bot.send_message(m.chat.id, "Salom! Hot Pizza ga xush kelibsiz 🍕\nMenyu uchun \"🍕 Menyu\" tugmasini bosing.", reply_markup=kb)

# ====== Menyu ======
@bot.message_handler(func=lambda m: m.text == "🍕 Menyu")
def show_menu(m):
    for item in MENU:
        caption = f"*{item['name']}*\n{item['desc']}\nNarx (25 sm): {item['base_price']} so'm"
        sent = try_send_photo(m.chat.id, item.get("img"), caption=caption)
        if not sent:
            bot.send_message(m.chat.id, caption)
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🛒 Tanlash", callback_data=f"select_{item['id']}"))
        bot.send_message(m.chat.id, "Tanlash uchun tugmani bosing", reply_markup=kb)

# ====== Pitsa tanlandi ======
@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("select_"))
def on_select(call):
    try:
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        pid = int(call.data.split("_")[1])
        item = next((x for x in MENU if x["id"] == pid), None)
        if not item:
            bot.send_message(chat_id, "Pitsa topilmadi. Iltimos menyudan qayta tanlang.")
            return
        USER_SESSION[chat_id] = {
            "pizza_id": pid,
            "pizza_name": item["name"],
            "base_price": item["base_price"],
            "size": None,
            "quantity": 1,
            "extras": [],
            "drinks": [],
            "customer_name": None,
            "phone": None,
            "address": None,
            "payment_type": None,
            "total": 0,
            "courier": None,
            "status": "Yangi"
        }
        kb = types.InlineKeyboardMarkup()
        for s in SIZE_MULTIPLIERS.keys():
            kb.add(types.InlineKeyboardButton(f"{s} sm", callback_data=f"size_{s}"))
        bot.send_message(chat_id, f"{item['name']} tanlandi. O'lchamni tanlang:", reply_markup=kb)
    except Exception:
        print(traceback.format_exc())

# ====== O'lcham ======
@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("size_"))
def on_size(call):
    try:
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        if chat_id not in USER_SESSION:
            bot.send_message(chat_id, "Sessiya topilmadi. /start bilan boshlang.")
            return
        size = call.data.split("_")[1]
        USER_SESSION[chat_id]["size"] = size
        kb = types.InlineKeyboardMarkup()
        for q in range(1, 11):
            kb.add(types.InlineKeyboardButton(f"{q} dona", callback_data=f"quantity_{q}"))
        bot.send_message(chat_id, f"O'lcham {size} sm tanlandi. Nechta pitsa olasiz?", reply_markup=kb)
    except Exception:
        print(traceback.format_exc())

# ====== Miqdor ======
@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("quantity_"))
def on_quantity(call):
    try:
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        if chat_id not in USER_SESSION:
            bot.send_message(chat_id, "Sessiya topilmadi.")
            return
        q = int(call.data.split("_")[1])
        USER_SESSION[chat_id]["quantity"] = q
        kb = types.InlineKeyboardMarkup()
        for d, price in DRINKS.items():
            kb.add(types.InlineKeyboardButton(f"{d} (+{price})", callback_data=f"drink_{d}"))
        kb.add(types.InlineKeyboardButton("⏭️ Ichimliksiz davom etish", callback_data="drinks_done"))
        bot.send_message(chat_id, "Ichimlik tanlang (istasa bir nechta tanlash mumkin):", reply_markup=kb)
    except Exception:
        print(traceback.format_exc())

# ====== Ichimliklar ======
@bot.callback_query_handler(func=lambda call: call.data and (call.data.startswith("drink_") or call.data == "drinks_done"))
def on_drink(call):
    try:
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        session = USER_SESSION.get(chat_id)
        if not session:
            bot.send_message(chat_id, "Sessiya topilmadi.")
            return
        if call.data == "drinks_done":
            kb = types.InlineKeyboardMarkup()
            for ex, price in EXTRAS.items():
                kb.add(types.InlineKeyboardButton(f"{ex} (+{price})", callback_data=f"extra_{ex}"))
            kb.add(types.InlineKeyboardButton("⏭️ Qo'shimchalarsiz davom etish", callback_data="extras_done"))
            bot.send_message(chat_id, "Qo'shimchalarni tanlang:", reply_markup=kb)
            return
        dname = call.data.split("_", 1)[1]
        if dname in session["drinks"]:
            session["drinks"].remove(dname)
            bot.send_message(chat_id, f"❌ {dname} olib tashlandi")
        else:
            session["drinks"].append(dname)
            bot.send_message(chat_id, f"✅ {dname} qo'shildi")
            img = DRINK_IMAGES.get(dname)
            if img:
                try_send_photo(chat_id, img, caption=f"{dname} tanlandi")
        kb = types.InlineKeyboardMarkup()
        for d, price in DRINKS.items():
            label = f"{d} (+{price})"
            if d in session["drinks"]:
                label = "✓ " + label
            kb.add(types.InlineKeyboardButton(label, callback_data=f"drink_{d}"))
        kb.add(types.InlineKeyboardButton("⏭️ Ichimliksiz davom etish", callback_data="drinks_done"))
        bot.send_message(chat_id, "Yana ichimlik tanlang yoki davom eting:", reply_markup=kb)
    except Exception:
        print(traceback.format_exc())

# ====== Qo'shimchalar ======
@bot.callback_query_handler(func=lambda call: call.data and (call.data.startswith("extra_") or call.data == "extras_done"))
def on_extra(call):
    try:
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        session = USER_SESSION.get(chat_id)
        if not session:
            bot.send_message(chat_id, "Sessiya topilmadi.")
            return
        if call.data == "extras_done":
            bot.send_message(chat_id, "Ismingizni kiriting:")
            bot.register_next_step_handler_by_chat_id(chat_id, ask_name)
            return
        ex = call.data.split("_", 1)[1]
        if ex in session["extras"]:
            session["extras"].remove(ex)
            bot.send_message(chat_id, f"❌ {ex} olib tashlandi")
        else:
            session["extras"].append(ex)
            bot.send_message(chat_id, f"✅ {ex} qo'shildi")
        kb = types.InlineKeyboardMarkup()
        for ex_name, price in EXTRAS.items():
            label = f"{ex_name} (+{price})"
            if ex_name in session["extras"]:
                label = "✓ " + label
            kb.add(types.InlineKeyboardButton(label, callback_data=f"extra_{ex_name}"))
        kb.add(types.InlineKeyboardButton("⏭️ Qo'shimchalarsiz davom etish", callback_data="extras_done"))
        bot.send_message(chat_id, "Yana qo'shimcha tanlang yoki davom eting:", reply_markup=kb)
    except Exception:
        print(traceback.format_exc())

# ====== Ism -> Telefon -> Manzil ======
def ask_name(message):
    try:
        chat_id = message.chat.id
        session = USER_SESSION.get(chat_id)
        if not session:
            bot.send_message(chat_id, "Sessiya topilmadi.")
            return
        session["customer_name"] = (message.text or "").strip()
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(types.KeyboardButton("📲 Kontaktni yuborish", request_contact=True))
        kb.add("Raqamni matn qilib yuboraman")
        bot.send_message(chat_id, "Telefon raqamingizni yuboring:", reply_markup=kb)
        bot.register_next_step_handler_by_chat_id(chat_id, ask_phone)
    except Exception:
        print(traceback.format_exc())

def ask_phone(message):
    try:
        chat_id = message.chat.id
        session = USER_SESSION.get(chat_id)
        if not session:
            bot.send_message(chat_id, "Sessiya topilmadi.")
            return
        if message.contact:
            phone = message.contact.phone_number
        else:
            phone = (message.text or "").strip()
            if phone == "Raqamni matn qilib yuboraman":
                bot.send_message(chat_id, "Telefon raqamingizni matn sifatida kiriting:")
                bot.register_next_step_handler_by_chat_id(chat_id, ask_phone)
                return
        if not re.match(r'^(\+998|998|0)\d{9}$', phone):
            bot.send_message(chat_id, "Telefon noto'g'ri format. Qayta yuboring:")
            bot.register_next_step_handler_by_chat_id(chat_id, ask_phone)
            return
        session["phone"] = phone
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(types.KeyboardButton("📍 Joylashuvni yuborish", request_location=True))
        kb.add("Manzilni matn ko'rinishida yozaman")
        bot.send_message(chat_id, "Manzilingizni yuboring:", reply_markup=kb)
        bot.register_next_step_handler_by_chat_id(chat_id, ask_address)
    except Exception:
        print(traceback.format_exc())

def ask_address(message):
    try:
        chat_id = message.chat.id
        session = USER_SESSION.get(chat_id)
        if not session:
            bot.send_message(chat_id, "Sessiya topilmadi.")
            return
        if message.location:
            loc = message.location
            session["address"] = f"Lat:{loc.latitude} Lon:{loc.longitude}"
        else:
            text = (message.text or "").strip()
            if text == "Manzilni matn ko'rinishida yozaman":
                bot.send_message(chat_id, "Manzilingizni toʻliq matn sifatida kiriting:")
                bot.register_next_step_handler_by_chat_id(chat_id, ask_address)
                return
            session["address"] = text
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("Naqd", callback_data="pay_cash"))
        kb.add(types.InlineKeyboardButton("Karta (online)", callback_data="pay_card"))
        bot.send_message(chat_id, "To'lov turini tanlang:", reply_markup=kb)
    except Exception:
        print(traceback.format_exc())

# ====== To'lov va Hisoblash ======
@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("pay_"))
def on_pay(call):
    try:
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        session = USER_SESSION.get(chat_id)
        if not session:
            bot.send_message(chat_id, "Sessiya topilmadi.")
            return
        pay_type = call.data.split("_")[1]
        session["payment_type"] = "Naqd" if pay_type == "cash" else "Karta"
        total = int(session["base_price"] * SIZE_MULTIPLIERS.get(session["size"], 1.0) * session.get("quantity", 1))
        for ex in session.get("extras", []):
            total += EXTRAS.get(ex, 0) * session.get("quantity", 1)
        for d in session.get("drinks", []):
            total += DRINKS.get(d, 0)
        session["total"] = total
        text = (
            f"✅ Buyurtma tayyor:\nIsm: {session.get('customer_name')}\nTel: {session.get('phone')}\n"
            f"Manzil: {session.get('address')}\n🍕 {session.get('pizza_name')} ({session.get('size')} sm) x{session.get('quantity')}\n"
            f"Qo'shimchalar: {', '.join(session.get('extras') or ['yoq'])}\n"
            f"Ichimliklar: {', '.join(session.get('drinks') or ['yoq'])}\n"
            f"To'lov: {session.get('payment_type')}\n💰 Jami: {session.get('total')} so'm\n\n"
            "Tasdiqlaysizmi?"
        )
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("✅ Tasdiqlayman", callback_data="order_confirm"))
        kb.add(types.InlineKeyboardButton("❌ Bekor qilaman", callback_data="order_cancel"))
        bot.send_message(chat_id, text, reply_markup=kb)
    except Exception:
        print(traceback.format_exc())

# ====== Buyurtma tasdiqlash / bekor ======
@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("order_"))
def on_order(call):
    try:
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        if call.data == "order_cancel":
            USER_SESSION.pop(chat_id, None)
            bot.edit_message_text("❌ Buyurtma bekor qilindi", chat_id, call.message.message_id)
            return
        session = USER_SESSION.get(chat_id)
        if not session:
            bot.send_message(chat_id, "Sessiya topilmadi.")
            return
        order = {
            "id": new_order_id(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "chat_id": chat_id,
            "customer_name": session.get("customer_name"),
            "phone": session.get("phone"),
            "address": session.get("address"),
            "pizza_id": session.get("pizza_id"),
            "pizza_name": session.get("pizza_name"),
            "size": session.get("size"),
            "quantity": session.get("quantity"),
            "extras": session.get("extras", []),
            "drinks": session.get("drinks", []),
            "payment_type": session.get("payment_type"),
            "total": session.get("total"),
            "status": "Yangi",
            "courier": None,
            "eta": None
        }
        orders = load_orders()
        orders.append(order)
        save_orders(orders)
        USER_SESSION.pop(chat_id, None)
        bot.edit_message_text("🎉 Buyurtmangiz qabul qilindi! Admin tez orada tekshiradi.", chat_id, call.message.message_id)
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📥 Qabul qilindi", callback_data=f"admin_accept_{order['id']}"))
        kb.add(types.InlineKeyboardButton("🚚 Kuryer biriktir", callback_data=f"admin_courier_{order['id']}"))
        kb.add(types.InlineKeyboardButton("✅ Yetkazildi", callback_data=f"admin_delivered_{order['id']}"))
        bot.send_message(ADMIN_ID, "📬 Yangi buyurtma:\n\n" + format_order_full(order), reply_markup=kb)
    except Exception:
        print(traceback.format_exc())

# ====== Admin callback handler ======
@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("admin_"))
def admin_cb(call):
    try:
        bot.answer_callback_query(call.id)
        parts = call.data.split("_", 2)
        action = parts[1]
        order_id = int(parts[2])
        orders = load_orders()
        order = next((o for o in orders if o.get("id") == order_id), None)
        if not order:
            bot.send_message(call.message.chat.id, "Buyurtma topilmadi.")
            return
        if action == "accept":
            order["status"] = "Qabul qilindi"
            save_orders(orders)
            bot.send_message(order["chat_id"], f"📥 Buyurtmangiz qabul qilindi (ID:{order_id})")
            bot.send_message(call.message.chat.id, f"Buyurtma {order_id} qabul qilindi.")
        elif action == "courier":
            msg = bot.send_message(call.message.chat.id, "Kuryer nomini kiriting (masalan: Ali):")
            bot.register_next_step_handler(msg, lambda m: admin_assign_courier(m, order_id))
        elif action == "delivered":
            order["status"] = "Yetkazildi"
            save_orders(orders)
            bot.send_message(order["chat_id"], f"🚚 Buyurtmangiz yetkazildi (ID:{order_id}). Rahmat!")
            bot.send_message(call.message.chat.id, f"Buyurtma {order_id} yetkazildi.")
        save_orders(orders)
    except Exception:
        print(traceback.format_exc())

def admin_assign_courier(message, order_id):
    try:
        courier = message.text.strip()
        orders = load_orders()
        order = next((o for o in orders if o.get("id") == order_id), None)
        if not order:
            bot.send_message(message.chat.id, "Buyurtma topilmadi.")
            return
        order["courier"] = courier
        order["status"] = "Kuryerga berildi"
        eta = random.randint(15, 45)
        order["eta"] = f"{eta} daqiqa"
        save_orders(orders)
        bot.send_message(order["chat_id"], f"🚚 Sizning buyurtmangiz kuryerga topshirildi. Kuryer: {courier}. ETA: {eta} daqiqa.")
        bot.send_message(message.chat.id, f"Buyurtma {order_id} kuryerga berildi ({courier}). ETA: {eta} daqiqa")
    except Exception:
        print(traceback.format_exc())

# ====== Buyurtmalarim ======
@bot.message_handler(func=lambda m: m.text == "📦 Buyurtmalarim")
def my_orders(m):
    try:
        orders = load_orders()
        user_orders = [o for o in orders if o.get("chat_id") == m.chat.id]
        if not user_orders:
            bot.send_message(m.chat.id, "Sizda buyurtma topilmadi.")
            return
        for o in sorted(user_orders, key=lambda x: x["id"], reverse=True)[:10]:
            bot.send_message(m.chat.id, format_order_short(o))
    except Exception:
        print(traceback.format_exc())

# ====== Kontakt ======
@bot.message_handler(func=lambda m: m.text == "📞 Biz bilan bog'lanish")
def contact(m):
    bot.send_message(m.chat.id, "☎️ +998 90 123 45 67\n⏰ Ish vaqti: 10:00 - 23:00")

# ====== Fallback ======
@bot.message_handler(func=lambda m: True)
def fallback(m):
    bot.send_message(m.chat.id, "Iltimos menyudan birini tanlang yoki /start")

# ====== Run bot ======
if __name__ == "__main__":
    print("HotPizzaBot ishga tushdi...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
