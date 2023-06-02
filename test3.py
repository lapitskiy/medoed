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
