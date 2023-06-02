import redis
from datetime import datetime, timedelta, date, time
from time import sleep
from binance_api import Binance
import decimal
from settings import settings
import sys

bot = Binance(
    API_KEY='7LH6PLMh9lugIcF4cF9Gls65AQUQD3SpXdbK433bFuPnyGeDODZYjStfO86edbfd',
    API_SECRET='D7q65O3Kstmp9Is4fzpd74kylug4t6yewZ4UG8ChX7YBA1WSPWRFcbnofMsj2DrX'
)

recvGlobal = 60000

 #print('account', bot.account())
 #print(bot.ping())


# проверяем последний день записи в редисе
def redis_check_last_day_limit(coin,day,interval):
    r = redis_db_check(15)

    # время сейчас и таймстамп сейчас
    dt = datetime.strptime(str(datetime.now()).split('.')[0],'%Y-%m-%d %H:%M:%S')
    dts = str(datetime.today().timestamp()).split('.')[0]
    print('Время текущие: ', dt, ', ', dts)

    # -365
    dt365 = datetime.combine(date.today(), time(3, 0, 0))
    dt365 = datetime.strptime(str(dt365 + timedelta(days=-day)).split('.')[0],'%Y-%m-%d %H:%M:%S')
    dts365 = str(dt365.timestamp()).split('.')[0]
    print('Время 365 дней назад: ', dt365, ', ', dts365)

    # проверяем в базе наличие записи
    redis_check_back_day(r,coin,interval,day)
    result = dt
    return result


# проверяем последний день записи в редисе
def redis_db_check(dbname):
    # 12 - setting
    # 13 - margin
    # 14 - simple
    try:
        r = redis.StrictRedis(host='localhost', db=dbname)
    except redis.exceptions.ResponseError:
        print('redis err')
    return r

# проверяем последний день записи в редисе
def redis_check_back_day(r,coin,interval,day):
    for i in range(int(day)):
        now = datetime.now()
        #print(datetime.strptime(str(datetime.now().time()).split('.')[0],'%H:%M:%S'), ' = ', time(3, 0, 0))
        if i == 0 and time(now.hour, now.minute, now.second) < time(3, 0, 0): continue
        dts = str(datetime.combine(date.today()+ timedelta(days=-i), time(3, 0, 0)).timestamp()).split('.')[0]
        if not r.hexists(coin + '_' + interval, dts):
            print('Нет: ',str(datetime.fromtimestamp(int(dts)).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0], ', ', dts)
        else:
            print('Выкачиваем столько дней ', i)
            llist = bot.klines(symbol=coin, interval=interval, limit=i)
            for cendel in llist:
                coin_ts = int(str(cendel[0])[:-3])
                coin_dt = str(datetime.fromtimestamp(coin_ts).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0]
                print('Время крипты текущие: ', coin_dt, ', ', coin_ts)
                r.hsetnx(coin + '_' + interval, coin_ts, str(cendel))
            break


# проверяем последние 5м записи в редисе
def redis_check_back_5m(r,coin,interval,min5_now, checkall=False):
    print('min5_now:', str(min5_now))
    dl_cendel = False
    tag = 0
    for i in range(2500,0,-5):
        min5ts = str((min5_now + timedelta(minutes=-i)).timestamp()).split('.')[0]

        if not r.hexists(coin + '_' + interval, min5ts):
            #print('Нет: ',str(datetime.fromtimestamp(int(min5ts)).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0], ', ', min5ts)
            dl_cendel = True
            tag = i
            break

    '''
        else:
            print('Есть: ', str(datetime.fromtimestamp(int(min5ts)).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0], ', ',min5ts)
            print(r.hget(coin + '_' + interval, min5ts))
            tag = i
            break
    '''
    if checkall:
        tag = 2500

    if dl_cendel:
        tag = int(tag / 5) + 1
        print('Выкачиваем столько свечей ', tag)
        llist = bot.klines(symbol=coin, interval=interval, limit=tag)
        i = 0
        tag2 = False
        for cendel in llist:
            coin_ts = int(str(cendel[0])[:-3])
            # if not r.hexists(coin + '_' + interval, coin_ts): print('нет,создаем запись: ', str(datetime.fromtimestamp(coin_ts).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0])
            coin_dt = str(datetime.fromtimestamp(coin_ts).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0]
            r.hsetnx(coin + '_' + interval, coin_ts, str(cendel))

            # проверка на ошибку в бинансе, на гепы или пустые свечи создание пустых свечей
            if tag2:
                delta = (datetime.fromtimestamp(coin_ts) - datetime.fromtimestamp(pred_coin_ts)) / timedelta(minutes=1)
                if delta > 5:
                    print(delta)
                    print(delta/5)
                    for i in range(1,int(delta/5)):
                        coin_gap_cendel = datetime.fromtimestamp(pred_coin_ts) + timedelta(minutes=i * 5)
                        print('####')
                        print('есть гэп, создаем дублирующую свечу')
                        print(coin_gap_cendel)
                        r.hsetnx(coin + '_' + interval, int(str(coin_gap_cendel.timestamp()).split('.')[0]), str(cendel))


            # print('создаем запись :',str(datetime.fromtimestamp(coin_ts).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0])
            # print('создаем свечу: ', str(cendel))
            # print('####')


            tag2 = True # певаря свеча уже прошла
            pred_coin_ts = coin_ts
            #print('####')
            #print('создаем запись :',str(datetime.fromtimestamp(coin_ts).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0])
            #print('создаем свечу: ', str(cendel))
            #print('####')
            '''
                        if r.hexists(coin + '_' + interval, coin_ts):
                print('ЗАПИСЬ создана')
            print('####')
            print('создаем запись ',i,':',str(datetime.fromtimestamp(coin_ts).strftime('%Y-%m-%d %H:%M:%S')).split('.')[0])
            print('создаем свечу: ', str(cendel))
            print('####')
            i += 1
            '''
    #print(r.hgetall(coin + '_' + interval))

# проверяем последний день записи в редисе
def buy_order_bi():
    print('createOrder', bot.createOrder(
        symbol='BNBBTC',
        recvWindow=recvGlobal,
        side='BUY',
        type='MARKET',
        quantity=1
    ))

# получаем текущую и предыдущую пять минут - 2 свечи
def take_now_cendel_binance(limit):
    llist = bot.klines(symbol=settings.COIN, interval=settings.CENDEL_INTERVAL, limit=limit)
    return llist


###
#   функции проверки денег
###

#  хватает ли денег
def check_money_balance():
    if settings.TRADE_STG == 'STANDART':
        COIN_free = get_free_balance('BTC')
        USDT_free = get_free_balance('USDT')
        if decimal.Decimal(COIN_free) < 0.00166 and decimal.Decimal(USDT_free) < 11:
            print('COIN и USDT не достаточно для торговли, sleep+return')
            print('COIN_free ', COIN_free, '; USDT_free ', USDT_free)
            sleep(60)
            return False
        else:
            return True

    if settings.TRADE_STG == 'MARGIN_DOWN':
        ddict = bot.marginAccount(recvWindow=recvGlobal)
        COIN_free = ddict['totalAssetOfBtc']
        if decimal.Decimal(COIN_free) < 0.00166:
            print('COIN не достаточно для торговли, sleep+return')
            print('COIN_free ', COIN_free)
            sleep(60)
            return False
        else:
            return True



# проверяем сколько за доллары можно купить битка по рыночной цене  - 23 доллара / 8619 = 0,02740 битка
def check_coin_buy_BTC_in_USDT_tick(free):
    coin_tick = bot.tickerPrice(symbol=settings.COIN)
    qtyB = decimal.Decimal(free) / decimal.Decimal(coin_tick['price'])
    qtyB = decimal.Decimal(qtyB).quantize(decimal.Decimal('.00001'), rounding=decimal.ROUND_DOWN)
    return qtyB

# проверяем сколько за биток можно купить доллара по рыночной цене
#def check_coin_buy_BTC_in_USDT_tick(free):
#    coin_tick = bot.tickerPrice(symbol=settings.COIN)
#    qtyB = decimal.Decimal(free) / decimal.Decimal(coin_tick['price'])
#    qtyB = qtyB - ((qtyB / 100) * 1)
#    qtyB = decimal.Decimal(qtyB).quantize(decimal.Decimal('.00001'), rounding=decimal.ROUND_DOWN)
#    return qtyB

# проверяем сколько за доллары можно купить битка при опрделенной цене
def check_coin_buy_BTC_in_USDT_limit(free, price):
    qtyB = decimal.Decimal(free) / decimal.Decimal(price)
    qtyB = decimal.Decimal(qtyB).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN)
    return qtyB # количества битка к цене доллара

# режем проецент сколько надо
def cut_percent(count, percent):
    count = decimal.Decimal(count) - ((decimal.Decimal(count) / 100) * percent)
    count = decimal.Decimal(count).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN)
    return count

# проверяем quantity для продажи - 0,02740 битка * 8619 курс доллара к битку = 23 доллара
def check_coin_QtySell(free, coin, price):
    if decimal.Decimal(price) > 0:
        ret = decimal.Decimal(free) * decimal.Decimal(price)
        ret = ret - ((ret / 100) * 1)
        return decimal.Decimal(ret).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)
    else:
        coin_tick = bot.tickerPrice(symbol=coin)
        ret = decimal.Decimal(free) * decimal.Decimal(coin_tick['price'])
        ret = ret - ((ret / 100) * 1)
        return decimal.Decimal(ret).quantize(decimal.Decimal('.00001'), rounding=decimal.ROUND_DOWN)


# получаем сколько денег на акаунте по каждой крипте и оставляем только крипту с деньгами
def account_only_free_balance():
    llist = []
    if settings.TRADE_STG == 'STANDART':
        ddict = bot.account(recvWindow=recvGlobal)
        if ddict:
            if 'code' in ddict.keys():
                print('bin_fun account_only_free_balance ERROR ')
                return ddict
            for balance in ddict['balances']:
                if float(balance['free']) > 0 or float(balance['locked']) > 0:
                    llist.append(balance)
        return llist

    if settings.TRADE_STG == 'MARGIN_DOWN':
        ddict = bot.marginAccount(recvWindow=recvGlobal)
        #print('bin_fun margin_account_only_free_balance', ddict)
        if ddict:
            if 'code' in ddict.keys():
                print('bin_fun account_only_free_balance ERROR ')
                return ddict
            for balance in ddict['userAssets']:
                if float(balance['free']) > 0 or float(balance['locked']) > 0:
                    llist.append(balance)
        return llist




# получаем сколько денег по USDT и по BTC
# Если даем вместо coin 1, return только USDT или COIN
def get_free_balance(COIN):
    COIN_free = 0
    llist = account_only_free_balance()
    #print('get_free_balance llist', llist)

    if llist:
        for tag in llist:
            if tag['asset'] == COIN:
                COIN_free = tag['free']
    return COIN_free






###
#   функции работы с ордером
###
def all_order_cancel():
    if settings.TRADE_STG == 'STANDART':
        llist = bot.openOrders(symbol=settings.COIN,recvWindow=recvGlobal)
        #print('all_order_cancel', llist)
        for order in llist:
            print('order', order)
            print('orderId', order['orderId'])
            bot.cancelOrder(orderId=int(order['orderId']),symbol=settings.COIN, recvWindow=recvGlobal)
            print('отменен ордер: ', order)

    if settings.TRADE_STG == 'MARGIN_DOWN':
        llist = bot.marginOpenOrders(symbol=settings.COIN, recvWindow=recvGlobal)
        #print('all_order_cancel', llist)
        # print('bin_fun margin_all_order_cancel ',llist)
        for order in llist:
            bot.marginCancelOrder(orderId=int(order['orderId']), symbol=settings.COIN, recvWindow=recvGlobal)
            print('отменен ордер: ', order)

    while check_stop_loss_limit_buy_order(): # ждем пока снимется ордер
        print('Ждем снятия ордеров...')
        sleep(0.2)


def sell_all_order_cancel(coin):
    llist = bot.openOrders(symbol=settings.COIN, recvWindow=recvGlobal)
    for i in llist:
        #print('all_order_cancel', llist)
        if i['type'] == 'STOP_LOSS_LIMIT' and i['side'] == 'SELL':
            bot.cancelOrder(orderId=i['orderId'], symbol=maxstg['coin'], recvWindow=recvGlobal)


# проверяем наличие только стоп лосс sell ордеров
def check_stop_loss_sell_order():
    sleep(3)
    now = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    if settings.TRADE_STG == 'STANDART':
        llist = bot.openOrders(symbol=settings.COIN, recvWindow=recvGlobal)
        for i in llist:
            if i['type'] == 'STOP_LOSS_LIMIT' and i['side'] == 'SELL':
                return True
        print('check_stop_loss_sell_order нет стопа: ', llist)
        print('now', now)
        print('check_stop_loss_sell_order: usdt ', get_free_balance('USDT'), '; btc ', get_free_balance('BTC'))
        return False
    if settings.TRADE_STG == 'MARGIN_DOWN':
        llist = bot.marginOpenOrders(symbol=settings.COIN, recvWindow=recvGlobal)

        for i in llist:
            if i['type'] == 'STOP_LOSS_LIMIT' and i['side'] == 'BUY':
                return True
        print('check_stop_loss_sell_order нет стопа: ',llist)
        print('check_stop_loss_sell_order: usdt ', get_free_balance('USDT'), '; btc ', get_free_balance('BTC'))
        print('now', now)
        return False


def check_pump(enterPrice):
    tick = bot.tickerPrice(symbol=settings.COIN)
    f1 = abs(decimal.Decimal(enterPrice) - decimal.Decimal(tick['price']))
    f2 = (decimal.Decimal(enterPrice) / 100) * decimal.Decimal(1)

    if f1 > f2:
        #print('tick цена пампа: ', str(tick['price']))
        #print('f1', str(f1), 'и f2', str(f2))
        return True
    else:
        return False


# проверяем наличие только стоп лосс LIMIT BUY ордеров
def check_stop_loss_limit_buy_order():
    if settings.TRADE_STG == 'STANDART':
        llist = bot.openOrders(symbol=settings.COIN, recvWindow=recvGlobal)


        for i in llist:
            if i['type'] == 'STOP_LOSS_LIMIT' and i['side'] == 'BUY':
                return True
        return False

    if settings.TRADE_STG == 'MARGIN_DOWN':
        llist = bot.marginOpenOrders(symbol=settings.COIN, recvWindow=recvGlobal)
        for i in llist:
            if i['type'] == 'STOP_LOSS_LIMIT' and i['side'] == 'SELL':
                return True
        return False

# проверяем наличие только стоп лосс LIMIT BUY ордеров
def check_orderid():
    if settings.STOP_LOSS_LIMIT_BUY_ORDERID is not None:
        if settings.TRADE_STG == 'STANDART':
            llist = bot.orderInfo(symbol=settings.COIN, orderId=int(settings.STOP_LOSS_LIMIT_BUY_ORDERID), recvWindow=recvGlobal)
            return llist

        if settings.TRADE_STG == 'MARGIN_DOWN':
            llist = bot.marginOrderInfo(symbol=settings.COIN, orderId=int(settings.STOP_LOSS_LIMIT_BUY_ORDERID), recvWindow=recvGlobal)
            return llist

# проверяем наличие только стоп лосс LIMIT BUY ордеров
def check_order_history():
    llist = bot.myTrades(symbol=settings.COIN, limit=5 , recvWindow=recvGlobal)
    return llist


# проверяем наличие только стоп лосс LIMIT BUY ордеров
def check_orderid_cancel_or_executed():
    # 1 - executed; 2 - cancel; 3 - open
    llist = check_orderid()
    if llist is not None:
        if 'Order does not exist' in llist:
            return False
        else: return True



def convert_deposit_to_start_trade():
    all_order_cancel()

    if settings.TRADE_STG == 'STANDART':
        print('convert_deposit_to_start_trade: usdt ', get_free_balance('USDT'), '; btc ', get_free_balance('BTC'))
        if float(get_free_balance('BTC')) > 0.0013:
            sell_order = sell_order_market()
            print('convert_deposit_to_start_trade ', sell_order)
            if 'code' in sell_order.keys():
                print('Error sell market 1cc')


    if settings.TRADE_STG == 'MARGIN_DOWN':
        print('convert_deposit_to_start_trade: usdt ', get_free_balance('USDT'), '; btc ', get_free_balance('BTC'))
        if float(get_free_balance('USDT')) > 11:
            sell_order = sell_order_market()
            print('convert_deposit_to_start_trade ', sell_order)
            print('convert_deposit_to_start_trade: usdt ', get_free_balance('USDT'), '; btc ', get_free_balance('BTC'))
            if 'code' in sell_order.keys():
                print('Error sell market 1cc')


# вход в рынок
def buy_order_market():
    now = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    settings.LOG_TRADE['timestamp'] = int(str(now.timestamp()).split('.')[0])

    if settings.TRADE_STG == 'STANDART':
        settings.LOG_TRADE['enterDeposit'] = get_free_balance('USDT')
        qty = check_coin_buy_BTC_in_USDT_tick(settings.LOG_TRADE['enterDeposit'])
        qty = cut_percent(qty,1)
        side = 'BUY'
        order = bot.createOrder(
            symbol=settings.COIN,
            recvWindow=recvGlobal,
            side=side,
            type='MARKET',
            quantity=decimal.Decimal(qty).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
            newOrderRespType='FULL'
        )
    if settings.TRADE_STG == 'MARGIN_DOWN':
        settings.LOG_TRADE['enterDeposit'] = get_free_balance('BTC')
        qty = cut_percent(settings.LOG_TRADE['enterDeposit'],1)
        side = 'SELL'
        order = bot.marginCreateOrder(
            symbol=settings.COIN,
            recvWindow=recvGlobal,
            side=side,
            type='MARKET',
            quantity=decimal.Decimal(qty).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
            newOrderRespType='FULL'
        )

    if 'code' in order.keys():
        print('Error buy_order_market')
        print('usdt', get_free_balance('USDT'))
        print('btc', get_free_balance('BTC'))
        print('qty', qty)
        return 'return'
    settings.LOG_TRADE['enterPrice'] = order['fills'][0]['price']
    print('buy_order_market settings.LOG_TRADE[enterPrice]', settings.LOG_TRADE['enterPrice'])
    return order


# выход из рынка маржа или биржа
def sell_order_market():
    if settings.TRADE_STG == 'STANDART':
        qty = cut_percent(get_free_balance('BTC'),1)
        side = 'SELL'
        order = bot.createOrder(
            symbol=settings.COIN,
            recvWindow=recvGlobal,
            side=side,
            type='MARKET',
            quantity=decimal.Decimal(qty).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
            newOrderRespType='FULL'
        )
    if settings.TRADE_STG == 'MARGIN_DOWN':
        qty = check_coin_buy_BTC_in_USDT_tick(get_free_balance('USDT'))
        qty = cut_percent(qty,1)
        side = 'BUY'
        order = bot.marginCreateOrder(
            symbol=settings.COIN,
            recvWindow=recvGlobal,
            side=side,
            type='MARKET',
            quantity=decimal.Decimal(qty).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
            newOrderRespType='FULL'
        )
    if 'code' in order.keys():
        print('Error sell_order_market 412')
        return 'return'
    return order



# ставим стоп лосс ордера
def stop_loss_limit_order(stop_price):

    all_order_cancel()

    if settings.TRADE_STG == 'STANDART':
        side = 'SELL' # при бычем стопе продаем

        free = '0.0'
        tag = 0
        while decimal.Decimal(free) < decimal.Decimal('0.0011'):  # ждем пока снимется ордер
            tag += 1
            sleep(0.1)
            free = cut_percent(get_free_balance('BTC'), 1)
            if tag == 10: print('Ждем получение баланса... free:', free,'; get_free_balance(BTC):', get_free_balance('BTC'),'; get_free_balance(USDT):', get_free_balance('USDT'))
            if tag == 1000: print('Ждем получение баланса... free:', free, '; get_free_balance(BTC):', get_free_balance('BTC'), '; get_free_balance(USDT):', get_free_balance('USDT'))
            if tag == 10000: print('Ждем получение баланса... free:', free, '; get_free_balance(BTC):', get_free_balance('BTC'), '; get_free_balance(USDT):', get_free_balance('USDT'))


        order = bot.createOrder(
            symbol=settings.COIN,
            recvWindow=recvGlobal,
            side=side,
            type='STOP_LOSS_LIMIT',
            quantity=free, # уже decimal
            price=decimal.Decimal(stop_price).quantize(
                decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN) - decimal.Decimal('0.01'),
            stopPrice=decimal.Decimal(stop_price).quantize(
                decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN),
            timeInForce='GTC'
        )
        print('stop_loss_limit_order: free ', free, 'btc ', get_free_balance('BTC'))

    if settings.TRADE_STG == 'MARGIN_DOWN':
        side = 'BUY'
        print('usdt ', get_free_balance('USDT'))
        qtyB = check_coin_buy_BTC_in_USDT_limit(get_free_balance('USDT'), decimal.Decimal(stop_price).quantize(
                decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN) + decimal.Decimal('0.01'))
        qtyB = cut_percent(qtyB,1)
        print('TRY Margin Order >>>')
        order = bot.marginCreateOrder(
            symbol=settings.COIN,
            recvWindow=recvGlobal,
            side=side,
            type='STOP_LOSS_LIMIT',
            quantity=decimal.Decimal(qtyB).quantize(
                decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
            price=decimal.Decimal(stop_price).quantize(
                decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN) + decimal.Decimal('0.01'),
            stopPrice=decimal.Decimal(stop_price).quantize(
                decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN),
            timeInForce='GTC'
        )
        print('stop_loss_limit_order: qtyB ', qtyB, '; btc ', get_free_balance('BTC'), '; usdt ', get_free_balance('USDT'))
        print('order ', order)

    if 'code' in order.keys():
        if 'MIN_NOTIONAL' in order['msg']:
            print('>>>>STOP LOSS MIN_NOTIONAL, проверяем данные по остатку монет (stop_loss_limit_order bin_fun 456)<<<<<')
            llist = account_only_free_balance()
            if llist:
                for tag in llist:
                    if tag['asset'] == 'USDT':
                        print('account_only_free_balance USDT free', tag['free'])
                        print('account_only_free_balance USDT locked', tag['locked'])
                    if tag['asset'] == 'BTC':
                        print('account_only_free_balance BTC free', tag['free'])
                        print('account_only_free_balance BTC locked', tag['locked'])


        if 'trigger immediately' in order['msg']:
            print('>>>>STOP LOSS immediately, просто продаем по рыночной<<<<<')
            sell_order = sell_order_market()
            print('sell_order stop immediately: ', sell_order['fills'][0]['price'])
            if 'code' in sell_order.keys():
                print('Error sell market #461')
                return 'return'
            settings.LOG_TRADE['exitPrice'] = sell_order['fills'][0]['price']
            settings.LOG_TRADE['exitDeposit'] = get_free_balance('USDT')
            sell_log()
            settings.BUY = False
            return 'return'

        print('Error stop loss #469')
        settings.BUY = False
        return 'return'
    settings.LOG_TRADE['exitPrice'] = stop_price
    # спим 1 секунду, чтобы стоп успел поставится
    sleep(1)
    return order

# ставим лимит на вход в рынок
def buy_limit_order(price):
    # LOG

    all_order_cancel()

    now = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    settings.LOG_TRADE['timestamp'] = int(str(now.timestamp()).split('.')[0])
    settings.LOG_TRADE['enterPrice'] = price

    if settings.TRADE_STG == 'STANDART':
        side = 'BUY'
        settings.LOG_TRADE['enterDeposit'] = get_free_balance('USDT')
        qty = check_coin_buy_BTC_in_USDT_limit(get_free_balance('USDT'),decimal.Decimal(price).quantize(
            decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN) - decimal.Decimal('0.01'))


        qty = cut_percent(qty, 1)
        order = bot.createOrder(
            symbol=settings.COIN,
            recvWindow=recvGlobal,
            side=side,
            type='STOP_LOSS_LIMIT',
            quantity=decimal.Decimal(qty).quantize(
                decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
            price=decimal.Decimal(price).quantize(
                decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN) - decimal.Decimal('0.01'),
            stopPrice=decimal.Decimal(price).quantize(
                decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN),
            timeInForce='GTC'
        )

    if settings.TRADE_STG == 'MARGIN_DOWN':
        side = 'SELL'
        settings.LOG_TRADE['enterDeposit'] = get_free_balance('BTC')
        qty = cut_percent(get_free_balance('BTC'), 1)
        order = bot.marginCreateOrder(
            symbol=settings.COIN,
            recvWindow=recvGlobal,
            side=side,
            type='STOP_LOSS_LIMIT',
            quantity=decimal.Decimal(qty).quantize(
                decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
            price=decimal.Decimal(price).quantize(
                decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN) + decimal.Decimal('0.01'),
            stopPrice=decimal.Decimal(price).quantize(
                decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN),
            timeInForce='GTC'
        )



    if 'code' in order.keys():
        if 'trigger immediately' in order['msg']:
            print('>>>>BUY LIMIT immediately, просто покупаем по рыночной<<<<<')
            buy_order = buy_order_market()
            print(' immediately: ', buy_order['fills'][0]['price'])
            if 'code' in buy_order.keys():
                print('Error sell market #461')
                return 'return'
            settings.LOG_TRADE['exitPrice'] = buy_order['fills'][0]['price']
            settings.LOG_TRADE['exitDeposit'] = get_free_balance('USDT')
            sell_log()
            settings.BUY = True
            return 'return'

        print('Error stop loss #530 RETURN')
        print('price ', price, '; usdt ', get_free_balance('USDT'),'; btc ', get_free_balance('BTC'), '; qty ',qty)

        settings.BUY = False
        return 'return'
    print('order buy_limit_order ', order)
    settings.STOP_LOSS_LIMIT_BUY_ORDERID = order['orderId']
    print('check_orderid: ', check_orderid())
    print('check_order_history: ', check_order_history())
    print('price', price)
    return order

# цвет свечи
def cendel_color():
    tick = bot.tickerPrice(symbol=settings.COIN)
    cendel = take_now_cendel_binance(1)
    if settings.TRADE_STG == 'STANDART':
        if float(tick['price']) > float(cendel[0][1]):
            return True # свеча зеленая
        else:
            return False # свеча красная


    if settings.TRADE_STG == 'MARGIN_DOWN':
        if float(tick['price']) < float(cendel[0][1]):
            return True  # свеча зеленая
        else:
            return False  # свеча красная



###
#   MARGIN function
###


# получаем сколько денег по USDT и по BTC
# сли даем вместо coin 1, return только USDT или COIN
def margin_get_free_balance(COIN, USDT):
    llist = margin_account_only_free_balance()
    #print('bin_fun margin_get_free_balance', llist)
    COIN_free = 0
    USDT_free = 0
    if llist:
        for tag in llist:
            if tag['asset'] == COIN: COIN_free = tag['free']
            if tag['asset'] == USDT: USDT_locked = tag['locked']
            if tag['asset'] == USDT: USDT_free = tag['free']

        if COIN == 0:
            return USDT_free
        if COIN == 'locked':
            return USDT_locked
        if USDT == 0:
            return COIN_free
        return COIN_free, USDT_free

# получаем сколько денег на акаунте по каждой крипте и оставляем только крипту с деньгами

def margin_account_repay():
    ddict = bot.marginAccount(recvWindow=recvGlobal)
    return ddict['totalLiabilityOfBtc']



def margin_account_only_free_balance():
    llist = []
    ddict = bot.marginAccount(recvWindow=recvGlobal)
    #print('bin_fun margin_account_only_free_balance', ddict)
    if ddict:
        if 'code' in ddict.keys():
            print('bin_fun account_only_free_balance ERROR ')
            return ddict
        for balance in ddict['userAssets']:
            if float(balance['free']) > 0 or float(balance['locked']) > 0:
                llist.append(balance)
    return llist

# проверяем наличие только стоп лосс LIMIT BUY ордеров
def margin_check_stop_loss_limit_buy_order(coin):
    llist = bot.marginOpenOrders(symbol=coin, recvWindow=recvGlobal)
    for i in llist:
        if i['type'] == 'STOP_LOSS_LIMIT' and i['side'] == 'SELL':
            return True
    return False

# проверяем наличие только стоп лосс sell ордеров
def margin_sell_or_buy_stop_loss_limit_order(coin,side,qty,price):
    order = bot.marginCreateOrder(
        symbol=coin,
        recvWindow=recvGlobal,
        side=side,
        type='STOP_LOSS_LIMIT',
        quantity=decimal.Decimal(qty).quantize(
            decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
        price=decimal.Decimal(price).quantize(
            decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN),
        stopPrice=decimal.Decimal(price).quantize(
            decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN),
        timeInForce='GTC'
    )
    return order


# проверяем наличие только стоп лосс sell ордеров
def margin_check_stop_loss_sell_order(coin):
    llist = bot.marginOpenOrders(symbol=coin, recvWindow=recvGlobal)
    for i in llist:
        if i['type'] == 'STOP_LOSS_LIMIT' and i['side'] == 'BUY':
            return True
    return False


# проверяем наличие только стоп лосс sell ордеров
def margin_buy_or_sell_order_market(coin,side,qty):
    order = bot.marginCreateOrder(
        symbol=coin,
        recvWindow=recvGlobal,
        side=side,
        type='MARKET',
        quantity=decimal.Decimal(qty).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN),
        newOrderRespType='FULL'
        )
    return order

# MARGIN AND SIMPLE FUNCTION
def data_before_cendel():
    llist = bot.klines(symbol=settings.COIN, interval=settings.CENDEL_INTERVAL, limit=2)
    if settings.TRADE_STG == 'STANDART':
        return llist[0][3] #low
    if settings.TRADE_STG == 'MARGIN_DOWN':
        return llist[0][2] #high

# возвращает стоп для лимита (предыдущая свечаили текущая,смотря какой стоп выше)
def limitbuy_stoploss_before_cendel():
    llist = bot.klines(symbol=settings.COIN, interval=settings.CENDEL_INTERVAL, limit=2)
    if settings.TRADE_STG == 'STANDART':
        if llist[0][3]>llist[1][3]: return llist[1][3]  # low
        if llist[0][3]<=llist[1][3]: return llist[0][3]  # low
    if settings.TRADE_STG == 'MARGIN_DOWN':
        if llist[0][3]>llist[1][3]: return llist[0][2]  # low
        if llist[0][3]<=llist[1][3]: return llist[1][2]  # low


# берем маржу максимальную
def take_margin_loan():
    amount_loan = bot.marginMaxBorrowable(asset='BTC', recvWindow=recvGlobal)

    if decimal.Decimal(amount_loan['amount']) > 0:
        print('TRY LOAN', bot.marginLoan(asset='BTC', amount=amount_loan['amount'], recvWindow=recvGlobal))



#
#  LOG FUNCTION
#

def sell_log():
    """
    при покупке, создаем запись в редис, чтобы потом иметь архив данных
    """
    if settings.TRADE_STG == 'STANDART':
        dbname = 14
    if settings.TRADE_STG == 'MARGIN_DOWN':
        dbname = 13

    # timestamp, coin, interval, enterPrice, enterDeposit, exitDeposit, exitPrice]
    settings.LOG_TRADE['coin'] = settings.COIN
    settings.LOG_TRADE['interval'] = settings.CENDEL_INTERVAL
    settings.LOG_TRADE['enterPrice'] = float(settings.LOG_TRADE['enterPrice'])
    settings.LOG_TRADE['enterDeposit'] = float(settings.LOG_TRADE['enterDeposit'])
    settings.LOG_TRADE['exitDeposit'] = float(settings.LOG_TRADE['exitDeposit'])
    settings.LOG_TRADE['exitPrice'] = float(settings.LOG_TRADE['exitPrice'])

    r = redis_db_check(14)

    mapping = {}
    mapping[settings.LOG_TRADE['timestamp']] = settings.LOG_TRADE['timestamp']
    r.zadd(settings.TRADE_STG + settings.COIN, mapping)
    #test = r.zrange(zkey, 0, -1, desc=True)
    #print('log:', test)

    #? r.hset(zkey + '_data', log[0], str(log))
    tt = settings.TRADE_STG + settings.COIN+'_DATA'
    print(tt)
    r.hset(str(tt), settings.LOG_TRADE['timestamp'], str(settings.LOG_TRADE))

