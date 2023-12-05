import sys
from PyQt5.QtWidgets import QApplication
from gui.menu import Menu
from manager.manager_service import ManagerService

def main():
    app = QApplication(sys.argv)
    manager = ManagerService()
    window = Menu(manager)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
