import re

from aiogram import types
from dispatcher import dp

from actions.auth import CheckToken

from handlers.ratelimit import rate_limit
