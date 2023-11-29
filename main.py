import sys
from PyQt5.QtWidgets import QApplication
from interface import StockAnalysisApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = StockAnalysisApp()
    main_window.show()
    sys.exit(app.exec_())
