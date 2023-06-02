# -*- coding: utf-8 -*-
from cl_medoed import *
from fu_tools import *
from flask import Flask, jsonify, request, render_template, redirect, url_for, make_response
import io
import json
from binance_fun import *
from fu_2 import *
from cl_thread import *
from settings import settings


CASH = 100000
MAX_STG = {}

# Flask
# Instantiate the Node
app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/uploadfile', methods=['GET'])
def getfile():
    return render_template('uploadfile.html')

@app.route('/data', methods=['GET'])
def data():
    r = redis_db_check(14)
    last = r.zrange(settings.TRADE_STG + settings.COIN, 0, -1, desc=True)
    t = 0
    data = {}
    green = 0
    red = 0
    red_percent = 0
    green_percent = 0
    print(last)
    for i in last:
        t += 1
        dictt = r.hget(settings.TRADE_STG + settings.COIN+'_DATA', i.decode())
        dictt = ast.literal_eval(dictt.decode())

        dictt['timestamp'] = str(datetime.fromtimestamp(dictt['timestamp']))
        dictt['enterDeposit'] = decimal.Decimal(dictt['enterDeposit']).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)
        dictt['exitDeposit'] = decimal.Decimal(dictt['exitDeposit']).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)

        num = 100 * abs(decimal.Decimal(dictt['enterPrice']) - decimal.Decimal(dictt['exitPrice'])) / decimal.Decimal(dictt['enterPrice'])
        dictt['percentMove'] = decimal.Decimal(num).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)

        if float(dictt['enterPrice']) > float(dictt['exitPrice']):
            dictt['green'] = False
            red += 1
            red_percent += num
        else:
            dictt['green'] = True
            green += 1
            green_percent += num
        data[t] = dictt
        red_percent = decimal.Decimal(red_percent).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)
        green_percent = decimal.Decimal(green_percent).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)
    return render_template('data.html', data = data, green=green, red=red, red_percent=red_percent, green_percent=green_percent)

'''
@app.route('/data', methods=['GET'])
def data():
    # 13 db margin
    r = redis_db_check(14)
    last = r.zrange(settings.TRADE_STG + settings.COIN, 0, -1, desc=True)
    data = {}
    t = 0
    green = 0
    red = 0
    red_percent = 0
    green_percent = 0
    for i in last:
        data2 = {}
        t += 1
        lline = r.hget(settings.TRADE_STG + settings.COIN+'_DATA', i.decode())
        lline = ast.literal_eval(lline.decode())
        dictt['timestamp'] = str(datetime.fromtimestamp(dictt['timestamp']))

        dictt['enterDeposit'] = decimal.Decimal(dictt['enterDeposit']).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)
        dictt['exitDeposit'] = decimal.Decimal(dictt['exitDeposit']).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)

        num = 100 * abs(decimal.Decimal(dictt['enterPrice']) - decimal.Decimal(dictt['exitPrice'])) / decimal.Decimal(dictt['enterPrice'])
        dictt['percentMove'] = decimal.Decimal(num).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)

        #num = 100 * abs(decimal.Decimal(lline[4]) - decimal.Decimal(lline[5])) / decimal.Decimal(lline[4])

        if float(dictt['enterPrice']) > float(dictt['exitPrice']):
            dictt['green'] = False
            red += 1
            red_percent += num
        else:
            dictt['green'] = True
            green += 1
            green_percent += num
        data[t] = dictt

        #if float(lline[4]) > float(lline[5]):
        #    data2['result'] = False
         #   red += 1
         #   red_percent += num

        data[t] = dictt

    return render_template('data.html', data = data, green=green, red=red, red_percent=red_percent, green_percent=green_percent)
'''

@app.route('/exit_margin', methods=['GET', 'POST'])
def exit_simple():
    settings.EXIT_MARGIN = True
    result = settings.EXIT_MARGIN
    return jsonify(result=result)

@app.route('/delete_id', methods=['GET', 'POST'])
def delete_id():
    sstr = request.args.get('delete_id', 0, type=str)
    llist = sstr.split('&')
    delete_id = llist[0]
    dbname = llist[1]
    print(delete_id)
    print(dbname)
    delete_id = datetime.strptime(delete_id, '%Y-%m-%d %H:%M:%S')
    delete_id = str(delete_id.timestamp()).split('.')[0]
    print(delete_id)
    r = redis_db_check(dbname)
    print(r.hget('BTCUSDT_data', delete_id))
    r.hdel('BTCUSDT_data', delete_id)
    # 1587243596
    r.zrem('BTCUSDT', delete_id)
    test = r.zrange('BTCUSDT', 0, 1, desc=True)
    print('log:', test)
    result = delete_id
    return jsonify(result=result)

@app.route('/ajax_config', methods=['GET', 'POST'])
def ajax_config():
    createConfig()
    return jsonify(result='Config setting.ini создан')



@app.route('/ajax_upload', methods=['GET', 'POST'])
def ajax_upload():
    result = 'none'
    json_dict = {}

    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            result = 'No selected file'
        if '.csv' in file.filename:

            file_stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)

            csvfile = read_csv(file_stream, ',')

            #dict_result['Стратегия 1'] = strategy_1(csvfile,CASH)
            result = 'Стратегия 1: ' + str(strategy_1(csvfile,CASH))

            file_stream.seek(0)

            result = result + '; ' + 'Стратегия 2: ' + str(strategy_2(csvfile, CASH))

            json_dict = strategy_3(file_stream, CASH,200,10000,200)

    return jsonify(result=result, json_dict=json_dict)


@app.route('/ajax_get_binance', methods=['GET', 'POST'])
def ajax_get_binance():
    allstg = {}
    beststg = {}


    return jsonify(result=allstg, beststg=beststg)

@app.route('/ajax_cendel', methods=['GET'])
def ajax_cendel():
    result = 'none'
    if request.method == 'GET':
        result = redis_check_last_day_limit('BTCUSDT',365,'1d')
    print(result)

    return jsonify(result=result)


def main():
    #crudConfig('setting.ini')

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
    #print(str(now.timestamp()).split('.')[0])
    # ts_5min_now = str(datetime.combine(date.today(), time(now.hour, need_minute, 0)).timestamp()).split('.')[0]

    # берем маржу максимальную
    settings.TRADE_STG = 'MARGIN_DOWN'

    if settings.TRADE_STG == 'MARGIN_DOWN':
        take_margin_loan()

    convert_deposit_to_start_trade()


    amount_loan = bot.marginMaxBorrowable(asset='BTC', recvWindow=recvGlobal)
    if decimal.Decimal(amount_loan['amount']) > 0:
        print('TRY LOAN', bot.marginLoan(asset='BTC', amount=amount_loan['amount'], recvWindow=recvGlobal))

    #print('==========GO StartCheckStg Thread==========')
    #check_stg = StartCheckStg()
    #check_stg.start()
    print('==========GO Trade Thread==========')
    trade = StartTrade()
    trade.start()



if __name__ == '__main__':

    main()

    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=55555, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)