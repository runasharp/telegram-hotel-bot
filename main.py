import logging
import os
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
from dotenv import load_dotenv


# Do not forget to create a .env file with the Telegram Bot API token
# Alternatively, you can set the TOKEN up in your deployment environment settings, e.g. on Heroku 
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

subscribers = {}

# Function to start the bot and get the chat ID dynamically
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    context.bot_data['chat_id'] = chat_id  # Store the chat ID in bot data
    await context.bot.send_message(chat_id=chat_id, text="I'm a bot, please talk to me!\n\n" + help_text())
    # Schedule the test message job only once
    if not context.bot_data.get('job_scheduled', False):
        context.application.job_queue.run_repeating(check_price, interval=150, first=10)
        context.bot_data['job_scheduled'] = True

# Function to handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response = f'You said: {text}'
    await update.message.reply_text(response)

# Function to store /help text
def help_text():
    return (
        "/start - Start the bot and see this message\n"
        "/seturl <id> <url> - Set a tracking URL (ID should be between 1 and 10)\n"
        "/setprice <id> <price> - Set a target price for a tracking URL\n"
        "/currentprice <id> - Get the current price for a tracking URL\n"
        "/listurls - List all your tracking URLs\n"
        "/deleteurl <id> - Delete a tracking URL\n"
        "/help - Show this help message"
    )

# Function to handle the /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(help_text())

# Function to set the URL of a Booking.com search
async def set_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /seturl <id> <url>")
        return

    try:
        url_id = int(context.args[0])
        if url_id < 1 or url_id > 10:
            raise ValueError
    except ValueError:
        await update.message.reply_text("ID should be a number between 1 and 10.")
        return

    url = context.args[1]
    if chat_id not in subscribers:
        subscribers[chat_id] = {}

    subscribers[chat_id][url_id] = {'url': url, 'target_price': None, 'last_notified_price': None}
    await update.message.reply_text(f"Tracking URL {url_id} has been set to: {url}")

# Function to set the price for an ID
async def set_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /setprice <id> <price>")
        return

    try:
        url_id = int(context.args[0])
        target_price = float(context.args[1])
        if chat_id not in subscribers or url_id not in subscribers[chat_id]:
            await update.message.reply_text(f"No URL set for ID {url_id}.")
            return

        subscribers[chat_id][url_id]['target_price'] = target_price
        await update.message.reply_text(f"Your target price has been set to: {target_price} EUR for URL ID {url_id}")

        # Call check_price immediately after setting the price so that user can see that the bot works properly
        await check_price(context)
    except ValueError:
        await update.message.reply_text("Please provide a valid number for the ID and price.")

# Function to get the minimum price from the URL
def get_minimum_price(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Adjust the search criteria based on the new format
    price_elements = soup.find_all('div', {'class': 'a53cbfa6de'})
    if not price_elements:
        return None

    prices = []
    for element in price_elements:
        text = element.get_text(strip=True)
        if '€' in text and '-' in text:
            price_range = text.split('-')
            if len(price_range) == 2:
                try:
                      # Currently only works for €
                    low_price = float(price_range[0].replace('€', '').replace(',', '.').strip())
                    prices.append(low_price)
                except ValueError:
                    continue

    if not prices:
        return None

    return min(prices)

# Function to check the price and notify the user if it is below the target price
async def check_price(context: CallbackContext):
    for chat_id, urls in subscribers.items():
        for url_id, data in urls.items():
            url = data.get('url')
            target_price = data.get('target_price')
            last_notified_price = data.get('last_notified_price')
            if url and target_price is not None:
                min_price = get_minimum_price(url)
                if min_price is not None and min_price <= target_price and min_price != last_notified_price:
                    await context.bot.send_message(chat_id=chat_id,
                                                   text=f"The price has dropped to {min_price} EUR for URL ID {url_id}! Check it out at {url}")
                    subscribers[chat_id][url_id]['last_notified_price'] = min_price

# Function to get the current price
async def current_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /currentprice <id>")
        return

    try:
        url_id = int(context.args[0])
        if chat_id in subscribers and url_id in subscribers[chat_id] and subscribers[chat_id][url_id]['url']:
            url = subscribers[chat_id][url_id]['url']
            min_price = get_minimum_price(url)
            if min_price is not None:
                await update.message.reply_text(f"The current minimum price is {min_price} EUR for URL ID {url_id}.")
            else:
                await update.message.reply_text("Unable to retrieve the current minimum price. Please check your URL.")
        else:
            await update.message.reply_text(f"No URL set for ID {url_id}.")
    except ValueError:
        await update.message.reply_text("Please provide a valid number for the ID.")

# Function to list all tracking URLs
async def list_urls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in subscribers:
        message = "Your tracking URLs:\n"
        for url_id, data in subscribers[chat_id].items():
            url = data.get('url')
            target_price = data.get('target_price')
            message += f"ID {url_id}: {url} (Target Price: {target_price} EUR)\n"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("You have no tracking URLs set.")

# Function to delete a tracking URL
async def delete_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /deleteurl <id>")
        return

    try:
        url_id = int(context.args[0])
        if chat_id in subscribers and url_id in subscribers[chat_id]:
            del subscribers[chat_id][url_id]
            await update.message.reply_text(f"Deleted tracking URL ID {url_id}.")
        else:
            await update.message.reply_text(f"No URL set for ID {url_id}.")
    except ValueError:
        await update.message.reply_text("Please provide a valid number for the ID.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Add handlers for commands and messages
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('seturl', set_url))
    app.add_handler(CommandHandler('setprice', set_price))
    app.add_handler(CommandHandler('currentprice', current_price))
    app.add_handler(CommandHandler('listurls', list_urls))
    app.add_handler(CommandHandler('deleteurl', delete_url))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Start the bot
    logger.info("Starting bot...")
    app.run_polling()

if __name__ == '__main__':
    main()
