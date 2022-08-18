import os
from dotenv import load_dotenv
load_dotenv()

bot_token = os.getenv('bot_token')
prefix = os.getenv('prefix')