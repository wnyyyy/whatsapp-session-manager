from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QTableWidget, QTableWidgetItem

class Menu(QMainWindow):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Session Manager')
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()

        self.table = QTableWidget(len(self.manager.sessions), 3)
        self.table.setHorizontalHeaderLabels(["Session", "Running", "Logged In"])
        for i, session in enumerate(self.manager.sessions):
            self.table.setItem(i, 0, QTableWidgetItem(session.name))
            self.table.setItem(i, 1, QTableWidgetItem(str(session.running)))
            self.table.setItem(i, 2, QTableWidgetItem(str(session.logged_in)))
        layout.addWidget(self.table)

        self.nameInput = QLineEdit(self)
        layout.addWidget(self.nameInput)

        createButton = QPushButton('Create Session', self)
        createButton.clicked.connect(self.createSession)
        layout.addWidget(createButton)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def createSession(self):
        session_name = self.nameInput.text()
        self.manager.create_session(session_name)
