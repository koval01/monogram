from dotenv import load_dotenv

import logging
import os

# Find .env file with os variables
load_dotenv("dev.env")

# retrieve config variables
try:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    REDIS_URL = os.getenv("REDIS_URL")
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    BOT_OWNERS = [int(x) for x in os.getenv('BOT_OWNERS').split(",")]
    GA_ID = os.getenv("GA_ID")
    GA_SECRET = os.getenv("GA_SECRET")
    
except (TypeError, ValueError) as ex:
    logging.error(f"Error while reading config: {ex}")
