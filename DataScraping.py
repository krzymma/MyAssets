from bs4 import BeautifulSoup
import requests
NO_COL_CURR = 5
NO_COL_CRYPTO = 5
NO_COL_STOCK = 6

def convert_data_to_dict(data_csv, no_columns):
    tmp_data1 = [y.split('\n') for y in data_csv.content.decode("utf-8").replace(',', '').replace('""', '"').split('"')]
    tmp_data2 = []
    for el in tmp_data1:
        for i in range(0, len(el)):
            if el[i] != '':
                tmp_data2.append(el[i])
    res = {}
    for i in range(1, len(tmp_data2) - 1, no_columns):
        res[tmp_data2[i]] = tuple(tmp_data2[j] for j in range(i+1, i+no_columns))

    return res

def get_currency_historical_data(from_currency, to_currency, from_date, to_date, day_interval):
    url = 'https://www.marketwatch.com/investing/currency/'+from_currency+to_currency+\
          '/downloaddatapartial?startdate='+from_date+'+%2000:00:00&enddate='+ to_date +'%2023:59:59&daterange=d30&frequency=p'+ day_interval +\
          'd&csvdownload=true&downloadpartial=false&newdates=false'
    data_csv = requests.get(url)
    return convert_data_to_dict(data_csv, NO_COL_CURR)


def get_crypto_historical_data(crypto, from_date, to_date, day_interval, to_currency = 'usd'):
    url = 'https://www.marketwatch.com/investing/cryptocurrency/'+ crypto + to_currency +'' \
          '/downloaddatapartial?startdate='+ from_date +'%2000:00:00&enddate='+ to_date +'%2023:59:59&daterange=d30&frequency=' \
          'p'+ day_interval +'d&csvdownload=true&downloadpartial=false&newdates=false'
    data_csv = requests.get(url)
    return convert_data_to_dict(data_csv, NO_COL_CRYPTO)

def get_stock_historical_data(stock, from_date, to_date, day_interval):
    url = 'https://www.marketwatch.com/investing/stock/'+ stock +'' \
          '/downloaddatapartial?startdate='+ from_date +'%2000:00:00&enddate='+ to_date +'%2023:59:59&daterange=d30&frequency=' \
          'p'+ day_interval +'d&csvdownload=true&downloadpartial=false&newdates=false'
    data_csv = requests.get(url)
    return convert_data_to_dict(data_csv, NO_COL_STOCK)

def get_live_val(adress):
    html_data = requests.get(adress).text
    soup = BeautifulSoup(html_data, 'lxml')
    rate = soup.find('bg-quote', class_="value").text.replace(',', '')
    return rate

def get_live_stock_rate( stock ):
    adress = 'https://www.marketwatch.com/investing/stock/'+stock+'/download-data?startDate=03/13/2021&endDate=04/12/2021'
    return get_live_val(adress)

def get_live_currency_exchange_rate( from_currency, to_currency ):
    adress = 'https://www.marketwatch.com/investing/currency/'+from_currency+to_currency+'?mod=mw_quote_recentlyviewed'
    return get_live_val(adress)

def get_live_crypto_rate( crypto, to_currency = 'usd' ):
    adress = 'https://www.marketwatch.com/investing/cryptocurrency/'+crypto+to_currency+'?mod=mw_quote_recentlyviewed'
    return get_live_val(adress)
