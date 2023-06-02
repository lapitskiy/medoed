# settings.py
from binance_fun import *
import redis
import logging

# add filemode="w" to overwrite
logging.basicConfig(filename="log\log.log", level=logging.INFO, filemode='w')

class Global_Settings:
    def __init__(self):
        self.BESTSTG = {}
        self.COIN = 'BTCUSDT'
        self._EXIT_TRADE = False
        self.FLAT = False
        self.FLAT_ENTER_PRICE = 0
        self.CENDEL_INTERVAL = '5m'
        self._BUY = False
        self.TRADE_STG = None
        self.LOG_TRADE = {}
        self.PORT = 55555
        self._TELETIPE = {}
        #self.BUG_EXIT = False
        #self.RESTART = False

        self.STOP_LOSS_LIMIT_BUY_ORDERID = None

        # внутренние
        self.r = None
        self.init()


    @property
    def BUY(self):
        return self._BUY
    @BUY.setter
    def BUY(self, value):
        if value != self._BUY:
            #print('setting.BUY = ', value)
            self.r.hset('setting'+self.TRADE_STG, 'BUY', str(value))
            #print(self.r.hget('setting'+self.TRADE_STG, 'BUY').decode(),' - ',type(self.r.hget('setting', 'BUY').decode()))
        self._BUY = value

    @property
    def TELETIPE(self):
        return self._TELETIPE
    @BUY.setter
    def TELETIPE(self, value):
        if value != self._TELETIPE:
            #print('setting.BUY = ', value)
            strr = '[' + self.TRADE_STG + '] ' + value
            self.r.hset('setting', 'TELETIPE', strr)
            #print(self.r.hget('setting'+self.TRADE_STG, 'BUY').decode(),' - ',type(self.r.hget('setting', 'BUY').decode()))

        self._TELETIPE = value

    @property
    def EXIT_TRADE(self):
        return self._EXIT_TRADE
    @EXIT_TRADE.setter
    def EXIT_TRADE(self, value):
        self._EXIT_TRADE = value


    def init(self):
        try:
            self.r = redis.StrictRedis(host='localhost', db=12)
        except redis.exceptions.ResponseError:
            print('redis err')

        #if self.r.hget('setting'+self.TRADE_STG, 'BUY').decode:
        #    print('Запускаем restart системы, так как при выходе была покупка')
        #    self.RESTART = True


settings = Global_Settings()


        # Какой-то код, перерисовывающий инерфейс
        # в соответствии с новым размером шрифта

    # coin
    #global COIN
    #COIN = 'BTCUSDT'

    # принудительный выход из позиции через кнопку на сайте
    #global EXIT_SIMPLE
    #global EXIT_MARGIN
    #EXIT_SIMPLE = False
    #EXIT_MARGIN = False

    # БОКОВИК
    #global FLAT
    #global FLAT_HIGH
    #global FLAT_LOW
    #FLAT = False
    #FLAT_HIGH = 0
    #FLAT_LOW = 0

    # ИНТЕРВАЛ
    #global CENDEL_INTERVAL
    #CENDEL_INTERVAL = '1h' #4h 5m 1h




