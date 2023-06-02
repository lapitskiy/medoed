#bot settings.py
import redis
from distutils.util import strtobool

class Global_Settings:
    def __init__(self):
        self.FRESH_DATA = False
        self.TELETIPE = ''
        self._EXIT_SIMPLE = False
        self._EXIT_MARGIN = False
        self._BUY = False
        # внутренние
        self.r = None
        #функция старт
        self.init()

    @property
    def BUY(self):
        return self._BUY
    @BUY.setter
    def BUY(self, value):
        self._BUY = value

    @property
    def EXIT_SIMPLE(self):
        return self._EXIT_SIMPLE
    @EXIT_SIMPLE.setter
    def EXIT_SIMPLE(self, value):
        self._EXIT_SIMPLE = value

    @property
    def EXIT_MARGIN(self):
        return self._EXIT_MARGIN
    @EXIT_MARGIN.setter
    def EXIT_MARGIN(self, value):
        self._EXIT_MARGIN = value


    def init(self):
        try:
            self.r = redis.StrictRedis(host='localhost', db=12)
        except redis.exceptions.ResponseError:
            print('redis err')
        self._BUY = self.r.hget('setting', 'BUY').decode()
        self._BUY = bool(self._BUY)
        #self.TELETIPE = self.r.hget('setting', 'TELETIPE').decode()


settings = Global_Settings()