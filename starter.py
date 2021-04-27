from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QToolBar, QAction, QVBoxLayout, QHBoxLayout, QFrame, QWidget
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

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.setWindowTitle("MyAssets")

        vbox = QVBoxLayout()
        container_wid = QWidget()
        self.setCentralWidget(container_wid)
        container_wid.setLayout(vbox)
        header = Header()
        upper_frame = QFrame(self)
        upper_frame.setFrameShape(QFrame.Panel | QFrame.Sunken)
        
        bottom_frame = QFrame(self)
        bottom_frame.setFrameShape(QFrame.Panel | QFrame.Sunken)
        vbox.addWidget(header)

        vbox.addWidget(upper_frame)
        vbox.addWidget(bottom_frame)
    ''' 
        self.setWindowTitle("Start")

        label = QLabel("Label")
        label.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(label)

        toolbar = QToolBar("My Toolbar")
        self.addToolBar(toolbar)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)

        button_action = QAction(QIcon("plus-icon.png"), "Button", self)
        button_action.setIcon(QIcon("plus-icon.png"))
        button_action.setStatusTip("This is my button")
        button_action.triggered.connect(self.onMyToolBarButtonClick)
        button_action.setCheckable(True)
        toolbar.addAction(button_action)

        self.setStatusBar(QStatusBar(self))
    '''



    def onMyToolBarButtonClick(self, s):
        print("click", s)

app = QApplication([])
window = MainWindow()
window.show()

app.exec_()
