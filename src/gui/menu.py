from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
import re
from gui.execute_button import ExecuteButton

class Menu(QMainWindow):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.is_creating_session = False
        self.initUI()
        self.start_polling()

    def initUI(self):
        self.setWindowTitle('Session Manager')
        self.setGeometry(625, 325, 600, 400)
        self.resize(850, 400)
        
        layout = QVBoxLayout()
        self.table = QTableWidget(0, 6)
        self.create_table()
        layout.addWidget(self.table)
        
        self.name_input = QLineEdit(self)     
        self.name_input.setPlaceholderText('Name')
        self.name_input.hide()   
        layout.addWidget(self.name_input)
        
        self.number_input = QLineEdit(self)     
        self.number_input.setPlaceholderText('Number')
        self.number_input.hide()   
        layout.addWidget(self.number_input)

        self.create_button = QPushButton('Create Session', self)
        self.create_button.clicked.connect(self.create_session)
        layout.addWidget(self.create_button)
        
        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.clicked.connect(self.cancel_create_session)
        self.cancel_button.hide()
        layout.addWidget(self.cancel_button)

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
        self.table.setHorizontalHeaderLabels(['Session', 'Number', 'Running', 'Logged In', 'Context', None])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i, session in enumerate(self.manager.sessions):
            name_item = QTableWidgetItem(session.name) 
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)              
            self.table.setItem(i, 0, name_item)
            
            number_item = QTableWidgetItem(session.number)
            number_item.setTextAlignment(Qt.AlignCenter)         
            number_item.setFlags(number_item.flags() & ~Qt.ItemIsEditable)   
            self.table.setItem(i, 1, number_item)
            self.table.setColumnWidth(1, 150)
            
            running = "Yes" if session.running else "No"
            running_item = QTableWidgetItem(running)
            running_item.setTextAlignment(Qt.AlignCenter)
            running_item.setFlags(running_item.flags() & ~Qt.ItemIsEditable)   
            self.table.setItem(i, 2, running_item)
            
            logged_in = "Yes" if session.logged_in else "No" if session.logged_in is not None else "Unknown"
            logged_in_item = QTableWidgetItem(logged_in)
            logged_in_item.setTextAlignment(Qt.AlignCenter)
            logged_in_item.setFlags(logged_in_item.flags() & ~Qt.ItemIsEditable)   
            self.table.setItem(i, 3, logged_in_item)
            
            context_item = QTableWidgetItem(str(session.context.name))
            context_item.setTextAlignment(Qt.AlignCenter)
            context_item.setFlags(context_item.flags() & ~Qt.ItemIsEditable)   
            self.table.setItem(i, 4, context_item)
            self.table.setColumnWidth(4, 200)
            
            button = ExecuteButton(session)
            btn_layout = QHBoxLayout()            
            btn_layout.addWidget(button.btn)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            self.table.setCellWidget(i, 5, btn_widget)
            self.table.setRowHeight(i, button.btn.sizeHint().height()*2)            
        
    def update_table(self):
        for i, session in enumerate(self.manager.sessions):
            running = "Yes" if session.running else "No"
            running_item = QTableWidgetItem(running)
            running_item.setTextAlignment(Qt.AlignCenter)      
            running_item.setFlags(running_item.flags() & ~Qt.ItemIsEditable)      
            self.table.setItem(i, 2, running_item)
            
            logged_in = "Yes" if session.logged_in else "No" if session.logged_in is not None else "Unknown"
            logged_in_item = QTableWidgetItem(logged_in)
            logged_in_item.setTextAlignment(Qt.AlignCenter)
            logged_in_item.setFlags(logged_in_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 3, logged_in_item)
            
    def save_session(self):
        session_name = self.name_input.text()
        session_number = self.number_input.text()
        if session_name != '' and session_number != '' and all(session_name != s.name for s in self.manager.sessions) and re.match(r'^\w+$', session_name):
            self.manager.create_session(session_name, session_number)
            self.name_input.clear()
            self.number_input.clear()
            self.create_table()
            self.toggle_create_session_view()

    def create_session(self):
        self.toggle_create_session_view()
        
    def cancel_create_session(self):
        self.toggle_create_session_view()
        
    def toggle_create_session_view(self):
        if self.is_creating_session:
            self.name_input.hide()
            self.number_input.hide()
            self.cancel_button.hide()
            self.create_button.setText('Create Session')
            self.create_button.clicked.disconnect()
            self.create_button.clicked.connect(self.create_session)
        else:
            self.name_input.show()
            self.number_input.show()
            self.cancel_button.show()
            self.create_button.setText('Save')
            self.create_button.clicked.disconnect()
            self.create_button.clicked.connect(self.save_session)
        self.is_creating_session = not self.is_creating_session
