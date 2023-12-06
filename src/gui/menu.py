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
        self.resize(600, 400)
        
        layout = QVBoxLayout()
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
        self.table = QTableWidget(len(self.manager.sessions), 4)
        self.table.setHorizontalHeaderLabels(['Session', 'Running', 'Logged In', None])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i, session in enumerate(self.manager.sessions):
            self.table.setItem(i, 0, QTableWidgetItem(session.name))
            self.table.setItem(i, 1, QTableWidgetItem(str(session.running)))
            self.table.setItem(i, 2, QTableWidgetItem(str(session.logged_in)))
            button = ExecuteButton(session)
            btn_layout = QHBoxLayout()            
            btn_layout.addWidget(button.btn)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            self.table.setCellWidget(i, 3, btn_widget)
        
    def update_table(self):
        for i, session in enumerate(self.manager.sessions):
            self.table.setItem(i, 1, QTableWidgetItem(str(session.running)))
            self.table.setItem(i, 2, QTableWidgetItem(str(session.logged_in)))        

    def createSession(self):
        session_name = self.nameInput.text()
        self.manager.create_session(session_name)
