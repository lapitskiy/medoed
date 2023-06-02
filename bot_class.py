#
# поток связанный с ботом
#
from bot_settings import settings
import threading
import redis
from time import sleep



class ThreadData(threading.Thread):
    """StartTrade"""
    def __init__(self):
        threading.Thread.__init__(self)
        self.update = None
        self.context = None


    def run(self):
        self.start_thread()

    def start_thread(self):
        r = red.redis_db_check(12)
        while True:
            if settings.FRESH_DATA:
                if r.hget('setting', 'TELETIPE') is not None:
                    if settings.TELETIPE != r.hget('setting', 'TELETIPE').decode():
                        settings.TELETIPE = r.hget('setting', 'TELETIPE').decode()
                        print('######### TELETIPE NEW')
                        self.context.bot.send_message(chat_id=self.update.effective_chat.id, text=settings.TELETIPE)
                '''
                if not settings.BUY and r.hget('setting', 'BUY').decode() == 'True':
                    print('############')
                    print('Покупка')
                    print('############')
                    settings.BUY = True
                    self.context.bot.send_message(chat_id=self.update.effective_chat.id, text='Покупка')
                if settings.BUY and r.hget('setting', 'BUY').decode() == 'False':
                    print('############')
                    print('Ищем патерн на вход')
                    print('############')
                    settings.BUY = False
                    self.context.bot.send_message(chat_id=self.update.effective_chat.id, text='Вышли из биржи и ищем паттерн на вход')
                '''



    def bot_updater(self, update, context):
        self.update = update
        self.context = context



#
# redis class
#
# проверяем последний день записи в редисе
class Rediss:
    def __init__(self):
        self.db = 12

    def redis_db_check(self, dbname):
        try:
            r = redis.StrictRedis(host='localhost', db=dbname)
        except redis.exceptions.ResponseError:
            print('redis err')
        return r

red = Rediss()


#
# Telegram class
#
