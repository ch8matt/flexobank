from PyQt5.QtWidgets import (QApplication, QWidget, QCheckBox, QVBoxLayout, 
                             QPushButton, QScrollArea, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QDesktopWidget, 
                             QSizePolicy)
from PyQt5.QtCore import Qt
import sys

class TradeDecisionApp(QWidget):
    decisions_made = {}  # Class attribute to store decisions

    def __init__(self, potential_trades):
        super().__init__()
        self.potential_trades = potential_trades
        self.decisions = {f"{trade['ticker']}_{i}": False for i, trade in enumerate(potential_trades)}
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Trade Decisions')
        self.centerWindow()
        self.resize(650, 400)  # Set the window size to 800x600

        # Main layout
        mainLayout = QVBoxLayout(self)

        # Scroll Area
        scroll = QScrollArea(self)
        scrollWidget = QWidget()
        scroll.setWidget(scrollWidget)
        scroll.setWidgetResizable(True)

        layout = QVBoxLayout(scrollWidget)

        # Table for trades
        self.table = QTableWidget(len(self.potential_trades), 4, self)
        self.table.setHorizontalHeaderLabels(['Ticker', 'Close', 'Analyse', 'Confirm'])
        
        # Set the header section resize mode to ResizeToContents individually
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        for i, trade in enumerate(self.potential_trades):
            self.table.setItem(i, 0, QTableWidgetItem(trade['ticker']))
            self.table.setItem(i, 1, QTableWidgetItem(str(trade['close'])))
            self.table.setItem(i, 2, QTableWidgetItem(trade['action']))
            
            chkBox = QCheckBox(self)
            chkBox.stateChanged.connect(lambda state, x=f"{trade['ticker']}_{i}": self.setDecision(x, state))
            self.table.setCellWidget(i, 3, chkBox)

        layout.addWidget(self.table)

        # Submit button
        btnSubmit = QPushButton('Submit Decisions', self)
        btnSubmit.clicked.connect(self.onSubmit)
        layout.addWidget(btnSubmit)

        mainLayout.addWidget(scroll)

    def setDecision(self, key, state):
        self.decisions[key] = state == Qt.Checked

    def onSubmit(self):
        TradeDecisionApp.decisions_made = self.decisions  # Store decisions in class attribute
        self.close()

    def centerWindow(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

def ask_user_decisions(potential_trades):
    app = QApplication(sys.argv)
    ex = TradeDecisionApp(potential_trades)
    ex.show()
    app.exec_()  # Run the event loop
    return TradeDecisionApp.decisions_made
