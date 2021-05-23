import fetch
import utils
from utils import Interval
import pandas as pd

"""functions load data from fav.txt file"""
def load_currency(values, idx, asset):
    idx.append(asset[1])
    currencies = asset[1].split('-')
    values.append(fetch.get_live_currency_exchange_rate(currencies[0], currencies[1]))


def load_crypto(values, idx, asset):
    idx.append(asset[1])
    values.append(fetch.get_live_crypto_rate(asset[1]))


def load_material(values, idx, asset):
    idx.append(asset[1])
    values.append(fetch.get_live_material_rate(asset[1]))


def load_stock(values, idx, asset):
    idx.append(asset[1])
    values.append(fetch.get_live_crypto_rate(asset[1]))


def load_fav_assets():
    content = [y.split(': ') for y in utils.read_file('fav.txt')];
    '''-> [asset_type, asset_name]'''
    idx = []
    values = []

    for el in content:
        if el[0] == 'EXRATE':
            load_currency(values, idx, el)
        elif el[0] == 'CRYPTO':
            load_crypto(values, idx, el)
        elif el[0] == 'MATERIALS':
            load_material(values, idx, el)
        elif el[0] == 'STOCK':
            load_stock(values, idx, el)
        else:
            '''do nothing'''
    d = {'VALUE': values}
    df = pd.DataFrame(data=d, index=idx)
    return df


"""historical data from dictionary to dataframe which will be show in GUI"""


def load_historical_assets(tile_type, asset_code, date_from, date_to, interval=Interval.DAY):
    if tile_type == utils.TileType.CURRENCIES:
        code = asset_code.split('-')
        if len(code) == 1:
            dict_data = {}
        else:
            dict_data = fetch.get_currency_historical_data(code[0], code[1], date_from, date_to, interval)
        columns = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE']

    elif tile_type == utils.TileType.STOCKS:
        dict_data = fetch.get_stock_historical_data(asset_code, date_from, date_to, interval)
        columns = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']

    elif tile_type == utils.TileType.CRYPTO:
        dict_data = fetch.get_crypto_historical_data(asset_code, date_from, date_to, interval)
        columns = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE']

    elif tile_type == utils.TileType.MATERIALS:
        dict_data = fetch.get_futures_historical_data(asset_code, date_from, date_to, interval)
        columns = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE']

    result = merge_key_value(dict_data)
    data = pd.DataFrame(result,
                        columns=columns,
                        index=range(1, len(result) + 1))
    return data


def load_top_currencies(currency):
    rates = fetch.get_top_currencies(currency)
    if rates is None:
        return None
    result = merge_key_value(rates)
    data = pd.DataFrame(result,
                        columns=['Name', 'To ' + currency, 'From ' + currency],
                        index=range(1, len(result) + 1))
    return data


def load_top_stocks():
    rates = fetch.get_most_active_stocks()
    result = merge_key_value(rates)
    data = pd.DataFrame(result,
                        columns=['Code', 'Name', 'Last price'],
                        index=range(1, len(result) + 1)
    )
    return data

def load_top_futures():
    rates = fetch.get_top_futures()
    result = merge_key_value(rates)
    data = pd.DataFrame(result,
                        columns=['Code', 'Name', 'Last price'],
                        index=range(1, len(result) + 1)
                        )
    return data

def load_top_cryptos():
    rates = fetch.get_top_cryptos()
    result = merge_key_value(rates)
    data = pd.DataFrame(result,
                        columns=['Code', 'Name', 'Last price'],
                        index=range(1, len(result) + 1)
                        )
    return data

def merge_key_value(rates):
    result = []
    for i in range(0, len(list(rates.values()))):
        result.append((list(rates.keys())[i],) + list(rates.values())[i])
    return result
