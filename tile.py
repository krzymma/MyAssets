from specific import SpecWindow
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QWidget, QMessageBox
from utils import TileType
import load
import os

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


class Tile(QWidget):
    btn_size = 15

    def __init__(self, current_window, x_coord, tile_type, start_date, end_date, tile_option=None, asset_code='USD'):
        super(QWidget, self).__init__()
        self.x_coord = 0
        self.y_coord = 0
        self.start_date = start_date
        self.end_date = end_date
        self.tile_option = tile_option
        self.asset_code = asset_code
        self.data = None
        self.tile_width = MIN_TILE_WIDTH
        self.tile_height = current_window.height()
        self.frame = current_window #??? 
        self.window = current_window #???
        self.x_coord = x_coord
        self.data_table = None
        self.resizing_btn = None
        self.moving_btn = None
        self.spec_window = None
        self.tile_type = tile_type
        self.load_data()
        self.move = 0
        if self.data is not None:
            self.model = TableModel(self.data)
        self.init_ui()

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
        if self.data is not None:
            self.data_table.setModel(self.model)
            self.data_table.doubleClicked.connect(self.handle_double_click)

        self.data_table.setGeometry(self.x_coord, self.y_coord, self.tile_width, self.tile_height)
        self.data_table.show()

        self.resizing_btn = QtWidgets.QPushButton(self.frame)
        self.resizing_btn.pressed.connect(self.resizing_on)
        self.resizing_btn.setGeometry(self.y_coord, self.x_coord, self.btn_size, self.btn_size)
        self.resizing_btn.move(self.tile_width - self.btn_size + self.x_coord, self.tile_height - self.btn_size)
        self.resizing_btn.setStyleSheet("background-color: lightgrey;")
        self.resizing_btn.show()

        self.save_btn = QtWidgets.QPushButton(self.frame)
        self.save_btn.setText("Save")
        self.save_btn.pressed.connect(self.save_data_to_file)
        self.save_btn.setGeometry(self.y_coord, self.x_coord, 3*self.btn_size, self.btn_size)
        self.save_btn.move(self.x_coord + 2*self.btn_size, self.y_coord)
        self.save_btn.setStyleSheet("background-color: lightgrey;")
        self.save_btn.show()

        self.remove_btn = QtWidgets.QPushButton(self.frame)
        self.remove_btn.pressed.connect(self.remove_self)
        self.remove_btn.setText("X")
        self.remove_btn.setGeometry(self.y_coord, self.x_coord, self.btn_size, self.btn_size)
        self.remove_btn.move(self.tile_width - self.btn_size + self.x_coord, self.y_coord)
        self.remove_btn.setStyleSheet("background-color: red;")
        self.remove_btn.show()

        self.moving_btn = QtWidgets.QPushButton(self.frame)
        self.moving_btn.pressed.connect(self.moving_on)
        self.moving_btn.setGeometry(self.x_coord, self.y_coord, self.btn_size, self.btn_size)
        self.moving_btn.setStyleSheet("background-color: grey;")
        self.moving_btn.show()

    def save_data_to_file(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select folder where your data will be saved')
        print(folder_path)
        if folder_path != '':
            self.data.to_csv(folder_path + '/dataCSV.csv', index=False, header=True)
            self.data.to_html(folder_path + '/dataHTML.html')
            info = "Your data saved successfully"
        else:
            info = 'Data not saved'

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(info)
        msg.setWindowTitle("Saving Data")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def remove_self(self):
        self.frame.remove_tile(self)
        self.remove_btn.hide()
        self.resizing_btn.hide()
        self.moving_btn.hide()
        self.save_btn.hide()
        self.data_table.hide()

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
            self.save_btn.move(self.window.mouse_x_coord + 2*self.btn_size, self.y_coord)
            self.remove_btn.move(self.window.mouse_x_coord - self.btn_size + self.tile_width, self.y_coord)
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
            self.remove_btn.move(self.window.mouse_x_coord - self.btn_size, self.y_coord)
            self.data_table.setGeometry(self.x_coord, self.y_coord, self.tile_width, self.tile_height)

    def handle_single_click(self, item):
        #This function will manage adding asset to wallet
        pass

    def handle_double_click(self, item):
        asset_code = self.data.index[item.row()]
        name = self.data['Name'][item.row()]
        self.spec_window = SpecWindow(self.tile_type, asset_code, name)
        self.spec_window.show()
