from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QDialog, QLineEdit, QDateEdit
from PyQt5 import QtCore, QtWidgets

import utils

"""Adding tile additional settings dialog"""
class OpDialog(QDialog):

    def __init__(self, tile_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Input")
        self.gui_init()
        self.approved = False
        self.tile_option = ""
        self.tile_type = tile_type

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

        self.date_from = QDateEdit(QDate().currentDate())
        self.date_to = QDateEdit(QDate().currentDate())

        row_3 = QHBoxLayout()
        row_3.addWidget(self.date_from)
        row_3.addWidget(self.date_to)

        row_4 = QHBoxLayout()
        row_4.addWidget(close_btn)
        row_4.addWidget(ok_btn)

        layout = QVBoxLayout()
        layout.addLayout(row_1)
        layout.addLayout(row_2)
        layout.addLayout(row_3)
        layout.addLayout(row_4)

        self.setLayout(layout)

    @QtCore.pyqtSlot(QtWidgets.QAction)
    def on_menu_triggered(self, action):
        self.menu_btn.setText(action.text())
        self.tile_option = action.text()
        if action.text() == 'Top':
            self.add_asset.setDisabled(True)
            self.date_from.setDisabled(True)
            self.date_to.setDisabled(True)

        if action.text() == 'Historical' or self.tile_type == utils.TileType.CURRENCIES:
            self.add_asset.setEnabled(True)

        if action.text() == 'Historical':
            self.date_from.setEnabled(True)
            self.date_to.setEnabled(True)


    def get_data(self):

        chosen_date = self.date_from.text().split('.')
        start_date = '' + chosen_date[1] + '/' + chosen_date[0] + '/' + chosen_date[2] + ''
        chosen_date = self.date_to.text().split('.')
        end_date = '' + chosen_date[1] + '/' + chosen_date[0] + '/' + chosen_date[2] + ''

        if self.tile_option == "":
            self.approved = False

        if self.tile_option == 'Historical' or self.tile_type == utils.TileType.CURRENCIES:
            return self.approved, self.tile_option, self.add_asset.text(), start_date, end_date
        else:
            return self.approved, self.tile_option, '', start_date, end_date