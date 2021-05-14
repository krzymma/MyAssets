from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QToolBar, QAction, QVBoxLayout, QHBoxLayout, QFrame, \
    QWidget, QDialog, QLineEdit
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtWidgets
from enum import Enum
import pandas as pd
from bs4 import BeautifulSoup
import requests
import sys

NO_COL_CURR = 5
NO_COL_CRYPTO = 5
NO_COL_STOCK = 6
MIN_TILE_WIDTH = 200


class TileType(Enum):
    STOCKS = 1
    CURRENCIES = 2
    FAVOURITES = 3
    CRYPTO = 4
    MATERIALS = 5


def read_file(file_name):
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
        res[tmp_data2[i]] = tuple(tmp_data2[j] for j in range(i + 1, i + no_columns))

    return res


"""functions download historical data in csv format"""
def get_currency_historical_data(from_currency, to_currency, from_date, to_date, day_interval):
    url = 'https://www.marketwatch.com/investing/currency/' + from_currency + to_currency + \
          '/downloaddatapartial?startdate=' + from_date + '+%2000:00:00&enddate=' + to_date + '%2023:59:59&daterange=d30&frequency=p' + day_interval + \
          'd&csvdownload=true&downloadpartial=false&newdates=false'
    data_csv = requests.get(url)
    return convert_data_to_dict(data_csv, NO_COL_CURR)


def get_crypto_historical_data(crypto, from_date, to_date, day_interval, to_currency='usd'):
    url = 'https://www.marketwatch.com/investing/cryptocurrency/' + crypto + to_currency + '' \
           '/downloaddatapartial?startdate=' + from_date + '%2000:00:00&enddate=' + to_date + '%2023:59:59&daterange=d30&frequency=' \
           'p' + day_interval + 'd&csvdownload=true&downloadpartial=false&newdates=false'
    data_csv = requests.get(url)
    return convert_data_to_dict(data_csv, NO_COL_CRYPTO)


def get_stock_historical_data(stock, from_date, to_date, day_interval):
    url = 'https://www.marketwatch.com/investing/stock/' + stock + '' \
    '/downloaddatapartial?startdate=' + from_date + '%2000:00:00&enddate=' + to_date + '%2023:59:59&daterange=d30&frequency=' \
    'p' + day_interval + 'd&csvdownload=true&downloadpartial=false&newdates=false'
    data_csv = requests.get(url)
    return convert_data_to_dict(data_csv, NO_COL_STOCK)


"""functions download live values of assets"""
def get_live_val(adress):
    html_data = requests.get(adress).text
    soup = BeautifulSoup(html_data, 'lxml')
    rate = soup.find('bg-quote', class_="value").text.replace(',', '')
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
    rates = soup.find('table', class_="tablesorter ratesTable").find_all('td')
    result = {}
    for i in range(0, len(rates), 3):
        result[rates[i].text] = (rates[i + 1].text, rates[i + 2].text,)
    return result

"""return dictionary key: code, value: name,price"""
def get_top_futures():
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



"""functions load data from fav.txt file"""
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
    content = [y.split(': ') for y in read_file('fav.txt')];
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
def load_historical_assets(tile_type, date_from, date_to):  # dokonczyc
    if tile_type == TileType.CURRENCIES:
        data = pd.DataFrame(list(get_currency_historical_data('USD', 'PLN', '03/03/2021', '04/04/2021', '1').values()),
                            columns=['OPEN', 'HIGH', 'LOW', 'CLOSE'],
                            index=list(
                                get_currency_historical_data('USD', 'PLN', '03/03/2021', '04/04/2021', '1').keys()))
    elif tile_type == TileType.CURRENCIES:
        data = pd.DataFrame(list(get_currency_historical_data('USD', 'PLN', '03/03/2021', '04/04/2021', '1').values()),
                            columns=['OPEN', 'HIGH', 'LOW', 'CLOSE'],
                            index=list(
                                get_currency_historical_data('USD', 'PLN', '03/03/2021', '04/04/2021', '1').keys()))
    return data


def load_top_currencies(currency):
    rates = get_top_currencies(currency)
    data = pd.DataFrame(list(rates.values()),
                        columns=['To ' + currency, 'From ' + currency],
                        index=list(rates.keys()))
    return data


def load_top_stocks():
    rates = get_most_active_stocks()
    data = pd.DataFrame(list(rates.values()),
                        columns=['Name', 'Last price'],
                        index=list(rates.keys()))
    return data

def load_top_futures():
    rates = get_top_futures()
    data = pd.DataFrame(list(rates.values()),
                        columns=['Name', 'Last price'],
                        index=list(rates.keys()))
    return data

def load_top_cryptos():
    rates = get_top_cryptos()
    data = pd.DataFrame(list(rates.values()),
                        columns=['Name', 'Last price'],
                        index=list(rates.keys()))
    return data




"""table model in Tile"""
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


class Tile:
    btn_size = 15

    def __init__(self, current_window, x_coord, tile_type):
        self.x_coord = 0
        self.y_coord = 0
        self.data = None
        self.tile_width = MIN_TILE_WIDTH
        self.tile_height = current_window.height()
        self.frame = current_window
        self.window = current_window
        self.x_coord = x_coord
        self.data_table = None
        self.resizing_btn = None
        self.moving_btn = None
        self.tile_type = tile_type
        self.load_data()
        self.model = TableModel(self.data)
        self.move = 0
        self.init_ui()

    # TODO: add rest of loading functions
    def load_data(self):
        if self.tile_type == TileType.CURRENCIES:
            self.data = load_top_currencies('USD')
        elif self.tile_type == TileType.FAVOURITES:
            self.data = load_fav_assets()
        elif self.tile_type == TileType.STOCKS:
            self.data = load_top_stocks()
        elif self.tile_type == TileType.CRYPTO:
            self.data = load_top_cryptos()
        elif self.tile_type == TileType.MATERIALS:
            self.data = load_top_futures()

    def init_ui(self):

        self.data_table = QtWidgets.QTableView(self.frame)
        self.data_table.setModel(self.model)
        self.data_table.setGeometry(self.x_coord, self.y_coord, self.tile_width, self.tile_height)
        self.data_table.show()
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

    """move/resize tile functions"""
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

    """if it is possible move tile"""
    def move_tile(self, tiles):
        idx = tiles.index(self)
        if (idx == 0):
            left_limit = 0
        else:
            left_limit = tiles[idx - 1].x_coord + tiles[idx - 1].tile_width

        if idx == len(tiles) - 1:
            right_limit = self.window.width() - self.tile_width
        else:
            right_limit = tiles[idx + 1].x_coord - self.tile_width
        if left_limit < self.window.mouse_x_coord < right_limit:
            self.x_coord = self.window.mouse_x_coord

            self.moving_btn.move(self.window.mouse_x_coord, self.y_coord)
            self.resizing_btn.move(self.window.mouse_x_coord - self.btn_size + self.tile_width,
                                   self.y_coord - self.btn_size + self.tile_height)
            self.data_table.setGeometry(self.x_coord, self.y_coord, self.tile_width, self.tile_height)
        else:
            """do nothing"""

    """if it is possible resize tile"""
    def resize_tile(self, tiles):
        idx = tiles.index(self)
        if idx == len(tiles) - 1:
            next_tile_x = float("inf")
            next_tile_y = float("inf")
        else:
            next_tile_x = tiles[idx + 1].x_coord

        new_width = self.window.mouse_x_coord - self.x_coord
        if new_width + self.x_coord < next_tile_x and new_width > MIN_TILE_WIDTH:
            self.tile_width = new_width
            self.resizing_btn.move(self.window.mouse_x_coord - self.btn_size, self.tile_height - self.btn_size)
            self.data_table.setGeometry(self.x_coord, self.y_coord, self.tile_width, self.tile_height)


class Header(QWidget):
    def __init__(self, win):
        super(QWidget, self).__init__()
        self.window = win
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

        self.close_btn = QtWidgets.QPushButton('Exit')
        self.close_btn.clicked.connect(self.window.close)

        hbox.addWidget(self.close_btn, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)

        self.setLayout(hbox)


class MainSubFrame(QFrame):
    mouse_x_coord = 0
    mouse_y_coord = 0

    def __init__(self):
        super(MainSubFrame, self).__init__()
        self.setFrameShape(QFrame.Panel | QFrame.Sunken)
        self.tiles = []
        self.curr_tile = None
        self.adding_button = QtWidgets.QPushButton('Add')
        menu = QtWidgets.QMenu(
            self.adding_button,
            triggered=self.on_menu_triggered
        )
        for text in ("Favourites", "Currencies", "Stocks", "Materials", "Cryptocurrencies"):
            menu.addAction(text)
        self.adding_button.setMenu(menu)
        self.adding_button.setIcon(QIcon('add_icon.png'))  # DOESNT WORK :(

        self.vertical_layout = QVBoxLayout(self)
        self.vertical_layout.addWidget(self.adding_button, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

    def add_tile(self, tile_type):
        if len(self.tiles) == 0:
            self.tiles.append(Tile(self, 0, tile_type))
        else:
            l = len(self.tiles)
            self.tiles.append(Tile(self, self.tiles[l - 1].tile_width + self.tiles[l - 1].x_coord, tile_type))

    # TODO: apply additional setting of tiles
    @QtCore.pyqtSlot(QtWidgets.QAction)
    def on_menu_triggered(self, action):
        if action.text() == "Currencies":
            dialog = OpDialog()
            dialog.exec_()
            if dialog.get_data()[0] and (dialog.get_data()[1] == 'Top' or (dialog.get_data()[1] == 'Historical' and dialog.get_data()[2] != '')):
                self.add_tile(TileType.CURRENCIES)
        elif action.text() == "Favourites":
            self.add_tile(TileType.FAVOURITES)
        elif action.text() == "Stocks":
            dialog = OpDialog()
            dialog.exec_()
            if dialog.get_data()[0] and (dialog.get_data()[1] == 'Top' or (
                    dialog.get_data()[1] == 'Historical' and dialog.get_data()[2] != '')):
                self.add_tile(TileType.STOCKS)
        elif action.text() == "Materials":
            dialog = OpDialog()
            dialog.exec_()
            if dialog.get_data()[0] and (dialog.get_data()[1] == 'Top' or (
                    dialog.get_data()[1] == 'Historical' and dialog.get_data()[2] != '')):
                self.add_tile(TileType.MATERIALS)
        elif action.text() == "Cryptocurrencies":
            dialog = OpDialog()
            dialog.exec_()
            if dialog.get_data()[0] and (dialog.get_data()[1] == 'Top' or (
                    dialog.get_data()[1] == 'Historical' and dialog.get_data()[2] != '')):
                self.add_tile(TileType.CRYPTO)

    """functions read mouse position after mouse click and update tile"""
    def mouseMoveEvent(self, event):
        self.mouse_x_coord = event.x()
        self.mouse_y_coord = event.y()
        if self.curr_tile is not None:
            self.curr_tile.adjust_tile(self.tiles)

    def mouseReleaseEvent(self, event):
        self.curr_tile = None

"""Adding tile additional settings dialog"""
class OpDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Input")
        self.gui_init()
        self.approved = False
        self.tile_option = "Top"

    def push_ok(self):
        self.approved = True
        self.close()

    def push_close(self):
        self.approved = False
        self.close()

    def gui_init(self):
        self.add_asset = QLineEdit()

        row_2 = QHBoxLayout()
        row_2.addWidget(QLabel("Asset Code:"))
        row_2.addWidget(self.add_asset)

        self.menu_btn = QtWidgets.QPushButton()
        self.menu_btn.setText("Choose tile option")

        menu = QtWidgets.QMenu(
            self.menu_btn,
            triggered=self.on_menu_triggered
        )
        for text in ("Historical", "Top"):
            menu.addAction(text)
        self.menu_btn.setMenu(menu)

        row_1 = QHBoxLayout()
        row_1.addWidget(self.menu_btn)

        ok_btn = QtWidgets.QPushButton()
        ok_btn.setText("OK")
        ok_btn.pressed.connect(self.push_ok)

        close_btn = QtWidgets.QPushButton()
        close_btn.setText("CLOSE")
        close_btn.pressed.connect(self.push_close)

        row_3 = QHBoxLayout()
        row_3.addWidget(close_btn)
        row_3.addWidget(ok_btn)

        layout = QVBoxLayout()
        layout.addLayout(row_1)
        layout.addLayout(row_2)
        layout.addLayout(row_3)

        self.setLayout(layout)

    @QtCore.pyqtSlot(QtWidgets.QAction)
    def on_menu_triggered(self, action):
        self.menu_btn.setText(action.text())
        self.tile_option = action.text()
        if action.text() == 'Historical':
            self.add_asset.setEnabled(True)
        else:
            self.add_asset.setDisabled(True)#for top assets dont need to specify


    def get_data(self):
        if self.tile_option == 'Historical':
            return (self.approved, self.tile_option, self.add_asset.text())
        else:
            return (self.approved, self.tile_option, '')

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):

        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("MyAssets")
        self.setWindowFlags(Qt.FramelessWindowHint)
        vbox = QVBoxLayout()
        container_wid = QWidget()
        self.setCentralWidget(container_wid)
        container_wid.setLayout(vbox)

        header = Header(self)
        upper_frame = MainSubFrame()
        bottom_frame = MainSubFrame()

        vbox.addWidget(header)
        vbox.addWidget(upper_frame)
        vbox.addWidget(bottom_frame)



app = QApplication([])
window = MainWindow()
window.showMaximized()

app.exec_()
