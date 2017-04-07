# ------------------------------------------------------------------------------- Sys
import sys 
# ------------------------------------------------------------------------------- Matplotlib 
import matplotlib.pylab as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
e# ------------------------------------------------------------------------------- PyQt
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLineEdit, QFileDialog, QSlider, QWidget, QPushButton, QApplication
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
# ------------------------------------------------------------------------------- Pandas & Numpy
import numpy as np
import pandas as pd
# ------------------------------------------------------------------------------- testSeasonality
import testSeasonality # Executa in consola github/welch/seasonal si preia rezultatul prin RegEx

# ------------------------------------------------------------------------------- Statsmodels
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose


# ------------------------------------------------------------------------------- 
class trendSliderWindow(QWidget):
    '''
    Fereastra de tip QWidget, cu un slider.
    '''
    def __init__(self):
        super().__init__()
        
        self.trendSlider = QSlider(Qt.Horizontal, self)
        
        self.trendSlider.setFocus()
        
        self.trendSlider.setMinimum(3)
        self.trendSlider.setMaximum(6)
        
        self.trendSlider.setTickInterval(20)
        self.trendSlider.setSingleStep(20)
        
        self.trendSlider.setGeometry(50,20,200,10)
        self.setGeometry(200, 200, 300, 50)
        self.setWindowTitle('Precizie')
        self.setWindowIcon(QIcon('E:/Python_stuff/icon2.png'))
        
        self.move(860, 450)
        
        
class toolWindow(QWidget):
    '''
    Fereastra tip QWidget. Contine doua QLineEdit.
    Folosita pentru preluarea intervalului de predictie in cazul modelului ARMA
    '''
    def __init__(self):
        super().__init__()
        
        self.setGeometry(200, 200, 300, 50)
        self.setWindowTitle('ARMA')
        self.setWindowIcon(QIcon('E:/Python_stuff/icon2.png'))
        
        self.move(860, 450)
        grid = QVBoxLayout(self)
        
        text = QLabel('Predictie\nPerioada:')
        text.setAlignment(Qt.AlignCenter)
        
        self.edit1 = QLineEdit()
        self.edit1.setAlignment(Qt.AlignCenter)
        self.edit1.setMaxLength(4)
        
        self.edit2 = QLineEdit()
        self.edit2.setAlignment(Qt.AlignCenter)
        self.edit2.setMaxLength(4)
        
        grid.addWidget(text)
        grid.addWidget(self.edit1)
        grid.addWidget(self.edit2)
        
    def showt(self):
        '''
        Membra a clasei toolWindow - arata fereastra
        '''
        self.show()
        
        
class seasWindow(QWidget):
    '''
    Fereastra QWidget. Contine un singur Text Label.
    Displays information. Neinteractiva
    '''
    def __init__(self):
        super().__init__()
        
        self.setGeometry(200, 200, 300, 50)
        self.setWindowTitle('Periodicitate')
        self.setWindowIcon(QIcon('E:/Python_stuff/icon2.png'))
        
        self.move(860, 450)
        grid = QVBoxLayout(self)
        
        self.text = QLabel()
        self.text.setAlignment(Qt.AlignCenter)
        
        grid.addWidget(self.text)
        
    def showt(self):
        self.show()        
        
        

class Window(QMainWindow):
    '''
    Fereastra principala. Tip QMainWindow.
    '''
    def __init__(self):
        super().__init__()
        
        self.filename = None
        
        # ------------------------------------------------------------------------------- Menubar
        menubar = self.menuBar() #instantiere
        
        fileMenu = menubar.addMenu('&File') # Adauga optiunea File. Mai jos adauga la File Open,Save,Quit
        fileMenu.addAction('&Open', self.openFileBrowse, QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        fileMenu.addAction('&Save', self.saveFileBrowse, QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        fileMenu.addAction('&Quit', self.fileQuit,
                QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        
        helpMenu = menubar.addMenu('&Help') # Adauga optiunea Help. Mai jos Help -> About
        menubar.addSeparator()
        helpMenu.addAction('&About', self.about)
        
        self.initUI() # Functia principala a programului. Constructorul Window apeleaza functia pentru pornire
        
    def initUI(self):            
        '''
        Functia principala
        '''
        
        # ------------------------------------------------------------------------------- Datele
        if self.filename != None:
            
            if 'Air' not in self.filename: # Citeste datele din fisier
                dateparse = lambda dates: pd.datetime.strptime(dates, '%Y')
                self.data = pd.read_csv(self.filename, parse_dates = [0], index_col = 'Year', date_parser = dateparse)
             
                self.ts = self.data['Rate'] # Prelucreaza datele -> obiect tip time series
                self.mData = self.data.as_matrix(['Rate'])
                
                self.start = 1960 # Datele disponibile
                self.end = 2012
            else: # Pentru 'AirPassengers.csv' - are alt format
                dateparse = lambda dates: pd.datetime.strptime(dates, '%Y-%m')
                self.data = pd.read_csv(self.filename, parse_dates = [0], index_col = 'Month', date_parser = dateparse)
            
                self.ts = self.data['#Passengers']
                self.mData = self.data.as_matrix(['#Passengers'])
                
                self.start = 1950
                self.end = 1960
            
   
        # ------------------------------------------------------------------------------- Main Widget
        self.mainWidget = QWidget(self)
        
        self.figure = plt.figure(figsize = (15,5))
        self.canvas = FigureCanvas(self.figure) # Canvas pentru grafice
        
        grid = QVBoxLayout(self.mainWidget)
        
        
        grid.addWidget(self.canvas) # Adaugarea canvasului in fereastra principala
        # ------------------------------------------------------------------------------- Plot Button
        plotPB = QPushButton('Seria temporala initiala', self) # Instantiere
        
        plotPB.resize(plotPB.sizeHint()) # Marime
        plotPB.clicked.connect(self.plotTS) # Actiune
        
        grid.addWidget(plotPB) # Adaugare
        
        # ------------------------------------------------------------------------------- Trend Button
        trendPB = QPushButton('Vezi tendinta', self)
        
        trendPB.clicked.connect(self.Trend)
        trendPB.resize(trendPB.sizeHint())
        
        grid.addWidget(trendPB)
        
        # ------------------------------------------------------------------------------- MA Button
        maPB = QPushButton('Predictie - Model Moving Average', self)
        
        maPB.clicked.connect(self.MA)
        maPB.clicked.connect(self.sliderWindowClick)
        
        maPB.resize(maPB.sizeHint())
        
        # ------------------------------------------------------------------------------- Seas Numeric Button
        pPB = QPushButton('Vezi periodicitate - Numeric', self)
        
        pPB.clicked.connect(self.tsButton)
        pPB.resize(pPB.sizeHint())
        
        grid.addWidget(pPB)
        
        # ------------------------------------------------------------------------------- Seas Grafic Button
        seasPB = QPushButton('Vezi periodicitate - Grafic', self)
        
        seasPB.clicked.connect(self.plotSeasonality)
        seasPB.resize(seasPB.sizeHint())
        
        grid.addWidget(seasPB)
    
        # ------------------------------------------------------------------------------- ARMA Button
        predictPB = QPushButton('Predictie - Model ARMA', self)
        
        self.p = 1; self.i = 0; self.q = 1 # Parametrii pentru modelul ARMA. Daca i > 0 atunci e model ARIMA
                                         # Pentru simplitate ii vom lua predefiniti
                                             
        
        predictPB.clicked.connect(self.ARMA)
        predictPB.clicked.connect(self.toolWinAction)
        
        predictPB.resize(predictPB.sizeHint())
        
        grid.addWidget(maPB)
        grid.addWidget(predictPB)
        
        
        # --------------------------------------------------------------------- Alte variabile & Executia
        
        self.meanWindow = 3 # Precizia pentru MA 
        
        # ------------------------------------------------------------------------------- Instantiere obiect trendSliderWindow
        
        self.sWindow = trendSliderWindow()
        self.sWindow.trendSlider.valueChanged[int].connect(self.newRange) # Actiune
        
        # ------------------------------------------------------------------------------- Instantiere obiect toolWindow
        
        self.tWindow = toolWindow()
      
        self.tWindow.edit1.textChanged[str].connect(self.tchange) # Actiune
        self.tWindow.edit2.textChanged[str].connect(self.tchange) # Actiune
        
        # ------------------------------------------------------------------------------- Instantiere obiect seasWindow
        self.seas = seasWindow()
        
        # ------------------------------------------------------------------------------- Show - Fereastra Principala
        self.SHOW()

        
    def SHOW(self):
        '''
        Seteaza si afiseaza fereastra principala
        '''
        self.mainWidget.setFocus()
        self.setCentralWidget(self.mainWidget)
        
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Main')
        self.setWindowIcon(QIcon('E:/Python_stuff/icon3.png'))
        self.show()
        
        
    def toolWinAction(self):
        '''
        Deschide fereastra tool
        '''
        self.tWindow.showt()
        
        
    def tchange(self):
        '''
        Functia ce interactioneaza cu fereastra suplimentara a modelului ARMA
        Preia textul din cele doua QLineEdit-uri si seteaza ca interval de predictie
        '''
        self.start = int(self.tWindow.edit1.text())
        self.end = int(self.tWindow.edit2.text())
        self.ARMA()
        
    
    def openFileBrowse(self):
        '''
        File -> Open
        '''
        self.filename = str(QFileDialog.getOpenFileName(self)[0])
        
        self.initUI()
        
        
    def saveFileBrowse(self):
        '''
        File -> Save
        '''
        name = str(QFileDialog.getSaveFileName(self, 'Save File')[0])
        self.rezultatePredictie.to_csv(name, header = ['Rate'], index_label = 'Year')
        
        
    def ARMA (self):
        '''
        Functia de predictie 
        '''
        if 'swe' in self.filename:
            self.p = 4; self.q = 2;
        self.tsLog = np.log(self.ts) # Logaritmare - Penalizeaza valorile mari
        model = ARIMA(self.ts, order = (self.p, self.i, self.q)) # Apelarea modelului
        resultsARMA = model.fit(disp=-1) # Rezultate
        start = str(self.start) + '-01-01' 
        end = str(self.end) + '-01-01'
        
        x = resultsARMA.predict(start,end) # Predictia datelor de la 'start' la 'end'
#        x = np.exp(x) # Readucere la scala
        
        # -------------------------------------------------------------------------- Graficul
        plt.cla()
        plt.plot(self.ts, label = 'Seria originala', linestyle = '-', c = '0.6')
        plt.plot(x, color='r', label = 'Predictie', linewidth = 1.3)
        RSS = sum((np.log(resultsARMA.fittedvalues)-self.tsLog)**2)
        plt.legend(loc = 'best')
        plt.grid()
        
        plt.title(self.getTitle() + '\nRSS: ' + str(round(RSS, 4)))
        # --------------------------------------------------------------------------
        
        self.rezultatePredictie = x.to_frame() # Salvarea rezultatelor
            
        
        self.canvas.draw() # Afisare pe canvas
        
        
    def newRange(self):
        '''
        Modifica precizia MA in functie de valoarea sliderului
        '''
        self.meanWindow = int(self.sWindow.trendSlider.value())
        self.MA()
        
        
    def sliderWindowClick(self):
        '''
        Deschide fereastra cu slider
        '''
        self.sWindow.show()
        
    def plotSeasonality(self):
        '''
        Graficul periodicitatii
        '''
        if 'Air' not in self.filename:
            fq = 1
        else:
            fq = 12  
        
        plt.cla()
        decomp = seasonal_decompose(self.ts, freq = fq)
        plt.plot(decomp.seasonal, c='0.6')
        plt.title('Periodicitate')
        plt.grid()
        
        self.canvas.draw()
        
        
    def tsButton(self):
        '''
        Periodicitate numeric
        '''
        f = open(self.filename, 'r+')
        x = testSeasonality.testSeasonality(f)
        x = x.getResult()
        f.close()
        
        self.seas.text.setText('Dataset-ul are perioada: \n\n' + str(x))
        self.seas.showt()
        
       
    def plotTS(self):
        '''
        Graficul seriei temporale
        '''
        plt.cla()
        plt.plot(self.ts, c = '0.6')
        plt.grid()
        
        plt.title(self.getTitle())
                
        self.canvas.draw()
        
        
    def Trend(self):
        '''
        Graficul tendintei
        '''
        if 'Air' not in self.filename:
        
            z = np.polyfit(range(len(self.ts)), self.mData.flatten(), 1 )
            p = np.poly1d(z)
            
            plt.cla()
            plt.plot(self.ts, label = 'Seria Originala', c = '0.6')
            plt.plot(self.data.index, p(self.mData), 'red', label = 'Tendinta')
            plt.legend(loc = 'best')
            plt.grid()
            
            plt.title(self.getTitle())
        else:
            
            decomp = seasonal_decompose(self.ts)
            trend = decomp.trend
            
            plt.cla()
            plt.plot(self.ts, label = 'Seria Originala', c = '0.6')
            plt.plot(trend, 'red', label = 'Tendinta')
            plt.legend(loc = 'best')
            plt.grid()
        
        self.canvas.draw()
            
        
    def MA(self):
        '''
        Functia de predictie cu MA
        '''
        trend = self.ts.rolling(window = self.meanWindow).mean()
        
        plt.cla()
        plt.plot(self.ts, label = 'Seria originala', c = '0.6')
        plt.plot(trend, color = 'red', label = 'Predictie')
        plt.legend(loc = 'best')
        plt.grid()
        plt.title(self.getTitle())
            
        self.canvas.draw()
        
    def getTitle(self):          
        if 'spa' in self.filename:
            t = 'Rata sinuciderii in Spania (Date disponibile: 1988 - 2012)'
        elif 'fra' in self.filename:
            t = 'Rata sinuciderii in Franta (Date disponibile: 1960 - 2012)'
        elif 'ola' in self.filename:
            t = 'Rata sinuciderii in Olanda (Date disponibile: 1960 - 2012)'
        elif 'swe' in self.filename:
            t = 'Rata sinuciderii in Suedia (Date disponibile: 1960 - 2012)'
            
        return t
    
    def fileQuit(self):
        '''
        Inchidere fereastra
        '''
        self.close()
        
    def about(self):
        '''
        Help -> About
        '''
        self.seas.text.setText(""" Aplicatie pentru o analiza simpla a seriilor temporale.

Folosite:
Python:
- Framework - PyQt
- Librarii - Matplotlib, Statsmodels, Pandas, Numpy
Open-Source:
- Seasonal - (https://github.com/welch/seasonal)
""")
        self.seas.setWindowTitle('About')
        self.seas.showt()

                          
# ------------------------------------------------------------------- Executia
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())
