import sys
import mainmenu
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QStackedWidget

def main():
    application = QApplication(sys.argv)
    main = mainmenu.MainWindow()
    mainmenu.widget = QStackedWidget()
    mainmenu.widget.addWidget(main)
    mainmenu.widget.setFixedSize(800, 600)
    mainmenu.widget.show()
    try:
        sys.exit(application.exec_())
    except SystemExit:
        print("Exiting")

if __name__ == "__main__":
    main()



