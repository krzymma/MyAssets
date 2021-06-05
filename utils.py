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


def get_asset_code(asset):
    d = {}
    d['Argentine Peso'] = 'ARS'
    d['GC00'] = 'GOLD'
    return d[asset]


def unique_line_in_file(line, file_name):
    file_name = os.path.dirname(os.path.abspath(__file__)) + '/' + file_name
    with open(file_name, 'r') as f:
        return line in f.readlines()


def save_fav_asset(tile, asset_code):
    line = ""
    if tile.tile_type == TileType.CURRENCIES:
        line += "EXRATE: "
    elif tile.tile_type == TileType.CRYPTO:
        line += "CRYPTO: "
    elif tile.tile_type == TileType.MATERIALS:
        line += "MATERIALS: "
        asset_code = get_asset_code(asset_code)
    elif tile.tile_type == TileType.STOCKS:
        line += "STOCK: "
    else:
        """do nothing"""
    line += asset_code

    if not unique_line_in_file(line + '\n', 'fav.txt'):
        write_file('fav.txt', line)


def read_file(file_name):
    file_name = os.path.dirname(os.path.abspath(__file__)) + '/' + file_name
    with open(file_name, 'r') as f:
        content = (f.readlines())
    return [x.strip() for x in content]


def write_file(file_name, line):
    file_name = os.path.dirname(os.path.abspath(__file__)) + '/' + file_name
    with open(file_name, 'a') as f:
        f.write(line + "\n")


def convert_data_to_dict(data_csv, no_columns):
    """converting csv data format to dictionary - key: date, value: (OPEN,HIGH,LOW,CLOSE) """
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
