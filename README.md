
# Telegram Price Tracker Bot

## Overview

This Telegram bot was designed to keep track prices of various Booking.com search URLs, specifically for monitoring the cost of a stay in a hotel. User can perform a search on Booking.com, and use the link to interact with the bot. When the lowest price for the criteria selected by user in the link drops, user gets a message. 

## Motivation

The primary motivation for creating this bot was to track the price of stays in hotels. While researching, I found that the Booking.com API required registration, which was closed at the time. Therefore, the bot uses BeautifulSoup to scrape price data from websites.

## Features
- Set target prices for each URL
- Track up to 10 different URLs per user
- Receive notifications when the price drops below the target price.
- CRUD operations for tracking URLs.
- Simple commands to interact with the bot.

## Commands

- `/start` - Start the bot and see the welcome message along with available commands.
- `/seturl <id> <url>` - Set a tracking URL (ID should be between 1 and 10).
- `/setprice <id> <price>` - Set a target price for a tracking URL.
- `/currentprice <id>` - Get the current price for a tracking URL.
- `/listurls` - List all your tracking URLs.
- `/deleteurl <id>` - Delete a tracking URL.
- `/help` - Show the help message with all commands.

## Screenshot

![Bot Screenshot](/screenshot.PNG)

## Setting Up Your Bot on Telegram

1. **Find BotFather on Telegram**:
   - Open Telegram and search for `BotFather`.
   - Start a chat with BotFather.

2. **Create a New Bot**:
   - Use the `/newbot` command to create a new bot.
   - Follow the instructions to name your bot and create a username for it.

3. **Get Your HTTP API Token**:
   - After creating the bot, BotFather will provide an HTTP API token.
   - Copy this token and use it in your `.env` file as described in the installation steps.

## Installation

1. **Clone the repository**:
   ```sh
   git clone https://github.com/runasharp/telegram-hotel-bot.git
   cd telegram-price-tracker-bot
   ```

2. **Create a virtual environment and activate it**:
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up your environment variables**:
   Create a `.env` file in the root directory and add your Telegram bot token:
   ```
   TOKEN=your_telegram_bot_token
   ```

5. **Run the bot**:
   ```sh
   python bot.py
   ```

## Usage

1. Start a conversation with your bot on Telegram.
2. Use the `/start` command to initialize the bot and see the available commands.
3. Set URLs and target prices using the `/seturl` and `/setprice` commands.
4. Check current prices with `/currentprice` and list all tracked URLs with `/listurls`.
5. Delete URLs with the `/deleteurl` command when no longer needed.

## Dependencies

- `python-telegram-bot`
- `requests`
- `beautifulsoup4`
- `python-dotenv`

## Acknowledgements

- The `python-telegram-bot` library for seamless interaction with the Telegram Bot API.
- The `BeautifulSoup` library for making web scraping straightforward and efficient.
- Inspiration to track hotel prices from Booking.com.
