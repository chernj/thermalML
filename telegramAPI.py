__author__ = 'rcj1492'
__created__ = '2016.10'
__license__ = 'MIT'

from telegram import Bot
from credentials.credTelegram import *
telegram_bot = Bot(token=dryheatbot_access_token)
response = telegram_bot.getMe()
print(response)

if __name__ == '__main__':
    chat_id = telegram_admin_id
    msg_text = 'test'
    telegram_bot.sendMessage(chat_id=chat_id, text=msg_text)
