import sys
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtWidgets
from enum import Enum
import pandas as pd
from bs4 import BeautifulSoup
import requests
import copy
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


class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])


class TileType(Enum):
    STOCKS = 1
    CURRENCIES = 2


class Tile:
    """upper left corner"""
    x_coord = 0
    y_coord = 0

    tile_width = 100
    tile_height = 200

    btn_size = 15

    def __init__(self, current_window, x_coord, tile_type):
        self.window = current_window
        self.x_coord = x_coord
        self.label = None
        self.resizing_btn = None
        self.init_ui(tile_type)

    def init_ui(self, tile_type):

        self.label = QtWidgets.QTableView(self.window)

        """Example widget for USD -> PLN currency"""

        data = pd.DataFrame(list(get_currency_historical_data('USD', 'PLN', '03/03/2021', '04/04/2021', '1').values()),
                            columns=['OPEN', 'HIGH', 'LOW', 'CLOSE'],
                            index=list(get_currency_historical_data('USD', 'PLN', '03/03/2021', '04/04/2021', '1').keys()))

        self.model = TableModel(data)

        self.label.setModel(self.model)
        self.label.setGeometry(self.x_coord, self.y_coord, self.tile_width, self.tile_height)
        self.label.show()

        self.resizing_btn = QtWidgets.QPushButton(self.window)

        self.resizing_btn.pressed.connect(self.adjust_size_on)
        self.resizing_btn.setGeometry(self.y_coord, self.x_coord, self.btn_size, self.btn_size)
        self.resizing_btn.move(self.tile_width - self.btn_size + self.x_coord, self.tile_height - self.btn_size)
        self.resizing_btn.setStyleSheet("background-color: lightgrey;")
        self.resizing_btn.show()

    def adjust_size_on(self):
        self.window.curr_tile = self

    def update_size(self, tiles):
        idx = tiles.index(self)
        if idx == len(tiles) - 1:
            next_tile_x = float("inf")
            next_tile_y = float("inf")
        else:
            next_tile_x = tiles[idx + 1].x_coord

        new_width = self.window.mouse_x_coord - self.x_coord
        if new_width + self.x_coord < next_tile_x:
            self.tile_width = new_width
            self.resizing_btn.move(self.window.mouse_x_coord - self.btn_size, self.window.mouse_y_coord - self.btn_size)
            self.label.setGeometry(self.x_coord, self.y_coord, self.tile_width, self.window.mouse_y_coord)


class MyWindow(QMainWindow):
    mouse_x_coord = 0
    mouse_y_coord = 0
    Tiles = []

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(200, 200, 500, 300)
        self.setWindowTitle("MyAssets")
        self.curr_tile = None
        self.add_tile_btn = None
        self.init_ui()

    def init_ui(self):
        self.add_tile_btn = QtWidgets.QPushButton(self)
        self.add_tile_btn.clicked.connect(self.add_tile)
        self.add_tile_btn.setGeometry(150, 100, 15, 15)
        self.add_tile_btn.move(200, 200)
        self.add_tile_btn.setStyleSheet("background-color: red;")

    def add_tile(self):
        if len(self.Tiles) == 0:
            self.Tiles.append(Tile(self, 0, TileType.STOCKS))
        else:
            l = len(self.Tiles)
            self.Tiles.append(Tile(self, self.Tiles[l - 1].tile_width + self.Tiles[l - 1].x_coord, TileType.STOCKS))

    def mouseMoveEvent(self, event):
        self.mouse_x_coord = event.x()
        self.mouse_y_coord = event.y()

        if self.curr_tile is not None:
            self.curr_tile.update_size(self.Tiles)

    def mouseReleaseEvent(self, event):
        self.curr_tile = None


def window():
    app = QtWidgets.QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())


window()
