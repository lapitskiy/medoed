import csv
import ast
from datetime import datetime, timedelta, date, time
from binance_fun import redis_db_check
import configparser
from settings import settings


# определяем самую прибыльную страгеию из объема и цены
#
def check_max_stg(ddict):
    max_price = 0
    max_day = 0
    max_volume = 0
    dictt_max = {}

    for key in ddict:
        #print(ddict[key][1],' > ', max_price)
        if ddict[key][1] > max_price:
            max_price = ddict[key][1]
            dictt_max['price'] = ddict[key][1]
            dictt_max['day'] = key
            dictt_max['volume'] = ddict[key][0]
    return dictt_max

# определяем самую прибыльную позицию относительно обьема
#
def volume_max_check(ddict):
    max_number = 0
    volume = 0
    #max_tag = False
    volume_list = []

    for key in ddict:
        if ddict[key] < 100000: continue
        if ddict[key] > max_number:
            volume_list = []
            max_number = ddict[key]
            volume = key
            volume_list.append(key)

        if key > volume and ddict[key] == max_number:
            volume_list.append(key)


    #print('максимальная цена и объем: ', max_number,'; ',volume)
    #for key,value in ddict.items():
    #    print(key,':',value)
    while len(volume_list) > 2:
        volume_list.pop(1)
    #print(volume_list)
    max_result = [volume, max_number]
    return max_result



# читаем csv файл в объект
def read_csv(file_obj, simbol):
    """
    Read a CSV file using csv.DictReader
    """
    fieldnames = ['data', 'price', 'open', 'max', 'min', 'volume', 'percent']
    reader = csv.DictReader(file_obj, delimiter=simbol, fieldnames = fieldnames)
    next(reader)
    return reader

#
#  CONFIG
#

def crudConfig(path):
    """
    Create, read, update, delete config
    """
    if not os.path.exists(path):
        createConfig(path)

    config = configparser.ConfigParser()
    config.read(path)


def createConfig(path):
    """
    Create a config file
    """
    config = configparser.ConfigParser()
    config.add_section("BTCUSDT")
    config.set("Settings", "kypleno", "False")

    with open(path, "w") as config_file:
        config.write(config_file)






