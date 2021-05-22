import sys
from enum import Enum
import os

class TileType(Enum):
    STOCKS = 1
    CURRENCIES = 2
    FAVOURITES = 3
    CRYPTO = 4
    MATERIALS = 5

class Interval(Enum):
    DAY = '1d'
    WEEK = '7d'
    MONTH = '1m'

    def __str__(self):
        return self.value
        

def read_file(file_name):
    file_name = os.path.dirname(os.path.abspath(__file__)) + '/' + file_name
    with open(file_name, 'r') as f:
        content = (f.readlines())
    return [x.strip() for x in content]


def write_file(file_name, line):
    with open(file_name, 'a') as f:
        f.write(line + "\n")


"""converting csv data format to dictionary - key: date, value: (OPEN,HIGH,LOW,CLOSE) """
def convert_data_to_dict(data_csv, no_columns):
    tmp_data1 = [y.split('\n') for y in data_csv.content.decode("utf-8").replace(',', '').replace('""', '"').split('"')]
    tmp_data2 = []
    for el in tmp_data1:
        for i in range(0, len(el)):
            if el[i] != '':
                tmp_data2.append(el[i])
    res = {}
    for i in range(1, len(tmp_data2) - 1, no_columns):
        res[tmp_data2[i]] = tuple(float(tmp_data2[j]) for j in range(i + 1, i + no_columns))

    return res
