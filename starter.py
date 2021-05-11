from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QAction, QVBoxLayout, QHBoxLayout, QFrame, QWidget, QPushButton, QMenu
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

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

class MainSubFrame(QFrame):
    def __init__(self, *args, **kwargs):
        super(MainSubFrame, self).__init__(*args, **kwargs)

        self.setFrameShape(QFrame.Panel | QFrame.Sunken)

        self.adding_button = QtWidgets.QPushButton('Add')
        menu = QtWidgets.QMenu(
            self.adding_button, 
            triggered=self.on_menu_triggered
        )
        for text in ("", "Favourites", "Currencies", "Stocks"):
            menu.addAction(text)
        self.adding_button.setMenu(menu)
        self.adding_button.setIcon(QIcon('add_icon.png')) #DOESNT WORK :(
        
        self.vertical_layout = QVBoxLayout(self)
        self.vertical_layout.addWidget(self.adding_button, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        
    #TODO: add adding of tiles
    @QtCore.pyqtSlot(QtWidgets.QAction)
    def on_menu_triggered(self, action):
        print(action.text)

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.setWindowTitle("MyAssets")

        vbox = QVBoxLayout()
        container_wid = QWidget()
        self.setCentralWidget(container_wid)
        container_wid.setLayout(vbox)

        header = Header()
        upper_frame = MainSubFrame(self)
        bottom_frame = MainSubFrame(self)

        vbox.addWidget(header)
        vbox.addWidget(upper_frame)
        vbox.addWidget(bottom_frame)

app = QApplication([])
window = MainWindow()
window.show()

app.exec_()
