import os
from dotenv import load_dotenv
load_dotenv()

bot_token = os.getenv('bot_token')
prefix = os.getenv('prefix')
t_custom_message = os.getenv('custom_message')
if t_custom_message == 'none':
    custom_message = None
else:
    custom_message = t_custom_message