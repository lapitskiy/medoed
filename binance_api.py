import json
import urllib
import hmac, hashlib
import requests
from time import sleep
import time
from datetime import datetime, timedelta, date
from urllib.parse import urlparse, urlencode
from urllib.request import Request, urlopen

requests.adapters.DEFAULT_RETRIES = 10

class Binance():
    methods = {
        # public methods
        'ping': {'url': 'api/v1/ping', 'method': 'GET', 'private': False},
        'time': {'url': 'api/v1/time', 'method': 'GET', 'private': False},
        'exchangeInfo': {'url': 'api/v1/exchangeInfo', 'method': 'GET', 'private': False},
        'depth': {'url': 'api/v1/depth', 'method': 'GET', 'private': False},
        'trades': {'url': 'api/v1/trades', 'method': 'GET', 'private': False},
        'historicalTrades': {'url': 'api/v1/historicalTrades', 'method': 'GET', 'private': False},
        'aggTrades': {'url': 'api/v1/aggTrades', 'method': 'GET', 'private': False},
        'klines': {'url': 'api/v1/klines', 'method': 'GET', 'private': False},
        'ticker24hr': {'url': 'api/v1/ticker/24hr', 'method': 'GET', 'private': False},
        'tickerPrice': {'url': 'api/v3/ticker/price', 'method': 'GET', 'private': False},
        'tickerBookTicker': {'url': 'api/v3/ticker/bookTicker', 'method': 'GET', 'private': False},
        # private methods
        'createOrder': {'url': 'api/v3/order', 'method': 'POST', 'private': True},
        'testOrder': {'url': 'api/v3/order/test', 'method': 'POST', 'private': True},
        'orderInfo': {'url': 'api/v3/order', 'method': 'GET', 'private': True},
        'cancelOrder': {'url': 'api/v3/order', 'method': 'DELETE', 'private': True},
        'openOrders': {'url': 'api/v3/openOrders', 'method': 'GET', 'private': True},
        'allOrders': {'url': 'api/v3/allOrders', 'method': 'GET', 'private': True},
        'account': {'url': 'api/v3/account', 'method': 'GET', 'private': True},
        'myTrades': {'url': 'api/v3/myTrades', 'method': 'GET', 'private': True},
        # wapi
        'depositAddress': {'url': 'wapi/v3/depositAddress.html', 'method': 'GET', 'private': True},
        'withdraw': {'url': 'wapi/v3/withdraw.html', 'method': 'POST', 'private': True},
        'depositHistory': {'url': 'wapi/v3/depositHistory.html', 'method': 'GET', 'private': True},
        'withdrawHistory': {'url': 'wapi/v3/withdrawHistory.html', 'method': 'GET', 'private': True},
        'assetDetail': {'url': 'wapi/v3/assetDetail.html', 'method': 'GET', 'private': True},
        'tradeFee': {'url': 'wapi/v3/tradeFee.html', 'method': 'GET', 'private': True},
        'accountStatus': {'url': 'wapi/v3/accountStatus.html', 'method': 'GET', 'private': True},
        'systemStatus': {'url': 'wapi/v3/systemStatus.html', 'method': 'GET', 'private': True},
        'assetDust': {'url': 'sapi/v1/asset/dust', 'method': 'POST', 'private': True},
        'dustLog': {'url': 'wapi/v3/userAssetDribbletLog.html', 'method': 'GET', 'private': True},
        'assetAssetDividend': {'url': 'sapi/v1/asset/assetDividend', 'method': 'GET', 'private': True},
        # sapi
        'marginTransfer': {'url': 'sapi/v1/margin/transfer', 'method': 'POST', 'private': True},
        'marginLoan': {'url': 'sapi/v1/margin/loan', 'method': 'POST', 'private': True},
        'marginRepay': {'url': 'sapi/v1/margin/repay', 'method': 'POST', 'private': True},
        'marginCreateOrder': {'url': 'sapi/v1/margin/order', 'method': 'POST', 'private': True},
        'marginCancelOrder': {'url': 'sapi/v1/margin/order', 'method': 'DELETE', 'private': True},
        'marginOrderInfo': {'url': 'sapi/v1/margin/order', 'method': 'GET', 'private': True},
        'marginAccount': {'url': 'sapi/v1/margin/account', 'method': 'GET', 'private': True},
        'marginOpenOrders': {'url': 'sapi/v1/margin/openOrders', 'method': 'GET', 'private': True},
        'marginAllOrders': {'url': 'sapi/v1/margin/allOrders', 'method': 'GET', 'private': True},
        'marginAsset': {'url': 'sapi/v1/margin/asset', 'method': 'POST', 'private': True},
        'marginPair': {'url': 'sapi/v1/margin/pair', 'method': 'POST', 'private': True},
        'marginPriceIndex': {'url': 'sapi/v1/margin/priceIndex', 'method': 'POST', 'private': True},
        'marginMyTrades': {'url': 'sapi/v1/margin/myTrades', 'method': 'GET', 'private': True},
        'marginMaxBorrowable': {'url': 'sapi/v1/margin/maxBorrowable', 'method': 'GET', 'private': True},
        'marginmaxTransferable': {'url': 'sapi/v1/margin/maxTransferable', 'method': 'GET', 'private': True},
    }

    def __init__(self, API_KEY, API_SECRET):
        self.API_KEY = API_KEY
        self.API_SECRET = bytearray(API_SECRET, encoding='utf-8')
        self.shift_seconds = 0
        self.set_shift_seconds()

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            kwargs.update(command=name)
            return self.call_api(**kwargs)
        return wrapper

    def set_shift_seconds(self):
        mytime = time.time()
        bottime = self.call_api(command='time')['serverTime']
        if datetime.fromtimestamp(mytime) > datetime.fromtimestamp(int(str(bottime)[:-3])):
            self.shift_seconds = - (datetime.fromtimestamp(mytime) - datetime.fromtimestamp(int(str(bottime)[:-3]))).total_seconds()
        else:
            self.shift_seconds = (datetime.fromtimestamp(int(str(bottime)[:-3])) - datetime.fromtimestamp(mytime)).total_seconds()
        print('shift second 1', self.shift_seconds)
        print('mytime ', datetime.fromtimestamp(mytime))
        print('bot time ', datetime.fromtimestamp(int(str(bottime)[:-3])))

    def call_api(self, **kwargs):
        command = kwargs.pop('command')
        response = ''
        connect_loop = True
        while connect_loop:
            try:
                api_url = 'https://api.binance.com/' + self.methods[command]['url']
                payload = kwargs
                headers = {}

                payload_str = urllib.parse.urlencode(payload)

                if self.methods[command]['private']:
                    payload.update({'timestamp': int(time.time() + self.shift_seconds) * 1000})


                    payload_str = urllib.parse.urlencode(payload).encode('utf-8')
                    sign = hmac.new(
                        key=self.API_SECRET,
                        msg=payload_str,
                        digestmod=hashlib.sha256
                    ).hexdigest()

                    payload_str = payload_str.decode("utf-8") + "&signature=" + str(sign)
                    headers = {"X-MBX-APIKEY": self.API_KEY}

                if self.methods[command]['method'] == 'GET' or self.methods[command]['url'].startswith('sapi'):
                    api_url += '?' + payload_str


                response = requests.request(method=self.methods[command]['method'], url=api_url,
                                        data="" if self.methods[command]['method'] == 'GET' else payload_str,
                                        headers=headers)
                connect_loop = False

            # LPITSKY UPDATE 2 (доп защита)
            except requests.exceptions.RequestException:  # This is the correct syntax
                sleep(1)
                print(requests.exceptions.RequestException)
                print('TRY ConnectionError')
                connect_loop = True

            if 'code' in response:

                if 'error occurred' in response.text:
                    print('TRY Connection again (error occured while processing the request)')
                    connect_loop = True


                if 'outside of the recvWindow' in response.text:
                    print('TRY Connection again (outside of the recvWindow) ')
                    connect_loop = True

                if 'waiting for response from backend server' in response.text:
                    print('TRY Connection again (waiting for response from backend server)')
                    connect_loop = True

                if 'Timestamp' in response.text:
                    print('TRY Connection again (Timestamp problem) ')
                    self.set_shift_seconds()
                    connect_loop = True

                if 'server error' in response.text:
                    print('TRY Connection again (Internal server error) ')
                    self.set_shift_seconds()
                    connect_loop = True

                if 'Internal error' in response.text:
                    print('TRY Connection again (-1001 Internal error; unable to process your request) ')
                    self.set_shift_seconds()
                    connect_loop = True

                print(response.text)


        if self.methods[command]['url'] != 'api/v1/klines' and self.methods[command]['url'] != 'api/v3/openOrders' and self.methods[command]['url'] != 'sapi/v1/margin/openOrders' \
                and self.methods[command]['url'] != 'api/v3/account' and self.methods[command]['url'] != 'api/v3/ticker/price' and self.methods[command]['url'] != 'api/v3/account' \
                and self.methods[command]['url'] != 'sapi/v1/margin/maxBorrowable' and self.methods[command]['url'] != 'sapi/v1/margin/order' \
                and self.methods[command]['url'] != 'sapi/v1/margin/account' and self.methods[command]['url'] != 'api/v3/order':
            print(api_url, payload_str, self.methods[command])

        return response.json()