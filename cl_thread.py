import threading
from fu_tools import *
from settings import settings

import os
import logging
import telegram.bot
from telegram.ext import Updater, RegexHandler
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
from telegram import KeyboardButton


#
# поток связанный с чеканием стратегии
#

class StartCheckStg(threading.Thread):
    """StartCheckStg"""
    def __init__(self):
        threading.Thread.__init__ (self)

    def run(self):
        self.check_stg()


    def check_stg(self):
        while True:
            #print('==========GO StartCheckStg Thread==========')
            #check_flat(4) # coin. interval, limit
            #settings.BESTSTG = define_strategy()
            #print('BESTSTG:', settings.BESTSTG)
            sleep(300)

#
# поток связанный с торговлей на бинанс
#

class StartTrade(threading.Thread):
    """StartTrade"""
    def __init__(self):
        threading.Thread.__init__(self)
        #self.trade = trade

    def run(self):
        self.start_trade()

    def start_trade(self):
        #print('==========GO Trade Thread==========')
        while True:
            # start_trade_stg() обычная стратегия свечи+объем
            #start_trade_stg_only_stop_loss()
            #start_margin_trade_stg_only_stop_loss()
            #if self.trade == 'margin':
            #    start_trade_stg_only_stop_loss_margin(interval=settings.CENDEL_INTERVAL)
            #if self.trade == 'simple':
            #    start_trade_stg_only_stop_loss_4hour()
            start_trade_stg_margin_plus_birga()




