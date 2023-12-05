import sys
from PyQt5.QtWidgets import QApplication
from gui import Gui
from manager_service import ManagerService

def main():
    app = QApplication(sys.argv)
    manager = ManagerService()
    window = Gui(manager)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
