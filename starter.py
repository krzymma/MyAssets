import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QFrame, \
    QWidget
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtWidgets
from dialog import OpDialog
import tile
import utils


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
        self.adding_button.setIcon(QIcon(os.path.dirname(os.path.abspath(__file__)) + '/' + 'plus_icon.svg'))  # DOESNT WORK :(

        self.vertical_layout = QVBoxLayout(self)
        self.vertical_layout.addWidget(self.adding_button, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

    def add_tile(self, tile_type, tile_option=None, asset_code=None, start_date=None, end_date=None):
        if len(self.tiles) == 0:
            self.tiles.append(tile.Tile(self, 0, tile_type, start_date, end_date, tile_option, asset_code))
        else:
            l = len(self.tiles)
            self.tiles.append(tile.Tile(self, self.tiles[l - 1].tile_width + self.tiles[l - 1].x_coord,
                                        tile_type, start_date, end_date, tile_option, asset_code))

    def remove_tile(self, tile):
        self.tiles[self.tiles.index(tile)] = None
        new_tiles_list = []
        for i in range(0, len(self.tiles)):
            if self.tiles[i] is not None:
                new_tiles_list.append(self.tiles[i])
        self.tiles = new_tiles_list


    @QtCore.pyqtSlot(QtWidgets.QAction)
    def on_menu_triggered(self, action):
        if action.text() == "Currencies":
            dialog = OpDialog(utils.TileType.CURRENCIES)
            dialog.exec_()
            if dialog.get_data()[0] and (dialog.get_data()[1] == 'Top'
                                         or (dialog.get_data()[1] == 'Historical' and dialog.get_data()[2] != '')):
                self.add_tile(tile.TileType.CURRENCIES, dialog.get_data()[1], dialog.get_data()[2],
                              dialog.get_data()[3], dialog.get_data()[4])  # passing: Tiletype,
                                                                            # option-historical/live, asset symbol,
                                                                            # start date and end date
        elif action.text() == "Favourites":
            self.add_tile(tile.TileType.FAVOURITES)
        elif action.text() == "Stocks":
            dialog = OpDialog(utils.TileType.STOCKS)
            dialog.exec_()
            if dialog.get_data()[0] and (dialog.get_data()[1] == 'Top' or (
                    dialog.get_data()[1] == 'Historical' and dialog.get_data()[2] != '')):
                self.add_tile(tile.TileType.STOCKS, dialog.get_data()[1], dialog.get_data()[2],
                              dialog.get_data()[3], dialog.get_data()[4])
        elif action.text() == "Materials":
            dialog = OpDialog(utils.TileType.MATERIALS)
            dialog.exec_()
            if dialog.get_data()[0] and (dialog.get_data()[1] == 'Top' or (
                    dialog.get_data()[1] == 'Historical' and dialog.get_data()[2] != '')):
                self.add_tile(tile.TileType.MATERIALS, dialog.get_data()[1], dialog.get_data()[2],
                              dialog.get_data()[3], dialog.get_data()[4])
        elif action.text() == "Cryptocurrencies":
            dialog = OpDialog(utils.TileType.CRYPTO)
            dialog.exec_()
            if dialog.get_data()[0] and (dialog.get_data()[1] == 'Top' or (
                    dialog.get_data()[1] == 'Historical' and dialog.get_data()[2] != '')):
                self.add_tile(tile.TileType.CRYPTO, dialog.get_data()[1], dialog.get_data()[2],
                              dialog.get_data()[3], dialog.get_data()[4])

    """functions read mouse position after mouse click and update tile"""
    def mouseMoveEvent(self, event):
        self.mouse_x_coord = event.x()
        self.mouse_y_coord = event.y()
        if self.curr_tile is not None:
            self.curr_tile.adjust_tile(self.tiles)

    def mouseReleaseEvent(self, event):
        self.curr_tile = None

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
