import os
import logging
import telegram.bot
from telegram.ext import Updater, RegexHandler
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

from telegram import ReplyKeyboardMarkup
from telegram import KeyboardButton

import redis

#from bot_class import red

from bot_class import *

from bot_settings import settings

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '1149862512:AAFHaUq_sy_ucvENdke7lOOh9CxVWVnm9Qs'
REQUEST_KWARGS={
    # "USERNAME:PASSWORD@" is optional, if you need authentication:
    'proxy_url': 'http://KEy2hn:YJzsyg@186.65.115.105:9425/',
    'connect_timeout' : 60,
    'read_timeout' : 60
}

# ReplyKeyboardMarkup

def start(update, context):

    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!", reply_markup=get_keyboard())
    #context.bot.message.reply_text('Здравствуйте, {}! \nПоговорите со мной {}!'
    #                       .format(bot.message.chat.first_name, smile), reply_markup=get_keyboard())  # отправляем ответ


def echo(update, context):
    if update.message.text == 'Включить ленту данных':
        print('Уведомления включены ', update)
        thread.bot_updater(update, context)
        settings.FRESH_DATA = True
        #context.bot.send_message(chat_id=update.effective_chat.id, text="Уведомления включены")
    if update.message.text == 'Выключить ленту данных':
        print('Уведомления выключены ', update)
        #thread.bot_updater(update, context)
        settings.FRESH_DATA = False
        # context.bot.send_message(chat_id=update.effective_chat.id, text="Уведомления включены")


def last_data(update, context):
    text = 'Последние данные'
    print(text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


SMILE = ['😊', '😀', '😇', '🤠', '😎', '🤓', '👶', '🧑‍🚀', '👮', '🦸', '🧟']
CALLBACK_BUTTON_DATA = "Включить ленту данных"
CALLBACK_BUTTON_DATA_EXIT = "Выключить ленту данных"
CALLBACK_BUTTON_EXIT_BIRGA = "Выйти из позиции Биржа"
CALLBACK_BUTTON_EXIT_MARGA = "Выйти из позиции Маржа"



# функция создает клавиатуру и ее разметку
def get_keyboard():
    #contact_button = KeyboardButton('Отправить контакты', request_contact=True)
    #location_button = KeyboardButton('Отправить геопозицию', request_location=True)
    my_keyboard = ReplyKeyboardMarkup([[CALLBACK_BUTTON_DATA,CALLBACK_BUTTON_DATA_EXIT],
                                       [CALLBACK_BUTTON_EXIT_BIRGA, CALLBACK_BUTTON_EXIT_MARGA],
                                       ], resize_keyboard=True)  # добавляем кнопки
    return my_keyboard



if __name__ == '__main__':

    # запускаем поток для обработки свежих данных с основной программы
    thread = ThreadData()
    thread.start()

    # бот телега
    # updater = Updater(token=TOKEN, request_kwargs=REQUEST_KWARGS, use_context=True)
    updater = Updater(token=TOKEN, use_context=True)

    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    updater.start_polling()










