'''
маржинальная стратегия старая
'''
def start_trade_stg_only_stop_loss_4hour():
    maxstg = {}
    maxstg['coin'] = settings.COIN
    maxstg['interval'] = settings.CENDEL_INTERVAL
    if interval == '4h': minutdelta = 240
    if interval == '1h': minutdelta = 60
    if interval == '5m': minutdelta = 5

    all_order_cancel(maxstg['coin'])  # убираем все ордеры

    if not check_money_balance('simple'): return  # если нет денег выходим

    #print('account_only_free_balance: ', account_only_free_balance())

    settings.BUY = False
    limit_bool = False

    while True:

        # освежаем USDT и COIN
        COIN_free, USDT_free = get_free_balance('BTC', 'USDT')

        if limit_bool:
            if not check_stop_loss_limit_buy_order(maxstg['coin']):
                # ставим стоп под low

                print('###################################################')
                print('#########FFFFFFF LIMIT BUY BUY BUYLIMIT BUY BUY BUY########')
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                print('TIME ', now)
                print(' цена входа ', log_1[4])
                print('limit_stop_price ', limit_stop_price)
                print('stop buy сработал, ставим стоп под свечу входа')
                print('###################################################')
                print('###################################################')

                COIN_free = get_free_balance('BTC', 0)
                COIN_locked = get_free_balance('BTC', 'locked')
                print('COIN_locked', COIN_locked)
                print('COIN_free', COIN_free)

                stop_price = data_before_cendel('low')
                stop_loss = sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, stop_price)
                print('stop_loss ', stop_loss)
                if 'code' in stop_loss.keys():
                    print('stop buy err fff')
                    return
                limit_bool = False
                settings.BUY = True

        # биток куплен, ставим стопы и ждем вылета
        if settings.BUY:

            stop_timer = False
            before_cendel = False  # bool для проверки, что появилась следующая свеча
            first_pump_stop = False # используем first pump stop, для защиты от резких скачков и падений (только при заходе в торговлю в текущей свече)

            while True:
                # проверяем нет ли принудительного выхода
                if settings.EXIT_SIMPLE:
                    # освежаем USDT и COIN
                    all_order_cancel(maxstg['coin'])
                    COIN_free, USDT_free = get_free_balance('BTC', 'USDT')
                    print('COIN_free', COIN_free)
                    sell_order = buy_or_sell_order_market(maxstg['coin'], 'SELL', COIN_free)

                    print('sell_order  EXIT_SIMPLE', sell_order['fills'][0]['price'])

                    if 'code' in sell_order.keys():
                        print('Error sell market EXIT_SIMPLE')

                    print('###################################################')
                    print('#########ПРИНУДИТЕЛЬНЫЙ ВЫХОД######################')
                    print('#########ПРИНУДИТЕЛЬНЫЙ ВЫХОД######################')
                    print('###################################################')
                    log_1.append(float(sell_order['fills'][0]['price']))
                    # освежаем USDT для лог данные
                    USDT_free = get_free_balance(0, 'USDT')
                    log_1.append(float(USDT_free))
                    sell_log(log_1, 14)
                    settings.EXIT_SIMPLE = False
                    return

                # проверяем не сработал ли стоп
                if not check_stop_loss_sell_order(maxstg['coin']):
                    print('###################################################')
                    print('#########STOPLOSS1#STOPLOSS1STOPLOSS1##############')
                    print(str(stop_price))
                    print('###################################################')
                    print('###################################################')

                    log_1.append(float(stop_price))
                    log_1.append(float(get_free_balance(0, 'USDT')))
                    sell_log(log_1,14)
                    return

                # ставим стоп на вход, если цена резко взлетела на 0.5 и выше процента,  потом резко упала
                # находим раазницу в движении, если она больше 0.5 проента
                # используем first pump stop, для защиты от резких скачков и падений
                tick = bot.tickerPrice(symbol=maxstg['coin'])
                f1 = abs(decimal.Decimal(log_1[4])-decimal.Decimal(tick['price']))
                f2 = (decimal.Decimal(log_1[4]) / 100) * decimal.Decimal(0.5)
                if f1 > f2 and not first_pump_stop:
                    print('ЦЕНА ВЗЛЕТЕТА НА 0.5 ПРОЦЕНТ!!!!!!')
                    print('Разница в цене: ', str(f1))
                    print('0.5 процент от цены входа: ', str(f2))
                    print('ставим стоп на цену входа: ', str(log_1[4]))
                    all_order_cancel(maxstg['coin'])
                    first_pump_stop = True
                    # освежаем USDT и COIN
                    COIN_free, USDT_free = get_free_balance('BTC', 'USDT')

                    stop_loss = sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, log_1[4])

                    if 'code' in stop_loss.keys():

                        if 'trigger immediately' in stop_loss['msg']:
                            print('Стоп лосс выше, просто продаем по рыночной')

                            sell_order = buy_or_sell_order_market(maxstg['coin'], 'SELL', COIN_free)

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
                            sell_log(log_1, 14)
                            settings.BUY = False
                            return

                        print('Error stop loss 4 low')
                        settings.BUY = False
                        return

                    # сохраняем значение последнего стопа для лога и статистики
                    print('stop loss status:', stop_loss)
                    stop_price = llist_before[0][3]




                if not before_cendel:
                    print('###############')
                    print('###############')
                    print('wait cendel')
                    llist_before = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)
                    now_before = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    now_before = datetime.strptime(now_before, '%Y-%m-%d %H:%M:%S')
                    before_cendel = True
                    llist_now = llist_before
                    stop_loss_open = llist_now[0][1]
                else:
                    llist_now = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)
                    now_after = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    now_after = datetime.strptime(now_after, '%Y-%m-%d %H:%M:%S')
                    if int(str((datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])) + timedelta(minutes=minutdelta) - now_after).total_seconds())[:-2]) <= 10 and int(str((datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])) + timedelta(minutes=minutdelta) - now_after).total_seconds())[:-2]) > 1:
                        llist_before = llist_now # мы это делаем, чтобы свеча предпоследняя была свежая

                    # if int(str((datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])) + timedelta(5) - now_before).total_seconds())[:-2]) >= 7:  # если больше 5 сек до конца свечи, тогда ок
                    #    sleep(5)
                    # else:
                    #    sleep(int(str((datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])) + timedelta(5) - now_before).total_seconds())[:-2])+5)

                # print('before ', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])), '; now: ', datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])))
                if int(str(llist_before[0][0])[:-3]) != int(str(llist_now[0][0])[:-3]):
                    print('###############')
                    print('###############')
                    print('След свеча')
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                    print('TIME ', now)
                    print('llist_before[0][3] ', llist_before[0][3])
                    print('###############')
                    print('###############')
                    print('before ', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])), '; now: ', datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])))
                    if not stop_timer:
                        print('NEW FIRST STOP! Ставим новый стоп на свечу входа zzz')
                        before_cendel = False

                        all_order_cancel(maxstg['coin'])

                        # какой процент сделала пердыдущая свеча
                        print('llist_before ',llist_before)
                        print('before start', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])))
                        print('before end', datetime.fromtimestamp(int(str(llist_before[0][6])[:-3])))
                        openclose = decimal.Decimal(abs(float(llist_before[0][1]) - float(llist_before[0][4])))
                        allcendel = decimal.Decimal(float(llist_before[0][2]) - float(llist_before[0][3]))
                        amplituda = openclose / allcendel

                        print('openclose:', openclose)
                        print('allcendel:', allcendel)
                        print('amplituda:', amplituda)

                        # сохраняем значение первого стопа, чтобы не поставить ниже него на следующей свече
                        stop_loss_open = llist_before[0][4]

                        # ставим стоп под low

                        # освежаем USDT и COIN
                        COIN_free, USDT_free = get_free_balance('BTC', 'USDT')
                        COIN_locked = get_free_balance('BTC', 'locked')
                        print('COIN_locked', COIN_locked)
                        print('COIN_free', COIN_free)


                        stop_loss = sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, llist_before[0][3])

                        if 'code' in stop_loss.keys():

                            if 'trigger immediately' in stop_loss['msg']:
                                print('Стоп лосс выше, просто продаем по рыночной')

                                sell_order = buy_or_sell_order_market(maxstg['coin'], 'SELL', COIN_free)

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
                                sell_log(log_1,14)
                                settings.BUY = False
                                return

                            print('Error stop loss 4 low')
                            settings.BUY = False
                            return

                        # сохраняем значение последнего стопа для лога и статистики
                        print('stop loss status:', stop_loss)
                        stop_price = llist_before[0][3]

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
                    if stop_timer and float(stop_loss_open) < float(llist_before[0][3]):
                        before_cendel = False
                        print('NEW STOP! Ставим новый стоп под предыдущую свечу, но не ниже open xxx')
                        print('llist_next_stop ', llist_before[0])
                        print('llist_next_stop data ', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])))
                        all_order_cancel(maxstg['coin'])
                        print('time before stop', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])), '; stop price:', llist_before[0][3], '; COIN_free:', COIN_free)

                        stop_loss = sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, llist_before[0][3])

                        if 'code' in stop_loss.keys():

                            if 'trigger immediately' in stop_loss['msg']:
                                print('Стоп лосс выше, просто продаем по рыночной')

                                sell_order = buy_or_sell_order_market(maxstg['coin'], 'SELL', COIN_free)

                                print('sell_order 666 ', sell_order['fills'][0]['price'])

                                if 'code' in sell_order.keys():
                                    print('Error sell 987')

                                print('###################################################')
                                print('###################################################')
                                print('#########STOPLOSS6#STOPLOSS6STOPLOSS6##############')
                                print('###################################################')
                                print('###################################################')
                                print('###################################################')
                                log_1.append(float(sell_order['fills'][0]['price']))
                                # освежаем USDT для лог данные
                                USDT_free = get_free_balance(0, 'USDT')
                                log_1.append(float(USDT_free))
                                sell_log(log_1,14)
                                settings.BUY = False
                                return

                            print('Error stop loss 3 next')
                            return

                        # сохраняем значение последнего стопа для лога и статистики
                        print('stop loss status:', stop_loss)
                        stop_price = llist_before[0][3]
                    # чекаем по 10 сек, потом сравниваем
                    stop_timer = True

        print('### Ищем паттерн на вход ###')
        # биток не куплен, ждем свечу на вход
        llist = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)
        # print(llist)

        for cendel in llist:
            coin_ts_open = int(str(cendel[0])[:-3])
            coin_ts_close = int(str(cendel[6])[:-3])
            # print('ts open: ', str(datetime.fromtimestamp(coin_ts_open).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0])
            # print('ts close: ', str(datetime.fromtimestamp(coin_ts_close).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0])

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
        close_cendel = datetime.fromtimestamp(coin_ts_close)  # strftime('%Y-%m-%d %H:%M:%S')

        # print(type(now), ' - ',now)
        # print(type(close_cendel), ' - ', end_cendel)
        # print(int(str((end_cendel - now).total_seconds())[:-2]))


        if now < close_cendel and int(str((close_cendel - now).total_seconds())[:-2]) > 10:  # если больше 10 сек до конца свечи, тогда ок

            while True:

                # проверяем нет ли покупки по лимит
                if limit_bool:
                    if not check_stop_loss_limit_buy_order(maxstg['coin']):

                        print('check_stop_loss_limit_buy_order ', check_stop_loss_limit_buy_order(maxstg['coin']))
                        print('###################################################')
                        print('#########LIMIT BUY BUY BUYLIMIT BUY BUY BUY MMMMMMM########')
                        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')

                        print('TIME ', now)
                        print(' цена входа ', log_1[4])
                        print('stop buy сработал, ставим стоп под свечу входа')
                        print('###################################################')
                        print('###################################################')

                        stop_price = data_before_cendel('low')
                        COIN_free = get_free_balance('BTC', 0)
                        COIN_locked = get_free_balance('BTC', 'locked')
                        #print('COIN_locked', COIN_locked)
                        #print('COIN_free', COIN_free)
                        data_before_cendel('low')
                        stop_loss = sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, stop_price)

                        print('stop_loss ', stop_loss)
                        if 'code' in stop_loss.keys():
                            print('stop buy err fff')
                            return

                        limit_bool = False
                        settings.BUY = True
                        break


                sleep(3)
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                # print(end_cendel - now)
                if int(str((close_cendel - now).total_seconds())[:-2]) < 6 and int(str((close_cendel - now).total_seconds())[:-2]) > 0:

                    if settings.FLAT:
                        # удаляем все ордера для нового limit
                        all_order_cancel(maxstg['coin'])
                        limit_price = decimal.Decimal(settings.FLAT_HIGH) + 2

                        COIN_free = get_free_balance('BTC', 0)
                        qtyS = check_coin_QtySell(COIN_free, maxstg['coin'], limit_price)
                        print('COIN_free ', COIN_free, '; Сколько usdt в битках ', qtyS, '; limit_price ', limit_price)

                        if float(COIN_free) > 0.0016:
                            sell_order = buy_or_sell_order_market(maxstg['coin'], 'SELL', cut_percent(COIN_free,1))
                            print('sell_order main lkj', sell_order)
                            if 'code' in sell_order.keys():
                                print('Error sell market 1cc')
                                sleep(5)
                                return

                        USDT_free = get_free_balance(0, 'USDT')
                        qtyB = check_coin_QtyBuy_limit(USDT_free, maxstg['coin'], limit_price)
                        print('COIN_free ', COIN_free, '; USDT_free ', USDT_free, '; Сколько можно купить крипты на usd ', qtyB, '; ', limit_price, 'limit_price')

                        if qtyB > 0.001:  # проверяем есть ли доллары для покуки битка

                            print('###################################################')
                            print('######FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF##########')
                            print('###############LIMIT!FLAT!LIMIT!##################')
                            print('###############LIMITFLAT!LIMIT!####################')
                            print('###############FLATFLATFLATFLAT####################')
                            print('###################################################')

                            limit = sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'BUY', qtyB, limit_price)

                            limit_bool = True
                            print('llist узнать почему limit_stop_price берет неправильный [0][3] ', llist)
                            print('Время свечи ', datetime.fromtimestamp(int(str(llist[0][0])[:-3])))

                            limit_qty = decimal.Decimal(qtyB).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN)

                            log_1 = [int(str(now.timestamp()).split('.')[0]), maxstg['coin'], maxstg['interval'], USDT_free, float(limit_price)]
                            '''
                            log_dict = {
                                'timestamp' : int(str(now.timestamp()).split('.')[0]),
                                'coin' : maxstg['coin'],
                                'interval' : maxstg['interval'],
                                'deposit' : USDT_free,
                                'enterPrice' : float(limit_price)
                            }
                            '''
                            # {'orderId': 1630544816,'price': '6635.19000000', 'origQty': '0.00395000', 'cummulativeQuoteQty': '26.12692877', 'status': 'FILLED',
                        print('Боковик, cтавим только limit ', limit_price)
                        sleep(5)
                        break


                    tick_red_green = bot.tickerPrice(symbol=maxstg['coin'])
                    # print('проверяем свечу, если зеленая, тогда ставим флаг для покупки следующей постратгеии')
                    # print(tick['price'], ' > ', llist[0][1])
                    # print(maxstg['max']['volume'], '<=', llist[0][5])
                    llist = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)  # заного берем значение текущей свечи, чтобы получить свежий объем
                    # print(float(maxstg['max']['volume']), '<', float(llist[0][5])) объем
                    # rint(llist[0])
                    # print('Время свечи', datetime.fromtimestamp(int(str(llist[0][6])[:-3])))
                    # print('Время сейчас', now)
                    open_red_green = llist
                    if float(tick_red_green['price']) > float(open_red_green[0][1]):
                        # if float(tick_red_green['price']) > float(open_red_green[0][1]) and 200 <= float(llist[0][5]):

                        print('###################################################')
                        print('###################################################')
                        print('#########ПОКУПКА!ПОКУПКА!ПОКУПКА!##################')
                        print('#########ПОКУПКА!ПОКУПКА!ПОКУПКА!##################')
                        print('###################################################')
                        print('###################################################')
                        print('Время покупки (свеча ЭТО ПРеДЫДУЩАЯ):', datetime.fromtimestamp(int(str(llist[0][0])[:-3])))

                        # удаляем все ордера
                        all_order_cancel(maxstg['coin'])
                        # отменяем лимит
                        limit_bool = False

                        print('account_only_free_balance ', account_only_free_balance())

                        COIN_free, USDT_free = get_free_balance('BTC', 'USDT')

                        qtyB = check_coin_QtyBuy(USDT_free, maxstg['coin'], 10)
                        qtyS = check_coin_QtySell(COIN_free, maxstg['coin'], 0)

                        print('COIN_free ', COIN_free, '; USDT_free ', USDT_free, '; Сколько можно купить крипты на usd ', qtyB, '; Сколько usdt в битках ', qtyS)

                        if qtyB > 0.001:  # проверяем есть ли доллары для покуки битка

                            #
                            # покупаем
                            #
                            all_order_cancel(maxstg['coin'])  # отменяем все ордера во избежание проблем

                            stop_price = llist

                            # определяем, если свеча больше 1%, тогда стоп на середину ее тела
                            print('СВЕЧА ВРЕМЕНИ ',datetime.fromtimestamp(int(str(stop_price[0][0])[:-3])),': ', stop_price[0])
                            print('stop_price:', )

                            center = (decimal.Decimal(stop_price[0][2]) - decimal.Decimal(stop_price[0][3]))
                            razniza = (decimal.Decimal(stop_price[0][3]) / 100)
                            # percent = max(center, razniza) / min(center, razniza)
                            percent = center / razniza
                            print('percent:', percent)
                            if percent >= 5:
                                stop_price = abs((decimal.Decimal(stop_price[0][2]) - decimal.Decimal(stop_price[0][3])) / 2) + decimal.Decimal(stop_price[0][3])  # округлить бы
                                print('stop_price > 5 :', stop_price)
                            else:
                                stop_price = decimal.Decimal(stop_price[0][3])
                                print('stop_price < 5:', stop_price)

                            buy_order = buy_or_sell_order_market(maxstg['coin'], 'BUY', qtyB)
                            print('ЦЕНА ВХОДА ПО MARKET ', buy_order['fills'][0]['price'])
                            # print(buy_order)
                            if 'code' in buy_order.keys():
                                if buy_order['code'] == -2010:
                                    print('Покупаем на 2% меньше всего счета')

                                    buy_order = bot.createOrder(
                                        symbol=maxstg['coin'],
                                        recvWindow=5000,
                                        side='BUY',
                                        type='MARKET',
                                        quantity=decimal.Decimal(qtyB).quantize(
                                            decimal.Decimal('.000001'),
                                            rounding=decimal.ROUND_DOWN),
                                        newOrderRespType='FULL'
                                    )
                                    if 'code' in buy_order.keys():
                                        print('Error buy 0, return')
                                        return
                                    else:
                                        llist = account_only_free_balance()
                                        for tag in llist:
                                            if tag['asset'] == 'BTC': COIN_free = tag['free']

                                        stop_loss = sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, stop_price)

                                        # СЮДА ЕСЛИ ОШИБКА СТОП ЛОСА, НУЖНО ВЫХОДИТЬ ИЗ БИТКА!
                                        if 'code' in stop_loss.keys():
                                            if 'trigger immediately' in stop_loss['msg']:
                                                print('Стоп лосс выше, просто продаем по рыночной')

                                                sell_order = buy_or_sell_order_market(maxstg['coin'], 'SELL', COIN_free)

                                                print('sell_order 999 ', sell_order['fills'][0]['price'])

                                                if 'code' in sell_order.keys():
                                                    print('Error sell fff')

                                                print('###################################################')
                                                print('###################################################')
                                                print('#########STOPLOSS99#STOPLOSS99STOPLOSS99##############')

                                                print('###################################################')
                                                print('###################################################')
                                                print('###################################################')

                                                log_1 = [int(coin_ts_open), maxstg['coin'], maxstg['interval'], USDT_free,
                                                         float(buy_order['fills'][0]['price'])]
                                                log_1.append(float(sell_order['fills'][0]['price']))
                                                # освежаем USDT для лог данные
                                                USDT_free = get_free_balance(0, 'USDT')
                                                log_1.append(float(USDT_free))

                                                '''
                                                log_dict = {
                                                    'timestamp': int(coin_ts_open),
                                                    'coin': maxstg['coin'],
                                                    'interval': maxstg['interval'],
                                                    'deposit': USDT_free,
                                                    'enterPrice': float(buy_order['fills'][0]['price']),
                                                    'exitPrice' : float(sell_order['fills'][0]['price']),
                                                    'depositExit' : float(USDT_free),
                                                }
                                                '''
                                                sell_log(log_1,14)
                                                return
                                            print('Error stop loss 0')
                                            return
                                        sleep(10)  # чтобы оказаться в следующей свече, может while и tick?

                                else:
                                    print('Error buy unknown 0')
                                    return
                            else:
                                print('купили по полной цене -1%')
                                tick = bot.tickerPrice(symbol=maxstg['coin'])  # tick для logbug
                                # print(stop_price)
                                # print(datetime.fromtimestamp(stop_price[0]))
                                # qtyS = check_coin_QtySell(BTC_free, maxstg['coin'],stop_price[0][3])

                                # получаем свежий остаток по btc
                                llist = account_only_free_balance()
                                for tag in llist:
                                    if tag['asset'] == 'BTC': COIN_free = tag['free']

                                print('stop price btc:', stop_price, '; qtyS:', qtyS, '; COIN_free:', COIN_free)

                                stop_loss = sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, stop_price)

                                # print('qtyS: ', qtyS)
                                # print('stop_loss: ', stop_loss)

                                if 'code' in stop_loss.keys():
                                    if 'trigger immediately' in stop_loss['msg']:
                                        print('Стоп лосс выше, просто продаем по рыночной')

                                        sell_order = buy_or_sell_order_market(maxstg['coin'], 'SELL', COIN_free)

                                        print('sell_order zxc ', sell_order['fills'][0]['price'])

                                        if 'code' in sell_order.keys():
                                            print('Error sell 555')

                                        tick = bot.tickerPrice(symbol=maxstg['coin'])
                                        print('###################################################')
                                        print('###################################################')
                                        print('#########STOPLOSS6#STOPLOSS6STOPLOSS6##############')
                                        print('###################################################')
                                        print('###################################################')
                                        print('###################################################')
                                        log_1 = [int(coin_ts_open), maxstg['coin'], maxstg['interval'], USDT_free,
                                                 float(buy_order['fills'][0]['price'])]
                                        log_1.append(float(sell_order['fills'][0]['price']))
                                        # освежаем USDT для лог данные
                                        USDT_free = get_free_balance(0, 'USDT')
                                        log_1.append(float(USDT_free))
                                        sell_log(log_1,14)
                                        return
                                    print('Error stop loss 2')
                                    return

                                sleep(10)

                            log_1 = [int(coin_ts_open), maxstg['coin'], maxstg['interval'], USDT_free,
                                     float(buy_order['fills'][0]['price'])]
                            settings.BUY = True
                            break

                        elif qtyS > 10:  # у нас есть биток
                            #
                            # ставим флаг, что куплено, так как биток у нас на счету
                            #
                            print('У нас есть биток, и нет долларов. Ставим только стоп лосс')

                            all_order_cancel(maxstg['coin'])  # отменяем все ордера во избежание проблем

                            blist = account_only_free_balance()
                            for tag in blist:
                                if tag['asset'] == 'BTC':
                                    COIN_free = tag['free']

                            tick = bot.tickerPrice(symbol=maxstg['coin'])  # tick для logbug

                            stop_price = llist

                            # определяем, если свеча больше 1%, тогда стоп на середину ее тела
                            print('stop_price:', stop_price[0])
                            #print('stop_price[0][3]):', stop_price[0][3])
                            #print('stop_price[0][3]) DECIMAL:', decimal.Decimal(stop_price[0][3]))
                            #print('stop_price[0][2]):', stop_price[0][2])
                            #print('stop_price[0][2]) DECIMAL:', decimal.Decimal(stop_price[0][2]))
                            center = (decimal.Decimal(stop_price[0][2]) - decimal.Decimal(stop_price[0][3]))
                            razniza = (decimal.Decimal(stop_price[0][3]) / 100)
                            # percent = max(center, razniza) / min(center, razniza)
                            percent = center / razniza
                            #print('center:', center)
                            #print('razniza:', razniza)
                            #print('percent:', percent)
                            if interval == '4h': p = 4
                            if interval == '1h': p = 3
                            if interval == '5m': p = 1

                            if percent >= p:
                                stop_price = ((decimal.Decimal(stop_price[0][1]) - decimal.Decimal(stop_price[0][4])) / 2) + decimal.Decimal(stop_price[0][1])  # округлить бы
                                print('stop_price > 1 :', stop_price)
                            else:
                                stop_price = decimal.Decimal(stop_price[0][3])
                                print('stop_price < 1:', stop_price)
                            # print(datetime.fromtimestamp(stop_price[0]))
                            # qtyS = check_coin_QtySell(BTC_free, maxstg['coin'],stop_price[0][3])
                            print('stop price usdt:', stop_price, '; qtyS:', qtyS,
                                  '; COIN_free:', COIN_free)

                            stop_loss = bot.createOrder(
                                symbol=maxstg['coin'],
                                recvWindow=5000,
                                side='SELL',
                                type='STOP_LOSS_LIMIT',
                                quantity=decimal.Decimal(float(COIN_free)).quantize(
                                    decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
                                price=decimal.Decimal(stop_price).quantize(
                                    decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
                                stopPrice=decimal.Decimal(stop_price).quantize(
                                    decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
                                timeInForce='GTC'
                            )

                            # print('qtyS: ', qtyS)
                            # print('stop_loss: ', stop_loss)
                            if 'code' in stop_loss.keys():
                                print('Error stop loss 3')
                                print('RETURN!RETURN!RETURN!')
                                return
                            sleep(10)

                            log_1 = [int(coin_ts_open), maxstg['coin'], maxstg['interval'], float(qtyS),
                                     float(tick['price'])]
                            settings.BUY = True
                            break
                        else:
                            print('Нет денег на счету по битку и доллару')

                        print('КАК Я ТУТ ОКАЗАЛСЯ? qtB и qtS по нулю, где-то ошибка')
                        return  # это похоже мертвая функция

                    else:

                        print('Свеча красная или объем не прошел!')
                        if float(tick_red_green['price']) < float(open_red_green[0][1]):

                            # удаляем все ордера для нового limit
                            all_order_cancel(maxstg['coin'])

                            limit_price = decimal.Decimal(open_red_green[0][2]) + 2

                            USDT_free = get_free_balance(0, 'USDT')

                            qtyB = check_coin_QtyBuy_limit(USDT_free, maxstg['coin'], limit_price)

                            print('COIN_free ', COIN_free, '; USDT_free ', USDT_free, '; Сколько можно купить крипты на usd ', qtyB, '; ', limit_price, 'limit_price')

                            print(open_red_green[0])
                            if qtyB > 0.001:  # проверяем есть ли доллары для покуки битка

                                print('###################################################')
                                print('###################################################')
                                print('###############LIMIT!LIMIT!LIMIT!##################')
                                print('###############LIMIT!LIMIT!LIMIT!##################')
                                print('###################################################')
                                print('###################################################')

                                qtyB = decimal.Decimal(qtyB) - ((decimal.Decimal(qtyB) / 100) * 1)

                                limit = bot.createOrder(
                                    symbol=maxstg['coin'],
                                    recvWindow=5000,
                                    side='BUY',
                                    type='STOP_LOSS_LIMIT',
                                    quantity=decimal.Decimal(qtyB).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
                                    # это количество которе округляем в меньшую
                                    price=limit_price,  # это цена бай
                                    stopPrice=limit_price,
                                    timeInForce='GTC'
                                )

                                limit_bool = True
                                limit_stop_price = open_red_green[0][3]
                                limit_qty = decimal.Decimal(qtyB).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN)

                                log_1 = [int(str(now.timestamp()).split('.')[0]), maxstg['coin'], maxstg['interval'], USDT_free, float(limit_price)]
                                print('limit:', limit)
                                # {'orderId': 1630544816,'price': '6635.19000000', 'origQty': '0.00395000', 'cummulativeQuoteQty': '26.12692877', 'status': 'FILLED',




                        sleep(5)
                        break

'''
MARGIN стратегия стоплосс - новая
'''
def start_trade_stg_only_stop_loss_margin(interval):
    maxstg = {}
    maxstg['coin'] = 'BTCUSDT'
    maxstg['interval'] = interval
    if interval == '4h': minutdelta = 240
    if interval == '1h': minutdelta = 60
    if interval == '5m': minutdelta = 5


    margin_all_order_cancel(maxstg['coin'])

    # берем маржу максимальную
    amount_loan = bot.marginMaxBorrowable(asset='BTC', recvWindow=recvGlobal)
    #print('marginMaxBorrowable ', amount_loan['amount'])

    if decimal.Decimal(amount_loan['amount']) > 0:
        print('TRY LOAN', bot.marginLoan(asset='BTC', amount=amount_loan['amount'], recvWindow=recvGlobal))

    if not check_money_balance('margin'): return # если нет денег выходим


    account_balance = margin_account_only_free_balance()
    #print('account_only_free_balance: ', account_balance)

    settings.BUY = False
    limit_bool = False

    while True:

        # освежаем USDT и COIN
        COIN_free, USDT_free = margin_get_free_balance('BTC', 'USDT')

        if limit_bool:
            if not margin_check_stop_loss_limit_buy_order(maxstg['coin']):
                # ставим стоп под low

                print('###################################################')
                print('#########FFFFFFF LIMIT MARGIN BUY BUY LIMIT BUY BUY BUY MARGIN########')
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                print('TIME ', now)
                print(' цена входа ', log_1[4])
                print('stop buy сработал, ставим стоп на хай свечу входа')
                print('###################################################')
                print('###################################################')

                USDT_free = margin_get_free_balance(0, 'USDT')
                USDT_locked = margin_get_free_balance('locked','USDT')
                print('USDT_locked', USDT_locked)
                print('USDT_free', USDT_free)
                stop_price = data_before_cendel('high')
                qtyB = check_coin_QtyBuy_limit(USDT_free, maxstg['coin'], stop_price)
                print('COIN_free ', COIN_free, '; USDT_free ', USDT_free, '; Сколько можно купить крипты на usd qtyB ', qtyB, '; Сколько usdt в битках ', qtyS)

                stop_loss = margin_sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'BUY', qtyB, stop_price)
                print('stop_loss ', stop_loss)
                if 'code' in stop_loss.keys():
                    print('stop buy err fff')
                    return
                limit_bool = False
                settings.BUY = True

        # биток куплен, ставим стопы и ждем вылета
        if settings.BUY:

            stop_timer = False
            before_cendel = False  # bool для проверки, что появилась следующая свеча
            settings.EXIT_MARGIN = False

            while True:
                # проверяем нет ли принудительного выхода
                if settings.EXIT_MARGIN:
                    # освежаем USDT и COIN

                    margin_all_order_cancel(maxstg['coin'])

                    # освежаем USDT и COIN

                    USDT_free = margin_get_free_balance(0, 'USDT')
                    print('USDT_free', USDT_free)

                    qtyB = check_coin_QtyBuy(USDT_free, maxstg['coin'], 10)
                    sell_order = margin_buy_or_sell_order_market(maxstg['coin'], 'BUY', qtyB)

                    print('sell_order  EXIT_SIMPLE', sell_order['fills'][0]['price'])

                    if 'code' in sell_order.keys():
                        print('Error sell market EXIT_SIMPLE')

                    print('###################################################')
                    print('#########ПРИНУДИТЕЛЬНЫЙ ВЫХОД######################')
                    print('#########ПРИНУДИТЕЛЬНЫЙ ВЫХОД######################')
                    print('###################################################')
                    log_1.append(float(sell_order['fills'][0]['price']))
                    # освежаем USDT для лог данные
                    COIN_free = margin_get_free_balance('BTC', 0)
                    log_1.append(float(COIN_free))
                    sell_log(log_1, 13)
                    settings.EXIT_MARGIN = False
                    return


                # проверяем не сработал ли стоп
                if not margin_check_stop_loss_sell_order(maxstg['coin']):
                    print('###################################################')
                    print('#########STOPLOSS1#STOPLOSS1STOPLOSS1##############')
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                    print(now)
                    print(str(stop_price))
                    print('###################################################')
                    print('###################################################')

                    log_1.append(float(stop_price))
                    log_1.append(float(margin_get_free_balance('BTC', 0)))
                    sell_log(log_1,13)
                    return

                # ставим стоп на вход, если цена резко взлетела на 0.5 и выше процента,  потом резко упала
                # находим раазницу в движении, если она больше 0.5 проента
                # используем first pump stop, для защиты от резких скачков и падений
                tick = bot.tickerPrice(symbol=maxstg['coin'])
                f1 = abs(decimal.Decimal(log_1[4]) - decimal.Decimal(tick['price']))
                f2 = (decimal.Decimal(log_1[4]) / 100) * decimal.Decimal(0.5)
                if f1 > f2 and not first_pump_stop:
                    print('MARGIN ЦЕНА ПАДЕНИЯ НА 0.5 ПРОЦЕНТ!!!!!!')
                    print('Разница в цене: ', str(f1))
                    print('0.5 процент от цены входа: ', str(f2))
                    print('ставим стоп на цену входа: ', str(log_1[4]))
                    margin_all_order_cancel(maxstg['coin'])
                    first_pump_stop = True

                    # освежаем USDT и COIN
                    USDT_free = margin_get_free_balance(0, 'USDT')
                    print('USDT_free', USDT_free)
                    qtyB = check_coin_QtyBuy_limit(USDT_free, maxstg['coin'], log_1[4])

                    stop_loss = margin_sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'BUY', qtyB, log_1[4])

                    if 'code' in stop_loss.keys():

                        if 'trigger immediately' in stop_loss['msg']:

                            print('Стоп лосс выше, просто продаем по рыночной 098')
                            qtyB = check_coin_QtyBuy(USDT_free, maxstg['coin'], 10)

                            sell_order = margin_buy_or_sell_order_market(maxstg['coin'], 'BUY', qtyB)

                            print('sell_order 333 ', sell_order['fills'][0]['price'])

                            if 'code' in sell_order.keys():
                                print('Error sell market 1')

                            print('###################################################')
                            print('#########STOPLOSS3#STOPLOSS3STOPLOSS3##############')
                            print('###################################################')
                            print('###################################################')
                            log_1.append(float(sell_order['fills'][0]['price']))
                            # освежаем USDT для лог данные
                            COIN_free = margin_get_free_balance('BTC', 0)
                            log_1.append(float(COIN_free))
                            sell_log(log_1, 13)
                            return

                        print('Error stop loss 4 low')
                        settings.BUY = False
                        return

                    # сохраняем значение последнего стопа для лога и статистики
                    print('stop loss status:', stop_loss)
                    stop_price = llist_before[0][3]


                if not before_cendel:
                    print('###############')
                    print('###############')
                    print('wait cendel')
                    llist_before = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)
                    now_before = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    now_before = datetime.strptime(now_before, '%Y-%m-%d %H:%M:%S')
                    before_cendel = True
                    llist_now = llist_before
                else:
                    llist_now = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)
                    now_after = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    now_after = datetime.strptime(now_after, '%Y-%m-%d %H:%M:%S')
                    #print('now:', now_after)
                    #print('before', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])))
                    #print('time minus:', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])) + timedelta(minutes=5))
                    #print(str(((datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])) + timedelta(minutes=5)) - now_after).total_seconds())[:-2])

                    #if int(str((close_cendel - now).total_seconds())[:-2]) < 6 and int(str((close_cendel - now).total_seconds())[:-2]) > 0:


                    if int(str((datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])) + timedelta(minutes=minutdelta) - now_after).total_seconds())[:-2]) <= 10 and int(str((datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])) + timedelta(minutes=minutdelta) - now_after).total_seconds())[:-2]) > 1:
                        llist_before = llist_now # мы это делаем, чтобы свеча предпоследняя была свежая


                    # if int(str((datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])) + timedelta(5) - now_before).total_seconds())[:-2]) >= 7:  # если больше 5 сек до конца свечи, тогда ок
                    #    sleep(5)
                    # else:
                    #    sleep(int(str((datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])) + timedelta(5) - now_before).total_seconds())[:-2])+5)

                # print('before ', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])), '; now: ', datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])))
                if int(str(llist_before[0][0])[:-3]) != int(str(llist_now[0][0])[:-3]):
                    print('###############')
                    print('###############')
                    print('before', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])))
                    print('before NOW', now_before)
                    print('before TS', str(llist_before[0][0]))
                    print('after', datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])))
                    print('after NOW', now_after)
                    print('after TS', str(llist_now[0][0]))
                    print('###############')
                    print('###############')
                    print('След свеча')
                    print('###############')
                    print('###############')
                    print('before ', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])), '; now: ', datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])))
                    print('before close time', datetime.fromtimestamp(int(str(llist_before[0][6])[:-3])))
                    if not stop_timer:
                        print('NEW FIRST STOP! Ставим новый стоп на хай свечи входа zzz')
                        before_cendel = False


                        margin_all_order_cancel(maxstg['coin'])

                        # какой процент сделала пердыдущая свеча
                        print('llist_before ',llist_before)

                        print('before start', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])))
                        print('before end', datetime.fromtimestamp(int(str(llist_before[0][6])[:-3])))
                        openclose = decimal.Decimal(abs(float(llist_before[0][1]) - float(llist_before[0][4])))
                        allcendel = decimal.Decimal(float(llist_before[0][2]) - float(llist_before[0][3]))
                        amplituda = openclose / allcendel

                        print('openclose:', openclose)
                        print('allcendel:', allcendel)
                        print('amplituda:', amplituda)



                        # ставим стоп под low

                        # освежаем USDT и COIN
                        USDT_free = margin_get_free_balance(0, 'USDT')
                        print('USDT_free', USDT_free)

                        qtyB = check_coin_QtyBuy_limit(USDT_free, maxstg['coin'], llist_before[0][2])


                        stop_loss_open = llist_before[0][2]  # сохраняем значение первого стопа, чтобы не поставить ниже него на следующей свече
                        stop_loss = margin_sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'BUY', qtyB, llist_before[0][2])

                        if 'code' in stop_loss.keys():

                            if 'trigger immediately' in stop_loss['msg']:

                                print('Стоп лосс выше, просто продаем по рыночной 555')
                                qtyB = check_coin_QtyBuy(USDT_free, maxstg['coin'], 10)


                                sell_order = margin_buy_or_sell_order_market(maxstg['coin'], 'BUY', qtyB)

                                print('sell_order 333 ', sell_order['fills'][0]['price'])

                                if 'code' in sell_order.keys():
                                    print('Error sell market 1')

                                print('###################################################')
                                print('#########STOPLOSS3#STOPLOSS3STOPLOSS3##############')
                                print('###################################################')
                                print('###################################################')
                                log_1.append(float(sell_order['fills'][0]['price']))
                                # освежаем USDT для лог данные
                                COIN_free = margin_get_free_balance('BTC', 0)
                                log_1.append(float(COIN_free))
                                sell_log(log_1,13)
                                return

                            print('Error stop loss 4 low')
                            return

                        # сохраняем значение последнего стопа для лога и статистики
                        print('stop loss status:', stop_loss)
                        stop_price = llist_before[0][2]


                    if stop_timer and float(stop_loss_open) > float(llist_before[0][2]):
                        before_cendel = False
                        print('NEW STOP! Ставим новый стоп под предыдущую свечу, но не ниже open xxx')
                        print('llist_before ', llist_before[0])
                        print('llist_before data ', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])))
                        margin_all_order_cancel(maxstg['coin'])
                        print('time before stop', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])), '; stop price:', llist_before[0][2], '; USDT_free:', USDT_free)

                        USDT_free = margin_get_free_balance(0, 'USDT')
                        print('USDT_free', USDT_free)
                        qtyB = check_coin_QtyBuy_limit(USDT_free, maxstg['coin'], llist_before[0][2])

                        stop_loss = margin_sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'BUY', qtyB , llist_before[0][2])

                        if 'code' in stop_loss.keys():

                            if 'trigger immediately' in stop_loss['msg']:
                                print('Стоп лосс выше, просто продаем по рыночной')
                                USDT_free = margin_get_free_balance(0, 'USDT')
                                qtyB = check_coin_QtyBuy(USDT_free, maxstg['coin'], 10)
                                sell_order = margin_buy_or_sell_order_market(maxstg['coin'], 'BUY', qtyB)

                                print('sell_order 666 ', sell_order['fills'][0]['price'])

                                if 'code' in sell_order.keys():
                                    print('Error sell 987')

                                print('###################################################')
                                print('###################################################')
                                print('#########STOPLOSS6#STOPLOSS6STOPLOSS6##############')
                                print('###################################################')
                                print('###################################################')
                                print('###################################################')
                                log_1.append(float(sell_order['fills'][0]['price']))
                                # освежаем USDT для лог данные
                                COIN_free = margin_get_free_balance('BTC', 0)
                                log_1.append(float(COIN_free))
                                sell_log(log_1,13)
                                return

                            print('Error stop loss 3 next')
                            return

                        # сохраняем значение последнего стопа для лога и статистики
                        print('stop loss status:', stop_loss)
                        stop_price = llist_before[0][2]
                    # чекаем по 10 сек, потом сравниваем
                    stop_timer = True

        print('### Ищем паттерн на вход ###')
        # биток не куплен, ждем свечу на вход
        llist = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)
        # print(llist)

        for cendel in llist:
            coin_ts_open = int(str(cendel[0])[:-3])
            coin_ts_close = int(str(cendel[6])[:-3])
            # print('ts open: ', str(datetime.fromtimestamp(coin_ts_open).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0])
            # print('ts close: ', str(datetime.fromtimestamp(coin_ts_close).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0])

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
        close_cendel = datetime.fromtimestamp(coin_ts_close)  # strftime('%Y-%m-%d %H:%M:%S')

        # print(type(now), ' - ',now)
        # print(type(close_cendel), ' - ', end_cendel)
        # print(int(str((end_cendel - now).total_seconds())[:-2]))


        if now < close_cendel and int(str((close_cendel - now).total_seconds())[:-2]) > 10:  # если больше 10 сек до конца свечи, тогда ок

            while True:

                # проверяем нет ли покупки по лимит
                if limit_bool:
                    if not margin_check_stop_loss_limit_buy_order(maxstg['coin']):

                        print('check_stop_loss_limit_buy_order ', margin_check_stop_loss_limit_buy_order(maxstg['coin']))
                        print('###################################################')
                        print('#########LIMIT BUY BUY BUYLIMIT BUY BUY BUY########')
                        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                        print('TIME ', now)
                        print(' цена входа ', log_1[4])
                        print('stop buy сработал, ставим стоп под свечу входа')
                        print('###################################################')
                        print('###################################################')

                        USDT_free = margin_get_free_balance(0, 'USDT')
                        USDT_locked = margin_get_free_balance('locked', 'USDT')
                        print('USDT_locked', USDT_locked)
                        print('USDT_free', USDT_free)
                        stop_price = data_before_cendel('high')
                        qtyB = check_coin_QtyBuy_limit(USDT_free, maxstg['coin'], stop_price)
                        print('COIN_free ', COIN_free, '; USDT_free ', USDT_free, '; Сколько можно купить крипты на usd qtyB ', qtyB, '; Сколько usdt в битках ', qtyS)

                        stop_loss = margin_sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'BUY', qtyB, stop_price)

                        print('stop_loss ', stop_loss)
                        if 'code' in stop_loss.keys():
                            print('stop buy err fff')
                            return

                        limit_bool = False
                        settings.BUY = True
                        break

                sleep(3)
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                # print(end_cendel - now)
                if int(str((close_cendel - now).total_seconds())[:-2]) < 6 and int(str((close_cendel - now).total_seconds())[:-2]) > 0:

                    if settings.FLAT:

                        # удаляем все ордера для нового limit
                        margin_all_order_cancel(maxstg['coin'])
                        print(settings.FLAT_LOW)
                        limit_price = decimal.Decimal(settings.FLAT_LOW) - 2

                        USDT_free = margin_get_free_balance(0, 'USDT')
                        qtyB = check_coin_QtyBuy(USDT_free, maxstg['coin'], 10)

                        if float(USDT_free) > 11:
                            sell_order = margin_buy_or_sell_order_market(maxstg['coin'], 'BUY', qtyB)
                            print('sell_order main', sell_order)
                            if 'code' in sell_order.keys():
                                print('Error sell market 1')
                                sleep(5)
                                return

                        COIN_free = margin_get_free_balance('BTC', 0)

                        qtyS = check_coin_QtySell(COIN_free, maxstg['coin'], limit_price)
                        print('COIN_free ', COIN_free, '; Сколько usdt в битках ', qtyS, '; limit_price ', limit_price)

                        if float(COIN_free) > 0.0016:  # проверяем есть ли для покуки доллара

                            print('###################################################')
                            print('###############FLAT FLAT FLAT!!####################')
                            print('###############LIMIT!LIMIT!LIMIT!##################')
                            print('###############LIMIT!LIMIT!LIMIT!##################')
                            print('################fffffffffffffff####################')
                            print('###################################################')

                            limit = margin_sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, limit_price)

                            limit_bool = True
                            limit_stop_price = llist[0][3]
                            limit_qty = decimal.Decimal(qtyS).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN)

                            log_1 = [int(str(now.timestamp()).split('.')[0]), maxstg['coin'], maxstg['interval'], COIN_free, float(limit_price)]
                            print('limit flat:', limit)
                        print('Боковик, cтавим только limit low ', limit_price)
                        sleep(5)
                        break

                    tick_red_green = bot.tickerPrice(symbol=maxstg['coin'])
                    # print('проверяем свечу, если зеленая, тогда ставим флаг для покупки следующей постратгеии')
                    # print(tick['price'], ' > ', llist[0][1])
                    # print(maxstg['max']['volume'], '<=', llist[0][5])
                    llist = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)  # заного берем значение текущей свечи, чтобы получить свежий объем
                    # print(float(maxstg['max']['volume']), '<', float(llist[0][5])) объем
                    # rint(llist[0])
                    # print('Время свечи', datetime.fromtimestamp(int(str(llist[0][6])[:-3])))
                    # print('Время сейчас', now)
                    open_red_green = llist
                    if float(tick_red_green['price']) < float(open_red_green[0][1]):
                        # if float(tick_red_green['price']) > float(open_red_green[0][1]) and 200 <= float(llist[0][5]):

                        print('###################################################')
                        print('########MARGINMARGINMARGINMARGIN###################')
                        print('#########ПОКУПКА!ПОКУПКА!ПОКУПКА!##################')
                        print('#########SHORTSHORTSHORTSHORT!!!!##################')
                        print('###################################################')
                        print('###################################################')
                        print('Время покупки (ЭТО ВРЕМЯ ПРЕДЫДУЩЕЙ СВЕЧИ, цена входа след.):', datetime.fromtimestamp(int(str(llist[0][0])[:-3])))

                        # удаляем все ордера
                        margin_all_order_cancel(maxstg['coin'])
                        # отменяем лимит
                        limit_bool = False

                        USDT_free = margin_get_free_balance(0, 'USDT')
                        qtyB = check_coin_QtyBuy(USDT_free, maxstg['coin'], 10)

                        if float(USDT_free) > 11:
                            sell_order = margin_buy_or_sell_order_market(maxstg['coin'], 'BUY', qtyB)
                            print('sell_order main', sell_order)
                            if 'code' in sell_order.keys():
                                print('Error sell market 1')
                                sleep(5)
                                return

                        qtyS = check_coin_QtySell(COIN_free, maxstg['coin'], 0)

                        print('COIN_free ', COIN_free, '; USDT_free ', USDT_free, '; Сколько можно купить крипты на usd qtyB ', qtyB, '; Сколько usdt в битках ', qtyS)
                        COIN_free = margin_get_free_balance('BTC', 0)
                        if float(COIN_free) > 0.0016:
                            #
                            # покупаем
                            #
                            stop_price = llist

                            # определяем, если свеча больше 1%, тогда стоп на середину ее тела
                            print('СВЕЧА ВРЕМЕНИ ', datetime.fromtimestamp(int(str(stop_price[0][0])[:-3])), ': ', stop_price[0])

                            center = (decimal.Decimal(stop_price[0][2]) - decimal.Decimal(stop_price[0][3]))
                            razniza = (decimal.Decimal(stop_price[0][3]) / 100)
                            # percent = max(center, razniza) / min(center, razniza)
                            percent = center / razniza
                            print('percent:', percent)
                            if interval == '4h': p = 5
                            if interval == '1h': p = 3
                            if interval == '5m': p = 1
                            if percent >= p:
                                stop_price = abs((decimal.Decimal(stop_price[0][2]) - decimal.Decimal(stop_price[0][3])) / 2) + decimal.Decimal(stop_price[0][3])  # округлить бы
                                print('stop_price > 5 :', stop_price)
                            else:
                                stop_price = decimal.Decimal(stop_price[0][2])
                                print('stop_price < 5:', stop_price)


                            buy_order = margin_buy_or_sell_order_market(maxstg['coin'], 'SELL', COIN_free)

                            print('ЦЕНА ВХОДА ПО MARKET ', buy_order['fills'][0]['price'])
                            # print(buy_order)

                            if 'code' in buy_order.keys():
                                print('Error buy unknown 0')
                                return
                            else:
                                print('купили по полной цене -1%')

                                # получаем свежий остаток по btc

                                USDT_free = margin_get_free_balance(0, 'USDT')
                                print('USDT_free', USDT_free)
                                qtyB = check_coin_QtyBuy_limit(USDT_free, maxstg['coin'], stop_price)

                                print('stop price btc:', stop_price, '; qtyB:', qtyB, '; USDT_free:', USDT_free)


                                stop_loss =  margin_sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'BUY', qtyB, stop_price)

                                if 'code' in stop_loss.keys():
                                    if 'trigger immediately' in stop_loss['msg']:
                                        print('Стоп лосс выше, просто продаем по рыночной')

                                        USDT_free = margin_get_free_balance(0, 'USDT')
                                        qtyB = check_coin_QtyBuy(USDT_free, maxstg['coin'], 10)

                                        sell_order = margin_buy_or_sell_order_market(maxstg['coin'], 'BUY', qtyB)

                                        print('sell_order zxc ', sell_order['fills'][0]['price'])

                                        if 'code' in sell_order.keys():
                                            print('Error sell 555')

                                        print('###################################################')
                                        print('###################################################')
                                        print('#########STOPLOSS6#STOPLOSS6STOPLOSS6##############')
                                        print('###################################################')
                                        print('###################################################')
                                        print('###################################################')
                                        log_1 = [int(coin_ts_open), maxstg['coin'], maxstg['interval'], COIN_free,
                                                 float(buy_order['fills'][0]['price'])]
                                        log_1.append(float(sell_order['fills'][0]['price']))
                                        # освежаем USDT для лог данные
                                        COIN_free = margin_get_free_balance('BTC', 0)
                                        log_1.append(float(COIN_free))
                                        sell_log(log_1,13)
                                        return
                                    print('Error stop loss 2')
                                    return

                                sleep(10)

                            log_1 = [int(coin_ts_open), maxstg['coin'], maxstg['interval'], COIN_free,
                                     float(buy_order['fills'][0]['price'])]
                            settings.BUY = True
                            break

                    else:
                        # иначе получается свеча зеленая
                        print('Свеча зеленая!')

                        # удаляем все ордера для нового limit
                        margin_all_order_cancel(maxstg['coin'])

                        limit_price = decimal.Decimal(open_red_green[0][3]) - 2

                        USDT_free = margin_get_free_balance(0, 'USDT')
                        qtyB = check_coin_QtyBuy(USDT_free, maxstg['coin'], 10)

                        if float(USDT_free) > 11:
                            sell_order = margin_buy_or_sell_order_market(maxstg['coin'], 'BUY', qtyB)
                            print('sell_order main', sell_order)
                            if 'code' in sell_order.keys():
                                print('Error sell market vvv')
                                sleep(5)
                                return

                        COIN_free = margin_get_free_balance('BTC', 0)

                        qtyS = check_coin_QtySell(COIN_free, maxstg['coin'], limit_price)
                        print('COIN_free ', COIN_free,'; Сколько usdt в битках ', qtyS, '; limit_price ', limit_price)


                        if float(COIN_free) > 0.0016:  # проверяем есть ли для покуки доллара


                            print('###################################################')
                            print('###################################################')
                            print('###############LIMIT!LIMIT!LIMIT!##################')
                            print('###############LIMIT!LIMIT!LIMIT!##################')
                            print('###################################################')
                            print('###################################################')



                            limit = margin_sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, limit_price)

                            limit_bool = True
                            limit_qty = decimal.Decimal(qtyS).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN)

                            log_1 = [int(str(now.timestamp()).split('.')[0]), maxstg['coin'], maxstg['interval'], COIN_free, float(limit_price)]
                            print('limit:', limit)
                            # {'orderId': 1630544816,'price': '6635.19000000', 'origQty': '0.00395000', 'cummulativeQuoteQty': '26.12692877', 'status': 'FILLED',

                        sleep(5)
                        break


def start_margin_trade_stg_only_stop_loss():
    maxstg = {}

    if not settings.BESTSTG:
        print('сратеги нет, ждем')
        sleep(10)
        return
    else:
        for key, val in settings.BESTSTG.items():
            maxstg = val  # тут надо выбрать лучшую стратегию, от BTC до ETH (в данный момент только одна стратегию через цикл)
        print(maxstg)
        if maxstg['max'] is None or maxstg['max']['price'] < 100000:  # !!! потом убрать, поставить return и sleep, для поиска след стратгеии
            # maxstg['max'] = {}
            # maxstg['max']['day'] = 2
            # maxstg['max']['volume'] = 200
            print('сратегия есть, но она не прибыльная')
            print(maxstg['coin'][0:3])
            # return

    margin_all_order_cancel(maxstg['coin'])  # убираем все ордеры

    COIN_free, USDT_free = margin_get_free_balance('BTC', 'USDT')

    if float(COIN_free) < 0.002 and float(USDT_free) < 11:
        print('COIN и USDT не достаточно для торговли, sleep+return')
        print('COIN_free ', COIN_free, '; USDT_free ', USDT_free)

        sleep(60)
        return

    print('account_only_free_balance: ', margin_account_only_free_balance())

    kypil = False
    limit_bool = False

    while True:

        # освежаем USDT и COIN
        COIN_free, USDT_free = margin_get_free_balance('BTC', 'USDT')

        if limit_bool:
            if not margin_check_stop_loss_limit_buy_order(maxstg['coin']):
                # ставим стоп под low

                print('###################################################')
                print('#########FFFFFFF LIMIT BUY BUY BUYLIMIT BUY BUY BUY########')
                print('COIN_free ', COIN_free, '; USDT_free ', USDT_free)
                print('limit_qty ', limit_qty, '; limit_stop_price ', limit_stop_price)
                print('stop buy сработал, ставим стоп под свечу входа')
                print('###################################################')
                print('###################################################')
                print('openOrder ', bot.marginOpenOrders(symbol=maxstg['coin']))

                COIN_free = margin_get_free_balance('BTC', 0)
                COIN_locked = margin_get_free_balance('BTC', 'locked')
                print('COIN_locked', COIN_locked)
                print('COIN_free', COIN_free)
                stop_loss = margin_sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, limit_stop_price)
                print('stop_loss ', stop_loss)
                if 'code' in stop_loss.keys():
                    print('stop buy err fff')
                    return
                limit_bool = False
                kypil = True

        # биток куплен, ставим стопы и ждем вылета
        if kypil:

            stop_timer = False
            before_cendel = False  # bool для проверки, что появилась следующая свеча

            while True:
                # проверяем не сработал ли стоп

                if not margin_check_stop_loss_sell_order(maxstg['coin']):
                    print('###################################################')
                    print('#########STOPLOSS1#STOPLOSS1STOPLOSS1##############')
                    print(str(stop_price))
                    print('###################################################')
                    print('###################################################')

                    log_1.append(float(stop_price))
                    log_1.append(float(get_free_balance(0, 'USDT')))
                    sell_log(log_1)
                    return

                if not before_cendel:
                    print('###############')
                    print('###############')
                    print('wait cendel')
                    llist_before = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)
                    now_before = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    now_before = datetime.strptime(now_before, '%Y-%m-%d %H:%M:%S')
                    before_cendel = True
                    llist_now = llist_before
                else:
                    llist_now = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)
                    now_after = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    now_after = datetime.strptime(now_after, '%Y-%m-%d %H:%M:%S')

                    # if int(str((datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])) + timedelta(5) - now_before).total_seconds())[:-2]) >= 7:  # если больше 5 сек до конца свечи, тогда ок
                    #    sleep(5)
                    # else:
                    #    sleep(int(str((datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])) + timedelta(5) - now_before).total_seconds())[:-2])+5)

                # print('before ', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])), '; now: ', datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])))
                if int(str(llist_before[0][0])[:-3]) != int(str(llist_now[0][0])[:-3]):
                    print('before', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])))
                    print('before NOW', now_before)
                    print('before TS', str(llist_before[0][0]))
                    print('after', datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])))
                    print('after NOW', now_after)
                    print('after TS', str(llist_now[0][0]))
                    print('###############')
                    print('###############')
                    print('След свеча')
                    print('before ', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])), '; now: ', datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])))
                    print('###############')
                    print('###############')
                    if not stop_timer:
                        print('NEW FIRST STOP! Ставим новый стоп на свечу входа zzz')
                        before_cendel = False

                        margin_all_order_cancel(maxstg['coin'])

                        # какой процент сделала пердыдущая свеча
                        print(llist_before)
                        openclose = decimal.Decimal(abs(float(llist_before[0][1]) - float(llist_before[0][4])))

                        allcendel = decimal.Decimal(float(llist_before[0][2]) - float(llist_before[0][3]))
                        amplituda = float(llist_before[0][3]) / allcendel
                        amplituda = decimal.Decimal(amplituda).quantize(decimal.Decimal('.00001'), rounding=decimal.ROUND_DOWN)

                        print('openclose:', openclose)
                        print('allcendel:', allcendel)
                        print('amplituda:', amplituda)

                        # сохраняем значение первого стопа, чтобы не поставить ниже него на следующей свече
                        stop_loss_open = llist_before[0][4]

                        if amplituda <= 0.0030:

                            # ставим стоп под low

                            # освежаем USDT и COIN
                            COIN_free, USDT_free = margin_get_free_balance('BTC', 'USDT')
                            COIN_locked = margin_get_free_balance('BTC', 'locked')
                            print('COIN_locked', COIN_locked)
                            print('COIN_free', COIN_free)
                            qtyS = check_coin_QtySell(COIN_free, maxstg['coin'], llist_before[0][3])
                            stop_loss = margin_sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'BUY', qtyS, llist_before[0][3])

                            if 'code' in stop_loss.keys():

                                if 'trigger immediately' in stop_loss['msg']:
                                    print('Стоп лосс выше, просто продаем по рыночной')

                                    sell_order = margin_buy_or_sell_order_market(maxstg['coin'], 'BUY', COIN_free)

                                    print('sell_order 333 ', sell_order['fills'][0]['price'])

                                    if 'code' in sell_order.keys():
                                        print('Error sell market 1')

                                    print('###################################################')
                                    print('#########STOPLOSS3#STOPLOSS3STOPLOSS3##############')
                                    print('###################################################')
                                    print('###################################################')
                                    log_1.append(float(sell_order['fills'][0]['price']))
                                    # освежаем USDT для лог данные
                                    USDT_free = margin_get_free_balance(0, 'USDT')
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

                            # освежаем USDT и COIN
                            COIN_free, USDT_free = margin_get_free_balance('BTC', 'USDT')

                            COIN_locked = margin_get_free_balance('BTC', 'locked')
                            print('COIN_locked', COIN_locked)
                            print('COIN_free', COIN_free)

                            # ставим стоп под open
                            stop_loss = margin_sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, llist_before[0][1])

                            if 'code' in stop_loss.keys():

                                if 'trigger immediately' in stop_loss['msg']:
                                    print('Стоп лосс выше, просто продаем по рыночной')

                                    sell_order = margin_buy_or_sell_order_market(maxstg['coin'], 'SELL', COIN_free)

                                    print('sell_order vvv ', sell_order['fills'][0]['price'])

                                    if 'code' in sell_order.keys():
                                        print('Error sell zzz123')

                                    print('###################################################')
                                    print('###################################################')
                                    print('#########STOPLOSS5#STOPLOSS5STOPLOSS5##############')
                                    print('###################################################')
                                    print('###################################################')
                                    print('###################################################')
                                    log_1.append(float(sell_order['fills'][0]['price']))

                                    # освежаем USDT для лог данные
                                    USDT_free = margin_get_free_balance(0, 'USDT')
                                    log_1.append(float(USDT_free))
                                    sell_log(log_1)
                                    kypil = False
                                    return

                                print('Error stop loss 3 next')
                                return
                            stop_price = llist_before[0][1]

                    if stop_timer and stop_loss_open < llist_next_stop[0][3]:
                        before_cendel = False
                        print('NEW STOP! Ставим новый стоп под предыдущую свечу, но не ниже open xxx')
                        print('llist_next_stop ', llist_next_stop[0])
                        print('llist_next_stop data ', datetime.fromtimestamp(int(str(llist_next_stop[0][0])[:-3])))
                        margin_all_order_cancel(maxstg['coin'])
                        print('time before stop', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])), '; stop price:', llist_next_stop[0][3], '; COIN_free:', COIN_free)

                        stop_loss = margin_sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, llist_next_stop[0][3])

                        if 'code' in stop_loss.keys():

                            if 'trigger immediately' in stop_loss['msg']:
                                print('Стоп лосс выше, просто продаем по рыночной')

                                sell_order = margin_buy_or_sell_order_market(maxstg['coin'], 'SELL', COIN_free)

                                print('sell_order 666 ', sell_order['fills'][0]['price'])

                                if 'code' in sell_order.keys():
                                    print('Error sell 987')

                                tick = bot.tickerPrice(symbol=maxstg['coin'])
                                print('###################################################')
                                print('###################################################')
                                print('#########STOPLOSS6#STOPLOSS6STOPLOSS6##############')
                                print('###################################################')
                                print('###################################################')
                                print('###################################################')
                                log_1.append(float(sell_order['fills'][0]['price']))
                                # освежаем USDT для лог данные
                                USDT_free = margin_get_free_balance(0, 'USDT')
                                log_1.append(float(USDT_free))
                                sell_log(log_1)
                                kypil = False
                                return

                            print('Error stop loss 3 next')
                            return

                        # сохраняем значение последнего стопа для лога и статистики
                        print('stop loss status:', stop_loss)
                        stop_price = llist_next_stop[0][3]
                    # чекаем по 10 сек, потом сравниваем
                    llist_next_stop = llist_before
                    stop_timer = True

        print('### Ищем паттерн на вход ###')
        # биток не куплен, ждем свечу на вход
        llist = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)
        # print(llist)

        for cendel in llist:
            coin_ts_open = int(str(cendel[0])[:-3])
            coin_ts_close = int(str(cendel[6])[:-3])
            # print('ts open: ', str(datetime.fromtimestamp(coin_ts_open).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0])
            # print('ts close: ', str(datetime.fromtimestamp(coin_ts_close).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0])

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
        close_cendel = datetime.fromtimestamp(coin_ts_close)  # strftime('%Y-%m-%d %H:%M:%S')

        # print(type(now), ' - ',now)
        # print(type(close_cendel), ' - ', end_cendel)
        # print(int(str((end_cendel - now).total_seconds())[:-2]))


        if now < close_cendel and int(str((close_cendel - now).total_seconds())[:-2]) > 10:  # если больше 10 сек до конца свечи, тогда ок

            while True:

                # проверяем нет ли покупки по лимит
                if limit_bool:
                    if not margin_check_stop_loss_limit_buy_order(maxstg['coin']):

                        print('check_stop_loss_limit_buy_order ', margin_check_stop_loss_limit_buy_order(maxstg['coin']))
                        print('###################################################')
                        print('#########LIMIT BUY BUY BUYLIMIT BUY BUY BUY########')
                        print('COIN_free ', COIN_free, '; USDT_free ', USDT_free)
                        print('limit_qty ', limit_qty, '; limit_stop_price ', limit_stop_price)
                        print('stop buy сработал, ставим стоп под свечу входа')
                        print('###################################################')
                        print('###################################################')
                        print('openOrder ', bot.marginOpenOrders(symbol=maxstg['coin']))

                        COIN_free = margin_get_free_balance('BTC', 0)
                        COIN_locked = margin_get_free_balance('BTC', 'locked')
                        print('COIN_locked', COIN_locked)
                        print('COIN_free', COIN_free)

                        stop_loss = margin_sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, limit_stop_price)
                        print('stop_loss ', stop_loss)
                        if 'code' in stop_loss.keys():
                            print('stop buy err fff')
                            return

                        limit_bool = False
                        kypil = True
                        break

                sleep(3)
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                # print(end_cendel - now)
                if int(str((close_cendel - now).total_seconds())[:-2]) < 6 and int(str((close_cendel - now).total_seconds())[:-2]) > 0:
                    tick_red_green = bot.tickerPrice(symbol=maxstg['coin'])
                    # print('проверяем свечу, если зеленая, тогда ставим флаг для покупки следующей постратгеии')
                    # print(tick['price'], ' > ', llist[0][1])
                    # print(maxstg['max']['volume'], '<=', llist[0][5])
                    llist = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)  # заного берем значение текущей свечи, чтобы получить свежий объем
                    # print(float(maxstg['max']['volume']), '<', float(llist[0][5])) объем
                    # rint(llist[0])
                    # print('Время свечи', datetime.fromtimestamp(int(str(llist[0][6])[:-3])))
                    # print('Время сейчас', now)
                    open_red_green = llist
                    if float(tick_red_green['price']) > float(open_red_green[0][1]):
                        # if float(tick_red_green['price']) > float(open_red_green[0][1]) and 200 <= float(llist[0][5]):

                        print('###################################################')
                        print('###################################################')
                        print('#########ПОКУПКА!ПОКУПКА!ПОКУПКА!##################')
                        print('#########ПОКУПКА!ПОКУПКА!ПОКУПКА!##################')
                        print('###################################################')
                        print('###################################################')
                        print('Время покупки (свеча пердыдущая):', datetime.fromtimestamp(int(str(llist[0][0])[:-3])))

                        # удаляем все ордера
                        margin_all_order_cancel(maxstg['coin'])
                        # отменяем лимит
                        limit_bool = False

                        print('account_only_free_balance ', margin_account_only_free_balance())

                        COIN_free, USDT_free = margin_get_free_balance('BTC', 'USDT')

                        qtyB = check_coin_QtyBuy(USDT_free, maxstg['coin'], 10)
                        qtyS = check_coin_QtySell(COIN_free, maxstg['coin'], 0)

                        print('COIN_free ', COIN_free, '; USDT_free ', USDT_free, '; Сколько можно купить крипты на usd ', qtyB, '; Сколько usdt в битках ', qtyS)

                        if qtyB > 0.001:  # проверяем есть ли доллары для покуки битка

                            #
                            # покупаем
                            #
                            margin_all_order_cancel(maxstg['coin'])  # отменяем все ордера во избежание проблем

                            stop_price = llist

                            # определяем, если свеча больше 1%, тогда стоп на середину ее тела
                            print('stop_price:', stop_price[0])
                            print('stop_price:', datetime.fromtimestamp(int(str(stop_price[0][0])[:-3])))

                            print('stop_price[0][3]):', stop_price[0][3])
                            print('stop_price[0][3]) DECIMAL:', decimal.Decimal(stop_price[0][3]))
                            print('stop_price[0][2]):', stop_price[0][2])
                            print('stop_price[0][2]) DECIMAL:', decimal.Decimal(stop_price[0][2]))
                            center = (decimal.Decimal(stop_price[0][2]) - decimal.Decimal(stop_price[0][3]))
                            razniza = (decimal.Decimal(stop_price[0][3]) / 100)
                            # percent = max(center, razniza) / min(center, razniza)
                            percent = center / razniza
                            print('center:', center)
                            print('razniza:', razniza)
                            print('percent:', percent)
                            if percent >= 1:
                                stop_price = abs((decimal.Decimal(stop_price[0][2]) - decimal.Decimal(stop_price[0][3])) / 2) + decimal.Decimal(stop_price[0][3])  # округлить бы
                                print('stop_price > 1 :', stop_price)
                            else:
                                stop_price = decimal.Decimal(stop_price[0][3])
                                print('stop_price < 1:', stop_price)

                            qtyB = qtyB - ((qtyB / 100) * 1)

                            buy_order = margin_buy_or_sell_order_market(maxstg['coin'], 'BUY', qtyB)

                            # print(buy_order)
                            if 'code' in buy_order.keys():
                                if buy_order['code'] == -2010:
                                    print('Покупаем на 2% меньше всего счета')
                                    # print(qtyB)
                                    qtyB = qtyB - ((qtyB / 100) * 1)
                                    # print(qtyB)

                                    buy_order = margin_buy_or_sell_order_market(maxstg['coin'], 'BUY', qtyB)

                                    if 'code' in buy_order.keys():
                                        print('Error buy 0, return')
                                        return
                                    else:
                                        llist = margin_account_only_free_balance()
                                        for tag in llist:
                                            if tag['asset'] == 'BTC': COIN_free = tag['free']

                                        stop_loss = margin_sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, stop_price)

                                        # СЮДА ЕСЛИ ОШИБКА СТОП ЛОСА, НУЖНО ВЫХОДИТЬ ИЗ БИТКА!
                                        if 'code' in stop_loss.keys():
                                            if 'trigger immediately' in stop_loss['msg']:
                                                print('Стоп лосс выше, просто продаем по рыночной')

                                                sell_order = margin_buy_or_sell_order_market(maxstg['coin'], 'SELL', COIN_free)

                                                print('sell_order 999 ', sell_order['fills'][0]['price'])

                                                if 'code' in sell_order.keys():
                                                    print('Error sell fff')

                                                tick = bot.tickerPrice(symbol=maxstg['coin'])
                                                print('###################################################')
                                                print('###################################################')
                                                print('#########STOPLOSS99#STOPLOSS99STOPLOSS99##############')

                                                print('###################################################')
                                                print('###################################################')
                                                print('###################################################')
                                                log_1 = [coin_ts_open, maxstg['coin'], maxstg['interval'], USDT_free,
                                                         float(sell_order['fills'][0]['price'])]
                                                log_1.append(float(sell_order['fills'][0]['price']))
                                                # освежаем USDT для лог данные
                                                USDT_free = margin_get_free_balance(0, 'USDT')
                                                log_1.append(float(USDT_free))
                                                sell_log(log_1)
                                                return
                                            print('Error stop loss 0')
                                            return
                                        sleep(10)  # чтобы оказаться в следующей свече, может while и tick?

                                else:
                                    print('Error buy unknown 0')
                                    return
                            else:
                                print('купили по полной цене -1%')
                                tick = bot.tickerPrice(symbol=maxstg['coin'])  # tick для logbug
                                # print(stop_price)
                                # print(datetime.fromtimestamp(stop_price[0]))
                                # qtyS = check_coin_QtySell(BTC_free, maxstg['coin'],stop_price[0][3])

                                # получаем свежий остаток по btc
                                llist = margin_account_only_free_balance()
                                for tag in llist:
                                    if tag['asset'] == 'BTC': COIN_free = tag['free']

                                print('stop price btc:', stop_price, '; qtyS:', qtyS, '; COIN_free:', COIN_free)

                                stop_loss = margin_sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, stop_price)

                                # print('qtyS: ', qtyS)
                                # print('stop_loss: ', stop_loss)

                                if 'code' in stop_loss.keys():
                                    if 'trigger immediately' in stop_loss['msg']:
                                        print('Стоп лосс выше, просто продаем по рыночной')

                                        sell_order = margin_buy_or_sell_order_market(maxstg['coin'], 'SELL', COIN_free)

                                        print('sell_order zxc ', sell_order['fills'][0]['price'])

                                        if 'code' in sell_order.keys():
                                            print('Error sell 555')

                                        tick = bot.tickerPrice(symbol=maxstg['coin'])
                                        print('###################################################')
                                        print('###################################################')
                                        print('#########STOPLOSS6#STOPLOSS6STOPLOSS6##############')
                                        print('###################################################')
                                        print('###################################################')
                                        print('###################################################')
                                        log_1 = [coin_ts_open, maxstg['coin'], maxstg['interval'], USDT_free,
                                                 float(sell_order['fills'][0]['price'])]
                                        log_1.append(float(sell_order['fills'][0]['price']))
                                        # освежаем USDT для лог данные
                                        USDT_free = margin_get_free_balance(0, 'USDT')
                                        log_1.append(float(USDT_free))
                                        sell_log(log_1, 13)
                                        return
                                    print('Error stop loss 2')
                                    return

                                sleep(10)

                            log_1 = [coin_ts_open, maxstg['coin'], maxstg['interval'], USDT_free,
                                     float(tick['price'])]
                            kypil = True
                            break

                        elif qtyS > 10:  # у нас есть биток
                            #
                            # ставим флаг, что куплено, так как биток у нас на счету
                            #
                            print('У нас есть биток, и нет долларов. Ставим только стоп лосс')

                            margin_all_order_cancel(maxstg['coin'])  # отменяем все ордера во избежание проблем

                            blist = margin_account_only_free_balance()
                            for tag in blist:
                                if tag['asset'] == 'BTC':
                                    COIN_free = tag['free']

                            tick = bot.tickerPrice(symbol=maxstg['coin'])  # tick для logbug

                            stop_price = llist

                            # определяем, если свеча больше 1%, тогда стоп на середину ее тела
                            print('stop_price:', stop_price[0])
                            print('stop_price[0][3]):', stop_price[0][3])
                            print('stop_price[0][3]) DECIMAL:', decimal.Decimal(stop_price[0][3]))
                            print('stop_price[0][2]):', stop_price[0][2])
                            print('stop_price[0][2]) DECIMAL:', decimal.Decimal(stop_price[0][2]))
                            center = (decimal.Decimal(stop_price[0][2]) - decimal.Decimal(stop_price[0][3]))
                            razniza = (decimal.Decimal(stop_price[0][3]) / 100)
                            # percent = max(center, razniza) / min(center, razniza)
                            percent = center / razniza
                            print('center:', center)
                            print('razniza:', razniza)
                            print('percent:', percent)
                            if percent >= 1:
                                stop_price = ((decimal.Decimal(stop_price[0][1]) - decimal.Decimal(stop_price[0][4])) / 2) + decimal.Decimal(stop_price[0][1])  # округлить бы
                                print('stop_price > 1 :', stop_price)
                            else:
                                stop_price = decimal.Decimal(stop_price[0][3])
                                print('stop_price < 1:', stop_price)
                            # print(datetime.fromtimestamp(stop_price[0]))
                            # qtyS = check_coin_QtySell(BTC_free, maxstg['coin'],stop_price[0][3])
                            print('stop price usdt:', stop_price, '; qtyS:', qtyS,
                                  '; COIN_free:', COIN_free)

                            stop_loss = margin_sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, stop_price)

                            # print('qtyS: ', qtyS)
                            # print('stop_loss: ', stop_loss)
                            if 'code' in stop_loss.keys():
                                print('Error stop loss 3')
                                print('RETURN!RETURN!RETURN!')
                                return
                            sleep(10)

                            log_1 = [coin_ts_open, maxstg['coin'], maxstg['interval'], float(qtyS),
                                     float(tick['price'])]
                            kypil = True
                            break
                        else:
                            print('Нет денег на счету по битку и доллару')

                        print('КАК Я ТУТ ОКАЗАЛСЯ? qtB и qtS по нулю, где-то ошибка')
                        return  # это похоже мертвая функция

                    else:

                        print('Свеча красная или объем не прошел!')
                        if float(tick_red_green['price']) < float(open_red_green[0][1]):

                            # спим, чтобы не вылетела ошибка max retry
                            sleep(0.1)
                            # удаляем все ордера для нового limit
                            margin_all_order_cancel(maxstg['coin'])

                            limit_price = decimal.Decimal(open_red_green[0][2]) + 2

                            USDT_free = margin_get_free_balance(0, 'USDT')

                            qtyB = check_coin_QtyBuy_limit(USDT_free, maxstg['coin'], limit_price)

                            print('COIN_free ', COIN_free, '; USDT_free ', USDT_free, '; Сколько можно купить крипты на usd ', qtyB, '; ', limit_price, 'limit_price')

                            print(open_red_green[0])
                            if qtyB > 0.001:  # проверяем есть ли доллары для покуки битка

                                print('###################################################')
                                print('###################################################')
                                print('###############LIMIT!LIMIT!LIMIT!##################')
                                print('###############LIMIT!LIMIT!LIMIT!##################')
                                print('###################################################')
                                print('###################################################')

                                qtyB = decimal.Decimal(qtyB) - ((decimal.Decimal(qtyB) / 100) * 1)

                                limit = margin_sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'BUY', qtyB, limit_price)

                                limit_bool = True
                                limit_stop_price = open_red_green[0][3]
                                limit_qty = decimal.Decimal(qtyB).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN)

                                log_1 = [datetime.now(), maxstg['coin'], maxstg['interval'], USDT_free, float(limit_price)]
                                print('limit:', limit)
                                # {'orderId': 1630544816,'price': '6635.19000000', 'origQty': '0.00395000', 'cummulativeQuoteQty': '26.12692877', 'status': 'FILLED',

                        sleep(5)
                        break


'''
обычная стратегия стоплосс, старая
'''


def start_trade_stg_only_stop_loss():
    maxstg = {}

    if not settings.BESTSTG:
        print('сратеги нет, ждем')
        sleep(10)
        return
    else:
        for key, val in settings.BESTSTG.items():
            maxstg = val  # тут надо выбрать лучшую стратегию, от BTC до ETH (в данный момент только одна стратегию через цикл)
        print(maxstg)
        if maxstg['max'] is None or maxstg['max']['price'] < 100000:  # !!! потом убрать, поставить return и sleep, для поиска след стратгеии
            # maxstg['max'] = {}
            # maxstg['max']['day'] = 2
            # maxstg['max']['volume'] = 200
            print('сратегия есть, но она не прибыльная')
            print(maxstg['coin'][0:3])
            # return

    all_order_cancel(maxstg['coin'])  # убираем все ордеры

    COIN_free, USDT_free = get_free_balance('BTC', 'USDT')

    if float(COIN_free) < 0.002 and float(USDT_free) < 11:
        print('COIN и USDT не достаточно для торговли, sleep+return')
        print('COIN_free ', COIN_free, '; USDT_free ', USDT_free)

        sleep(60)
        return

    print('account_only_free_balance: ', account_only_free_balance())

    kypil = False
    limit_bool = False

    while True:

        # освежаем USDT и COIN
        COIN_free, USDT_free = get_free_balance('BTC', 'USDT')

        if limit_bool:
            if not check_stop_loss_limit_buy_order(maxstg['coin']):
                # ставим стоп под low

                print('###################################################')
                print('#########FFFFFFF LIMIT BUY BUY BUYLIMIT BUY BUY BUY########')
                print('COIN_free ', COIN_free, '; USDT_free ', USDT_free)
                print('limit_qty ', limit_qty, '; limit_stop_price ', limit_stop_price)
                print('stop buy сработал, ставим стоп под свечу входа')
                print('###################################################')
                print('###################################################')
                print('openOrder ', bot.openOrders(symbol=maxstg['coin']))

                COIN_free = get_free_balance('BTC', 0)
                COIN_locked = get_free_balance('BTC', 'locked')
                print('COIN_locked', COIN_locked)
                print('COIN_free', COIN_free)
                stop_loss = sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, limit_stop_price)
                print('stop_loss ', stop_loss)
                if 'code' in stop_loss.keys():
                    print('stop buy err fff')
                    return
                stop_price = limit_stop_price
                limit_bool = False
                kypil = True

        # биток куплен, ставим стопы и ждем вылета
        if kypil:

            stop_timer = False
            before_cendel = False  # bool для проверки, что появилась следующая свеча

            while True:
                # проверяем не сработал ли стоп

                if not check_stop_loss_sell_order(maxstg['coin']):
                    print('###################################################')
                    print('#########STOPLOSS1#STOPLOSS1STOPLOSS1##############')
                    print(str(stop_price))
                    print('###################################################')
                    print('###################################################')

                    log_1.append(float(stop_price))
                    log_1.append(float(get_free_balance(0, 'USDT')))
                    sell_log(log_1)
                    return

                if not before_cendel:
                    print('###############')
                    print('###############')
                    print('wait cendel')
                    llist_before = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)
                    now_before = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    now_before = datetime.strptime(now_before, '%Y-%m-%d %H:%M:%S')
                    before_cendel = True
                    llist_now = llist_before
                else:
                    llist_now = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)
                    now_after = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    now_after = datetime.strptime(now_after, '%Y-%m-%d %H:%M:%S')

                    # if int(str((datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])) + timedelta(5) - now_before).total_seconds())[:-2]) >= 7:  # если больше 5 сек до конца свечи, тогда ок
                    #    sleep(5)
                    # else:
                    #    sleep(int(str((datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])) + timedelta(5) - now_before).total_seconds())[:-2])+5)

                # print('before ', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])), '; now: ', datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])))
                if int(str(llist_before[0][0])[:-3]) != int(str(llist_now[0][0])[:-3]):
                    print('before', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])))
                    print('before NOW', now_before)
                    print('before TS', str(llist_before[0][0]))
                    print('after', datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])))
                    print('after NOW', now_after)
                    print('after TS', str(llist_now[0][0]))
                    print('###############')
                    print('###############')
                    print('След свеча')
                    print('before ', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])), '; now: ', datetime.fromtimestamp(int(str(llist_now[0][0])[:-3])))
                    print('###############')
                    print('###############')
                    if not stop_timer:
                        print('NEW FIRST STOP! Ставим новый стоп на свечу входа zzz')
                        before_cendel = False

                        all_order_cancel(maxstg['coin'])

                        # какой процент сделала пердыдущая свеча
                        print(llist_before)
                        openclose = decimal.Decimal(abs(float(llist_before[0][1]) - float(llist_before[0][4])))
                        allcendel = decimal.Decimal(float(llist_before[0][2]) - float(llist_before[0][3]))
                        amplituda = openclose / allcendel

                        print('openclose:', openclose)
                        print('allcendel:', allcendel)
                        print('amplituda:', amplituda)

                        # сохраняем значение первого стопа, чтобы не поставить ниже него на следующей свече
                        stop_loss_open = llist_before[0][4]

                        # ставим стоп под low

                        # освежаем USDT и COIN
                        COIN_free, USDT_free = get_free_balance('BTC', 'USDT')
                        COIN_locked = get_free_balance('BTC', 'locked')
                        print('COIN_locked', COIN_locked)
                        print('COIN_free', COIN_free)

                        stop_loss = sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, llist_before[0][3])

                        if 'code' in stop_loss.keys():

                            if 'trigger immediately' in stop_loss['msg']:
                                print('Стоп лосс выше, просто продаем по рыночной')

                                sell_order = buy_or_sell_order_market(maxstg['coin'], 'SELL', COIN_free)

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
                                sell_log(log_1, 13)
                                kypil = False
                                return

                            print('Error stop loss 4 low')
                            kypil = False
                            return

                        # сохраняем значение последнего стопа для лога и статистики
                        print('stop loss status:', stop_loss)
                        stop_price = llist_before[0][3]

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
                    if stop_timer and stop_loss_open < llist_next_stop[0][3]:
                        before_cendel = False
                        print('NEW STOP! Ставим новый стоп под предыдущую свечу, но не ниже open xxx')
                        print('llist_next_stop ', llist_next_stop[0])
                        print('llist_next_stop data ', datetime.fromtimestamp(int(str(llist_next_stop[0][0])[:-3])))
                        all_order_cancel(maxstg['coin'])
                        print('time before stop', datetime.fromtimestamp(int(str(llist_before[0][0])[:-3])), '; stop price:', llist_next_stop[0][3], '; COIN_free:', COIN_free)

                        stop_loss = sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, llist_next_stop[0][3])

                        if 'code' in stop_loss.keys():

                            if 'trigger immediately' in stop_loss['msg']:
                                print('Стоп лосс выше, просто продаем по рыночной')

                                sell_order = buy_or_sell_order_market(maxstg['coin'], 'SELL', COIN_free)

                                print('sell_order 666 ', sell_order['fills'][0]['price'])

                                if 'code' in sell_order.keys():
                                    print('Error sell 987')

                                tick = bot.tickerPrice(symbol=maxstg['coin'])
                                print('###################################################')
                                print('###################################################')
                                print('#########STOPLOSS6#STOPLOSS6STOPLOSS6##############')
                                print('###################################################')
                                print('###################################################')
                                print('###################################################')
                                log_1.append(float(sell_order['fills'][0]['price']))
                                # освежаем USDT для лог данные
                                USDT_free = get_free_balance(0, 'USDT')
                                log_1.append(float(USDT_free))
                                sell_log(log_1, 13)
                                kypil = False
                                return

                            print('Error stop loss 3 next')
                            return

                        # сохраняем значение последнего стопа для лога и статистики
                        print('stop loss status:', stop_loss)
                        stop_price = llist_next_stop[0][3]
                    # чекаем по 10 сек, потом сравниваем
                    llist_next_stop = llist_before
                    stop_timer = True

        print('### Ищем паттерн на вход ###')
        # биток не куплен, ждем свечу на вход
        llist = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)
        # print(llist)

        for cendel in llist:
            coin_ts_open = int(str(cendel[0])[:-3])
            coin_ts_close = int(str(cendel[6])[:-3])
            # print('ts open: ', str(datetime.fromtimestamp(coin_ts_open).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0])
            # print('ts close: ', str(datetime.fromtimestamp(coin_ts_close).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0])

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
        close_cendel = datetime.fromtimestamp(coin_ts_close)  # strftime('%Y-%m-%d %H:%M:%S')

        # print(type(now), ' - ',now)
        # print(type(close_cendel), ' - ', end_cendel)
        # print(int(str((end_cendel - now).total_seconds())[:-2]))


        if now < close_cendel and int(str((close_cendel - now).total_seconds())[:-2]) > 10:  # если больше 10 сек до конца свечи, тогда ок

            while True:

                # проверяем нет ли покупки по лимит
                if limit_bool:
                    if not check_stop_loss_limit_buy_order(maxstg['coin']):

                        print('check_stop_loss_limit_buy_order ', check_stop_loss_limit_buy_order(maxstg['coin']))
                        print('###################################################')
                        print('#########LIMIT BUY BUY BUYLIMIT BUY BUY BUY########')
                        print('COIN_free ', COIN_free, '; USDT_free ', USDT_free)
                        print('limit_qty ', limit_qty, '; limit_stop_price ', limit_stop_price)
                        print('stop buy сработал, ставим стоп под свечу входа')
                        print('###################################################')
                        print('###################################################')
                        print('openOrder ', bot.openOrders(symbol=maxstg['coin']))

                        COIN_free = get_free_balance('BTC', 0)
                        COIN_locked = get_free_balance('BTC', 'locked')
                        print('COIN_locked', COIN_locked)
                        print('COIN_free', COIN_free)

                        stop_loss = sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, limit_stop_price)

                        print('stop_loss ', stop_loss)
                        if 'code' in stop_loss.keys():
                            print('stop buy err fff')
                            return

                        stop_price = limit_stop_price

                        limit_bool = False
                        kypil = True
                        break

                sleep(3)
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                # print(end_cendel - now)
                if int(str((close_cendel - now).total_seconds())[:-2]) < 6 and int(str((close_cendel - now).total_seconds())[:-2]) > 0:
                    tick_red_green = bot.tickerPrice(symbol=maxstg['coin'])
                    # print('проверяем свечу, если зеленая, тогда ставим флаг для покупки следующей постратгеии')
                    # print(tick['price'], ' > ', llist[0][1])
                    # print(maxstg['max']['volume'], '<=', llist[0][5])
                    llist = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)  # заного берем значение текущей свечи, чтобы получить свежий объем
                    # print(float(maxstg['max']['volume']), '<', float(llist[0][5])) объем
                    # rint(llist[0])
                    # print('Время свечи', datetime.fromtimestamp(int(str(llist[0][6])[:-3])))
                    # print('Время сейчас', now)
                    open_red_green = llist
                    if float(tick_red_green['price']) > float(open_red_green[0][1]):
                        # if float(tick_red_green['price']) > float(open_red_green[0][1]) and 200 <= float(llist[0][5]):

                        print('###################################################')
                        print('###################################################')
                        print('#########ПОКУПКА!ПОКУПКА!ПОКУПКА!##################')
                        print('#########ПОКУПКА!ПОКУПКА!ПОКУПКА!##################')
                        print('###################################################')
                        print('###################################################')
                        print('Время покупки (свеча пердыдущая):', datetime.fromtimestamp(int(str(llist[0][0])[:-3])))

                        # удаляем все ордера
                        all_order_cancel(maxstg['coin'])
                        # отменяем лимит
                        limit_bool = False

                        print('account_only_free_balance ', account_only_free_balance())

                        COIN_free, USDT_free = get_free_balance('BTC', 'USDT')

                        qtyB = check_coin_QtyBuy(USDT_free, maxstg['coin'], 10)
                        qtyS = check_coin_QtySell(COIN_free, maxstg['coin'], 0)

                        print('COIN_free ', COIN_free, '; USDT_free ', USDT_free, '; Сколько можно купить крипты на usd ', qtyB, '; Сколько usdt в битках ', qtyS)

                        if qtyB > 0.001:  # проверяем есть ли доллары для покуки битка

                            #
                            # покупаем
                            #
                            all_order_cancel(maxstg['coin'])  # отменяем все ордера во избежание проблем

                            stop_price = llist

                            # определяем, если свеча больше 1%, тогда стоп на середину ее тела
                            print('stop_price:', stop_price[0])
                            print('stop_price:', datetime.fromtimestamp(int(str(stop_price[0][0])[:-3])))

                            print('stop_price[0][3]):', stop_price[0][3])
                            print('stop_price[0][3]) DECIMAL:', decimal.Decimal(stop_price[0][3]))
                            print('stop_price[0][2]):', stop_price[0][2])
                            print('stop_price[0][2]) DECIMAL:', decimal.Decimal(stop_price[0][2]))
                            center = (decimal.Decimal(stop_price[0][2]) - decimal.Decimal(stop_price[0][3]))
                            razniza = (decimal.Decimal(stop_price[0][3]) / 100)
                            # percent = max(center, razniza) / min(center, razniza)
                            percent = center / razniza
                            print('center:', center)
                            print('razniza:', razniza)
                            print('percent:', percent)
                            if percent >= 1:
                                stop_price = abs((decimal.Decimal(stop_price[0][2]) - decimal.Decimal(stop_price[0][3])) / 2) + decimal.Decimal(stop_price[0][3])  # округлить бы
                                print('stop_price > 1 :', stop_price)
                            else:
                                stop_price = decimal.Decimal(stop_price[0][3])
                                print('stop_price < 1:', stop_price)

                            qtyB = qtyB - ((qtyB / 100) * 1)

                            buy_order = buy_or_sell_order_market(maxstg['coin'], 'BUY', qtyB)

                            # print(buy_order)
                            if 'code' in buy_order.keys():
                                if buy_order['code'] == -2010:
                                    print('Покупаем на 2% меньше всего счета')
                                    # print(qtyB)
                                    qtyB = qtyB - ((qtyB / 100) * 1)
                                    # print(qtyB)
                                    buy_order = bot.createOrder(
                                        symbol=maxstg['coin'],
                                        recvWindow=5000,
                                        side='BUY',
                                        type='MARKET',
                                        quantity=decimal.Decimal(qtyB).quantize(
                                            decimal.Decimal('.000001'),
                                            rounding=decimal.ROUND_DOWN),
                                        newOrderRespType='FULL'
                                    )
                                    if 'code' in buy_order.keys():
                                        print('Error buy 0, return')
                                        return
                                    else:
                                        llist = account_only_free_balance()
                                        for tag in llist:
                                            if tag['asset'] == 'BTC': COIN_free = tag['free']

                                        stop_loss = sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, stop_price)

                                        # СЮДА ЕСЛИ ОШИБКА СТОП ЛОСА, НУЖНО ВЫХОДИТЬ ИЗ БИТКА!
                                        if 'code' in stop_loss.keys():
                                            if 'trigger immediately' in stop_loss['msg']:
                                                print('Стоп лосс выше, просто продаем по рыночной')

                                                sell_order = buy_or_sell_order_market(maxstg['coin'], 'SELL', COIN_free)

                                                print('sell_order 999 ', sell_order['fills'][0]['price'])

                                                if 'code' in sell_order.keys():
                                                    print('Error sell fff')

                                                tick = bot.tickerPrice(symbol=maxstg['coin'])
                                                print('###################################################')
                                                print('###################################################')
                                                print('#########STOPLOSS99#STOPLOSS99STOPLOSS99##############')

                                                print('###################################################')
                                                print('###################################################')
                                                print('###################################################')
                                                log_1 = [int(coin_ts_open), maxstg['coin'], maxstg['interval'], USDT_free,
                                                         float(sell_order['fills'][0]['price'])]
                                                log_1.append(float(sell_order['fills'][0]['price']))
                                                # освежаем USDT для лог данные
                                                USDT_free = get_free_balance(0, 'USDT')
                                                log_1.append(float(USDT_free))
                                                sell_log(log_1, 13)
                                                return
                                            print('Error stop loss 0')
                                            return
                                        sleep(10)  # чтобы оказаться в следующей свече, может while и tick?

                                else:
                                    print('Error buy unknown 0')
                                    return
                            else:
                                print('купили по полной цене -1%')
                                tick = bot.tickerPrice(symbol=maxstg['coin'])  # tick для logbug
                                # print(stop_price)
                                # print(datetime.fromtimestamp(stop_price[0]))
                                # qtyS = check_coin_QtySell(BTC_free, maxstg['coin'],stop_price[0][3])

                                # получаем свежий остаток по btc
                                llist = account_only_free_balance()
                                for tag in llist:
                                    if tag['asset'] == 'BTC': COIN_free = tag['free']

                                print('stop price btc:', stop_price, '; qtyS:', qtyS, '; COIN_free:', COIN_free)

                                stop_loss = sell_or_buy_stop_loss_limit_order(maxstg['coin'], 'SELL', COIN_free, stop_price)

                                # print('qtyS: ', qtyS)
                                # print('stop_loss: ', stop_loss)

                                if 'code' in stop_loss.keys():
                                    if 'trigger immediately' in stop_loss['msg']:
                                        print('Стоп лосс выше, просто продаем по рыночной')

                                        sell_order = buy_or_sell_order_market(maxstg['coin'], 'SELL', COIN_free)

                                        print('sell_order zxc ', sell_order['fills'][0]['price'])

                                        if 'code' in sell_order.keys():
                                            print('Error sell 555')

                                        tick = bot.tickerPrice(symbol=maxstg['coin'])
                                        print('###################################################')
                                        print('###################################################')
                                        print('#########STOPLOSS6#STOPLOSS6STOPLOSS6##############')
                                        print('###################################################')
                                        print('###################################################')
                                        print('###################################################')
                                        log_1 = [int(coin_ts_open), maxstg['coin'], maxstg['interval'], USDT_free,
                                                 float(sell_order['fills'][0]['price'])]
                                        log_1.append(float(sell_order['fills'][0]['price']))
                                        # освежаем USDT для лог данные
                                        USDT_free = get_free_balance(0, 'USDT')
                                        log_1.append(float(USDT_free))
                                        sell_log(log_1, 13)
                                        return
                                    print('Error stop loss 2')
                                    return

                                sleep(10)

                            log_1 = [int(coin_ts_open), maxstg['coin'], maxstg['interval'], USDT_free,
                                     float(tick['price'])]
                            kypil = True
                            break

                        elif qtyS > 10:  # у нас есть биток
                            #
                            # ставим флаг, что куплено, так как биток у нас на счету
                            #
                            print('У нас есть биток, и нет долларов. Ставим только стоп лосс')

                            all_order_cancel(maxstg['coin'])  # отменяем все ордера во избежание проблем

                            blist = account_only_free_balance()
                            for tag in blist:
                                if tag['asset'] == 'BTC':
                                    COIN_free = tag['free']

                            tick = bot.tickerPrice(symbol=maxstg['coin'])  # tick для logbug

                            stop_price = llist

                            # определяем, если свеча больше 1%, тогда стоп на середину ее тела
                            print('stop_price:', stop_price[0])
                            print('stop_price[0][3]):', stop_price[0][3])
                            print('stop_price[0][3]) DECIMAL:', decimal.Decimal(stop_price[0][3]))
                            print('stop_price[0][2]):', stop_price[0][2])
                            print('stop_price[0][2]) DECIMAL:', decimal.Decimal(stop_price[0][2]))
                            center = (decimal.Decimal(stop_price[0][2]) - decimal.Decimal(stop_price[0][3]))
                            razniza = (decimal.Decimal(stop_price[0][3]) / 100)
                            # percent = max(center, razniza) / min(center, razniza)
                            percent = center / razniza
                            print('center:', center)
                            print('razniza:', razniza)
                            print('percent:', percent)
                            if percent >= 1:
                                stop_price = ((decimal.Decimal(stop_price[0][1]) - decimal.Decimal(stop_price[0][4])) / 2) + decimal.Decimal(stop_price[0][1])  # округлить бы
                                print('stop_price > 1 :', stop_price)
                            else:
                                stop_price = decimal.Decimal(stop_price[0][3])
                                print('stop_price < 1:', stop_price)
                            # print(datetime.fromtimestamp(stop_price[0]))
                            # qtyS = check_coin_QtySell(BTC_free, maxstg['coin'],stop_price[0][3])
                            print('stop price usdt:', stop_price, '; qtyS:', qtyS,
                                  '; COIN_free:', COIN_free)

                            stop_loss = bot.createOrder(
                                symbol=maxstg['coin'],
                                recvWindow=5000,
                                side='SELL',
                                type='STOP_LOSS_LIMIT',
                                quantity=decimal.Decimal(float(COIN_free)).quantize(
                                    decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
                                price=decimal.Decimal(stop_price).quantize(
                                    decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
                                stopPrice=decimal.Decimal(stop_price).quantize(
                                    decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
                                timeInForce='GTC'
                            )

                            # print('qtyS: ', qtyS)
                            # print('stop_loss: ', stop_loss)
                            if 'code' in stop_loss.keys():
                                print('Error stop loss 3')
                                print('RETURN!RETURN!RETURN!')
                                return
                            sleep(10)

                            log_1 = [int(coin_ts_open), maxstg['coin'], maxstg['interval'], float(qtyS),
                                     float(tick['price'])]
                            kypil = True
                            break
                        else:
                            print('Нет денег на счету по битку и доллару')

                        print('КАК Я ТУТ ОКАЗАЛСЯ? qtB и qtS по нулю, где-то ошибка')
                        return  # это похоже мертвая функция

                    else:

                        print('Свеча красная или объем не прошел!')
                        if float(tick_red_green['price']) < float(open_red_green[0][1]):

                            # спим, чтобы не вылетела ошибка max retry
                            sleep(0.1)
                            # удаляем все ордера для нового limit
                            all_order_cancel(maxstg['coin'])

                            limit_price = decimal.Decimal(open_red_green[0][2]) + 2

                            USDT_free = get_free_balance(0, 'USDT')

                            qtyB = check_coin_QtyBuy_limit(USDT_free, maxstg['coin'], limit_price)

                            print('COIN_free ', COIN_free, '; USDT_free ', USDT_free, '; Сколько можно купить крипты на usd ', qtyB, '; ', limit_price, 'limit_price')

                            print(open_red_green[0])
                            if qtyB > 0.001:  # проверяем есть ли доллары для покуки битка

                                print('###################################################')
                                print('###################################################')
                                print('###############LIMIT!LIMIT!LIMIT!##################')
                                print('###############LIMIT!LIMIT!LIMIT!##################')
                                print('###################################################')
                                print('###################################################')

                                qtyB = decimal.Decimal(qtyB) - ((decimal.Decimal(qtyB) / 100) * 1)

                                limit = bot.createOrder(
                                    symbol=maxstg['coin'],
                                    recvWindow=5000,
                                    side='BUY',
                                    type='STOP_LOSS_LIMIT',
                                    quantity=decimal.Decimal(qtyB).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
                                    # это количество которе округляем в меньшую
                                    price=limit_price,  # это цена бай
                                    stopPrice=limit_price,
                                    timeInForce='GTC'
                                )

                                limit_bool = True
                                limit_stop_price = open_red_green[0][3]
                                limit_qty = decimal.Decimal(qtyB).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN)

                                log_1 = [int(str(now.timestamp()).split('.')[0]), maxstg['coin'], maxstg['interval'], USDT_free, float(limit_price)]
                                print('limit:', limit)
                                # {'orderId': 1630544816,'price': '6635.19000000', 'origQty': '0.00395000', 'cummulativeQuoteQty': '26.12692877', 'status': 'FILLED',

                        sleep(5)
                        break


# запуск анализа стратегии по обьему и количеству свечей
#
def start_trade_stg():
    """
        1) определяем, есть ли на балансе доллар или монета торговая
        2) тиково ищем стратегию на вход (объем + зеленая свеча)
        - покупаем на все биток
        - ставим стоп под предыдущую свечу
        - тиково смотрим наступление новой свечи, стоп переставляем под предыдущую
        - запоминаем точку входа, выход по монете через столько то свечей по MAXSTG. если стоп сработал, выходим в доллар
        - пишем в файл - когда зашли, когда вышли, на сколько купили, процент прибыли за сделку, комиссия
        - если ок, по стратегии находим паттерн
        - если есть свободные доллары, покупаем на все биток, если биток уже есть, оставляем все как есть
    """

    maxstg = {}

    if not settings.BESTSTG:
        print('сратеги нет, ждем')
        sleep(10)
        return
    else:
        for key, val in settings.BESTSTG.items():
            maxstg = val  # тут надо выбрать лучшую стратегию, от BTC до ETH (в данный момент только одна стратегию через цикл)
        print(maxstg)
        if maxstg['max'] is None or maxstg['max']['price'] < 101000:  # !!! потом убрать, поставить return и sleep, для поиска след стратгеии
            # maxstg['max'] = {}
            # maxstg['max']['day'] = 2
            # maxstg['max']['volume'] = 200
            print('сратегия есть, но она не прибыльная, запускаем тестовую сратегию')
            print(maxstg['coin'][0:3])
            sleep(300)
            return

    # print(maxstg['coin'][0:3])
    # print(maxstg['coin'])
    all_order_cancel(maxstg['coin'])

    # 1) определяем, есть ли на балансе доллар или монета торговая

    llist = account_only_free_balance()
    COIN_free = 0
    USDT_free = 0
    for tag in llist:
        if tag['asset'] == maxstg['coin'][0:3]: COIN_free = tag['free']
        if tag['asset'] == 'USDT': USDT_free = tag['free']

    if float(COIN_free) > 0 or float(USDT_free) > 0:
        print('$$$ Начали искать паттерны на вход $$$')

    else:
        print('COIN и USDT нет, счет нулевой, sleep 60')
        sleep(60)
        return

    # 2) тиково ищем стратегию на вход (объем + зеленая свеча)
    kypil = False
    exit_loop = False

    while True:

        # повторяем тоже что сверху, если стратегия изменилась (ЭТОР БРЕД ТАК КАК ПРИ ПРОДАЖЕ МЫ ВЫХОДИМ ПОЛЬНОСТЬЮ ИЗ ЦИКЛА!)
        for key, val in settings.BESTSTG.items():
            maxstg = val  # тут надо выбрать лучшую стратегию, от BTC до ETH (в данный момент только одна стратегию через цикл)

        # освежаем USDT, если система вылетела из-за какой-то ошибки (ЭТО НЕ ОБЯЗАТЕЛЬНЫЙ КОД!)
        llist = account_only_free_balance()
        for tag in llist:
            if tag['asset'] == 'USDT': USDT_free = tag['free']

        # биток куплен, ждем свечу на выход
        if kypil:
            datetime_open = datetime.fromtimestamp(coin_ts_open)
            check_cendel = datetime_open + timedelta(
                minutes=maxstg['max']['day'] * 5 + 5)  # +5 потому что выход происходит не вконце свечи, а в начале, получается проходит на одну свечу меньше
            # print('check_cendel clear', datetime_open)
            # print('check_cendel +10 = ', check_cendel)

            while True:
                # print('openOrders', bot.openOrders(symbol=maxstg['coin'],))

                # беру текущую свечу в цикле, если она не подходит, ждем 60 сек
                llist = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)

                # print('coin_ts_open: ', datetime_open)
                # print('coin_ts_open type: ', type(datetime_open))
                # print('check_cendel: ', check_cendel)
                # print('check_cendel type: ', type(check_cendel))
                cendel_exit = int(str(llist[0][0])[:-3])
                cendel_exit_date = datetime.fromtimestamp(cendel_exit)

                # проверяем не сработал ли стоп
                stop = bot.openOrders(symbol=maxstg['coin'])
                blist = account_only_free_balance()  # освежаем USDT для лог данные
                for tag in blist:
                    if tag['asset'] == 'USDT': USDT_free = tag['free']
                    # COIN_free не надо, так как у нас после стоп лоса, это значение становится 0

                if not stop:
                    print('###################################################')
                    print('###################################################')
                    print('#########STOPLOSS!#STOPLOSS!STOPLOSS!##############')
                    print('#########STOPLOSS!#STOPLOSS!STOPLOSS!##############')
                    print('###################################################')
                    print('###################################################')
                    log_1.append(float(stop_price[0][3]))
                    log_1.append(float(USDT_free))
                    sell_log(log_1)
                    kypil = False
                    exit_loop = True
                    break

                if check_cendel == cendel_exit_date:
                    print('Паттерн на выход, продаем оп рыночной цене')
                    # print('Данные по COIN_free:', round(float(COIN_free), 6))
                    # отменяем ордера и можем продавать
                    all_order_cancel(maxstg['coin'])
                    buy_order = bot.createOrder(
                        symbol=maxstg['coin'],
                        recvWindow=5000,
                        side='SELL',
                        type='MARKET',
                        quantity=decimal.Decimal(float(COIN_free)).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
                        newOrderRespType='FULL'
                    )
                    if 'code' in buy_order.keys():
                        print('Error sell ((')

                    print('###################################################')
                    print('###################################################')
                    print('#########ПРОДАНО!#ПРОДАНО!ПРОДАНО!#################')
                    print('#########ПРОДАНО!#ПРОДАНО!ПРОДАНО!#################')
                    print('###################################################')
                    print('###################################################')
                    # [ts,coin,interval,usdt_begin,tick buy, tick sell,usdt_end]
                    tick = bot.tickerPrice(symbol=maxstg['coin'])
                    log_1.append(float(tick['price']))

                    blist = account_only_free_balance()  # освежаем USDT для лог данные
                    for tag in blist:
                        if tag['asset'] == 'USDT': USDT_free = tag['free']

                    log_1.append(float(USDT_free))
                    sell_log(log_1, 13)
                    # print('check_cendel: ', check_cendel, '; cendel_exit_date: ',cendel_exit_date)
                    sleep(60)
                    kypil = False
                    exit_loop = True
                    break
                else:
                    print('Ищем свечу на продажу')
                    print('Время сейчас ', cendel_exit_date, ' => время выхода ', check_cendel)
                    # print('check_cendel: ', check_cendel, '; cendel_exit_date: ', cendel_exit_date)
                    sleep(300)
                    # берем свечу покупки, опредлеям +свечей вперед, определяем какой это будет ts  как тоолько достигаем тако свеячи, выходим
                    # каждый раз проверяем не сработал ли стоп, если сработал, то тоже выходим и опять ищем модель на вход

            if exit_loop:  # продали, значит начинаем все заного, так как стратегия могла поменяться
                break

        # биток не куплен, ждем свечу на вход
        llist_all_cendel = []
        llist = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)
        # print(llist)

        for cendel in llist:
            coin_ts_open = int(str(cendel[0])[:-3])
            coin_ts_close = int(str(cendel[6])[:-3])
            # print('ts open: ', str(datetime.fromtimestamp(coin_ts_open).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0])
            # print('ts close: ', str(datetime.fromtimestamp(coin_ts_close).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0])

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
        end_cendel = datetime.fromtimestamp(coin_ts_close)  # strftime('%Y-%m-%d %H:%M:%S')

        # print(type(now), ' - ',now)
        # print(type(end_cendel), ' - ', end_cendel)
        # print(int(str((end_cendel - now).total_seconds())[:-2]))


        if now < end_cendel and int(str((end_cendel - now).total_seconds())[:-2]) > 10:
            while True:

                sleep(5)
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                # print(end_cendel - now)
                if int(str((end_cendel - now).total_seconds())[:-2]) < 6 and int(str((end_cendel - now).total_seconds())[:-2]) > 0:
                    try:
                        tick = bot.tickerPrice(symbol=maxstg['coin'])
                    except requests.exceptions.ConnectionError:
                        print('Error connect sleep 10 and repeat')
                        sleep(10)
                        continue

                    # print('проверяем свечу, если зеленая, тогда ставим флаг для покупки следующей постратгеии')
                    # print(tick['price'], ' > ', llist[0][1])
                    # print(maxstg['max']['volume'], '<=', llist[0][5])
                    llist = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)  # заного берем значение текущей свечи, чтобы получить свежий объем
                    # print(float(maxstg['max']['volume']), '<', float(llist[0][5])) объем
                    # rint(llist[0])
                    # print('Время свечи', datetime.fromtimestamp(int(str(llist[0][6])[:-3])))
                    # print('Время сейчас', now)
                    if float(tick['price']) > float(llist[0][1]) and float(maxstg['max']['volume']) <= float(llist[0][5]):
                        # if float(tick['price']) > float(llist[0][1]):
                        print('###################################################')
                        print('###################################################')
                        print('#########ПОКУПКА!ПОКУПКА!ПОКУПКА!##################')
                        print('#########ПОКУПКА!ПОКУПКА!ПОКУПКА!##################')
                        print('###################################################')
                        print('###################################################')
                        print('Время свечи покупки', datetime.fromtimestamp(int(str(llist[0][0])[:-3])))

                        qtyB = check_coin_QtyBuy(USDT_free, maxstg['coin'], 10)
                        qtyS = check_coin_QtySell(COIN_free, maxstg['coin'], 0)
                        print('COIN_free ', COIN_free, '; USDT_free ', USDT_free, '; Крипта к доллару qtyB ', qtyB, '; Сколько usdt в битках ', qtyS)
                        if qtyB > 0.001:  # проверяем есть ли доллары для покуки битка

                            #
                            # покупаем
                            #
                            #
                            stop_price = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)

                            qtyB = qtyB - ((qtyB / 100) * 1)
                            buy_order = bot.createOrder(
                                symbol=maxstg['coin'],
                                recvWindow=5000,
                                side='BUY',
                                type='MARKET',
                                quantity=decimal.Decimal(qtyB).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
                                newOrderRespType='FULL'
                            )

                            # print(buy_order)
                            if 'code' in buy_order.keys():
                                if buy_order['code'] == -2010:
                                    print('Покупаем на 2% меньше всего счета')
                                    # print(qtyB)
                                    qtyB = qtyB - ((qtyB / 100) * 2)
                                    # print(qtyB)
                                    buy_order = bot.createOrder(
                                        symbol=maxstg['coin'],
                                        recvWindow=5000,
                                        side='BUY',
                                        type='MARKET',
                                        quantity=decimal.Decimal(qtyB).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
                                        newOrderRespType='FULL'
                                    )
                                    if 'code' in buy_order.keys():
                                        print('Error buy 0')
                                        break
                                    else:
                                        llist = account_only_free_balance()
                                        for tag in llist:
                                            if tag['asset'] == 'BTC': COIN_free = tag['free']
                                        stop_loss = bot.createOrder(
                                            symbol=maxstg['coin'],
                                            recvWindow=5000,
                                            side='SELL',
                                            type='STOP_LOSS_LIMIT',
                                            quantity=decimal.Decimal(float(COIN_free)).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
                                            # это количество которе округляем в меньшую
                                            price=stop_price[0][3],  # это цена стопа
                                            stopPrice=stop_price[0][3],
                                            timeInForce='GTC'
                                        )
                                        sleep(10)
                                        if 'code' in stop_loss.keys():
                                            print('Error buy 1')
                                            break

                                else:
                                    break
                            else:
                                print('покупаем по полной цене -1%')
                                tick = bot.tickerPrice(symbol=maxstg['coin'])  # tick для logbug
                                # print(stop_price)
                                # print(datetime.fromtimestamp(stop_price[0]))
                                # qtyS = check_coin_QtySell(BTC_free, maxstg['coin'],stop_price[0][3])

                                # получаем свежий остаток по btc
                                llist = account_only_free_balance()
                                for tag in llist:
                                    if tag['asset'] == 'BTC': COIN_free = tag['free']

                                print('stop price btc:', stop_price[0][3], '; qtyS:', qtyS, '; COIN_free:', COIN_free)
                                stop_loss = bot.createOrder(
                                    symbol=maxstg['coin'],
                                    recvWindow=5000,
                                    side='SELL',
                                    type='STOP_LOSS_LIMIT',
                                    quantity=decimal.Decimal(float(COIN_free)).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
                                    price=stop_price[0][3],
                                    stopPrice=stop_price[0][3],
                                    timeInForce='GTC'
                                )
                                # print('qtyS: ', qtyS)
                                # print('stop_loss: ', stop_loss)
                                sleep(10)
                                if 'code' in stop_loss.keys():
                                    print('Error buy 2')
                                    break
                                    # ставим стоп

                            log_1 = [coin_ts_open, maxstg['coin'], maxstg['interval'], float(USDT_free), float(tick['price'])]
                            kypil = True
                            break
                        elif qtyS > 10:  # у нас есть биток
                            #
                            # ставим флаг, что куплено, так как биток у нас на счету
                            #
                            print('У нас есть биток, и нет долларов. ставим только стоп лосс')

                            blist = account_only_free_balance()
                            COIN_free = 0
                            for tag in blist:
                                if tag['asset'] == 'BTC':
                                    COIN_free = tag['free']

                            tick = bot.tickerPrice(symbol=maxstg['coin'])  # tick для logbug
                            stop_price = take_now_cendel_binance(maxstg['coin'], maxstg['interval'], 1)
                            # print(datetime.fromtimestamp(stop_price[0]))
                            # qtyS = check_coin_QtySell(BTC_free, maxstg['coin'],stop_price[0][3])
                            print('stop price usdt:', stop_price[0][3], '; qtyS:', qtyS, '; COIN_free:', COIN_free)
                            stop_loss = bot.createOrder(
                                symbol=maxstg['coin'],
                                recvWindow=5000,
                                side='SELL',
                                type='STOP_LOSS_LIMIT',
                                quantity=decimal.Decimal(float(COIN_free)).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
                                price=stop_price[0][3],
                                stopPrice=stop_price[0][3],
                                timeInForce='GTC'
                            )

                            # print('qtyS: ', qtyS)
                            # print('stop_loss: ', stop_loss)
                            sleep(10)
                            if 'code' in stop_loss.keys():
                                print('Error buy 3')
                                break
                            log_1 = [coin_ts_close, maxstg['coin'], maxstg['interval'], float(qtyS), float(tick['price'])]
                            kypil = True
                            break
                        else:
                            print('Нет денег на счету по битку и доллару')

                        sleep(10)
                        break
                    else:
                        print('Свеча красная или объем не прошел! ждем след свечу')
                        sleep(20)
                        break


# Проходим все стратегии и определяем наилучшую
#

def define_strategy():
    """
        stg1: покупаем сразу за зеленой свечой, продаем при минусовой свече в конце дня
    """
    r = redis_db_check(15)
    result = {}
    coin = 'BTCUSDT'
    # result['str1_5m'] = strategy_1_binance_5m(r, coin, '5m', 100000)
    # result['str2_5m'] = strategy_2_binance_5m(r, coin, '5m', 100000)
    # result['str3_5m'] = strategy_3_binance_5m(r, coin, '5m', 100000, 200, 1500, 100)
    # result['str4_5m'] = strategy_4_binance_5m(r, coin, '5m', 100000, 200, 1500, 100)
    # result['str5_5m'] = strategy_5_binance_5m(r, coin, '5m', 100000, 200, 1500, 100)
    # result['str6_5m'] = strategy_6_binance_5m(r, coin, '5m', 100000, 200, 1500, 100)
    # result['str7_5m'] = strategy_7_binance_5m(r, coin,'5m', 100000, 30, 990, 30)
    result['str8_5m'] = strategy_8_binance_5m(r, coin, '5m', 100000, 30, 990, 30)  # дописаная 7 стратегия, убраны ошибки

    # result['str1_1d'] = strategy_1_binance_1d(r,coin,interval,period,100000)
    # result['str2_1d'] = strategy_2_binance(r, coin, interval, period, 100000)
    # result['str3_1d'] = strategy_3_binance(r, coin, interval, period, 100000,min_volume,max_volume,range_volume)

    return result


# Стратегия 8

def strategy_8_binance_5m(r, coin, interval, cash, min_volume, max_volume, range_volume):
    """
    Если свеча в плюс, то
    покупаем при открытии следующий свечи, и держим в цикле от 1 свечи до 10 и выходим (при разных объемах). и показываем лучший вход

    скопировано с 3-й стратегии изначально

    берем обьем 200
    если плюсовая свеча, объем указанный, покупаем по 2 свечи - проходим все 500 свечей
    если плюсовая свеча, объем указанный, покупаем по 3 свечи - проходим все 500 свечей

    стоп ставим лоу купленной свечи

    """

    hold_money = False  # держу акции
    buy_flag = False
    allvolume_dict = {}
    allcendel_dict = {}
    dictt = {}

    now = datetime.now()
    print('stg 7: ', now)
    if len(str(now.minute)) > 1:
        if int(str(now.minute)[1]) < 5:
            need_minute = int(str(now.minute)[0] + '0')
        else:
            need_minute = int(str(now.minute)[0] + '5')
    else:
        if int(now.minute) < 5:
            need_minute = 0
        else:
            need_minute = 5

    cash = 0
    for cendel in range(5, 15):
        # print('cendel : ',cendel)
        for step in range(min_volume, max_volume, range_volume):
            cash = 100000
            min5_now = datetime.combine(date.today(), time(now.hour, need_minute, 0))

            # ts_5min_now = str(datetime.combine(date.today(), time(now.hour, need_minute, 0)).timestamp()).split('.')[0]
            k = 2505
            for i in range(2500, 5, -5):

                cendel_in = cendel  # при срабатывании стопа в цикуле while, мы указываем сколько свечей прошел цикл, чтобы потом умножить для смещения

                if i >= k: continue
                # print('Свеча входа ',i)
                min5ts = str((min5_now + timedelta(minutes=-i)).timestamp()).split('.')[0]
                min5ts2 = str((min5_now + timedelta(minutes=-i + 5)).timestamp()).split('.')[0]

                if not r.hexists(coin + '_' + interval, min5ts):
                    redis_check_back_5m(r, coin, interval, min5_now)
                elif not r.hexists(coin + '_' + interval, min5ts2):
                    redis_check_back_5m(r, coin, interval, min5_now)

                lline = r.hget(coin + '_' + interval, min5ts)
                # print(i,':',min5ts, ' : ', min5_now + timedelta(minutes=-i), ' : ', lline)

                try:
                    lline = ast.literal_eval(lline.decode())
                except AttributeError:
                    print('error')
                    redis_check_back_5m(r, coin, interval, min5_now, checkall=True)
                    print(lline)
                    print(i, ' - ', int(i / 5), ' - ', cendel)
                    print('time:', datetime.fromtimestamp(int(min5ts)), '; time2:', datetime.fromtimestamp(int(min5ts2)))
                    sys.exit()

                volume = lline[5].split('.')[0]

                if float(lline[4]) > float(lline[1]) and int(volume) >= step and int(i / 5) > cendel:

                    # print('покупаю по текущей цене')
                    # print(i,' - ',int(i/5),' - ', cendel)
                    # print('time:',datetime.fromtimestamp(int(min5ts)),'; time2:', datetime.fromtimestamp(int(min5ts2)))
                    # print('time:',datetime.fromtimestamp(int(min5ts)),'; volume:', lline[5])

                    # lline_buyday = r.hget(coin + '_' + interval, min5ts2)
                    # lline_buyday = ast.literal_eval(lline_buyday.decode())
                    price = float(lline[4])
                    cash = cash - (cash * 0.000750)
                    akcii = cash / price

                    # продаю
                    min5ts_sell = str((min5_now + timedelta(minutes=-i + (cendel * 5))).timestamp()).split('.')[0]

                    if not r.hexists(coin + '_' + interval, min5ts_sell):
                        redis_check_back_5m(r, coin, interval, min5_now)

                    # ищем в промежутке покупки и продажи, есть ли свеча меньше стопа и продаем тогда
                    min5ts_stop = min5ts

                    # print('свеча покупки ',i,' : ', datetime.fromtimestamp(int(min5ts_stop)))
                    # print('свеча продажи', datetime.fromtimestamp(int(min5ts_sell)))
                    # print('min5ts_stop:', min5ts_stop)
                    # print('min5ts_sell:', int(min5ts_sell))
                    # print('min5ts_stop:', int(str(min5ts_stop.timestamp()).split('.')[0]))
                    # print('min5ts_sell:', int(min5ts_sell))

                    price_stop = False
                    cen = 1
                    while int(min5ts_stop) < int(min5ts_sell):
                        min5ts_stop = str((datetime.fromtimestamp(int(min5ts_stop)) + timedelta(minutes=5)).timestamp()).split('.')[0]
                        # print('min5ts_stop while ts:', min5ts_stop)
                        # print('min5ts_stop while data:', datetime.fromtimestamp(int(min5ts_stop)))
                        lline_stop = r.hget(coin + '_' + interval, min5ts_stop)
                        lline_stop = ast.literal_eval(lline_stop.decode())
                        # min5ts_stop = datetime.strptime(min5ts_stop, '%Y-%m-%d %H:%M:%S')
                        if float(lline_stop[4]) <= float(lline[3]):
                            cendel_in = cen
                            price_stop = True
                            # print('вылетиле по стопу и свеча ', cendel_in)
                            break
                        cen += 1

                    # print('time:', datetime.fromtimestamp(int(min5ts2)), '; time2:',datetime.fromtimestamp(int(min5ts_sell)))
                    lline_sellday = r.hget(coin + '_' + interval, min5ts_sell)

                    try:
                        lline_sellday = ast.literal_eval(lline_sellday.decode())
                    except AttributeError:
                        print('begin:', i - 5)
                        print('time:', datetime.fromtimestamp(int(min5ts2)))
                        print('end:', i)
                        print('time:', datetime.fromtimestamp(int(min5ts_sell)))
                        print('===============================================')
                        if r.hexists(coin + '_' + interval, min5ts_sell):
                            print('=====================Есть==================')
                        print('===============================================')
                        sys.exit()

                    price2 = float(lline_sellday[4])
                    if price2 <= float(lline[3]) or price_stop:
                        price2 = float(lline[3])
                    cash = akcii * price2
                    cash = cash - (cash * 0.000750)
                    # print('свеча i ', i)
                    k = i - (cendel_in * 5)
                    # print('свеча выхода ', k)
                    # print('====================')
                    # print('buy: ', price, '; sell: ', price2, '; cash: ',cash)

            if cash == 100000: break
            allvolume_dict[step] = round(cash, 1)

        allcendel_dict[cendel] = volume_max_check(allvolume_dict)

        # print('stg ', cendel, ' : ', allcendel_dict[cendel])
        # print('====================================')

    dictt['stg'] = 'vc7'  # volume and cendel
    dictt['interval'] = '5m'
    dictt['max'] = check_max_stg(allcendel_dict)
    dictt['data'] = allcendel_dict
    dictt['coin'] = coin
    # print(dictt)
    if not dictt['max']:
        dictt['max'] = None
        return dictt
    return dictt


# Стратегия 7

def strategy_7_binance_5m(r, coin, interval, cash, min_volume, max_volume, range_volume):
    """
    Если свеча в плюс, то
    покупаем при открытии следующий свечи, и держим в цикле от 1 свечи до 10 и выходим (при разных объемах). и показываем лучший вход

    скопировано с 3-й стратегии изначально

    берем обьем 200
    если плюсовая свеча, объем указанный, покупаем по 2 свечи - проходим все 500 свечей
    если плюсовая свеча, объем указанный, покупаем по 3 свечи - проходим все 500 свечей

    стоп ставим лоу купленной свечи

    """

    hold_money = False  # держу акции
    buy_flag = False
    allvolume_dict = {}
    allcendel_dict = {}
    dictt = {}

    now = datetime.now()
    print('stg 7: ', now)
    if len(str(now.minute)) > 1:
        if int(str(now.minute)[1]) < 5:
            need_minute = int(str(now.minute)[0] + '0')
        else:
            need_minute = int(str(now.minute)[0] + '5')
    else:
        if int(now.minute) < 5:
            need_minute = 0
        else:
            need_minute = 5

    cash = 0
    for cendel in range(5, 15):
        # print('cendel : ',cendel)
        for step in range(min_volume, max_volume, range_volume):
            cash = 100000
            min5_now = datetime.combine(date.today(), time(now.hour, need_minute, 0))

            # ts_5min_now = str(datetime.combine(date.today(), time(now.hour, need_minute, 0)).timestamp()).split('.')[0]
            k = 2505
            for i in range(2500, 5, -5):
                if i >= k: continue
                # print('Свеча входа ',i)
                min5ts = str((min5_now + timedelta(minutes=-i)).timestamp()).split('.')[0]
                min5ts2 = str((min5_now + timedelta(minutes=-i + 5)).timestamp()).split('.')[0]

                if not r.hexists(coin + '_' + interval, min5ts):
                    redis_check_back_5m(r, coin, interval, min5_now)
                elif not r.hexists(coin + '_' + interval, min5ts2):
                    redis_check_back_5m(r, coin, interval, min5_now)

                lline = r.hget(coin + '_' + interval, min5ts)
                # print(i,':',min5ts, ' : ', min5_now + timedelta(minutes=-i), ' : ', lline)

                try:
                    lline = ast.literal_eval(lline.decode())
                except AttributeError:
                    print('error')
                    redis_check_back_5m(r, coin, interval, min5_now, checkall=True)
                    print(lline)
                    print(i, ' - ', int(i / 5), ' - ', cendel)
                    print('time:', datetime.fromtimestamp(int(min5ts)), '; time2:', datetime.fromtimestamp(int(min5ts2)))
                    sys.exit()

                volume = lline[5].split('.')[0]

                if float(lline[4]) > float(lline[1]) and int(volume) >= step and int(i / 5) > cendel:

                    # print('покупаю по текущей цене')
                    # print(i,' - ',int(i/5),' - ', cendel)
                    # print('time:',datetime.fromtimestamp(int(min5ts)),'; time2:', datetime.fromtimestamp(int(min5ts2)))
                    # print('time:',datetime.fromtimestamp(int(min5ts)),'; volume:', lline[5])

                    # lline_buyday = r.hget(coin + '_' + interval, min5ts2)
                    # lline_buyday = ast.literal_eval(lline_buyday.decode())
                    price = float(lline[4])
                    cash = cash - (cash * 0.000750)
                    akcii = cash / price

                    # продаю
                    min5ts_sell = str((min5_now + timedelta(minutes=-i + (cendel * 5))).timestamp()).split('.')[0]

                    # print('свеча покупки ',i,' : ', datetime.fromtimestamp(int(min5ts)))
                    # print('свеча продажи', datetime.fromtimestamp(int(min5ts_sell)))

                    if not r.hexists(coin + '_' + interval, min5ts_sell):
                        redis_check_back_5m(r, coin, interval, min5_now)
                    # print('time:', datetime.fromtimestamp(int(min5ts2)), '; time2:',datetime.fromtimestamp(int(min5ts_sell)))
                    lline_sellday = r.hget(coin + '_' + interval, min5ts_sell)

                    try:
                        lline_sellday = ast.literal_eval(lline_sellday.decode())
                    except AttributeError:
                        print('begin:', i - 5)
                        print('time:', datetime.fromtimestamp(int(min5ts2)))
                        print('end:', i)
                        print('time:', datetime.fromtimestamp(int(min5ts_sell)))
                        print('===============================================')
                        if r.hexists(coin + '_' + interval, min5ts_sell):
                            print('=====================Есть==================')
                        print('===============================================')
                        sys.exit()

                    price2 = float(lline_sellday[4])
                    if price2 <= float(lline[3]):
                        price2 = float(lline[3])
                    cash = akcii * price2
                    cash = cash - (cash * 0.000750)
                    # print('свеча i ', i)
                    k = i - (cendel * 5)
                    # print('свеча выхода ', k)
                    # print('====================')
                    # print('buy: ', price, '; sell: ', price2, '; cash: ',cash)

            if cash == 100000: break
            allvolume_dict[step] = round(cash, 1)

        allcendel_dict[cendel] = volume_max_check(allvolume_dict)

        # print('stg ', cendel, ' : ', allcendel_dict[cendel])
        # print('====================================')

    dictt['stg'] = 'vc7'  # volume and cendel
    dictt['interval'] = '5m'
    dictt['max'] = check_max_stg(allcendel_dict)
    dictt['data'] = allcendel_dict
    dictt['coin'] = coin
    # print(dictt)
    if not dictt['max']:
        dictt['max'] = None
        return dictt
    return dictt


#
# СТРАТЕГИИ при загрузке с binance 5 min
#

def strategy_1_binance_5m(r, coin, interval, cash):
    """
    Если свеча 5 мин в начале в плюс
    покупаем при открытии следующий свечи, продаем при наступлении минусового дня
    """

    hold_money = False  # держу акции
    buy_flag = False
    dictt = {}
    now = datetime.now()
    print('stg 1: ', now)
    if len(str(now.minute)) > 1:
        if int(str(now.minute)[1]) < 5:
            need_minute = int(str(now.minute)[0] + '0')
        else:
            need_minute = int(str(now.minute)[0] + '5')
    else:
        if int(now.minute) < 5:
            need_minute = 0
        else:
            need_minute = 5

    min5_now = datetime.combine(date.today(), time(now.hour, need_minute, 0))
    ts_5min_now = str(datetime.combine(date.today(), time(now.hour, need_minute, 0)).timestamp()).split('.')[0]

    for i in range(2500, 5, -5):

        min5ts = str((min5_now + timedelta(minutes=-i)).timestamp()).split('.')[0]
        min5ts2 = str((min5_now + timedelta(minutes=-i + 5)).timestamp()).split('.')[0]
        if not r.hexists(coin + '_' + interval, min5ts) or not r.hexists(coin + '_' + interval, min5ts2):
            redis_check_back_5m(r, coin, interval, min5_now)

        lline = r.hget(coin + '_' + interval, min5ts)
        # print(min5ts, ' : ', min5_now + timedelta(minutes=-i),' : ', lline)
        lline = ast.literal_eval(lline.decode())

        if buy_flag and not hold_money:
            price = float(lline[1])
            cash = cash - (cash * 0.001)
            akcii = cash / price
            # print('Купил акции ', line['data'], ': ', akcii, '; Процент: ', cash * 0.001 )
            hold_money = True

        if not buy_flag and hold_money:
            cash = akcii * float(lline[1])
            cash = cash - (cash * 0.001)
            # print('Продал акции ', line['data'], ': ', cash, '; Процент: ', cash * 0.001)
            hold_money = False

        # определяем красная ли свеча
        # print('min2ts: ', datetime.fromtimestamp(int(min5ts)))
        # print('min2ts2: ', datetime.fromtimestamp(int(min5ts2)))

        # print(i)
        lline2 = r.hget(coin + '_' + interval, min5ts2)
        # print(lline2)
        lline2 = ast.literal_eval(lline2.decode())
        updown = float(lline[4]) - float(lline2[4])

        # datetime.fromtimestamp(int(str(lline[0]).split('.')[0])).strftime('%Y-%m-%d %H:%M:%S')
        # tm2 = datetime.fromtimestamp(int(str(lline2[0])[:-3])).strftime('%Y-%m-%d %H:%M:%S')
        # tm1 = datetime.fromtimestamp(int(str(lline[0])[:-3])).strftime('%Y-%m-%d %H:%M:%S')
        # print(tm1,' :', lline[1],' - ', tm2,':',lline2[1],';')
        if '-' not in str(updown):
            buy_flag = True
        if '-' in str(updown):
            buy_flag = False

    if hold_money:
        cash = akcii * price
        cash = cash - (cash * 0.001)
    dictt['stg'] = 'one'
    dictt['interval'] = '5m'
    dictt['max'] = round(cash, 1)

    return dictt


def strategy_2_binance_5m(r, coin, interval, cash):
    """
    Если свеча в плюс
    покупаем при открытии следующий свечи, продаем в конце нее
    """
    hold_money = False  # держу акции
    buy_flag = False
    dictt = {}
    now = datetime.now()
    print('stg 2: ', now)
    if len(str(now.minute)) > 1:
        if int(str(now.minute)[1]) < 5:
            need_minute = int(str(now.minute)[0] + '0')
        else:
            need_minute = int(str(now.minute)[0] + '5')
    else:
        if int(now.minute) < 5:
            need_minute = 0
        else:
            need_minute = 5

    min5_now = datetime.combine(date.today(), time(now.hour, need_minute, 0))
    ts_5min_now = str(datetime.combine(date.today(), time(now.hour, need_minute, 0)).timestamp()).split('.')[0]

    tag = False

    for i in range(2500, 5, -5):
        if i == 0: break
        min5ts = str((min5_now + timedelta(minutes=-i)).timestamp()).split('.')[0]
        min5ts2 = str((min5_now + timedelta(minutes=-i + 5)).timestamp()).split('.')[0]
        if not r.hexists(coin + '_' + interval, min5ts) or not r.hexists(coin + '_' + interval, min5ts2):
            print('Пытаемся скачать свечи')
            redis_check_back_5m(r, coin, interval, min5_now)

        lline = r.hget(coin + '_' + interval, min5ts)
        # print(min5ts, ' : ', min5_now + timedelta(minutes=-i),' : ', lline)
        lline = ast.literal_eval(lline.decode())
        price = float(lline[4])

        if hold_money:
            cash = akcii * price
            cash = cash - (price * 0.001)
            hold_money = False
            buy_flag = False

        if buy_flag:
            cash = cash - (price * 0.001)
            akcii = cash / price
            hold_money = True

        # print('min2ts2: ', datetime.fromtimestamp(int(min5ts2)))
        lline2 = r.hget(coin + '_' + interval, min5ts2)
        lline2 = ast.literal_eval(lline2.decode())
        updown = float(lline[4]) - float(lline2[4])

        if '-' not in str(updown) and not buy_flag:
            buy_flag = True
            tag = True

    if tag:
        if hold_money:
            cash = akcii * price
            cash = cash - (cash * 0.001)

    dictt['stg'] = 'one'
    dictt['interval'] = '5m'
    dictt['max'] = round(cash, 1)
    return dictt


# Стратегия 3

def strategy_3_binance_5m(r, coin, interval, cash, min_volume, max_volume, range_volume):
    """
    Если свеча в плюс и объем большой , то
    покупаем при открытии следующий день, и держим до первого минуса

    Объем проходит через цикл, и выбирается лучший показатель объема
    """

    hold_money = False  # держу акции
    buy_flag = False
    allvolume_dict = {}
    dictt = {}

    now = datetime.now()
    print('stg 3: ', now)
    if len(str(now.minute)) > 1:
        if int(str(now.minute)[1]) < 5:
            need_minute = int(str(now.minute)[0] + '0')
        else:
            need_minute = int(str(now.minute)[0] + '5')
    else:
        if int(now.minute) < 5:
            need_minute = 0
        else:
            need_minute = 5

    for step in range(min_volume, max_volume, range_volume):
        cash = 100000
        hold_money = False
        tag = False
        min5_now = datetime.combine(date.today(), time(now.hour, need_minute, 0))

        # ts_5min_now = str(datetime.combine(date.today(), time(now.hour, need_minute, 0)).timestamp()).split('.')[0]
        for i in range(2500, 5, -5):
            min5ts = str((min5_now + timedelta(minutes=-i)).timestamp()).split('.')[0]
            min5ts2 = str((min5_now + timedelta(minutes=-i + 5)).timestamp()).split('.')[0]
            if not r.hexists(coin + '_' + interval, min5ts) or not r.hexists(coin + '_' + interval, min5ts2):
                redis_check_back_5m(r, coin, interval, min5_now)

            lline = r.hget(coin + '_' + interval, min5ts)
            # print(i,':',min5ts, ' : ', min5_now + timedelta(minutes=-i), ' : ', lline)
            lline = ast.literal_eval(lline.decode())
            volume = lline[5].split('.')[0]

            # покупаю если не куплено еще
            if buy_flag and not hold_money:
                price = float(lline[1])
                cash = cash - (cash * 0.001)
                akcii = cash / price
                hold_money = True
                # print(i,']buy flag[',step, '] : ', akcii,' - ', cash)

            if not buy_flag and hold_money:
                price = float(lline[4])
                cash = akcii * price
                cash = cash - (cash * 0.001)
                hold_money = False
                # print(i, ']not buy flag[', step, '] : ', akcii, ' - ', cash)

            # print(i-5, ': ', min5_now + timedelta(minutes=-i-5))
            lline2 = r.hget(coin + '_' + interval, min5ts2)
            lline2 = ast.literal_eval(lline2.decode())
            updown = float(lline[4]) - float(lline2[4])
            # print(lline[1],'-',lline2[1],'; ',updown)

            if '-' not in str(updown) and int(volume) >= step:
                buy_flag = True
                tag = True
            if '-' in str(updown):
                buy_flag = False

        if tag:
            if hold_money:
                cash = akcii * price
                cash = cash - (cash * 0.001)

            allvolume_dict[step] = round(cash, 1)

        else:
            break

    dictt['stg'] = 'volume'
    dictt['interval'] = '5m'
    dictt['period'] = allvolume_dict
    dictt['volume'] = volume_max_check(dictt['period'])

    max = 0
    for key, value in allvolume_dict.items():
        if value > max:
            max = value
    dictt['max'] = max

    return dictt


# Стратегия 4

def strategy_4_binance_5m(r, coin, interval, cash, min_volume, max_volume, range_volume):
    """
    Если свеча в плюс и проходим объем , то
    покупаем при открытии следующий день, и держим до первого минуса ИЛИ если цена ниже цены покупки

    Объем проходит через цикл, и выбирается лучший показатель объема
    """

    hold_money = False  # держу акции
    buy_flag = False
    allvolume_dict = {}
    dictt = {}

    now = datetime.now()
    print('stg 4: ', now)
    if len(str(now.minute)) > 1:
        if int(str(now.minute)[1]) < 5:
            need_minute = int(str(now.minute)[0] + '0')
        else:
            need_minute = int(str(now.minute)[0] + '5')
    else:
        if int(now.minute) < 5:
            need_minute = 0
        else:
            need_minute = 5

    for step in range(min_volume, max_volume, range_volume):
        cash = 100000
        price_before = 0
        hold_money = False
        tag = False
        min5_now = datetime.combine(date.today(), time(now.hour, need_minute, 0))

        # ts_5min_now = str(datetime.combine(date.today(), time(now.hour, need_minute, 0)).timestamp()).split('.')[0]
        for i in range(2500, 5, -5):
            min5ts = str((min5_now + timedelta(minutes=-i)).timestamp()).split('.')[0]
            min5ts2 = str((min5_now + timedelta(minutes=-i + 5)).timestamp()).split('.')[0]
            if not r.hexists(coin + '_' + interval, min5ts) or not r.hexists(coin + '_' + interval, min5ts2):
                redis_check_back_5m(r, coin, interval, min5_now)

            lline = r.hget(coin + '_' + interval, min5ts)
            # print(i,':',min5ts, ' : ', min5_now + timedelta(minutes=-i), ' : ', lline)
            lline = ast.literal_eval(lline.decode())
            volume = lline[5].split('.')[0]

            # покупаю если не куплено еще
            if buy_flag and not hold_money:
                price = float(lline[1])
                cash = cash - (cash * 0.001)
                akcii = cash / price

                price_before = price  # сюда сохраняем предыдузую цену, что сравнить в момент продажи акций с текущей ценой

                hold_money = True
                # print(i,']buy flag[',step, '] : ', akcii,' - ', cash)

            if not buy_flag and hold_money:
                price = float(lline[4])
                if price_before < price:  # здесь у нас идет по сути stop loss по закупочной цене (можно добавить сюда несколько пунктов)
                    cash = akcii * price
                else:
                    cash = akcii * price_before
                cash = cash - (cash * 0.001)
                hold_money = False
                # print(i, ']not buy flag[', step, '] : ', akcii, ' - ', cash)

            # print(i-5, ': ', min5_now + timedelta(minutes=-i-5))
            lline2 = r.hget(coin + '_' + interval, min5ts2)
            lline2 = ast.literal_eval(lline2.decode())
            updown = float(lline[4]) - float(lline2[4])
            # print(lline[1],'-',lline2[1],'; ',updown)

            if '-' not in str(updown) and int(volume) >= step:
                buy_flag = True
                tag = True
            if '-' in str(updown):
                buy_flag = False

        if tag:
            if hold_money:
                cash = akcii * price
                cash = cash - (cash * 0.001)

            allvolume_dict[step] = round(cash, 1)

        else:
            break

    dictt['stg'] = 'volume'
    dictt['interval'] = '5m'
    dictt['period'] = allvolume_dict
    dictt['volume'] = volume_max_check(dictt['period'])

    max = 0
    for key, value in allvolume_dict.items():
        if value > max:
            max = value
    dictt['max'] = max

    return dictt


# Стратегия 5

def strategy_5_binance_5m(r, coin, interval, cash, min_volume, max_volume, range_volume):
    """
    Если свеча в плюс, то
    покупаем при открытии следующий день, и держим до первого дня, который пробивает цену предыдущей свечи

    Объем проходит через цикл, и выбирается лучший показатель объема
    """

    hold_money = False  # держу акции
    buy_flag = False
    allvolume_dict = {}
    dictt = {}

    now = datetime.now()
    print('stg 5: ', now)
    if len(str(now.minute)) > 1:
        if int(str(now.minute)[1]) < 5:
            need_minute = int(str(now.minute)[0] + '0')
        else:
            need_minute = int(str(now.minute)[0] + '5')
    else:
        if int(now.minute) < 5:
            need_minute = 0
        else:
            need_minute = 5

    for step in range(min_volume, max_volume, range_volume):
        cash = 100000
        price_before = 0
        hold_money = False
        tag = False
        min5_now = datetime.combine(date.today(), time(now.hour, need_minute, 0))

        # ts_5min_now = str(datetime.combine(date.today(), time(now.hour, need_minute, 0)).timestamp()).split('.')[0]
        for i in range(2500, 5, -5):
            min5ts = str((min5_now + timedelta(minutes=-i)).timestamp()).split('.')[0]
            min5ts2 = str((min5_now + timedelta(minutes=-i + 5)).timestamp()).split('.')[0]
            if not r.hexists(coin + '_' + interval, min5ts) or not r.hexists(coin + '_' + interval, min5ts2):
                redis_check_back_5m(r, coin, interval, min5_now)

            lline = r.hget(coin + '_' + interval, min5ts)
            # print(i,':',min5ts, ' : ', min5_now + timedelta(minutes=-i), ' : ', lline)
            lline = ast.literal_eval(lline.decode())
            volume = lline[5].split('.')[0]

            # покупаю если не куплено еще
            if buy_flag and not hold_money:
                price = float(lline[1])
                cash = cash - (cash * 0.001)
                akcii = cash / price

                price_before = price  # сюда сохраняем предыдузую цену, что сравнить в момент продажи акций с текущей ценой

                hold_money = True
                # print(i,']buy flag[',step, '] : ', akcii,' - ', cash)

            if not buy_flag and hold_money:
                if price_before < price:  # здесь у нас идет по сути stop loss по закупочной цене (можно добавить сюда несколько пунктов)
                    price = float(lline[4])
                    cash = akcii * price
                else:
                    cash = akcii * price_before
                cash = cash - (cash * 0.001)
                hold_money = False
                # print(i, ']not buy flag[', step, '] : ', akcii, ' - ', cash)

            # print('line:',datetime.fromtimestamp(int(min5ts)),'; line2:', datetime.fromtimestamp(int(min5ts2)))
            # print(i-5, ': ', min5_now + timedelta(minutes=-i-5))
            lline2 = r.hget(coin + '_' + interval, min5ts2)
            lline2 = ast.literal_eval(lline2.decode())
            updown = float(lline[1]) - float(lline2[1])

            # print(lline[1],'-',lline2[1],'; ',updown)

            if float(lline[1]) < float(lline[4]) and int(volume) >= step and not buy_flag:
                buy_flag = True
                tag = True

            if lline[3] < lline2[4] and buy_flag and not tag:
                buy_flag = False

            if float(lline[1]) > float(lline[4]) and buy_flag:
                buy_flag = False

        if tag:
            if hold_money:
                cash = akcii * price
                cash = cash - (cash * 0.001)

            allvolume_dict[step] = round(cash, 1)

        else:
            break

    dictt['stg'] = 'volume'
    dictt['interval'] = '5m'
    dictt['period'] = allvolume_dict
    dictt['volume'] = volume_max_check(dictt['period'])

    max = 0
    for key, value in allvolume_dict.items():
        if value > max:
            max = value
    dictt['max'] = max

    return dictt


# Стратегия 6

def strategy_6_binance_5m(r, coin, interval, cash, min_volume, max_volume, range_volume):
    """
    Если свеча в плюс, то
    покупаем при открытии следующий свечи, и держим в цикле от 1 свечи до 20 и выходим (при разных объемах). и показываем лучший вход

    скопировано с 3-й стратегии изначально

    берем обьем 200
    если плюсовая свеча, объем указанный, покупаем по 2 свечи - проходим все 500 свечей
    если плюсовая свеча, объем указанный, покупаем по 3 свечи - проходим все 500 свечей

    """

    hold_money = False  # держу акции
    buy_flag = False
    allvolume_dict = {}
    allcendel_dict = {}
    dictt = {}

    now = datetime.now()
    print('stg 6: ', now)
    if len(str(now.minute)) > 1:
        if int(str(now.minute)[1]) < 5:
            need_minute = int(str(now.minute)[0] + '0')
        else:
            need_minute = int(str(now.minute)[0] + '5')
    else:
        if int(now.minute) < 5:
            need_minute = 0
        else:
            need_minute = 5

    cash = 0
    for cendel in range(1, 10):

        for step in range(min_volume, max_volume, range_volume):
            cash = 100000
            min5_now = datetime.combine(date.today(), time(now.hour, need_minute, 0))

            # ts_5min_now = str(datetime.combine(date.today(), time(now.hour, need_minute, 0)).timestamp()).split('.')[0]
            for i in range(2500, 5, -5):
                min5ts = str((min5_now + timedelta(minutes=-i)).timestamp()).split('.')[0]
                min5ts2 = str((min5_now + timedelta(minutes=-i + 5)).timestamp()).split('.')[0]

                if not r.hexists(coin + '_' + interval, min5ts) or not r.hexists(coin + '_' + interval, min5ts2):
                    redis_check_back_5m(r, coin, interval, min5_now)

                lline = r.hget(coin + '_' + interval, min5ts)
                # print(i,':',min5ts, ' : ', min5_now + timedelta(minutes=-i), ' : ', lline)
                lline = ast.literal_eval(lline.decode())
                volume = lline[5].split('.')[0]

                if float(lline[4]) > float(lline[1]) and int(volume) >= step and int(i / 5) > cendel:

                    # покупаю по текущей цене
                    # print(i,' - ',int(i/5),' - ', cendel)
                    # print('time:',datetime.fromtimestamp(int(min5ts)),'; time2:', datetime.fromtimestamp(int(min5ts2)))

                    # lline_buyday = r.hget(coin + '_' + interval, min5ts2)
                    # lline_buyday = ast.literal_eval(lline_buyday.decode())

                    price = float(lline[4])
                    cash = cash - (cash * 0.001)
                    akcii = cash / price

                    # продаю
                    min5ts_sell = str((min5_now + timedelta(minutes=-i + (cendel * 5))).timestamp()).split('.')[0]
                    if not r.hexists(coin + '_' + interval, min5ts_sell):
                        redis_check_back_5m(r, coin, interval, min5_now)
                    # print('time:', datetime.fromtimestamp(int(min5ts2)), '; time2:',datetime.fromtimestamp(int(min5ts_sell)))
                    lline_sellday = r.hget(coin + '_' + interval, min5ts_sell)

                    try:
                        lline_sellday = ast.literal_eval(lline_sellday.decode())
                    except AttributeError:
                        print('begin:', i - 5)
                        print('time:', datetime.fromtimestamp(int(min5ts2)))
                        print('end:', i)
                        print('time:', datetime.fromtimestamp(int(min5ts_sell)))
                        print('===============================================')
                        if r.hexists(coin + '_' + interval, min5ts_sell):
                            print('=====================Есть==================')
                        print('===============================================')
                        sys.exit()

                    price = float(lline_sellday[4])
                    cash = akcii * price
                    cash = cash - (cash * 0.001)
                    i = i - 10 - (cendel * 5)

            if cash == 100000: break
            allvolume_dict[step] = round(cash, 1)

        allcendel_dict[cendel] = volume_max_check(allvolume_dict)

        print(cendel, ' : ', allcendel_dict[cendel])
        print('====================================')

    dictt['stg'] = 'vc'  # volume and cendel
    dictt['interval'] = '5m'
    dictt['max'] = 1
    dictt['data'] = allcendel_dict
    # dictt['volume'] = vc_max_check(dictt['period'])

    return dictt


#
# СТРАТЕГИИ при загрузке с binance 1 day
#

def strategy_1_binance_1d(r, coin, interval, period, cash):
    """
    Если день в плюс
    покупаем при открытии следующий день, продаем при наступлении минусового дня
    """

    hold_money = False  # держу акции
    buy_flag = False
    dictt = {}

    for i in reversed(range(int(period))):
        if i == 0: break  # отключаем текущий день
        dts = str(datetime.combine(date.today() + timedelta(days=-i), time(3, 0, 0)).timestamp()).split('.')[0]
        dts2 = str(datetime.combine(date.today() + timedelta(days=-i + 1), time(3, 0, 0)).timestamp()).split('.')[0]
        if not r.hexists(coin + '_' + interval, dts) or not r.hexists(coin + '_' + interval, dts2):
            redis_check_back_day(r, coin, interval, int(period))

        lline = r.hget(coin + '_' + interval, dts)
        lline = ast.literal_eval(lline.decode())
        if buy_flag and not hold_money:
            price = float(lline[1])
            cash = cash - (cash * 0.001)
            akcii = cash / price
            # print('Купил акции ', line['data'], ': ', akcii, '; Процент: ', cash * 0.001 )
            hold_money = True

        if not buy_flag and hold_money:
            cash = akcii * float(lline[1])
            cash = cash - (cash * 0.001)
            # print('Продал акции ', line['data'], ': ', cash, '; Процент: ', cash * 0.001)
            hold_money = False

        lline2 = r.hget(coin + '_' + interval, dts2)
        lline2 = ast.literal_eval(lline2.decode())
        updown = float(lline[1]) - float(lline2[1])
        # print(lline[1],'-',lline2[1],'; ',updown)
        if '-' not in str(updown):
            buy_flag = True
        if '-' in str(updown):
            buy_flag = False

    if hold_money:
        cash = akcii * price
        cash = cash - (cash * 0.001)
    dictt['stg'] = 'one'
    dictt['max'] = round(cash, 1)
    return dictt


def strategy_2_binance(r, coin, interval, period, cash):
    """
    Если день в плюс
    покупаем при открытии следующий день, продаем в конце дня
    """

    hold_money = False  # держу акции
    buy_flag = False
    dictt = {}

    for i in reversed(range(int(period))):
        if i == 0: break  # отключаем текущий день
        dts = str(datetime.combine(date.today() + timedelta(days=-i), time(3, 0, 0)).timestamp()).split('.')[0]
        dts2 = str(datetime.combine(date.today() + timedelta(days=-i + 1), time(3, 0, 0)).timestamp()).split('.')[0]
        if not r.hexists(coin + '_' + interval, dts) or not r.hexists(coin + '_' + interval, dts2):
            redis_check_back_day(r, coin, interval, period)

        lline = r.hget(coin + '_' + interval, dts)
        lline = ast.literal_eval(lline.decode())
        price = float(lline[1])

        if hold_money:
            cash = akcii * price
            cash = cash - (price * 0.001)
            hold_money = False
            buy_flag = False

        if buy_flag:
            cash = cash - (price * 0.001)
            akcii = cash / price
            hold_money = True

        dts2 = str(datetime.combine(date.today() + timedelta(days=-(i + 1)), time(3, 0, 0)).timestamp()).split('.')[0]
        lline2 = r.hget(coin + '_' + interval, dts2)
        lline2 = ast.literal_eval(lline2.decode())
        updown = float(lline[1]) - float(lline2[1])

        if '-' not in str(updown) and not buy_flag:
            buy_flag = True

    dictt['stg'] = 'one'
    dictt['max'] = round(cash, 1)
    return dictt


# Стратегия 3
#
def strategy_3_binance(r, coin, interval, period, cash, min_volume, max_volume, range_volume):
    """
    Если день в плюс и объем большой (именно btc), то
    покупаем при открытии следующий день, и держим до первого минуса

    Объем проходит через цикл, и выбирается лучший показатель объема
    """

    hold_money = False  # держу акции
    buy_flag = False
    allvolume_dict = {}
    dictt = {}

    for step in range(min_volume, max_volume, range_volume):
        cash = 100000
        hold_money = False
        tag = False
        for i in reversed(range(int(period))):
            if i == 0: break  # отключаем текущий день
            dts = str(datetime.combine(date.today() + timedelta(days=-i), time(3, 0, 0)).timestamp()).split('.')[0]
            dts2 = str(datetime.combine(date.today() + timedelta(days=-i + 1), time(3, 0, 0)).timestamp()).split('.')[0]
            if not r.hexists(coin + '_' + interval, dts) or not r.hexists(coin + '_' + interval, dts2):
                redis_check_back_day(r, coin, interval, period)

            lline = r.hget(coin + '_' + interval, dts)
            lline = ast.literal_eval(lline.decode())
            price = float(lline[1])
            volume = lline[5].split('.')[0]

            # покупаю если не куплено еще
            if buy_flag and not hold_money:
                cash = cash - (cash * 0.001)
                akcii = cash / price
                hold_money = True
                # print(i,']buy flag[',step, '] : ', akcii,' - ', cash)

            if not buy_flag and hold_money:
                cash = akcii * price
                cash = cash - (cash * 0.001)
                hold_money = False
                # print(i, ']not buy flag[', step, '] : ', akcii, ' - ', cash)

            dts2 = str(datetime.combine(date.today() + timedelta(days=-(i + 1)), time(3, 0, 0)).timestamp()).split('.')[0]
            lline2 = r.hget(coin + '_' + interval, dts2)
            lline2 = ast.literal_eval(lline2.decode())
            updown = float(lline[1]) - float(lline2[1])
            # print(lline[1],'-',lline2[1],'; ',updown)

            if '-' not in str(updown) and int(volume) >= step:
                buy_flag = True
                tag = True
            if '-' in str(updown):
                buy_flag = False

        if tag:
            if hold_money:
                cash = akcii * price
                cash = cash - (cash * 0.001)

            allvolume_dict[step] = round(cash, 1)

        else:
            break

    # for key,value in allvolume_dict.items():
    #    print(key,':',value)

    dictt['stg'] = 'volume'
    dictt['period'] = allvolume_dict
    dictt['volume'] = volume_max_check(dictt['period'])

    max = 0
    for key, value in allvolume_dict.items():
        if value > max:
            max = value
    dictt['max'] = max

    return dictt


#
# СТРАТЕГИИ при загрузке файлом
#

# Стратегия 1
#
def strategy_1(csvfile, cash):
    """
    Если день в плюс
    покупаем при открытии следующий день, продаем при наступлении минусового дня
    """
    hold_money = False  # держу акции
    buy_flag = False

    for line in csvfile:
        # покупаю если не куплено еще
        if buy_flag and not hold_money:
            price = line['price'].replace('.', "")
            price = float(price.replace(',', "."))
            cash = cash - (cash * 0.001)
            akcii = cash / price
            # print('Купил акции ', line['data'], ': ', akcii, '; Процент: ', cash * 0.001 )
            hold_money = True

        if not buy_flag and hold_money:
            price = line['price'].replace('.', "")
            price = float(price.replace(',', "."))
            cash = akcii * price
            cash = cash - (cash * 0.001)
            # print('Продал акции ', line['data'], ': ', cash, '; Процент: ', cash * 0.001)
            hold_money = False

        if '-' not in line['percent']:
            buy_flag = True
        if '-' in line['percent']:
            buy_flag = False

    if hold_money:
        cash = akcii * price
        cash = cash - (cash * 0.001)
    return round(cash, 1)


# Стратегия 2
#
def strategy_2(csvfile, cash):
    """
    Если день в плюс
    покупаем при открытии следующий день, продаем в конце дня
    """
    hold_money = False  # держу акции
    buy_flag = False

    for line in csvfile:
        # покупаю если не куплено еще
        if hold_money:
            price = line['open'].replace('.', "")
            price = float(price.replace(',', "."))
            cash = akcii * price
            cash = cash - (price * 0.001)
            # print('Продал акции ', line['data'], ': ', cash, '; Процент: ', cash * 0.001)

            hold_money = False
            buy_flag = False

        if buy_flag:
            price = line['open'].replace('.', "")
            price = float(price.replace(',', "."))
            cash = cash - (price * 0.001)
            akcii = cash / price
            # print('Купил акции ', line['data'], ': ', akcii, '; Процент: ', cash * 0.001)
            hold_money = True

        if '-' not in line['percent'] and not buy_flag:
            buy_flag = True

    return round(cash, 1)


# Стратегия 3
#
def strategy_3(file_stream, cash, min_volume, max_volume, range_volume):
    """
    Если день в плюс и объем большой (именно btc), то
    покупаем при открытии следующий день, и держим до первого минуса

    Объем проходит через цикл, и выбирается лучший показатель объема
    """
    cash_dict = {}

    file_stream.seek(0)
    csvfile = read_csv(file_stream, ',')
    next(csvfile)

    hold_money = False  # держу акции
    buy_flag = False
    allvolume_dict = {}

    for step in range(min_volume, max_volume, range_volume):
        i = 0
        for line in csvfile:
            volume = line['volume'].replace(',', "")
            volume = int(volume.replace('K', ""))

            # покупаю если не куплено еще
            if buy_flag and not hold_money:
                price = line['price'].replace('.', "")
                price = float(price.replace(',', "."))
                cash = cash - (cash * 0.001)
                akcii = cash / price
                # print('Купил акции ', line['data'], ': ', akcii, '; Процент: ', cash * 0.001 )
                hold_money = True

            if not buy_flag and hold_money:
                price = line['price'].replace('.', "")
                price = float(price.replace(',', "."))
                cash = akcii * price
                cash = cash - (cash * 0.001)
                # print('Продал акции ', line['data'], ': ', cash, '; Процент: ', cash * 0.001)
                hold_money = False

            if '-' not in line['percent'] and volume >= step:
                print('tyt')
                buy_flag = True
                i = i + 1
            if '-' in line['percent']:
                buy_flag = False

        if i > 0:
            print(i)
            if hold_money:
                cash = akcii * price
                cash = cash - (cash * 0.001)

            allvolume_dict[step] = round(cash, 1)

            cash = 100000
            file_stream.seek(0)
            next(csvfile)

        else:
            break

    for key, value in allvolume_dict.items():
        print(key, ':', value)

    return allvolume_dict



