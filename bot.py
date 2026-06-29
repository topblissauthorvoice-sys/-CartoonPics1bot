import os
import logging
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ============= LOGGING SETUP =============
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============= ENVIRONMENT VARIABLES =============
BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_USERNAME = os.environ.get('BOT_USERNAME', 'CartoonPics1bot')
BOT_NAME = os.environ.get('BOT_NAME', 'CartoonPics1Bot')

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN environment variable is not set!")
    raise ValueError("BOT_TOKEN is required. Add it to Railway variables.")

logger.info(f"✅ Starting {BOT_NAME} (@{BOT_USERNAME})")

# ============= CARTOON IMAGES =============
CARTOON_IMAGES = [
    "https://i.imgur.com/1Xj0w3F.jpeg",
    "https://i.imgur.com/2Yk1w4G.jpeg",
    "https://i.imgur.com/3Zl2w5H.jpeg",
    "https://i.imgur.com/4Am3w6I.jpeg",
    "https://i.imgur.com/5Bn4w7J.jpeg",
    "https://i.imgur.com/6Co5w8K.jpeg",
    "https://i.imgur.com/7Dp6w9L.jpeg",
    "https://i.imgur.com/8Eq7w0M.jpeg",
    "https://i.imgur.com/9Fr8w1N.jpeg",
    "https://i.imgur.com/0Gs9w2O.jpeg",
]

UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY')

def fetch_cartoon_images_from_unsplash():
    """Fetch cartoon images from Unsplash API if key is provided."""
    if not UNSPLASH_ACCESS_KEY:
        return CARTOON_IMAGES
    
    try:
        url = "https://api.unsplash.com/photos/random"
        params = {
            "query": "cartoon character",
            "count": 10,
            "orientation": "squarish"
        }
        headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        images = [img['urls']['regular'] for img in response.json()]
        logger.info(f"✅ Fetched {len(images)} images from Unsplash")
        return images
    except Exception as e:
        logger.warning(f"⚠️ Failed to fetch from Unsplash: {e}")
        return CARTOON_IMAGES

CARTOON_IMAGES = fetch_cartoon_images_from_unsplash()

# ============= USER DATA =============
user_data = {}

# ============= COMMAND HANDLERS =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    first_name = user.first_name or "User"
    
    welcome_text = (
        f"🎨 *Welcome to {BOT_NAME}, {first_name}!*\n\n"
        f"I'm @{BOT_USERNAME}, your cartoon picture bot!\n\n"
        "🖼️ *What I can do:*\n"
        "• Send random cartoon pictures\n"
        "• Browse by categories\n"
        "• Save your favorites\n"
        "• Track your usage stats\n\n"
        "👇 *Click a button below to get started!*"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🎲 Random Picture", callback_data="random"),
            InlineKeyboardButton("📂 Categories", callback_data="categories"),
        ],
        [
            InlineKeyboardButton("❤️ Favorites", callback_data="favorites"),
            InlineKeyboardButton("📊 My Stats", callback_data="stats"),
        ],
        [
            InlineKeyboardButton("ℹ️ Help", callback_data="help"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    
    user_id = str(update.effective_user.id)
    if user_id not in user_data:
        user_data[user_id] = {
            'pics_received': 0,
            'favorites': []
        }


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "📖 *Help & Commands*\n\n"
        "🤖 *Commands:*\n"
        "/start - Start the bot\n"
        "/random - Get random cartoon\n"
        "/categories - Browse categories\n"
        "/stats - View your statistics\n"
        "/favorites - See saved favorites\n"
        "/help - Show this help\n\n"
        "🎯 *Tips:*\n"
        "• Click the buttons below messages\n"
        "• Save your favorite pictures\n"
        "• Check your stats anytime"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def random_picture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /random command."""
    user_id = str(update.effective_user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {'pics_received': 0, 'favorites': []}
    
    image_url = random.choice(CARTOON_IMAGES)
    user_data[user_id]['pics_received'] += 1
    
    caption = (
        f"🎨 *Here's your cartoon!*\n\n"
        f"🖼️ Picture #{user_data[user_id]['pics_received']}\n"
        "⭐ Click buttons below for more!"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🔄 Another", callback_data="random"),
            InlineKeyboardButton("❤️ Save", callback_data=f"save_{image_url}"),
        ],
        [
            InlineKeyboardButton("📂 Categories", callback_data="categories"),
            InlineKeyboardButton("🔙 Menu", callback_data="menu"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await update.message.reply_photo(
            photo=image_url,
            caption=caption,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error sending photo: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't load the image. Please try again!"
        )


async def categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /categories command."""
    keyboard = [
        [
            InlineKeyboardButton("😄 Funny", callback_data="cat_funny"),
            InlineKeyboardButton("🐱 Animal", callback_data="cat_animal"),
        ],
        [
            InlineKeyboardButton("🚀 Sci-Fi", callback_data="cat_scifi"),
            InlineKeyboardButton("🎨 Classic", callback_data="cat_classic"),
        ],
        [
            InlineKeyboardButton("🏰 Fantasy", callback_data="cat_fantasy"),
            InlineKeyboardButton("🤖 Robot", callback_data="cat_robot"),
        ],
        [
            InlineKeyboardButton("🔙 Back to Menu", callback_data="menu"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📂 *Choose a cartoon category:*\n\n"
        "Select a category to see pictures from that style!",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command."""
    user_id = str(update.effective_user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {'pics_received': 0, 'favorites': []}
    
    stats_text = (
        "📊 *Your Statistics*\n\n"
        f"🖼️ Total pictures received: *{user_data[user_id]['pics_received']}*\n"
        f"❤️ Saved favorites: *{len(user_data[user_id]['favorites'])}*\n"
        f"👤 User ID: `{user_id[:8]}...`\n\n"
        "Keep enjoying the cartoons! 🎨"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        stats_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /favorites command."""
    user_id = str(update.effective_user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {'pics_received': 0, 'favorites': []}
    
    favorites_list = user_data[user_id]['favorites']
    
    if not favorites_list:
        await update.message.reply_text(
            "💔 *You haven't saved any favorites yet!*\n\n"
            "Click the ❤️ button on any picture to save it.",
            parse_mode='Markdown'
        )
        return
    
    text = (
        f"❤️ *Your Favorites*\n\n"
        f"You have *{len(favorites_list)}* saved pictures.\n\n"
        "Click 🔙 to go back."
    )
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


# ============= CALLBACK QUERY HANDLERS =============

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = str(query.from_user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {'pics_received': 0, 'favorites': []}
    
    # Random Button
    if data == "random":
        image_url = random.choice(CARTOON_IMAGES)
        user_data[user_id]['pics_received'] += 1
        
        caption = f"🎨 *Here's your cartoon!*\n\n🖼️ Picture #{user_data[user_id]['pics_received']}"
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Another", callback_data="random"),
                InlineKeyboardButton("❤️ Save", callback_data=f"save_{image_url}"),
            ],
            [
                InlineKeyboardButton("📂 Categories", callback_data="categories"),
                InlineKeyboardButton("🔙 Menu", callback_data="menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_photo(
            photo=image_url,
            caption=caption,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # Categories Button
    elif data == "categories":
        keyboard = [
            [
                InlineKeyboardButton("😄 Funny", callback_data="cat_funny"),
                InlineKeyboardButton("🐱 Animal", callback_data="cat_animal"),
            ],
            [
                InlineKeyboardButton("🚀 Sci-Fi", callback_data="cat_scifi"),
                InlineKeyboardButton("🎨 Classic", callback_data="cat_classic"),
            ],
            [
                InlineKeyboardButton("🏰 Fantasy", callback_data="cat_fantasy"),
                InlineKeyboardButton("🤖 Robot", callback_data="cat_robot"),
            ],
            [
                InlineKeyboardButton("🔙 Back to Menu", callback_data="menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📂 *Choose a cartoon category:*\n\nSelect a category!",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # Category Selection
    elif data.startswith("cat_"):
        category = data.replace("cat_", "").capitalize()
        image_url = random.choice(CARTOON_IMAGES)
        user_data[user_id]['pics_received'] += 1
        
        caption = f"🎨 *{category} Cartoon*\n\n🖼️ Picture #{user_data[user_id]['pics_received']}"
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Another", callback_data="random"),
                InlineKeyboardButton("❤️ Save", callback_data=f"save_{image_url}"),
            ],
            [
                InlineKeyboardButton("📂 Categories", callback_data="categories"),
                InlineKeyboardButton("🔙 Menu", callback_data="menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_photo(
            photo=image_url,
            caption=caption,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # Save Favorite
    elif data.startswith("save_"):
        image_url = data.replace("save_", "")
        
        if image_url not in user_data[user_id]['favorites']:
            user_data[user_id]['favorites'].append(image_url)
            await query.edit_message_caption(
                caption=f"❤️ *Added to favorites!*\n\nYou now have *{len(user_data[user_id]['favorites'])}* favorites.",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_caption(
                caption="⚠️ *Already in favorites!*",
                parse_mode='Markdown'
            )
    
    # Favorites List
    elif data == "favorites":
        favorites_list = user_data[user_id]['favorites']
        
        if not favorites_list:
            text = "💔 *You haven't saved any favorites yet!*"
        else:
            text = f"❤️ *Your Favorites*\n\nYou have *{len(favorites_list)}* saved pictures."
        
        keyboard = [[InlineKeyboardButton("🔙 Menu", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # Stats
    elif data == "stats":
        stats_text = (
            "📊 *Your Statistics*\n\n"
            f"🖼️ Pictures received: *{user_data[user_id]['pics_received']}*\n"
            f"❤️ Favorites saved: *{len(user_data[user_id]['favorites'])}*"
        )
        keyboard = [[InlineKeyboardButton("🔙 Menu", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            stats_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # Help
    elif data == "help":
        help_text = (
            "📖 *Help & Commands*\n\n"
            "🤖 *Commands:*\n"
            "/start - Start the bot\n"
            "/random - Get random cartoon\n"
            "/categories - Browse categories\n"
            "/stats - View your statistics\n"
            "/favorites - See saved favorites\n"
            "/help - Show this help\n\n"
            "🎯 *Tips:*\n"
            "• Click the buttons below messages\n"
            "• Save your favorite pictures"
        )
        keyboard = [[InlineKeyboardButton("🔙 Menu", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # Menu
    elif data == "menu":
        keyboard = [
            [
                InlineKeyboardButton("🎲 Random Picture", callback_data="random"),
                InlineKeyboardButton("📂 Categories", callback_data="categories"),
            ],
            [
                InlineKeyboardButton("❤️ Favorites", callback_data="favorites"),
                InlineKeyboardButton("📊 My Stats", callback_data="stats"),
            ],
            [
                InlineKeyboardButton("ℹ️ Help", callback_data="help"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🎨 *Welcome back to CartoonPicsBot!*\n\nWhat would you like to do?",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )


# ============= MAIN FUNCTION =============

def main():
    """Start the bot."""
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("random", random_picture))
        application.add_handler(CommandHandler("categories", categories))
        application.add_handler(CommandHandler("stats", stats))
        application.add_handler(CommandHandler("favorites", favorites))
        
        application.add_handler(CallbackQueryHandler(button_handler))
        
        logger.info("🚀 Bot started successfully!")
        logger.info(f"📱 Bot username: @{BOT_USERNAME}")
        logger.info(f"👥 Running with {len(CARTOON_IMAGES)} cartoon images")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise


if __name__ == '__main__':
    main()
