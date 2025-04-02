import telebot
from telebot import types
from dotenv import load_dotenv
import os
import logging
from datetime import datetime, timedelta
import uuid
import time
import json

# Load environment variables from .env file
load_dotenv()

# Access the Telegram bot token from the .env file
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Initialize the bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Persistent storage for subscriptions
SUBSCRIPTIONS_FILE = "subscriptions.json"

def load_subscriptions():
    try:
        with open(SUBSCRIPTIONS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_subscriptions(subscriptions):
    with open(SUBSCRIPTIONS_FILE, "w") as f:
        json.dump(subscriptions, f, indent=4)

subscriptions = load_subscriptions()

# Admin chat ID (replace with actual admin Telegram chat ID)
ADMIN_CHAT_ID = "7944149645"

# Pagination settings
PAGE_SIZE = 5  # Number of subscriptions per page

# Set up logging
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Attractive text to append to every reply (now empty)
ATTRACTIVE_TEXT = ""

# Welcome description (shown every time "Store" is clicked)
WELCOME_DESCRIPTION = (
    "WELCOME TO OUR SHOP 🏪 HERE YOU’LL BE ABLE TO SEE WHATS AVAILABLE ON OUR MENU AND SHOP FOR TOP-TIER PUBLIC RECORDS 🔥 "
    "YOUR #1 PUBLIC RECORDS SUPPLIER‼️ BEST DEALS, BEST RATES, MONTHLY SPECIALS⚡️📈 🏪 CUSTOMER SUPPORT ☎️✅"
)

# Helper function to create custom keyboard markup
def get_custom_markup(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    buttons = [
        ("🛒 Store", "📞 Customer Support"),
        ("🔙 Back to Start", "📋 How To Order Step by Step"),
        ("📜 Return & Refund Policy", "💳 Payment & Checklist")
    ]
    for row in buttons:
        markup.row(*[types.KeyboardButton(btn) for btn in row])
    if str(chat_id) == ADMIN_CHAT_ID:
        markup.row(types.KeyboardButton("🛠️ Admin"))
        markup.row(types.KeyboardButton("🔄 Change Payment Method"))
    return markup

# Helper function to display welcome message and logo (every time "Store" is clicked)
def display_welcome_and_logo(chat_id):
    bot.send_message(chat_id, WELCOME_DESCRIPTION, parse_mode='Markdown')
    try:
        with open('logo.png', 'rb') as photo:
            bot.send_photo(chat_id, photo)
        logger.info(f"Sent logo image to user {chat_id}")
    except FileNotFoundError:
        logger.error(f"Logo image not found for user {chat_id}")
        bot.send_message(chat_id, "⚠️ Logo image not available. Please contact support.")
    except Exception as e:
        logger.error(f"Error sending logo image to user {chat_id}: {str(e)}")
        bot.send_message(chat_id, "⚠️ Error sending logo image. Please contact support.")

# Handler for the /start command (no welcome text/logo here)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    logger.info(f"User {message.chat.id} started the bot")
    markup = get_custom_markup(message.chat.id)
    bot.send_sticker(message.chat.id, "CAACAgQAAxkBAAEOHOhn2cf3AAHyh1ctojFLvQ_oA0lHDuwAAioDAAK8pBoD3ybItIoPIg82BA")
    welcome_message = (
        "✨ Dear Customers\n"
        "Welcome To Our Store Bots 🛒🤖🔥🔥🔥\n\n"
        "⚜️ Select One Of The Following Options:"
    ) + ATTRACTIVE_TEXT
    bot.send_message(message.chat.id, welcome_message, parse_mode='Markdown', reply_markup=markup)

# Handler for text messages (custom keyboard buttons)
@bot.message_handler(content_types=['text'])
def handle_text(message):
    logger.info(f"User {message.chat.id} sent message: {message.text}")

    if message.text == "🛒 Store":
        display_welcome_and_logo(message.chat.id)  # Welcome text and logo shown every time
        inline_markup = types.InlineKeyboardMarkup()
        our_shop_btn = types.InlineKeyboardButton("🏬 Our Shop", callback_data="our_shop")
        back_inline_btn = types.InlineKeyboardButton("🔙 Back", callback_data="back_inline")
        inline_markup.add(our_shop_btn, back_inline_btn)
        bot.send_message(
            message.chat.id,
            "🔹 Please select the desired option" + ATTRACTIVE_TEXT,
            parse_mode='Markdown',
            reply_markup=inline_markup
        )

    elif message.text == "🔙 Back to Start":
        send_welcome(message)

    elif message.text == "📜 Return & Refund Policy":
        refund_message = (
            "*📜 Refund Policy 📜*\n"
            "────\n"
            "Thank you for your purchase! We hope you're delighted with your order. If, however, you're not fully satisfied for any reason, you can request a refund before your order is processed. Please find more details on our cancellation and refund policy below.\n\n"
            "*Cancellation Policy*\n"
            "• Cancellations must be submitted within 1 hour of your purchase.\n\n"
            "*Return Process*\n"
            "• To cancel an order, please reach out to our customer service team at Service@prbot247.com to receive the Bitcoin, XRP, SOL, or ETH address for the refund.\n\n"
            "*Refunds*\n"
            "• Once we receive your cancellation request, we will initiate your refund. Please allow up to 1 day for processing, as we may be experiencing a high volume of requests.\n"
            "• We will notify you via email or Telegram once your refund has been processed.\n\n"
            "*Questions*\n"
            "• If you have any inquiries regarding our return and refund policy, please don’t hesitate to contact us at Service@prbot247.com.\n"
        ) + ATTRACTIVE_TEXT
        
        inline_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton("🔙 Back", callback_data="back_inline")
        inline_markup.add(back_btn)
        
        bot.reply_to(message, refund_message, parse_mode='Markdown', reply_markup=inline_markup)
        logger.info(f"User {message.chat.id} viewed Refund Policy")

    elif message.text == "📞 Customer Support":
        inline_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton("🔙 Back", callback_data="back_inline")
        inline_markup.add(back_btn)
        support_message = (
            "📲 Customer Support 📲\n"
            "@prbot247\n"
            "We’re here to help you 24/7! 💪"
        ) + ATTRACTIVE_TEXT
        bot.reply_to(message, support_message, parse_mode='Markdown', reply_markup=inline_markup)

    elif message.text == "📋 How To Order Step by Step":
        inline_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton("🔙 Back", callback_data="back_inline")
        inline_markup.add(back_btn)
        how_to_order_message = (
            "🤖 Step-by-Step Guide 🤖\n"
            "────\n"
            "Ordering is a breeze! Follow these steps: 🛍🛒\n\n"
            "1️⃣ Browse Products: Visit the Store section.\n\n"
            "2️⃣ Select a Plan or Price: Choose a subscription plan or regular price that suits you.\n\n"
            "3️⃣ Checkout: Choose your payment method and complete the payment via our website. Scroll down find the PR BOT Order Form!.\n\n"
            "4️⃣ Confirmation: You’ll receive a confirmation on your Phone or Telegram.\n\n"
            "🔗 Need more help? Contact Support ( @prbot247 )"
        ) + ATTRACTIVE_TEXT
        bot.reply_to(message, how_to_order_message, parse_mode='Markdown', reply_markup=inline_markup)

    elif message.text == "💳 Payment & Checklist":
        inline_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton("🔙 Back", callback_data="back_inline")
        inline_markup.add(back_btn)
        payments_message = (
            "Payment Options: BTC, XRP, SOL, LTC, ETH\n"
            "REQUEST ADDRESS LINK  @prbot247"
        ) + ATTRACTIVE_TEXT
        bot.reply_to(message, payments_message, parse_mode='Markdown', reply_markup=inline_markup)

    elif message.text == "🛠️ Admin" and str(message.chat.id) == ADMIN_CHAT_ID:
        logger.info(f"Admin {message.chat.id} accessed Admin panel")
        show_admin_panel(message, page=1)

    elif message.text == "🔄 Change Payment Method" and str(message.chat.id) == ADMIN_CHAT_ID:
        logger.info(f"Admin {message.chat.id} accessed Change Payment Method")
        show_change_payment_keyboard(message)

    else:
        unrecognized_message = "🤔 Please use the buttons below to navigate." + ATTRACTIVE_TEXT
        bot.reply_to(message, unrecognized_message, parse_mode='Markdown')
        logger.warning(f"User {message.chat.id} sent unrecognized message: {message.text}")

# Handler for inline keyboard callback queries
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    logger.info(f"User {call.message.chat.id} triggered callback: {call.data}")

    if call.data == "our_shop":
        inline_markup = types.InlineKeyboardMarkup()
        subscribe_btn = types.InlineKeyboardButton("📦 Subscription", callback_data="subscribe")
        regular_price_btn = types.InlineKeyboardButton("💰 Regular Price", callback_data="regular_price")
        member_prices_btn = types.InlineKeyboardButton("👥 Subscription Member Prices", callback_data="member_prices")
        back_btn = types.InlineKeyboardButton("🔙 Back", callback_data="back_inline")
        inline_markup.row(subscribe_btn, regular_price_btn)
        inline_markup.row(member_prices_btn, back_btn)
        shop_message = (
            "🏬 Welcome to Our Shop!\nBrowse our premium products here. 🎉"
        ) + ATTRACTIVE_TEXT
        bot.answer_callback_query(call.id, "Opening Our Shop...")
        bot.send_message(call.message.chat.id, shop_message, parse_mode='Markdown', reply_markup=get_custom_markup(call.message.chat.id))
        bot.send_message(call.message.chat.id, "🔹 Please select the desired option" + ATTRACTIVE_TEXT, parse_mode='Markdown', reply_markup=inline_markup)

    elif call.data == "subscribe":
        inline_markup = types.InlineKeyboardMarkup()
        plan_3m_btn = types.InlineKeyboardButton("💎 $45 / 3 Months", callback_data="plan_3m")
        plan_6m_btn = types.InlineKeyboardButton("💎 $72 / 6 Months", callback_data="plan_6m")
        plan_8m_btn = types.InlineKeyboardButton("💎 $95 / 8 Months", callback_data="plan_8m")
        plan_12m_btn = types.InlineKeyboardButton("💎 $145 / 12 Months", callback_data="plan_12m")
        back_to_shop_btn = types.InlineKeyboardButton("🔙 Back to Shop", callback_data="back_to_shop")
        inline_markup.row(plan_3m_btn, plan_6m_btn)
        inline_markup.row(plan_8m_btn, plan_12m_btn)
        inline_markup.row(back_to_shop_btn)
        plan_message = "📦 Subscription Plans" + ATTRACTIVE_TEXT
        bot.answer_callback_query(call.id, "Choose a subscription plan...")
        bot.send_message(call.message.chat.id, plan_message, parse_mode='Markdown', reply_markup=get_custom_markup(call.message.chat.id))
        bot.send_message(call.message.chat.id, "🔹 Please select the desired option" + ATTRACTIVE_TEXT, parse_mode='Markdown', reply_markup=inline_markup)

    elif call.data == "regular_price":
        inline_markup = types.InlineKeyboardMarkup()
        price_250_btn = types.InlineKeyboardButton("💰 250 Sites $25", callback_data="price_250")
        price_350_btn = types.InlineKeyboardButton("💰 350 Sites $40", callback_data="price_350")
        price_550_btn = types.InlineKeyboardButton("💰 550 Sites $50", callback_data="price_550")
        price_750_btn = types.InlineKeyboardButton("💰 750 Sites $65", callback_data="price_750")
        price_850_btn = types.InlineKeyboardButton("💰 850 Sites $79", callback_data="price_850")
        price_1000_btn = types.InlineKeyboardButton("💰 1000 Sites $95", callback_data="price_1000")
        price_1225_btn = types.InlineKeyboardButton("💰 1225 Sites $120", callback_data="price_1225")
        price_1350_btn = types.InlineKeyboardButton("💰 1350 Sites $129", callback_data="price_1350")
        price_1500_btn = types.InlineKeyboardButton("💰 1500 Sites $145", callback_data="price_1500")
        price_1700_btn = types.InlineKeyboardButton("💰 1700 Sites $159", callback_data="price_1700")
        price_1850_btn = types.InlineKeyboardButton("💰 1850 Sites $179", callback_data="price_1850")
        price_2000_btn = types.InlineKeyboardButton("💰 2000 Sites $195", callback_data="price_2000")
        price_2500_btn = types.InlineKeyboardButton("💰 2500 Sites $229", callback_data="price_2500")
        price_3000_btn = types.InlineKeyboardButton("💰 3000 Sites $295", callback_data="price_3000")  # New button
        back_to_shop_btn = types.InlineKeyboardButton("🔙 Back to Shop", callback_data="back_to_shop")
        inline_markup.row(price_250_btn, price_350_btn)
        inline_markup.row(price_550_btn, price_750_btn)
        inline_markup.row(price_850_btn, price_1000_btn)
        inline_markup.row(price_1225_btn, price_1350_btn)
        inline_markup.row(price_1500_btn, price_1700_btn)
        inline_markup.row(price_1850_btn, price_2000_btn)
        inline_markup.row(price_2500_btn, price_3000_btn)  # Adjusted to include new button
        inline_markup.row(back_to_shop_btn)
        price_message = "💰 Regular Price Options" + ATTRACTIVE_TEXT
        bot.answer_callback_query(call.id, "Viewing Regular Price options...")
        bot.send_message(call.message.chat.id, price_message, parse_mode='Markdown', reply_markup=get_custom_markup(call.message.chat.id))
        bot.send_message(call.message.chat.id, "🔹 Please select the desired option" + ATTRACTIVE_TEXT, parse_mode='Markdown', reply_markup=inline_markup)

    elif call.data == "member_prices":
        inline_markup = types.InlineKeyboardMarkup()
        member_250_btn = types.InlineKeyboardButton("💰 250 Sites $15", callback_data="member_250")
        member_350_btn = types.InlineKeyboardButton("💰 350 Sites $35", callback_data="member_350")
        member_550_btn = types.InlineKeyboardButton("💰 550 Sites $45", callback_data="member_550")
        member_750_btn = types.InlineKeyboardButton("💰 750 Sites $55", callback_data="member_750")
        member_850_btn = types.InlineKeyboardButton("💰 850 Sites $65", callback_data="member_850")
        member_1000_btn = types.InlineKeyboardButton("💰 1000 Sites $75", callback_data="member_1000")
        member_1225_btn = types.InlineKeyboardButton("💰 1225 Sites $100", callback_data="member_1225")
        member_1350_btn = types.InlineKeyboardButton("💰 1350 Sites $115", callback_data="member_1350")
        member_1500_btn = types.InlineKeyboardButton("💰 1500 Sites $135", callback_data="member_1500")
        member_1700_btn = types.InlineKeyboardButton("💰 1700 Sites $145", callback_data="member_1700")
        member_1825_btn = types.InlineKeyboardButton("💰 1825 Sites $165", callback_data="member_1825")
        member_2000_btn = types.InlineKeyboardButton("💰 2000 Sites $189", callback_data="member_2000")
        member_2500_btn = types.InlineKeyboardButton("💰 2500 Sites $220", callback_data="member_2500")
        member_3000_btn = types.InlineKeyboardButton("💰 3000 Sites $279", callback_data="member_3000")
        back_to_shop_btn = types.InlineKeyboardButton("🔙 Back to Shop", callback_data="back_to_shop")
        inline_markup.row(member_250_btn, member_350_btn)
        inline_markup.row(member_550_btn, member_750_btn)
        inline_markup.row(member_850_btn, member_1000_btn)
        inline_markup.row(member_1225_btn, member_1350_btn)
        inline_markup.row(member_1500_btn, member_1700_btn)
        inline_markup.row(member_1825_btn, member_2000_btn)
        inline_markup.row(member_2500_btn, member_3000_btn)
        inline_markup.row(back_to_shop_btn)
        price_message = "👥 Subscription Member Prices" + ATTRACTIVE_TEXT
        bot.answer_callback_query(call.id, "Viewing Subscription Member Prices...")
        bot.send_message(call.message.chat.id, price_message, parse_mode='Markdown', reply_markup=get_custom_markup(call.message.chat.id))
        bot.send_message(call.message.chat.id, "🔹 Please select the desired option" + ATTRACTIVE_TEXT, parse_mode='Markdown', reply_markup=inline_markup)

    elif call.data == "back_to_shop" or call.data == "back_inline":
        if call.data == "back_inline":
            bot.answer_callback_query(call.id, "Returning to main menu...")
            send_welcome(call.message)
        else:
            inline_markup = types.InlineKeyboardMarkup()
            subscribe_btn = types.InlineKeyboardButton("📦 Subscription", callback_data="subscribe")
            regular_price_btn = types.InlineKeyboardButton("💰 Regular Price", callback_data="regular_price")
            member_prices_btn = types.InlineKeyboardButton("👥 Subscription Member Prices", callback_data="member_prices")
            back_btn = types.InlineKeyboardButton("🔙 Back", callback_data="back_inline")
            inline_markup.row(subscribe_btn, regular_price_btn)
            inline_markup.row(member_prices_btn, back_btn)
            shop_message = (
                "🏬 Welcome to Our Shop!\nBrowse our premium products here. 🎉"
            ) + ATTRACTIVE_TEXT
            bot.answer_callback_query(call.id, "Returning to Our Shop...")
            bot.send_message(call.message.chat.id, shop_message, parse_mode='Markdown', reply_markup=get_custom_markup(call.message.chat.id))
            bot.send_message(call.message.chat.id, "🔹 Please select the desired option" + ATTRACTIVE_TEXT, parse_mode='Markdown', reply_markup=inline_markup)

    elif call.data in ["plan_3m", "plan_6m", "plan_8m", "plan_12m"]:
        plan_details = {
            "plan_3m": {"name": "$45 for 3 Months", "price": "$45"},
            "plan_6m": {"name": "$72 for 6 Months", "price": "$72"},
            "plan_8m": {"name": "$95 for 8 Months", "price": "$95"},
            "plan_12m": {"name": "$145 for 12 Months", "price": "$145"}
        }
        selected_plan = plan_details[call.data]
        user_id = str(call.message.chat.id)
        subscriptions[user_id] = {
            "plan": selected_plan["name"],
            "payment": f"Payment: {selected_plan['price']} via Website",
            "status": "pending"
        }
        save_subscriptions(subscriptions)
        logger.info(f"User {user_id} selected subscription plan {selected_plan['name']} for {selected_plan['price']}. Subscriptions: {subscriptions}")
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.row(
            types.InlineKeyboardButton("🌐 Pay via Website", callback_data=f"pay_website_{user_id}")
        )
        inline_markup.row(types.InlineKeyboardButton("🔙 Back to Plans", callback_data="subscribe"))
        payment_message = (
            f"💎 Subscription Plan Selected: {selected_plan['name']}\n"
            "💳 Payment Method: Choose below to complete your payment.\n"
            "⚠️ Your request is pending admin approval after payment. You’ll be notified once processed!\n"
        ) + ATTRACTIVE_TEXT
        bot.answer_callback_query(call.id, f"Selected {selected_plan['name']}")
        bot.send_message(call.message.chat.id, payment_message, parse_mode='Markdown', reply_markup=get_custom_markup(call.message.chat.id))
        bot.send_message(call.message.chat.id, "🔹 Please select the desired option" + ATTRACTIVE_TEXT, parse_mode='Markdown', reply_markup=inline_markup)

    elif call.data in ["price_250", "price_350", "price_550", "price_750", "price_850", "price_1000", "price_1225", "price_1350", "price_1500", "price_1700", "price_1850", "price_2000", "price_2500", "price_3000"]:
        price_details = {
            "price_250": {"name": "250 Sites $25", "price": "$25"},
            "price_350": {"name": "350 Sites $40", "price": "$40"},
            "price_550": {"name": "550 Sites $50", "price": "$50"},
            "price_750": {"name": "750 Sites $65", "price": "$65"},
            "price_850": {"name": "850 Sites $79", "price": "$79"},
            "price_1000": {"name": "1000 Sites $95", "price": "$95"},
            "price_1225": {"name": "1225 Sites $120", "price": "$120"},
            "price_1350": {"name": "1350 Sites $129", "price": "$129"},
            "price_1500": {"name": "1500 Sites $145", "price": "$145"},
            "price_1700": {"name": "1700 Sites $159", "price": "$159"},
            "price_1850": {"name": "1850 Sites $179", "price": "$179"},
            "price_2000": {"name": "2000 Sites $195", "price": "$195"},
            "price_2500": {"name": "2500 Sites $229", "price": "$229"},
            "price_3000": {"name": "3000 Sites $295", "price": "$295"}  # New entry
        }
        selected_price = price_details[call.data]
        user_id = str(call.message.chat.id)
        subscriptions[user_id] = {
            "plan": selected_price["name"],
            "payment": f"Payment: {selected_price['price']} via Website",
            "status": "pending"
        }
        save_subscriptions(subscriptions)
        logger.info(f"User {user_id} selected regular price {selected_price['name']} for {selected_price['price']}. Subscriptions: {subscriptions}")
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.row(
            types.InlineKeyboardButton("🌐 Pay via Website", callback_data=f"pay_website_{user_id}")
        )
        inline_markup.row(types.InlineKeyboardButton("🔙 Back to Prices", callback_data="regular_price"))
        payment_message = (
            f"💰 Regular Price Selected: {selected_price['name']}\n"
            "💳 Payment Method: Choose below to complete your payment.\n"
            "⚠️ Your request is pending admin approval after payment. You’ll be notified once processed!\n"
        ) + ATTRACTIVE_TEXT
        bot.answer_callback_query(call.id, f"Selected {selected_price['name']}")
        bot.send_message(call.message.chat.id, payment_message, parse_mode='Markdown', reply_markup=get_custom_markup(call.message.chat.id))
        bot.send_message(call.message.chat.id, "🔹 Please select the desired option" + ATTRACTIVE_TEXT, parse_mode='Markdown', reply_markup=inline_markup)

    elif call.data in ["member_250", "member_350", "member_550", "member_750", "member_850", "member_1000", "member_1225", "member_1350", "member_1500", "member_1700", "member_1825", "member_2000", "member_2500", "member_3000"]:
        member_price_details = {
            "member_250": {"name": "250 Sites $15", "price": "$15"},
            "member_350": {"name": "350 Sites $35", "price": "$35"},
            "member_550": {"name": "550 Sites $45", "price": "$45"},
            "member_750": {"name": "750 Sites $55", "price": "$55"},
            "member_850": {"name": "850 Sites $65", "price": "$65"},
            "member_1000": {"name": "1000 Sites $75", "price": "$75"},
            "member_1225": {"name": "1225 Sites $100", "price": "$100"},
            "member_1350": {"name": "1350 Sites $115", "price": "$115"},
            "member_1500": {"name": "1500 Sites $135", "price": "$135"},
            "member_1700": {"name": "1700 Sites $145", "price": "$145"},
            "member_1825": {"name": "1825 Sites $165", "price": "$165"},
            "member_2000": {"name": "2000 Sites $189", "price": "$189"},
            "member_2500": {"name": "2500 Sites $220", "price": "$220"},
            "member_3000": {"name": "3000 Sites $279", "price": "$279"}
        }
        selected_price = member_price_details[call.data]
        user_id = str(call.message.chat.id)
        subscriptions[user_id] = {
            "plan": selected_price["name"],
            "payment": f"Payment: {selected_price['price']} via Website",
            "status": "pending"
        }
        save_subscriptions(subscriptions)
        logger.info(f"User {user_id} selected member price {selected_price['name']} for {selected_price['price']}. Subscriptions: {subscriptions}")
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.row(
            types.InlineKeyboardButton("🌐 Pay via Website", callback_data=f"pay_website_{user_id}")
        )
        inline_markup.row(types.InlineKeyboardButton("🔙 Back to Member Prices", callback_data="member_prices"))
        payment_message = (
            f"👥 Subscription Member Price Selected: {selected_price['name']}\n"
            "💳 Payment Method: Choose below to complete your payment.\n"
            "⚠️ Your request is pending admin approval after payment. You’ll be notified once processed!\n"
        ) + ATTRACTIVE_TEXT
        bot.answer_callback_query(call.id, f"Selected {selected_price['name']}")
        bot.send_message(call.message.chat.id, payment_message, parse_mode='Markdown', reply_markup=get_custom_markup(call.message.chat.id))
        bot.send_message(call.message.chat.id, "🔹 Please select the desired option" + ATTRACTIVE_TEXT, parse_mode='Markdown', reply_markup=inline_markup)

    elif call.data.startswith("pay_website_"):
        user_id = call.data.split("_")[2]
        logger.info(f"Payment attempt for user_id: {user_id}. Current subscriptions: {subscriptions}")
        if user_id in subscriptions:
            timestamp = datetime.now()
            transaction_id = str(uuid.uuid4())
            subscriptions[user_id]["timestamp"] = str(timestamp)
            subscriptions[user_id]["transaction_id"] = transaction_id
            subscriptions[user_id]["payment"] = f"Payment: {subscriptions[user_id]['payment'].split(' via')[0]} via Website"
            save_subscriptions(subscriptions)
            logger.info(f"User {user_id} initiated Website payment for {subscriptions[user_id]['plan']} at {timestamp} with Transaction ID: {transaction_id}")
            admin_message = (
                f"🔔 New Website Payment Request\n"
                f"────\n"
                f"User ID: {user_id}\n"
                f"Transaction ID: {transaction_id}\n"
                f"Plan: {subscriptions[user_id]['plan']}\n"
                f"Payment: {subscriptions[user_id]['payment']}\n"
                f"Status: {subscriptions[user_id]['status']}\n"
                f"Timestamp: {timestamp}\n"
                "\n👉 Take action below:" + ATTRACTIVE_TEXT
            )
            admin_markup = types.InlineKeyboardMarkup()
            admin_markup.row(
                types.InlineKeyboardButton("✅ Approve", callback_data=f"activate_{user_id}"),
                types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
            )
            try:
                bot.send_message(ADMIN_CHAT_ID, admin_message, parse_mode='Markdown', reply_markup=admin_markup)
                logger.info(f"Admin {ADMIN_CHAT_ID} notified of Website payment request from user {user_id} with Transaction ID: {transaction_id}")
            except Exception as e:
                logger.error(f"Failed to notify admin {ADMIN_CHAT_ID} for user {user_id}: {str(e)}")
            payment_link = "https://prbot247.com/subscribe-now/#link" if "Months" in subscriptions[user_id]["plan"] else "https://prbot247.com/subscription-members/"
            payment_message = (
                f"🌐 Website Payment\n"
                f"────\n"
                f"Transaction ID: {transaction_id}\n"
                f"Plan: {subscriptions[user_id]['plan']}\n"
                "👉 Click the link below to complete your payment on our website.\n"
                f"[Pay Now]({payment_link})\n"
                "⚠️ After payment, your request is pending admin approval."
            ) + ATTRACTIVE_TEXT
            bot.send_message(call.message.chat.id, payment_message, parse_mode='Markdown', disable_web_page_preview=True)
        else:
            error_message = (
                "⚠️ Selection not found.\n"
                "It seems you haven’t selected a plan or price yet. Please choose an option first.\n"
                "👉 Go back and select from the 'Our Shop' menu."
            ) + ATTRACTIVE_TEXT
            bot.send_message(call.message.chat.id, error_message, parse_mode='Markdown')
            logger.warning(f"Subscription not found for user_id: {user_id}. Current subscriptions: {subscriptions}")

    elif call.data.startswith("activate_") or call.data.startswith("reject_") or call.data == "download_data":
        user_id = call.data.split("_")[1] if "_" in call.data else None
        if user_id and str(call.message.chat.id) == ADMIN_CHAT_ID:
            if call.data.startswith("activate_"):
                subscriptions[user_id]["status"] = "activated"
                save_subscriptions(subscriptions)
                user_message = (
                    f"🎉 Purchase Activated! 🎉\n"
                    f"────\n"
                    f"Transaction ID: {subscriptions[user_id]['transaction_id']}\n"
                    f"Your {subscriptions[user_id]['plan']} has been activated successfully! 💎\n"
                    f"Payment: {subscriptions[user_id]['payment']}\n"
                    "👉 Enjoy your premium features now! 🚀\n"
                ) + ATTRACTIVE_TEXT
                bot.send_message(int(user_id), user_message, parse_mode='Markdown')
                bot.answer_callback_query(call.id, f"Activated purchase for User ID {user_id}")
                logger.info(f"Admin {call.message.chat.id} activated purchase for user {user_id} with Transaction ID: {subscriptions[user_id]['transaction_id']}")
                show_admin_panel(call.message, page=1)
            elif call.data.startswith("reject_"):
                reason = "Reason not provided"
                subscriptions[user_id]["status"] = "rejected"
                save_subscriptions(subscriptions)
                user_message = (
                    f"❌ Purchase Rejected ❌\n"
                    f"────\n"
                    f"Transaction ID: {subscriptions[user_id]['transaction_id']}\n"
                    f"Your {subscriptions[user_id]['plan']} request has been rejected. 😔\n"
                    f"Reason: {reason}\n"
                    f"Payment: {subscriptions[user_id]['payment']}\n"
                    "👉 Contact support for assistance: [Support](https://prbot247.com/support)\n"
                ) + ATTRACTIVE_TEXT
                bot.send_message(int(user_id), user_message, parse_mode='Markdown')
                bot.answer_callback_query(call.id, f"Rejected purchase for User ID {user_id}")
                logger.info(f"Admin {call.message.chat.id} rejected purchase for user {user_id} with Transaction ID: {subscriptions[user_id]['transaction_id']}")
                show_admin_panel(call.message, page=1)
            elif call.data == "download_data":
                try:
                    user_data = "User Data with Payment Details:\n\n"
                    for uid, data in subscriptions.items():
                        user_data += f"User ID: {uid}\n"
                        user_data += f"Transaction ID: {data.get('transaction_id', 'N/A')}\n"
                        user_data += f"Plan: {data.get('plan', 'N/A')}\n"
                        user_data += f"Payment: {data.get('payment', 'N/A')}\n"
                        user_data += f"Status: {data.get('status', 'N/A')}\n"
                        user_data += f"Timestamp: {data.get('timestamp', 'N/A')}\n"
                        user_data += "────\n"
                    with open("user_data.txt", "w", encoding='utf-8') as f:
                        f.write(user_data)
                    with open("user_data.txt", "rb") as f:
                        bot.send_document(ADMIN_CHAT_ID, f)
                    bot.answer_callback_query(call.id, "User data downloaded as 'user_data.txt'")
                    logger.info(f"Admin {call.message.chat.id} downloaded user data")
                    os.remove("user_data.txt")
                except Exception as e:
                    logger.error(f"Failed to download user data for admin {call.message.chat.id}: {str(e)}")
                    bot.answer_callback_query(call.id, "Failed to download user data. Check logs for details.")
                    raise e

    elif call.data.startswith("change_payment_"):
        user_id = call.data.split("_")[2]
        if user_id in subscriptions and str(call.message.chat.id) == ADMIN_CHAT_ID:
            inline_markup = types.InlineKeyboardMarkup()
            inline_markup.row(
                types.InlineKeyboardButton("🌐 Website", callback_data=f"set_payment_website_{user_id}")
            )
            inline_markup.row(types.InlineKeyboardButton("🔙 Back", callback_data=f"back_to_admin_{user_id}"))
            bot.answer_callback_query(call.id, "Select new payment method...")
            bot.send_message(call.message.chat.id, f"🔄 Change Payment Method for User ID {user_id}\nSelect a new payment method:", parse_mode='Markdown', reply_markup=inline_markup)

    elif call.data.startswith("set_payment_"):
        user_id = call.data.split("_")[2]
        if user_id in subscriptions and str(call.message.chat.id) == ADMIN_CHAT_ID:
            method_mapping = {
                "website": "Website"
            }
            new_method_key = call.data.split("_")[2]
            new_method = method_mapping.get(new_method_key)
            if new_method:
                old_payment = subscriptions[user_id]["payment"]
                subscriptions[user_id]["payment"] = f"Payment: {old_payment.split(' via')[0]} via {new_method}"
                save_subscriptions(subscriptions)
                user_message = (
                    f"ℹ️ Payment Method Updated\n"
                    f"────\n"
                    f"User ID: {user_id}\n"
                    f"Old Payment: {old_payment}\n"
                    f"New Payment: {subscriptions[user_id]['payment']}\n"
                    "👉 Your payment method has been updated by the admin."
                ) + ATTRACTIVE_TEXT
                bot.send_message(int(user_id), user_message, parse_mode='Markdown')
                bot.answer_callback_query(call.id, f"Payment method changed to {new_method} for User ID {user_id}")
                logger.info(f"Admin {call.message.chat.id} changed payment method to {new_method} for user {user_id}")
                show_admin_panel(call.message, page=1)

    elif call.data.startswith("back_to_admin_"):
        user_id = call.data.split("_")[2]
        if str(call.message.chat.id) == ADMIN_CHAT_ID:
            bot.answer_callback_query(call.id, "Returning to Admin Panel...")
            show_admin_panel(call.message, page=1)

    elif call.data.startswith("page_"):
        page = int(call.data.split("_")[1])
        bot.answer_callback_query(call.id, f"Viewing page {page}...")
        logger.info(f"Admin {call.message.chat.id} viewed admin panel page {page}")
        show_admin_panel(call.message, page=page)

# Admin panel to manage subscriptions with pagination
def show_admin_panel(message, page=1):
    if str(message.chat.id) == ADMIN_CHAT_ID:
        pending_subscriptions = {uid: data for uid, data in subscriptions.items() if data.get("status") == "pending"}
        if not pending_subscriptions:
            no_pending_message = (
                "📋 No Pending Purchases 📋\n────\nNo requests are pending at the moment."
            ) + ATTRACTIVE_TEXT
            bot.reply_to(message, no_pending_message, parse_mode='Markdown')
            logger.info(f"Admin {message.chat.id} viewed admin panel: No pending subscriptions")
            return

        total_items = len(pending_subscriptions)
        total_pages = (total_items + PAGE_SIZE - 1) // PAGE_SIZE
        page = max(1, min(page, total_pages))
        start_idx = (page - 1) * PAGE_SIZE
        end_idx = min(start_idx + PAGE_SIZE, total_items)
        items_on_page = list(pending_subscriptions.items())[start_idx:end_idx]

        admin_message = (
            f"🛠️ Admin Panel: Manage Purchases 🛠️\n"
            f"────\n"
            f"📋 Pending Purchases (Page {page}/{total_pages})\n"
            f"Total Requests: {total_items}\n\n"
        )
        for user_id, data in items_on_page:
            admin_message += f"🔹 User ID: {user_id}\n"
            admin_message += f"  Transaction ID: {data.get('transaction_id', 'N/A')}\n"
            admin_message += f"  Plan: {data.get('plan', 'N/A')}\n"
            admin_message += f"  Payment: {data.get('payment', 'N/A')}\n"
            admin_message += f"  Timestamp: {data.get('timestamp', 'N/A')}\n"
            admin_message += "  👉 Actions:\n"

        admin_message += "\n🔔 Additional Admin Features:\n"
        admin_message += "  - Change Payment Method\n"
        admin_message += "  - Download User Data\n"
        admin_message += ATTRACTIVE_TEXT

        inline_markup = types.InlineKeyboardMarkup()
        for user_id, _ in items_on_page:
            inline_markup.row(
                types.InlineKeyboardButton("✅ Approve", callback_data=f"activate_{user_id}"),
                types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
            )
            inline_markup.row(
                types.InlineKeyboardButton("🔄 Change Payment", callback_data=f"change_payment_{user_id}")
            )

        pagination_row = []
        if page > 1:
            pagination_row.append(types.InlineKeyboardButton("⬅️ Previous", callback_data=f"page_{page-1}"))
        if page < total_pages:
            pagination_row.append(types.InlineKeyboardButton("➡️ Next", callback_data=f"page_{page+1}"))
        if pagination_row:
            inline_markup.row(*pagination_row)

        inline_markup.row(
            types.InlineKeyboardButton("📥 Download User Data", callback_data="download_data")
        )

        admin_options_message = "🔹 Admin Options:" + ATTRACTIVE_TEXT

        if hasattr(message, 'message_id'):
            try:
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    text=admin_message,
                    parse_mode='Markdown',
                    reply_markup=inline_markup
                )
                logger.info(f"Admin panel message edited for {message.chat.id}, message_id: {message.message_id}")
            except Exception as e:
                logger.error(f"Failed to edit admin panel message for {message.chat.id}, message_id: {message.message_id}: {str(e)}")
                try:
                    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                    logger.info(f"Deleted old admin panel message for {message.chat.id}, message_id: {message.message_id}")
                except Exception as delete_error:
                    logger.warning(f"Failed to delete old admin panel message for {message.chat.id}, message_id: {message.message_id}: {str(delete_error)}")
                new_message = bot.send_message(message.chat.id, admin_message, parse_mode='Markdown', reply_markup=inline_markup)
                logger.info(f"Sent new admin panel message for {message.chat.id}, new message_id: {new_message.message_id}")
        else:
            new_message = bot.reply_to(message, admin_message, parse_mode='Markdown', reply_markup=inline_markup)
            logger.info(f"Sent initial admin panel message for {message.chat.id}, message_id: {new_message.message_id}")

        bot.send_message(message.chat.id, admin_options_message, parse_mode='Markdown', reply_markup=get_custom_markup(message.chat.id))

# Function to show change payment method keyboard
def show_change_payment_keyboard(message):
    if str(message.chat.id) == ADMIN_CHAT_ID:
        pending_subscriptions = {uid: data for uid, data in subscriptions.items() if data.get("status") == "pending"}
        if not pending_subscriptions:
            no_pending_message = (
                "📋 No Pending Purchases 📋\n────\nNo requests are pending to change payment method."
            ) + ATTRACTIVE_TEXT
            bot.reply_to(message, no_pending_message, parse_mode='Markdown')
            logger.info(f"Admin {message.chat.id} viewed change payment: No pending subscriptions")
            return

        custom_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        custom_markup.row(types.KeyboardButton("🔙 Back to Admin"))
        for user_id in pending_subscriptions.keys():
            custom_markup.row(types.KeyboardButton(f"User {user_id}"))
        custom_markup.row(types.KeyboardButton("🌐 Website"))
        change_payment_message = (
            "🔄 Change Payment Method\n"
            "────\n"
            "Select a user ID and then a payment method to update:\n"
            "1. Choose a User ID from the list.\n"
            "2. Select a new payment method.\n"
        ) + ATTRACTIVE_TEXT
        bot.reply_to(message, change_payment_message, parse_mode='Markdown', reply_markup=custom_markup)
        logger.info(f"Admin {message.chat.id} accessed change payment method keyboard")

# Handler for changing payment method via custom keyboard
@bot.message_handler(content_types=['text'])
def handle_change_payment(message):
    if str(message.chat.id) == ADMIN_CHAT_ID:
        if message.text == "🔄 Change Payment Method":
            show_change_payment_keyboard(message)
        elif message.text == "🔙 Back to Admin":
            show_admin_panel(message, page=1)
        else:
            pending_subscriptions = {uid: data for uid, data in subscriptions.items() if data.get("status") == "pending"}
            user_id_match = None
            for uid in pending_subscriptions.keys():
                if message.text == f"User {uid}":
                    user_id_match = uid
                    break

            if user_id_match and user_id_match in subscriptions:
                bot.send_message(message.chat.id, f"ℹ️ Selected User ID: {user_id_match}\nNow select a payment method.", parse_mode='Markdown')
                bot.register_next_step_handler(message, process_payment_method, user_id_match)
            elif message.text == "🌐 Website":
                pass
            else:
                unrecognized_message = "🤔 Please select a valid user ID or payment method." + ATTRACTIVE_TEXT
                bot.reply_to(message, unrecognized_message, parse_mode='Markdown')
                logger.warning(f"Admin {message.chat.id} sent unrecognized change payment input: {message.text}")

# Process the payment method selection
def process_payment_method(message, user_id):
    if str(message.chat.id) == ADMIN_CHAT_ID:
        method_mapping = {
            "🌐 Website": "Website"
        }
        new_method = method_mapping.get(message.text)
        if new_method and user_id in subscriptions:
            old_payment = subscriptions[user_id]["payment"]
            subscriptions[user_id]["payment"] = f"Payment: {old_payment.split(' via')[0]} via {new_method}"
            save_subscriptions(subscriptions)
            user_message = (
                f"ℹ️ Payment Method Updated\n"
                f"────\n"
                f"User ID: {user_id}\n"
                f"Old Payment: {old_payment}\n"
                f"New Payment: {subscriptions[user_id]['payment']}\n"
                "👉 Your payment method has been updated by the admin."
            ) + ATTRACTIVE_TEXT
            bot.send_message(int(user_id), user_message, parse_mode='Markdown')
            bot.reply_to(message, f"✅ Payment method changed to {new_method} for User ID {user_id}", parse_mode='Markdown')
            logger.info(f"Admin {message.chat.id} changed payment method to {new_method} for user {user_id}")
            show_admin_panel(message, page=1)
        else:
            unrecognized_message = "🤔 Please select a valid payment method." + ATTRACTIVE_TEXT
            bot.reply_to(message, unrecognized_message, parse_mode='Markdown')
            logger.warning(f"Admin {message.chat.id} selected invalid payment method: {message.text} for User ID {user_id}")

# Start the bot with retry logic
while True:
    try:
        logger.info("Bot started")
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")
        time.sleep(5)
