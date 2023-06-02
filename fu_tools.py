from binance_fun import *
from fu_2 import *
import ast
import sys
from time import sleep
from settings import settings
import decimal
import logging
from telegram.ext import Updater

'''
обычная стратегия стоплосс - новая
'''

def start_trade_stg_margin_plus_birga():
    if settings.CENDEL_INTERVAL == '4h': minutdelta = 240
    if settings.CENDEL_INTERVAL == '1h': minutdelta = 60
    if settings.CENDEL_INTERVAL == '15m': minutdelta = 15
    if settings.CENDEL_INTERVAL == '5m': minutdelta = 5

    settings.BUY = False
    limit_bool = False  # флаг для лимита

    print('Start trade fun...')

    #all_order_cancel()  # убираем все ордеры
    #if not check_money_balance(): return  # если нет денег выходим
    # print('account_only_free_balance: ', account_only_free_balance())

    while True:#
        # освежаем USDT и COIN?? возможно это удалить
        #COIN_free = get_free_balance('BTC')
        #USDT_free = get_free_balance('USDT')

        if limit_bool:
            if not check_orderid_cancel_or_executed():
                # ставим стоп под low
                print('###################################################')
                print('###################################################')
                print('>>>>>>LIMIT BUY<<<<<<')
                settings.TELETIPE = 'Limit buy'
                print('>>>>>>{0}<<<<<<'.format(settings.TRADE_STG))

                print(check_orderid)

                settings.LOG_TRADE['enterStg'] = 'Limit'
                print('Cработал buy-limit по цене ', settings.LOG_TRADE['enterPrice'])
                print('Цена входа: ', settings.LOG_TRADE['enterPrice'])
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                print('Время события: ', now)
                stop_price = limitbuy_stoploss_before_cendel()
                stop_loss = stop_loss_limit_order(stop_price)
                if 'error' in stop_loss: return
                print('Ставим стоп: ', stop_price)
                print('#########                                ##########')
                print('###################################################')
                limit_bool = False
                settings.BUY = True

        # биток куплен, ставим стопы и ждем вылета
        if settings.BUY:

            stop_timer = False
            before_cendel = False  # bool для проверки, что появилась следующая свеча
            # используем first pump stop, для защиты от резких скачков и падений (только при заходе в торговлю в текущей свече)
            first_pump_stop = False

            while True:
                # проверяем нет ли принудительного выхода
                if settings.EXIT_TRADE:
                    print('###################################################')
                    print('###################################################')
                    print('>>>>ПРИНУДИТЕЛЬНЫЙ ВЫХОД ТЕЛЕГРАМ ИЛИ САЙТА<<<<<')
                    settings.TELETIPE = 'Принудительный выход'
                    all_order_cancel()
                    sell_order = sell_order_market() #выходим из рынка
                    if 'return' in sell_order: return
                    print('Данные выхода  ', sell_order['fills'][0]['price'])
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                    print('Время события: ', now)

                    settings.LOG_TRADE['exitPrice'] = sell_order['fills'][0]['price']
                    settings.LOG_TRADE['exitDeposit'] = get_free_balance('USDT')
                    settings.LOG_TRADE['exitStg'] = 'Force'
                    sell_log()
                    settings.EXIT_TRADE = False
                    print('##########                              ###########')
                    print('###################################################')
                    return

                # проверяем не сработал ли стоп
                if not check_stop_loss_sell_order():
                    print('###################################################')
                    print('###################################################')
                    print('>>>>СРАБОТАЛ STOPLOSS #1<<<<<')
                    settings.TELETIPE = 'Сработал StopLoss'
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                    print('Время события: ', now)
                    print('Цена стоп: ', settings.LOG_TRADE['exitPrice'])
                    print('##########                              ###########')
                    print('###################################################')
                    settings.LOG_TRADE['exitDeposit'] = get_free_balance('USDT')
                    settings.LOG_TRADE['exitStg'] = 'StopLoss'
                    sell_log()
                    return

                # ставим стоп на вход, если цена резко взлетела на 0.5 и выше процента,  потом резко упала
                # находим раазницу в движении, если она больше 0.5 проента
                # используем first pump stop, для защиты от резких скачков и падений

                if not first_pump_stop:
                    if check_pump(settings.LOG_TRADE['enterPrice']):
                        print('###################################################')
                        print('###################################################')
                        print('>>>>ЦЕНА УШЛА НА 1 ПРОЦЕНТ<<<<<')
                        settings.TELETIPE = 'Цена ушла на 1 процента'
                        print('Ставим стоп на цену входа: ', str(settings.LOG_TRADE['enterPrice']))
                        now = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                        print('ВРЕМЯ ', now)
                        first_pump_stop = True

                        stop_loss = stop_loss_limit_order(settings.LOG_TRADE['enterPrice'])
                        if 'return' in stop_loss: return
                        # сохраняем значение последнего стопа для лога и статистики
                        stop_price = llist_before[0][3]
                        sleep(5) # спим чтобы успел поставится стоп лосс


                if not before_cendel:
                    print('ZZZZZZZZZZZZZZZZZ...')
                    print('ZZZZZZZZZZZZZZZZZ...')
                    print('>>>>Ждем свечу<<<<<')
                    llist_before = take_now_cendel_binance(1)
                    before_cendel = True
                    llist_now = llist_before
                    stop_loss_open = llist_now[0][1]
                else:
                    llist_now = take_now_cendel_binance(1)
                    now_after = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    now_after = datetime.strptime(now_after, '%Y-%m-%d %H:%M:%S')
                    if int(str((datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])) + timedelta(minutes=minutdelta) - now_after).total_seconds())[:-2]) <= 10 and int(
                            str((datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])) + timedelta(minutes=minutdelta) - now_after).total_seconds())[:-2]) > 1:
                        llist_before = llist_now  # мы это делаем, чтобы свеча предпоследняя была свежая

                # print('before ', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])), '; now: ', datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])))
                if int(str(llist_before[0][0])[:-3]) != int(str(llist_now[0][0])[:-3]):
                    print('ZZZZZZZZZZZZZZZZZ...')
                    print('ZZZZZZZZZZZZZZZZZ...')
                    print('>>>>Следующая свеча<<<<<')
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                    print('Время сейчас ', now)
                    print('HIGH предыдущей свечи ', llist_before[0][2])
                    print('LOW предыдущей свечи ', llist_before[0][3])
                    print('Время предыдущей свечи ', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])), '; Текущая свеча ', datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])))
                    if not stop_timer:
                        print('>>>>ПЕРВЫЙ СТОП Ставим стоп на свечу входа<<<<<')
                        print('>>>>>>{0}<<<<<<'.format(settings.TRADE_STG))
                        before_cendel = False
                        all_order_cancel()
                        # какой процент сделала пердыдущая свеча
                        #print('llist_before ', llist_before)
                        #print('before start', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])))
                        #print('before end', datetime.fromtimestamp(int(str(llist_before[0][6])[:-3])))
                        openclose = decimal.Decimal(abs(float(llist_before[0][1]) - float(llist_before[0][4])))
                        allcendel = decimal.Decimal(float(llist_before[0][2]) - float(llist_before[0][3]))
                        amplituda = openclose / allcendel
                        #print('openclose:', openclose)
                        #print('allcendel:', allcendel)
                        #print('amplituda:', amplituda)
                        # сохраняем значение первого стопа, чтобы не поставить ниже него на следующей свече

                        if settings.TRADE_STG == 'STANDART':
                            stop_loss = stop_loss_limit_order(llist_before[0][3])
                            #??? stop_price = llist_before[0][3] # сохраняем значение последнего стопа для лога и статистики
                        if settings.TRADE_STG == 'MARGIN_DOWN':
                            stop_loss = stop_loss_limit_order(llist_before[0][2])
                            #??? stop_price = llist_before[0][2]  # сохраняем значение последнего стопа для лога и статистики

                        if 'return' in stop_loss:
                            print('Error stop loss #168')
                            settings.BUY = False
                            return

                        '''

                        #ЭТО БЛОК КОТОРЫЙ СТАВИТ СТОП НА СВЕЧУ ВХОДА НА СЕРЕДКУ ИЛИ ЛОУ

                        if amplituda <= 0.2:

                            # сохраняем значение первого стопа, чтобы не поставить ниже него на следующей свече
                            stop_loss_open = llist_before[0][4]

                            # ставим стоп под low

                            # освежаем USDT и COIN
                            COIN_free, USDT_free = get_free_balance('BTC', 'USDT')
                            COIN_locked = get_free_balance('BTC', 'locked')
                            print('COIN_locked', COIN_locked)
                            print('COIN_free', COIN_free)

                            stop_loss = sell_or_buy_stop_loss_limit_order(maxstg['coin'],'SELL',COIN_free,llist_before[0][4])

                            if 'code' in stop_loss.keys():

                                if 'trigger immediately' in stop_loss['msg']:
                                    print('Стоп лосс выше, просто продаем по рыночной')

                                    sell_order = buy_or_sell_order_market(maxstg['coin'],'SELL',COIN_free)

                                    print('sell_order 333 ', sell_order['fills'][0]['price'])

                                    if 'code' in sell_order.keys():
                                        print('Error sell market 1')

                                    tick = bot.tickerPrice(symbol=maxstg['coin'])
                                    print('###################################################')
                                    print('#########STOPLOSS3#STOPLOSS3STOPLOSS3##############')
                                    print('###################################################')
                                    print('###################################################')
                                    log_1.append(float(sell_order['fills'][0]['price']))
                                    # освежаем USDT для лог данные
                                    USDT_free = get_free_balance(0, 'USDT')
                                    log_1.append(float(USDT_free))
                                    sell_log(log_1)
                                    kypil = False
                                    return

                                print('Error stop loss 4 low')
                                kypil = False
                                return

                            # сохраняем значение последнего стопа для лога и статистики
                            print('stop loss status:', stop_loss)
                            stop_price = llist_before[0][3]

                        else:

                            # сохраняем значение первого стопа, чтобы не поставить ниже него на следующей свече
                            stop_loss_open = llist_before[0][1]

                            # освежаем USDT и COIN
                            COIN_free, USDT_free = get_free_balance('BTC', 'USDT')

                            COIN_locked = get_free_balance('BTC', 'locked')
                            print('COIN_locked', COIN_locked)
                            print('COIN_free', COIN_free)

                            # ставим стоп под open
                            stop_loss = sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, llist_before[0][1])

                            if 'code' in stop_loss.keys():

                                if 'trigger immediately' in stop_loss['msg']:
                                    print('Стоп лосс выше, просто продаем по рыночной')

                                    sell_order = buy_or_sell_order_market(maxstg['coin'],'SELL', COIN_free)

                                    print('sell_order vvv ', sell_order['fills'][0]['price'])

                                    if 'code' in sell_order.keys():
                                        print('Error sell zzz123')

                                    tick = bot.tickerPrice(symbol=maxstg['coin'])
                                    print('###################################################')
                                    print('###################################################')
                                    print('#########STOPLOSS5#STOPLOSS5STOPLOSS5##############')
                                    print('###################################################')
                                    print('###################################################')
                                    print('###################################################')
                                    log_1.append(float(sell_order['fills'][0]['price']))

                                    # освежаем USDT для лог данные
                                    USDT_free = get_free_balance(0, 'USDT')
                                    log_1.append(float(USDT_free))
                                    sell_log(log_1)
                                    kypil = False
                                    return

                                print('Error stop loss 3 next')
                                return
                            stop_price = llist_before[0][1]
                        '''

                    print('stop_loss_open ', stop_loss_open)
                    print('llist_before[0][3] ', llist_before[0][3])
                    print('llist_before[0][2] ', llist_before[0][2])


                    if stop_timer:

                        before_cendel = False
                        print('>>>>СЛЕДУЮЩИЙ СТОП Ставим стоп на предыдущую свечу++++++<<<<<')
                        print('>>>>>>{0}<<<<<<'.format(settings.TRADE_STG))
                        print('llist_next_stop ', llist_before[0])
                        print('llist_next_stop data ', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])))
                        all_order_cancel()
                        #print('time before stop', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])), '; stop price:', llist_before[0][3], '; COIN_free:', COIN_free)
                        stop_loss = stop_loss_limit_order(llist_before[0][3])
                        if 'return' in stop_loss: return
                        # сохраняем значение последнего стопа для лога и статистики
                        stop_price = llist_before[0][3]
                    stop_timer = True

       # print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        #print('$$$ Ищем паттерн на вход $$$')

        llist = take_now_cendel_binance(1)
        for cendel in llist:
            coin_ts_open = int(str(cendel[0])[:-3])
            coin_ts_close = int(str(cendel[6])[:-3])
            # print('ts open: ', str(datetime.fromtimestamp(coin_ts_open).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0])
            # print('ts close: ', str(datetime.fromtimestamp(coin_ts_close).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0])
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
        close_cendel = datetime.fromtimestamp(coin_ts_close)  # strftime('%Y-%m-%d %H:%M:%S')

        if now < close_cendel and int(str((close_cendel - now).total_seconds())[:-2]) > 10:  # если больше 10 сек до конца свечи, тогда ок
            print('$$$$$$$$$$$$$$$$$$$$$$$')
            print('Ищем паттерн на вход...')
            print('limit bool = ', limit_bool, '; check_stop_loss_limit_buy_order() = ', check_stop_loss_limit_buy_order())
            settings.TELETIPE = 'Ищем паттерн на вход'
            while True:
                # проверяем нет ли покупки по лимит
                if limit_bool:
                    if not check_orderid_cancel_or_executed():
                        print('###################################################')
                        print('###################################################')
                        print('>>>>>>LIMIT BUY в паттерне на вход<<<<<<')
                        settings.TELETIPE = 'Limit buy в паттерне на вход'
                        print('>>>>>>{0}<<<<<<'.format(settings.TRADE_STG))
                        print('Cработал buy-limit по цене ', settings.LOG_TRADE['enterPrice'])
                        print('orderInfo: ', check_orderid())
                        now = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                        settings.LOG_TRADE['timestamp'] = int(str(now.timestamp()).split('.')[0])
                        settings.LOG_TRADE['enterStg'] = 'Limit'
                        print('Время события: ', now)
                        stop_price = limitbuy_stoploss_before_cendel()
                        stop_loss = stop_loss_limit_order(stop_price)
                        if 'return' in stop_loss: return
                        print('Ставим стоп: ', stop_price)
                        print('##########                           ##############')
                        print('###################################################')
                        limit_bool = False
                        settings.BUY = True
                        break

                sleep(3)
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                # print(end_cendel - now)
                if int(str((close_cendel - now).total_seconds())[:-2]) < 6 and int(str((close_cendel - now).total_seconds())[:-2]) > 0:

                    if check_flat(4):
                        #qtyB = check_coin_QtyBuy_limit(get_free_balance('USDT'), limit_price)
                        print('###################################################')
                        print('###################################################')
                        print('>>>>>>СТАВИМ FLAT LIMIT<<<<<<')
                        print('>>>>>>{0}<<<<<<'.format(settings.TRADE_STG))
                        #print('COIN_free ', COIN_free, '; USDT_free ', USDT_free, '; Сколько можно купить крипты на usd ', qtyB, '; ', limit_price, 'limit_price')
                        print('Цена входа flat limit', settings.FLAT_ENTER_PRICE)
                        print('Время now ', now)

                        stop_loss = buy_limit_order(settings.FLAT_ENTER_PRICE)
                        if 'return' in stop_loss:
                            print('Return')
                            return

                        limit_bool = True
                        #print('llist узнать почему limit_stop_price берет неправильный [0][3] ', llist)
                        print('Время свечи ', datetime.fromtimestamp(int(str(llist[0][0])[:-3])))

                        #?? limit_qty = decimal.Decimal(qtyB).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN)

                        # {'orderId': 1630544816,'price': '6635.19000000', 'origQty': '0.00395000', 'cummulativeQuoteQty': '26.12692877', 'status': 'FILLED',
                        sleep(5)
                        break

                    # print('проверяем свечу, если зеленая, тогда ставим флаг для покупки следующей постратгеии')
                    # print(tick['price'], ' > ', llist[0][1])
                    # print(maxstg['max']['volume'], '<=', llist[0][5])

                    # print(float(maxstg['max']['volume']), '<', float(llist[0][5])) объем
                    # rint(llist[0])
                    # print('Время свечи', datetime.fromtimestamp(int(str(llist[0][6])[:-3])))
                    # print('Время сейчас', now)
                    llist = take_now_cendel_binance(1)
                      # заного берем значение текущей свечи, чтобы получить свежий объем
                    if cendel_color(): #если свеча зеленая или красная для маржи
                        # if float(tick_red_green['price']) > float(open_red_green[0][1]) and 200 <= float(llist[0][5]):
                        print('###################################################')
                        print('###################################################')
                        print('>>>>>>ПОКУПКА!ПОКУПКА!ПОКУПКА<<<<<<')
                        settings.TELETIPE = 'Покупка'
                        print('>>>>>>{0}<<<<<<'.format(settings.TRADE_STG))
                        print('Время покупки (ЭТО ВРЕМЯ ПРЕДЫДУЩЕЙ):', datetime.fromtimestamp(int(str(llist[0][0])[:-3])))
                        settings.LOG_TRADE['enterStg'] = 'Simple'

                        # отменяем лимит
                        limit_bool = False

                        #
                        # покупаем
                        #
                        all_order_cancel()  # отменяем все ордера во избежание проблем
                        stop_price = llist
                        # определяем, если свеча больше 1%, тогда стоп на середину ее тела
                        print('ВРЕМЯ СВЕЧИ ', datetime.fromtimestamp(int(str(stop_price[0][0])[:-3])), ': ', stop_price[0])


                        center = (decimal.Decimal(stop_price[0][2]) - decimal.Decimal(stop_price[0][3]))
                        razniza = (decimal.Decimal(stop_price[0][3]) / 100)
                        # percent = max(center, razniza) / min(center, razniza)
                        percent = center / razniza
                        print('percent:', percent)
                        if settings.CENDEL_INTERVAL == '4h': p = 5
                        if settings.CENDEL_INTERVAL == '1h': p = 3
                        if settings.CENDEL_INTERVAL == '15m': p = 1
                        if settings.CENDEL_INTERVAL == '5m': p = 1

                        if percent >= p:
                            stop_price = abs((decimal.Decimal(stop_price[0][2]) - decimal.Decimal(stop_price[0][3])) / 2) + decimal.Decimal(stop_price[0][3])  # округлить бы
                            print('stop_price > 5 :', stop_price)
                        else:
                            if settings.TRADE_STG == 'STANDART':
                                stop_price = decimal.Decimal(stop_price[0][3])
                            if settings.TRADE_STG == 'MARGIN_DOWN':
                                stop_price = decimal.Decimal(stop_price[0][2])
                            print('stop_price < 5:', stop_price)

                        buy_order = buy_order_market()
                        if 'return' in buy_order: return
                        print('ЦЕНА ВХОДА ПО MARKET ', str(buy_order['fills'][0]['price']))
                        # print(datetime.fromtimestamp(stop_price[0]))

                        stop_loss = stop_loss_limit_order(stop_price)
                        print('stop_loss: ', stop_loss)
                        settings.BUY = True
                        sleep(10)
                        break
                    else:
                        print('###################################################')
                        print('###################################################')
                        print('>>>>>>СТАВИМ LIMIT<<<<<<')
                        print('Cвеча красная или зеленая (при марже), или объем не прошел!')

                        limit_price = None
                        if settings.TRADE_STG == 'STANDART':
                            limit_price = decimal.Decimal(llist[0][2]) + 2

                        if settings.TRADE_STG == 'MARGIN_DOWN':
                            limit_price = decimal.Decimal(llist[0][3]) - 2
                        print('llist ', llist)
                        print('limit_price', limit_price)
                        buy_limit = buy_limit_order(limit_price)

                        if 'return' in buy_limit: return
                        print('limit:', buy_limit)

                        limit_bool = True
                        limit_stop_price = llist[0][3]

                        # {'orderId': 1630544816,'price': '6635.19000000', 'origQty': '0.00395000', 'cummulativeQuoteQty': '26.12692877', 'status': 'FILLED',

                        sleep(5)
                        break



def check_flat(limit):
    '''
    определение боковика
    '''

    now = datetime.now()
    tag = False
    llist = bot.klines(symbol=settings.COIN, interval=settings.CENDEL_INTERVAL, limit=limit)
    now_cendel = llist[limit-1]
    coin_ts = int(str(now_cendel[0])[:-3])
    coin_f = str(datetime.fromtimestamp(coin_ts).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0]
    #print('flat time first cendel ', coin_f)

    high = 0
    low = 200000
    if float(now_cendel[2]) > float(high): high = now_cendel[2]
    if float(now_cendel[3]) < float(low): low = now_cendel[3]

    for check in llist[:-1]:
        if float(check[2]) > float(high): high = check[2]
        if float(check[3]) < float(low): low = check[3]

        coin_ts = int(str(check[0])[:-3])
        coin_dt = str(datetime.fromtimestamp(coin_ts).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0]
        #print('^^^^^^^^^^^')
        #print('Свеча: ', coin_dt, ', ', 'high/low: ', check[2], '/', check[3])
        #print('Свеча последняя: ', coin_f, ', ', 'high/low: ', now_cendel[2], '/', now_cendel[3])
        if not range(max(round(float(check[2])), round(float(now_cendel[2]))), min(round(float(check[3])), round(float(now_cendel[3]))) + 1,-1):
            tag = True
            #print('Нет пересечение')


    if tag:
        print('Боковика нет')
        settings.FLAT = False
        return False
    else:
        print('Боковик есть')
        settings.FLAT = True
        if settings.TRADE_STG == 'STANDART':
            settings.FLAT_ENTER_PRICE = float(high) + 2
        if settings.TRADE_STG == 'MARGIN_DOWN':
            settings.FLAT_ENTER_PRICE = float(low) - 2
        return True




    '''
    high = 0
    low = 200000
    for cendel in llist:
        if float(cendel[2]) > float(high): high = cendel[2]
        if float(cendel[3]) < float(low): low = cendel[3]
        coin_ts = int(str(cendel[0])[:-3])
        coin_dt = str(datetime.fromtimestamp(coin_ts).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0]
        #print('$$$$$$$$$$$$$$')
        #print('Свеча: ', coin_dt, ', ', coin_ts, 'high/low: ', high, '/', low)
        c = 0
        for check in llist:
           # print('Боковик последние свечи: ', coin_dt, ', ', coin_ts, 'high/low: ', check[2], '/', check[3])
            if range(max(round(float(low)), round(float(cendel[3]))), min(round(float(cendel[2])), round(float(check[2]))) + 1, 1):
                (9474,)
                c += 1

    if c == limit:
        #print('Боковик есть')
        settings.FLAT = True
        if settings.TRADE_STG == 'STANDART':
            settings.FLAT_ENTER_PRICE = float(high) + 2
        if settings.TRADE_STG == 'MARGIN_DOWN':
            settings.FLAT_ENTER_PRICE = float(low) - 2
    else:
        #print('Боковика нет')
        settings.FLAT = False
    '''
























