from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QToolBar, QAction, QVBoxLayout, QHBoxLayout, QFrame, \
    QWidget
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
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

def get_live_material_rate(material):
    adress = 'https://www.marketwatch.com/investing/future/'+ material +''
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
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])


class TileType(Enum):
    STOCKS = 1
    CURRENCIES = 2


class Tile:
    btn_size = 15

    def __init__(self, current_window, x_coord, tile_type):
        self.x_coord = 0
        self.y_coord = 0

        self.tile_width = 100
        self.tile_height = 200
        self.frame = current_window.upper_frame
        self.window = current_window
        self.x_coord = x_coord
        self.label = None
        self.resizing_btn = None
        self.moving_btn = None
        self.init_ui(tile_type)

    def init_ui(self, tile_type):

        self.label = QtWidgets.QTableView(self.frame)

        """Example widget"""
        data1 = load_top_currencies('USD')
        self.model = TableModel(data1)

        self.label.setModel(self.model)
        self.label.setGeometry(self.x_coord, self.y_coord, self.tile_width, self.tile_height)
        self.label.show()

        self.resizing_btn = QtWidgets.QPushButton(self.frame)
        self.resizing_btn.pressed.connect(self.resizing_on)
        self.resizing_btn.setGeometry(self.y_coord, self.x_coord, self.btn_size, self.btn_size)
        self.resizing_btn.move(self.tile_width - self.btn_size + self.x_coord, self.tile_height - self.btn_size)
        self.resizing_btn.setStyleSheet("background-color: lightgrey;")
        self.resizing_btn.show()

        self.moving_btn = QtWidgets.QPushButton(self.frame)
        self.moving_btn.pressed.connect(self.moving_on)
        self.moving_btn.setGeometry(self.x_coord, self.y_coord, self.btn_size, self.btn_size)
        self.moving_btn.setStyleSheet("background-color: grey;")
        self.moving_btn.show()

    def moving_on(self):
        self.window.curr_tile = self
        self.move = 1

    def resizing_on(self):
        self.window.curr_tile = self
        self.move = 0

    def adjust_tile(self, tiles):
        if self.move == 1:
            self.move_tile(tiles)
        else:
            self.resize_tile(tiles)

    def move_tile(self, tiles):
        idx = tiles.index(self)
        left_limit = 0
        right_limit = 0
        if (idx == 0):
            left_limit = 0
        else:
            left_limit = tiles[idx - 1].x_coord + tiles[idx - 1].tile_width

        if idx == len(tiles) - 1:
            right_limit = float("inf")
        else:
            right_limit = tiles[idx + 1].x_coord - self.tile_width
        if left_limit < self.window.mouse_x_coord < right_limit:
            self.x_coord = self.window.mouse_x_coord

            self.moving_btn.move(self.window.mouse_x_coord, self.y_coord )
            self.resizing_btn.move(self.window.mouse_x_coord - self.btn_size + self.tile_width,
                                   self.y_coord  - self.btn_size + self.tile_height)
            self.label.setGeometry(self.x_coord, self.y_coord, self.tile_width, self.tile_height)
        else:
            """do nothing"""

    def resize_tile(self, tiles):
        idx = tiles.index(self)
        if idx == len(tiles) - 1:
            next_tile_x = float("inf")
            next_tile_y = float("inf")
        else:
            next_tile_x = tiles[idx + 1].x_coord

        new_width = self.window.mouse_x_coord - self.x_coord
        if new_width + self.x_coord < next_tile_x:
            self.tile_width = new_width
            self.resizing_btn.move(self.window.mouse_x_coord - self.btn_size, self.tile_height - self.btn_size)
            self.label.setGeometry(self.x_coord, self.y_coord, self.tile_width, self.tile_height)


class Header(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        self.setMaximumHeight(80)
        hbox = QHBoxLayout()

        logo_lab = QLabel('MyAssets')
        logo_lab.setFont(QFont('Helvetica', 24, QFont.DemiBold))

        balance_lab = QLabel('Balance')
        balance_lab.setFont(QFont('Serif', 18))

        cur_balance = 0.0
        change = 0.0
        balance_state_lab = QLabel('{:.2f} $ ({:.2f})%'.format(cur_balance, change))
        balance_state_lab.setFont(QFont('Serif', 12))

        hbox.addWidget(logo_lab)
        hbox.addStretch(1)
        hbox.addWidget(balance_lab)
        hbox.addWidget(balance_state_lab)

        self.setLayout(hbox)


class MainWindow(QMainWindow):
    mouse_x_coord = 0
    mouse_y_coord = 0
    Tiles = []
    def __init__(self, *args, **kwargs):
        self.curr_tile = None
        self.add_tile_btn = None
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("MyAssets")

        vbox = QVBoxLayout()
        container_wid = QWidget()
        self.setCentralWidget(container_wid)
        container_wid.setLayout(vbox)
        self.header = Header()

        self.upper_frame = QFrame(self)
        self.upper_frame.setFrameShape(QFrame.Panel | QFrame.Sunken)
        bottom_frame = QFrame(self)
        bottom_frame.setFrameShape(QFrame.Panel | QFrame.Sunken)
        vbox.addWidget(self.header)
        vbox.addWidget(self.upper_frame)
        vbox.addWidget(bottom_frame)
        self.init_ui()

    def init_ui(self):
        self.add_tile_btn = QtWidgets.QPushButton(self)
        self.add_tile_btn.clicked.connect(self.add_tile)
        self.add_tile_btn.setGeometry(150, 100, 15, 15)
        self.add_tile_btn.move(1815, 95)

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
            self.curr_tile.adjust_tile(self.Tiles)

    def mouseReleaseEvent(self, event):
        self.curr_tile = None

    def onMyToolBarButtonClick(self, s):
        print("click", s)
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def read_file(file_name):
    with open(file_name, 'r') as f:
        content = (f.readlines())
    return [x.strip() for x in content]


def write_file(file_name, line):
    with open(file_name, 'a') as f:
        f.write(line + "\n")


def load_currency(values, idx, asset):
    idx.append(asset[1])
    currencies = asset[1].split('-')
    values.append(get_live_currency_exchange_rate(currencies[0], currencies[1]))

def load_crypto(values, idx, asset):
    idx.append(asset[1])
    values.append(get_live_crypto_rate(asset[1]))

def load_material(values, idx, asset):
    idx.append(asset[1])
    values.append(get_live_material_rate(asset[1]))

def load_stock(values, idx, asset):
    idx.append(asset[1])
    values.append(get_live_crypto_rate(asset[1]))

def load_fav_assets():
    content = [y.split(': ') for y in read_file('fav.txt')]; '''-> [asset_type, asset_name]'''
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

def load_historical_assets(tile_type, date_from, date_to):#dokonczyc
    if tile_type == TileType.CURRENCIES:
        data = pd.DataFrame(list(get_currency_historical_data('USD', 'PLN', '03/03/2021', '04/04/2021', '1').values()),
                        columns=['OPEN', 'HIGH', 'LOW', 'CLOSE'],
                        index=list(get_currency_historical_data('USD', 'PLN', '03/03/2021', '04/04/2021', '1').keys()))
    elif tile_type == TileType.CURRENCIES:
        data = pd.DataFrame(list(get_currency_historical_data('USD', 'PLN', '03/03/2021', '04/04/2021', '1').values()),
                            columns=['OPEN', 'HIGH', 'LOW', 'CLOSE'],
                            index=list(
                                get_currency_historical_data('USD', 'PLN', '03/03/2021', '04/04/2021', '1').keys()))
    return data


def get_top_currencies(currency):
    adress = 'https://www.x-rates.com/table/?from='+ currency +'&amount=1'
    html_data = requests.get(adress).text
    soup = BeautifulSoup(html_data, 'lxml')
    rates = soup.find('table', class_="tablesorter ratesTable").find_all('td')
    result = {}
    for i in range(0, len(rates), 3):
        result[rates[i].text] = (rates[i+1].text, rates[i+2].text,)
    return result

def load_top_currencies(currency):
    rates = get_top_currencies(currency)
    data = pd.DataFrame(list(rates.values()),
                        columns=['To ' + currency, 'From ' + currency],
                        index=list(rates.keys()))
    return data



app = QApplication([])
window = MainWindow()
window.show()

app.exec_()
