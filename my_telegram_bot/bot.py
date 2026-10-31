import telebot
from telebot import types
import openai
import json
from datetime import datetime, timedelta
import os
import threading
from flask import Flask, jsonify, Response
from dicttoxml import dicttoxml

# ----------------- TOKENLAR -----------------
BOT_TOKEN = "8536562956:AAENmDTSUswpO0_F4i3SNahm2U7bYwg0s1s"
OPENAI_API_KEY = "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"
PAYMENT_PROVIDER_TOKEN = "YOUR_TELEGRAM_PAYMENT_PROVIDER_TOKEN"

ADMIN_IDS = [7165482615]  # Admin ID yozing

bot = telebot.TeleBot(BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

# ----------------- CONSTANTS -----------------
MENU_IMAGES = [
    {"title": "GPT Haftalik", "url": "https://via.placeholder.com/800x300?text=Haftalik"},
    {"title": "GPT Oylik", "url": "https://via.placeholder.com/800x300?text=Oylik"},
    {"title": "GPT Yillik", "url": "https://via.placeholder.com/800x300?text=Yillik"}
]

FREE_QUESTIONS_LIMIT = 10
DEFAULT_PRICES = {"weekly": 100, "monthly": 500, "yearly": 5000}

USERS_FILE = "users.json"
CONFIG_FILE = "config.json"

# ----------------- FILE HELPERS -----------------
def ensure_files():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump([], f)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"prices": DEFAULT_PRICES}, f, indent=4)

def load_users():
    ensure_files()
    return json.load(open(USERS_FILE))

def save_users(users):
    json.dump(users, open(USERS_FILE, "w"), indent=4)

def load_config():
    ensure_files()
    return json.load(open(CONFIG_FILE))

def save_config(cfg):
    json.dump(cfg, open(CONFIG_FILE, "w"), indent=4)

# ----------------- USER HELPERS -----------------
def get_user(user_id, username=None):
    users = load_users()
    for i, u in enumerate(users):
        if u["id"] == user_id:
            u.setdefault("count", 0)
            u.setdefault("paid", False)
            u.setdefault("expiry", None)
            users[i] = u
            save_users(users)
            return u

    new = {"id": user_id, "username": username or "", "count": 0, "paid": False, "expiry": None}
    users.append(new)
    save_users(users)
    return new

def update_user(u):
    users = load_users()
    for i, x in enumerate(users):
        if x["id"] == u["id"]:
            users[i] = u
            save_users(users)
            return
    users.append(u)
    save_users(users)

def is_admin(uid):
    return uid in ADMIN_IDS

# ----------------- KEYBOARDS -----------------
def main_keyboard(is_admin_user=False):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("/start", "/help")
    kb.add("/menu", "/profile")
    if is_admin_user:
        kb.add("/admin")
    return kb

def payment_menu_markup(prices):
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton(f"Haftalik — ${prices['weekly']/100:.2f}", callback_data="buy_weekly"))
    m.add(types.InlineKeyboardButton(f"Oylik — ${prices['monthly']/100:.2f}", callback_data="buy_monthly"))
    m.add(types.InlineKeyboardButton(f"Yillik — ${prices['yearly']/100:.2f}", callback_data="buy_yearly"))
    return m

# ----------------- START / HELP -----------------
@bot.message_handler(commands=["start"])
def cmd_start(m):
    u = get_user(m.from_user.id, m.from_user.username)
    remaining = max(FREE_QUESTIONS_LIMIT - u["count"], 0)
    bot.send_message(
        m.chat.id,
        f"Salom {m.from_user.first_name}! 🤖\nBepul savollar: {remaining}\n/menu — tariflar",
        reply_markup=main_keyboard(is_admin(m.from_user.id))
    )

@bot.message_handler(commands=["help"])
def cmd_help(m):
    bot.send_message(
        m.chat.id,
        "Savol yozing — GPT javob beradi.\n/menu — tariflar",
        reply_markup=main_keyboard(is_admin(m.from_user.id))
    )

@bot.message_handler(commands=["profile"])
def cmd_profile(m):
    u = get_user(m.from_user.id, m.from_user.username)
    status = "Ha" if u["paid"] else "Yo'q"
    expiry = u["expiry"] or "—"
    bot.send_message(
        m.chat.id,
        f"👤 Profil:\nID: {u['id']}\nFoydalangan savollar: {u['count']}\nTo‘lov qilgan: {status}\nMuddati: {expiry}"
    )

@bot.message_handler(commands=["menu"])
def cmd_menu(m):
    cfg = load_config()
    prices = cfg["prices"]
    for item in MENU_IMAGES:
        bot.send_photo(m.chat.id, item["url"], caption=item["title"])
    bot.send_message(m.chat.id, "Tarif tanlang:", reply_markup=payment_menu_markup(prices))

# ----------------- PACKAGE CHECK -----------------
def package_active(u):
    if not u["paid"] or not u["expiry"]:
        return False
    try:
        return datetime.now() <= datetime.fromisoformat(u["expiry"])
    except:
        return False

# ----------------- GPT LOGIC -----------------
@bot.message_handler(func=lambda m: True)
def handle_message(m):

    # admin blokini tekshirish
    if m.text.startswith("/admin") and not is_admin(m.from_user.id):
        return bot.reply_to(m, "Siz admin emassiz.")

    u = get_user(m.from_user.id, m.from_user.username)

    # muddat tugagan bo‘lsa
    if u["paid"] and u["expiry"] and datetime.now() > datetime.fromisoformat(u["expiry"]):
        u["paid"] = False
        u["expiry"] = None
        update_user(u)

    # bepul limit tugagan bo‘lsa
    if u["count"] >= FREE_QUESTIONS_LIMIT and not package_active(u):
        prices = load_config()["prices"]
        return bot.send_message(m.chat.id, "❗️ Bepul 10 savol tugadi. Paket tanlang:", reply_markup=payment_menu_markup(prices))

    # GPT JAVOB
    try:
        res = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": m.text}]
        )
        answer = res.choices[0].message.content
        bot.send_message(m.chat.id, answer)

    except Exception as e:
        return bot.send_message(m.chat.id, f"GPT xato: {e}")

    # savol sonini oshirish
    u["count"] += 1
    update_user(u)

# ----------------- PAYMENT -----------------
def send_invoice_for(chat_id, label, amount_cents, payload):
    prices = [types.LabeledPrice(label, amount_cents)]
    bot.send_invoice(
        chat_id,
        title=label,
        description=label,
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="USD",
        prices=prices,
        start_parameter=payload
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def cb_buy(call):
    p = load_config()["prices"]

    if call.data == "buy_weekly":
        send_invoice_for(call.from_user.id, "Haftalik obuna", p["weekly"], "weekly")
    elif call.data == "buy_monthly":
        send_invoice_for(call.from_user.id, "Oylik obuna", p["monthly"], "monthly")
    elif call.data == "buy_yearly":
        send_invoice_for(call.from_user.id, "Yillik obuna", p["yearly"], "yearly")

    bot.answer_callback_query(call.id)

@bot.pre_checkout_query_handler(func=lambda q: True)
def pre_checkout(pre_q):
    bot.answer_pre_checkout_query(pre_q.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(msg):
    u = get_user(msg.from_user.id, msg.from_user.username)
    payload = msg.successful_payment.invoice_payload
    now = datetime.now()

    if payload == "weekly":
        u["expiry"] = (now + timedelta(days=7)).isoformat()
    elif payload == "monthly":
        u["expiry"] = (now + timedelta(days=30)).isoformat()
    else:
        u["expiry"] = (now + timedelta(days=365)).isoformat()

    u["paid"] = True
    update_user(u)

    bot.send_message(msg.chat.id, "To‘lov tasdiqlandi! Obuna yoqildi. ✅")

# ----------------- API -----------------
app = Flask(__name__)

@app.route("/prices.json")
def prices_json():
    return jsonify(load_config()["prices"])

@app.route("/prices.xml")
def prices_xml():
    xml = dicttoxml(load_config()["prices"], custom_root='prices', attr_type=False)
    return Response(xml, mimetype="application/xml")

def run_flask():
    app.run(host="127.0.0.1", port=5000)

# ----------------- START -----------------
if __name__ == "__main__":
    ensure_files()
    threading.Thread(target=run_flask, daemon=True).start()
    print("Flask API → http://127.0.0.1:5000/prices.json")
    print("Bot ishga tushdi 🚀")
    bot.infinity_polling()
