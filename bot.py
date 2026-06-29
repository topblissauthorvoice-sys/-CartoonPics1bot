import os
import logging
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable (set in Railway)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

# List of cartoon image URLs (you can add more or use an API)
CARTOON_IMAGES = [
    "https://i.imgur.com/1Xj0w3F.jpeg",  # Replace with actual cartoon images
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

# Alternative: Use a free cartoon API (uncomment to use)
# CARTOON_API_URL = "https://api.unsplash.com/photos/random?query=cartoon&count=1"
# UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY')

# Store user data (in production, use a database)
user_data = {}

# ============= COMMAND HANDLERS =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    welcome_text = (
        f"🎨 Welcome to CartoonPicsBot, {user.first_name}!\n\n"
        "I send you amazing cartoon pictures! Here's what I can do:\n\n"
        "🖼️ /random - Get a random cartoon picture\n"
        "🎭 /categories - Browse cartoon categories\n"
        "📊 /stats - See how many pictures I've sent\n"
        "ℹ️ /help - Show this message again\n\n"
        "Click the buttons below to get started!"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🎲 Random Picture", callback_data="random"),
            InlineKeyboardButton("📂 Categories", callback_data="categories"),
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data="stats"),
            InlineKeyboardButton("📞 Contact", url="https://t.me/CartoonPics1bot"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    # Track user in stats
    user_id = str(update.effective_user.id)
    if user_id not in user_data:
        user_data[user_id] = {'pics_received': 0, 'favorites': []}


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message."""
    help_text = (
        "📖 *CartoonPicsBot Help*\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/random - Get a random cartoon picture\n"
        "/categories - Browse cartoon categories\n"
        "/stats - View your usage statistics\n"
        "/help - Show this help message\n\n"
        "You can also click the buttons below the messages!"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def random_picture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a random cartoon picture."""
    user_id = str(update.effective_user.id)
    
    # Select random image
    image_url = random.choice(CARTOON_IMAGES)
    
    # Track stats
    if user_id in user_data:
        user_data[user_id]['pics_received'] += 1
    
    # Send photo with caption
    caption = (
        "🎨 *Here's your cartoon picture!*\n\n"
        f"🖼️ Picture #{user_data.get(user_id, {}).get('pics_received', 0)} today\n"
        "🔄 Use /random for another one!"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🔄 Another", callback_data="random"),
            InlineKeyboardButton("❤️ Favorite", callback_data=f"fav_{image_url}"),
        ],
        [
            InlineKeyboardButton("📂 Categories", callback_data="categories"),
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
            "❌ Sorry, couldn't load the image. Please try again!"
        )


async def categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show cartoon categories."""
    keyboard = [
        [
            InlineKeyboardButton("😄 Funny Cartoons", callback_data="cat_funny"),
            InlineKeyboardButton("🐱 Animal Cartoons", callback_data="cat_animal"),
        ],
        [
            InlineKeyboardButton("🚀 Sci-Fi Cartoons", callback_data="cat_scifi"),
            InlineKeyboardButton("🎨 Classic Cartoons", callback_data="cat_classic"),
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
    """Show user statistics."""
    user_id = str(update.effective_user.id)
    stats_text = (
        "📊 *Your CartoonPicsBot Statistics*\n\n"
        f"🖼️ Total pictures received: {user_data.get(user_id, {}).get('pics_received', 0)}\n"
        f"❤️ Favorite pictures saved: {len(user_data.get(user_id, {}).get('favorites', []))}\n"
        f"👤 User ID: {user_id[:8]}...\n\n"
        "Keep enjoying the cartoons! 🎨"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(stats_text, parse_mode='Markdown', reply_markup=reply_markup)


# ============= CALLBACK QUERY HANDLERS =============

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback
    
    data = query.data
    user_id = str(query.from_user.id)
    
    # Initialize user data if not exists
    if user_id not in user_data:
        user_data[user_id] = {'pics_received': 0, 'favorites': []}
    
    if data == "random":
        # Send random picture
        image_url = random.choice(CARTOON_IMAGES)
        user_data[user_id]['pics_received'] += 1
        
        caption = f"🎨 *Here's your cartoon picture!*\n\n🖼️ Picture #{user_data[user_id]['pics_received']}"
        keyboard = [
            [
                InlineKeyboardButton("🔄 Another", callback_data="random"),
                InlineKeyboardButton("❤️ Favorite", callback_data=f"fav_{image_url}"),
            ],
            [InlineKeyboardButton("📂 Categories", callback_data="categories")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_photo(
            photo=image_url,
            caption=caption,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif data == "categories":
        # Show categories menu
        keyboard = [
            [
                InlineKeyboardButton("😄 Funny", callback_data="cat_funny"),
                InlineKeyboardButton("🐱 Animal", callback_data="cat_animal"),
            ],
            [
                InlineKeyboardButton("🚀 Sci-Fi", callback_data="cat_scifi"),
                InlineKeyboardButton("🎨 Classic", callback_data="cat_classic"),
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📂 *Choose a cartoon category:*",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif data == "stats":
        # Show stats
        stats_text = (
            "📊 *Your Statistics*\n\n"
            f"🖼️ Pictures received: {user_data[user_id]['pics_received']}\n"
            f"❤️ Favorites: {len(user_data[user_id]['favorites'])}"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(stats_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif data == "menu":
        # Return to main menu
        keyboard = [
            [
                InlineKeyboardButton("🎲 Random Picture", callback_data="random"),
                InlineKeyboardButton("📂 Categories", callback_data="categories"),
            ],
            [
                InlineKeyboardButton("📊 Stats", callback_data="stats"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🎨 *Welcome back to CartoonPicsBot!*\n\nWhat would you like to do?",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif data.startswith("fav_"):
        # Save favorite
        image_url = data.split("fav_")[1]
        if image_url not in user_data[user_id]['favorites']:
            user_data[user_id]['favorites'].append(image_url)
            await query.edit_message_caption(
                caption="❤️ *Added to favorites!*",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_caption(
                caption="⚠️ *Already in favorites!*",
                parse_mode='Markdown'
            )
    
    elif data.startswith("cat_"):
        # Handle category selection (simplified - just send random images from category)
        category = data.replace("cat_", "").capitalize()
        image_url = random.choice(CARTOON_IMAGES)
        user_data[user_id]['pics_received'] += 1
        
        caption = f"🎨 *{category} Cartoon*\n\n🖼️ Picture #{user_data[user_id]['pics_received']}"
        keyboard = [
            [
                InlineKeyboardButton("🔄 Another", callback_data="random"),
                InlineKeyboardButton("❤️ Favorite", callback_data=f"fav_{image_url}"),
            ],
            [InlineKeyboardButton("📂 Categories", callback_data="categories")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_photo(
            photo=image_url,
            caption=caption,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )


# ============= MAIN FUNCTION =============

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("random", random_picture))
    application.add_handler(CommandHandler("categories", categories))
    application.add_handler(CommandHandler("stats", stats))
    
    # Register callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Start the bot (long polling)
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
