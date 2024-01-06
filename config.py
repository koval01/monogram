from dotenv import load_dotenv

import logging
import os

# Load environment variables from .env file
load_dotenv("dev.env")

# Retrieve configuration variables from environment variables
try:
    # Bot Token for accessing the Telegram Bot API
    BOT_TOKEN = os.getenv('BOT_TOKEN')

    # URL for connecting to the Redis server
    REDIS_URL = os.getenv("REDIS_URL")

    # Sentry DSN (Data Source Name) for error tracking
    SENTRY_DSN = os.getenv("SENTRY_DSN")

    # List of user IDs who own the bot
    BOT_OWNERS = [int(x) for x in os.getenv('BOT_OWNERS').split(",")]

    # Google Analytics ID for tracking bot analytics
    GA_ID = os.getenv("GA_ID")

    # Google Analytics Secret for authentication
    GA_SECRET = os.getenv("GA_SECRET")

except (TypeError, ValueError) as ex:
    # Log an error if there's an issue while reading configuration variables
    logging.error(f"Error while reading config: {ex}")
    