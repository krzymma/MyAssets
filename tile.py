from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtWidgets
from utils import TileType
import load 

MIN_TILE_WIDTH = 200

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

    def __init__(self, current_window, x_coord, tile_type, start_date, end_date, tile_option=None,asset_code='USD'):
        self.x_coord = 0
        self.y_coord = 0
        self.start_date = start_date
        self.end_date = end_date
        self.tile_option = tile_option
        self.asset_code = asset_code
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

    # TODO: add rest of loading functions and add assetCode to top currencies
    def load_data(self):
        if self.tile_type == TileType.CURRENCIES:

            if self.tile_option == 'Top':
                self.data = load.load_top_currencies(self.asset_code)
            else:
                self.data = load.load_historical_assets(TileType.CURRENCIES, self.asset_code, self.start_date, self.end_date)

        elif self.tile_type == TileType.FAVOURITES:
            self.data = load.load_fav_assets()

        elif self.tile_type == TileType.STOCKS:

            if self.tile_option == 'Top':
                self.data = load.load_top_stocks()
            else:
                self.data = load.load_historical_assets(TileType.STOCKS, self.asset_code, self.start_date, self.end_date)

        elif self.tile_type == TileType.CRYPTO:

            if self.tile_option == 'Top':
                self.data = load.load_top_cryptos()
            else:
                self.data = load.load_historical_assets(TileType.CRYPTO, self.asset_code, self.start_date, self.end_date)

        elif self.tile_type == TileType.MATERIALS:

            if self.tile_option == 'Top':
                self.data = load.load_top_futures()
            else:
                self.data = load.load_historical_assets(TileType.MATERIALS, self.asset_code, self.start_date, self.end_date)

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