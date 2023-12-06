from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer

from gui.execute_button import ExecuteButton

class Menu(QMainWindow):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.initUI()
        self.start_polling()

    def initUI(self):
        self.setWindowTitle('Session Manager')
        self.setGeometry(625, 325, 600, 400)
        self.resize(650, 400)
        
        layout = QVBoxLayout()
        self.table = QTableWidget(0, 5)
        self.create_table()
        layout.addWidget(self.table)
        
        self.nameInput = QLineEdit(self)        
        layout.addWidget(self.nameInput)

        createButton = QPushButton('Create Session', self)
        createButton.clicked.connect(self.createSession)
        layout.addWidget(createButton)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
    def start_polling(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_table)
        self.timer.start(100)
        
    def create_table(self):
        self.table.setRowCount(0)
        self.table.setRowCount(len(self.manager.sessions))
        self.table.setHorizontalHeaderLabels(['Session', 'Number', 'Running', 'Logged In', None])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i, session in enumerate(self.manager.sessions):            
            self.table.setItem(i, 0, QTableWidgetItem(session.name))
            
            number_item = QTableWidgetItem(session.number)
            number_item.setTextAlignment(Qt.AlignCenter)            
            self.table.setItem(i, 1, number_item)
            self.table.setColumnWidth(1, 150)
            
            running_item = QTableWidgetItem(str(session.running))
            running_item.setTextAlignment(Qt.AlignCenter)            
            self.table.setItem(i, 2, running_item)
            
            logged_in_item = QTableWidgetItem(str(session.logged_in))
            logged_in_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 3, logged_in_item)
            
            button = ExecuteButton(session)
            btn_layout = QHBoxLayout()            
            btn_layout.addWidget(button.btn)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            self.table.setCellWidget(i, 4, btn_widget)
            self.table.setRowHeight(i, button.btn.sizeHint().height()*2)            
        
    def update_table(self):
        for i, session in enumerate(self.manager.sessions):
            running_item = QTableWidgetItem(str(session.running))
            running_item.setTextAlignment(Qt.AlignCenter)            
            self.table.setItem(i, 2, running_item)
            
            logged_in_item = QTableWidgetItem(str(session.logged_in))
            logged_in_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 3, logged_in_item)     

    def createSession(self):
        session_name = self.nameInput.text()
        if session_name != '' and all(session_name != s.name for s in self.manager.sessions) and session_name.isalnum():
            self.manager.create_session(session_name, '00000000000')
        self.create_table()
        self.nameInput.clear()
