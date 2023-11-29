from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QDesktopWidget, QDialog,
                             QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea, QCheckBox)
from PyQt5.QtCore import QThread
from retrieve import continuous_analysis, clear_database, create_tables
from analysis import calculate_technical_indicators
from datetime import datetime
import csv

class AnalysisThread(QThread):
    def run(self):
        continuous_analysis()  # Your long-running task

class StockAnalysisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        # Analysis Button
        self.analysis_button = QPushButton('Start Analysis', self)
        self.analysis_button.clicked.connect(self.start_analysis)
        self.layout.addWidget(self.analysis_button)

        # Button to open TradeDecisionApp
        self.trade_decision_button = QPushButton('Open Trade Decisions', self)
        self.trade_decision_button.clicked.connect(self.open_trade_decision)
        self.layout.addWidget(self.trade_decision_button)

        self.setWindowTitle('Stock Analysis App')
        self.resize(100, 100)
        self.centerWindow()

    def start_analysis(self):
        clear_database()  # Clear the database
        create_tables()   # Create necessary tables
        self.analysis_thread = AnalysisThread()
        self.analysis_thread.start()

    def open_trade_decision(self):
        # Open TradeDecisionApp in a new window
        self.trade_decision_window = TradeDecisionApp([])
        self.trade_decision_window.show()

    def centerWindow(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class TradeDecisionApp(QDialog):
    def __init__(self, potential_trades):
        super().__init__()
        self.potential_trades = potential_trades if potential_trades else self.get_potential_trades()
        self.initUI()
        self.setModal(True)

    def get_potential_trades(self):
        # Get potential trades from calculate_technical_indicators
        return calculate_technical_indicators()

    def initUI(self):
        self.setWindowTitle('Trade Decisions')
        self.resize(650, 400)
        layout = QVBoxLayout(self)

        # Table for trades
        self.table = QTableWidget(len(self.potential_trades), 4, self)
        self.table.setHorizontalHeaderLabels(['Ticker', 'Close', 'Analyse', 'Confirm'])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        for i, trade in enumerate(self.potential_trades):
            self.table.setItem(i, 0, QTableWidgetItem(trade['ticker']))
            self.table.setItem(i, 1, QTableWidgetItem(str(trade['Close'])))
            self.table.setItem(i, 2, QTableWidgetItem(trade['action']))
            chkBox = QCheckBox(self)
            self.table.setCellWidget(i, 3, chkBox)

        layout.addWidget(self.table)

        # Submit button
        btnSubmit = QPushButton('Submit Decisions', self)
        btnSubmit.clicked.connect(self.onSubmit)
        layout.addWidget(btnSubmit)

class TradeDecisionApp(QDialog):
    def __init__(self, potential_trades):
        super().__init__()
        self.potential_trades = potential_trades if potential_trades else self.get_potential_trades()
        self.initUI()
        self.setModal(True)

    def get_potential_trades(self):
        # Get potential trades from calculate_technical_indicators
        return calculate_technical_indicators()

    def initUI(self):
        self.setWindowTitle('Trade Decisions')
        self.resize(650, 400)
        layout = QVBoxLayout(self)

        # Table for trades
        self.table = QTableWidget(len(self.potential_trades), 5, self)  # Added one more column for the "Processed" status
        self.table.setHorizontalHeaderLabels(['Ticker', 'Close', 'Analyse', 'Confirm', 'Processed'])  # Added "Processed" column
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        for i, trade in enumerate(self.potential_trades):
            self.table.setItem(i, 0, QTableWidgetItem(trade['ticker']))
            self.table.setItem(i, 1, QTableWidgetItem(str(trade['Close'])))
            self.table.setItem(i, 2, QTableWidgetItem(trade['action']))
            chkBox = QCheckBox(self)
            self.table.setCellWidget(i, 3, chkBox)
            self.table.setItem(i, 4, QTableWidgetItem("Not Processed"))  # Initial value for "Processed" column

        layout.addWidget(self.table)

        # Submit button
        btnSubmit = QPushButton('Submit Decisions', self)
        btnSubmit.clicked.connect(self.onSubmit)
        layout.addWidget(btnSubmit)

    def onSubmit(self):
        # Extract data from the table and save it to the CSV file
        data_to_save = []

        for row in range(self.table.rowCount()):
            ticker = self.table.item(row, 0).text()
            close = self.table.item(row, 1).text()
            action = self.table.item(row, 2).text()
            chkBox = self.table.cellWidget(row, 3)  # Get the checkbox widget

            # Determine the "Processed" status based on checkbox state
            processed = "Processed" if chkBox.isChecked() else "Not Processed"

            # Create a dictionary with the data, including the "Processed" status and add a timestamp
            data_entry = {
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Ticker': ticker,
                'Close': close,
                'Analyse': action,
                'Processed': processed,
            }

            data_to_save.append(data_entry)

        # Save the data to the CSV file
        with open('shared_data.csv', 'a', newline='') as csvfile:
            fieldnames = ['Timestamp', 'Ticker', 'Close', 'Analyse', 'Processed']  # Adjust these column names accordingly
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Add a header row if the file is empty
            if csvfile.tell() == 0:
                writer.writeheader()

            # Write the data to the CSV file
            for data_entry in data_to_save:
                writer.writerow(data_entry)

        # Close the dialog
        self.close()

    def centerWindow(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
