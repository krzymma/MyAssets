from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from load import load_historical_assets
from PyQt5.QtGui import QFont
from utils import TileType
import datetime as dt
import matplotlib
from numpy import around
import pandas as pd
from utils import Interval
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class MplCanvas(FigureCanvasQTAgg):
    #Matplotlib wrapper for Qt
    def __init__(self, parent=None, width=4, height=6, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        fig.subplots_adjust(bottom=0.3)
        super(MplCanvas, self).__init__(fig)

class StatsLabel(QWidget):
    #Label showing name and value of statistic
    def __init__(self, parent, title, value1, value2=None):
        super(StatsLabel, self).__init__(parent)
        self.layout = QVBoxLayout()

        self.init_ui(title, value1, value2)

    def init_ui(self, title, value1, value2):
        labels_layout = QHBoxLayout()

        title_lab = QLabel(title)
        title_lab.setFont(QFont('Times', 12))
        value_lab = QLabel(str(value1))
        if value2 != None:
            value_lab.setText(str(value1) + ' - ' + str(value2))
        value_lab.setFont(QFont('Times', 12, weight=QFont.Bold))
        
        labels_layout.addWidget(title_lab)
        labels_layout.addStretch(1)
        labels_layout.addWidget(value_lab)
        
        sep_line = QFrame()
        sep_line.setFrameShape(QFrame.HLine)
        
        self.layout.addLayout(labels_layout)
        self.layout.addWidget(sep_line)
        self.setLayout(self.layout) 


class SpecWindow(QWidget):
    def __init__(self, tile_type, asset_code, name):
        super().__init__()
        self.setFixedSize(QSize(600, 500))
        self.setWindowTitle(asset_code)

        self.tile_type = tile_type
        self.code = asset_code
        self.name = name
        self.data = None #last year by days
        self.add_data = pd.DataFrame() #last 5 years by months

        self.yesterday = dt.date.today() - dt.timedelta(days=1)
        self.year_ago = self.yesterday - dt.timedelta(weeks=52)
        self.yesterday = self.yesterday.strftime('%m/%d/%y')
        self.year_ago = self.year_ago.strftime('%m/%d/%y')

        self.data = load_historical_assets(tile_type, asset_code, self.year_ago, self.yesterday)
        self.last_close = None
        self.fst_close = None
        self.day_range = None 
        self.year_range = None
        self.calc_stats()

        self.plot = MplCanvas(self)
        self.buttons = None

        self.layout = QVBoxLayout()
        self.init_ui()


    def calc_stats(self):
        self.last_close = self.data.iat[0, 4]
        self.fst_close = self.data.iat[-1, 4]

        #last day interval
        last_high = self.data.iat[0, 2]
        last_low = self.data.iat[0, 3]
        self.day_range = (last_low, last_high)

        #last year interval
        year_high = self.data['HIGH'].max()
        year_low = self.data['LOW'].min()
        self.year_range = (year_low, year_high)


    def update_plot(self):
        self.buttons[self.plot_state].toggle()
        self.plot_state = self.sender().text()   
        state = self.plot_state
        data = self.data[['DATE', 'CLOSE']]
        fmt = matplotlib.dates.DateFormatter('%d/%m')

        if state == '1 Week':
            data = data.head(7)
        elif state == '1 Month':
            data = data.head(30)
        elif state == '3 Months':
            data = data.head(90)
        elif state == '6 Months':
            data = data.head(180)
            fmt = None
        elif state == '1 Year':
            fmt = None
        else:
            fmt = None
            '''
            Clicking '5 Years' requires downloading more data
            Since our API allows us to download data that differ at most by year, 
            we have to repeat it 5 times
            '''
            if self.add_data.empty:
                start = dt.date.today() - dt.timedelta(days=1)
                end = start - dt.timedelta(weeks=52)
                for i in range(5):
                    yearly_data = load_historical_assets(
                                                        self.tile_type, 
                                                        self.code,
                                                        end.strftime('%m/%d/%y'),
                                                        start.strftime('%m/%d/%y'),
                                                        interval=Interval.WEEK )
                    self.add_data = self.add_data.append(yearly_data)
                    start = end
                    end = end - dt.timedelta(weeks=52)
                self.add_data = self.add_data[['DATE', 'CLOSE']]

            data = self.add_data

        self.plot.axes.cla()
        if data.iat[-1, 1] > data.iat[0, 1]:
            self.plot.axes.plot(data['DATE'], data['CLOSE'], 'r') #decline
        elif data.iat[-1, 1] <= data.iat[0, 1]:
            self.plot.axes.plot(data['DATE'], data['CLOSE'], 'g') #stonks
        self.plot.axes.tick_params('x', rotation=45)
        if fmt != None:
            self.plot.axes.xaxis.set_major_formatter(fmt)
        self.plot.draw()


    def init_ui(self):
        name_label = QLabel(self.name)
        name_label.setFont(QFont('Helvetica', 20))

        sep_line = QFrame()
        sep_line.setFrameShape(QFrame.HLine)
        sep_line.setLineWidth(1)

        hbox_buttons = QHBoxLayout()
        button_labs = ['1 Week', '1 Month', '3 Months',
                       '6 Months', '1 Year', '5 Years']
        self.buttons = {label:QPushButton(label) for label in button_labs}
        for button in self.buttons.values():
            hbox_buttons.addWidget(button)
            button.clicked.connect(self.update_plot)
            button.setCheckable(True)

        self.plot_state = '1 Week' 
        self.buttons['1 Week'].click()
        self.buttons['1 Week'].toggle()

        grid_labels = QGridLayout()
        year_delta = around(100*(self.last_close - self.fst_close)/self.fst_close, 2)
        grid_labels.addWidget(StatsLabel(self, 'Prev. Close:', self.last_close), 0, 0)
        grid_labels.addWidget(StatsLabel(self, 'Day Range:', self.day_range[0], self.day_range[1]), 0, 1)
        grid_labels.addWidget(StatsLabel(self, '1-Year Change:', str(year_delta)+' %'), 1, 0)
        grid_labels.addWidget(StatsLabel(self, '52-Week Range:', self.year_range[0], self.year_range[1]), 1, 1)

        self.layout.addWidget(name_label)
        self.layout.addWidget(sep_line)
        self.layout.addWidget(self.plot)
        self.layout.addLayout(hbox_buttons)
        self.layout.addLayout(grid_labels)
        self.layout.addStretch(1)
        self.setLayout(self.layout)