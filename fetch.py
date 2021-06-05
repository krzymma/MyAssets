from bs4 import BeautifulSoup
from utils import convert_data_to_dict
from utils import Interval
import requests
NO_COL_CURR = 5
NO_COL_CRYPTO = 5
NO_COL_STOCK = 6

"""functions download historical data in csv format"""
def get_currency_historical_data(from_currency, to_currency, from_date, to_date, interval=Interval.DAY):
    url = 'https://www.marketwatch.com/investing/currency/' + from_currency + to_currency + \
          '/downloaddatapartial?startdate=' + from_date + '+%2000:00:00&enddate=' + to_date + '%2023:59:59&daterange=d30&frequency=p' + str(interval) + \
          '&csvdownload=true&downloadpartial=false&newdates=false'
    data_csv = requests.get(url)
    return convert_data_to_dict(data_csv, NO_COL_CURR)


def get_crypto_historical_data(crypto, from_date, to_date, interval=Interval.DAY, to_currency='usd'):
    url = 'https://www.marketwatch.com/investing/cryptocurrency/' + crypto + to_currency + '' \
           '/downloaddatapartial?startdate=' + from_date + '%2000:00:00&enddate=' + to_date + '%2023:59:59&daterange=d30&frequency=' \
           'p' + str(interval) + '&csvdownload=true&downloadpartial=false&newdates=false'
    data_csv = requests.get(url)
    return convert_data_to_dict(data_csv, NO_COL_CRYPTO)


def get_stock_historical_data(stock, from_date, to_date, interval=Interval.DAY):
    url = 'https://www.marketwatch.com/investing/stock/' + stock + '' \
    '/downloaddatapartial?startdate=' + from_date + '%2000:00:00&enddate=' + to_date + '%2023:59:59&daterange=d30&frequency=' \
    'p' + str(interval) + '&csvdownload=true&downloadpartial=false&newdates=false'
    data_csv = requests.get(url)
    return convert_data_to_dict(data_csv, NO_COL_STOCK)


def get_material_historical_data(material, from_date, to_date, interval=Interval.DAY):
    url = 'https://www.marketwatch.com/investing/future/'+ material +\
        '/downloaddatapartial?startdate='+from_date+'%2000:00:00&enddate='+to_date+\
          '%2023:59:59&daterange=d30&frequency=p'+ str(interval) +'&csvdownload=true&downloadpartial=false&newdates=false'
    data_csv = requests.get(url)
    return convert_data_to_dict(data_csv, NO_COL_CURR)


"""functions download live values of assets"""
def get_live_val(adress):
    html_data = requests.get(adress).text
    soup = BeautifulSoup(html_data, 'lxml')
    rate = soup.find('div', class_="intraday__data").find(class_="value").text.replace(',', '')
    return rate


def get_live_stock_rate(stock):
    adress = 'https://www.marketwatch.com/investing/stock/' + stock + '/download-data?startDate=03/13/2021&endDate=04/12/2021'
    return get_live_val(adress)


def get_live_currency_exchange_rate(from_currency, to_currency):
    adress = 'https://www.marketwatch.com/investing/currency/' + from_currency + to_currency + '?mod=mw_quote_recentlyviewed'
    return get_live_val(adress)


def get_live_crypto_rate(crypto, to_currency='usd'):
    adress = 'https://www.marketwatch.com/investing/cryptocurrency/' + crypto + to_currency + '?mod=mw_quote_recentlyviewed'
    return get_live_val(adress)


def get_live_material_rate(material):
    adress = 'https://www.marketwatch.com/investing/future/' + material + ''
    return get_live_val(adress)


"""functions download top assets and return dictionary dictionary"""
def get_top_currencies(currency):
    adress = 'https://www.x-rates.com/table/?from=' + currency + '&amount=1'
    html_data = requests.get(adress).text

    soup = BeautifulSoup(html_data, 'lxml')

    if len(soup.find_all('table', class_="tablesorter ratesTable")) == 0:  # incorrect currency code provided
        return None

    rates = soup.find('table', class_="tablesorter ratesTable").find_all('td')

    result = {}
    for i in range(0, len(rates), 3):
        result[rates[i].text] = (rates[i + 1].text, rates[i + 2].text,)
    return result

"""return dictionary key: code, value: name,price"""
def get_top_materials():
    adress = 'https://www.marketwatch.com/investing/futures'
    html_data = requests.get(adress).text
    soup = BeautifulSoup(html_data, 'lxml')
    rates = soup.find('div', class_="overflow--table").find_all('td')
    result = {}
    for i in range(1, len(rates), 6):
        result[rates[i].text.strip()] = (rates[i + 1].text.strip(), rates[i + 2].text.strip(),)
    return result

"""return dictionary key: code, value: name,price"""
def get_top_cryptos():
    adress = 'https://www.marketwatch.com/column/cryptos'
    html_data = requests.get(adress).text
    soup = BeautifulSoup(html_data, 'lxml')
    rates = soup.find('div', class_="overflow--table").find_all('td')
    result = {}
    for i in range(1, len(rates), 6):
        result[rates[i].text.strip()] = (rates[i + 1].text.strip(), rates[i + 2].text.strip(),)
    return result

"""return dictionary key: code, value: name,price"""
def get_most_active_stocks():
    adress = 'https://www.marketwatch.com/tools/screener?exchange=Nasdaq&report=MostActiveByDollarsTraded'
    html_data = requests.get(adress).text
    soup = BeautifulSoup(html_data, 'lxml')
    rates = soup.find('tbody').find_all('td')
    result = {}
    for i in range(0, len(rates), 7):
        result[rates[i].text.strip()] = (rates[i + 1].text.strip(), rates[i + 2].text.strip(),)
    return result