from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QCheckBox, QComboBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIntValidator
import re
import common.consts as consts
from gui.execute_button import ExecuteButton
from common.enum import WhatsAppContext
from manager.manager_service import Options

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
        
        master_controls_layout = QHBoxLayout()
        master_controls_layout.setAlignment(Qt.AlignRight)
        master_controls_layout.setContentsMargins(0, 0, 80, 0)
        master_controls_layout.setSpacing(5)
        self._master_checkbox = QCheckBox()
        self._master_checkbox.stateChanged.connect(self._handle_master_checkbox)
        master_controls_layout.addWidget(self._master_checkbox)
        layout.addLayout(master_controls_layout)        
        
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
        
        self.script_contact_input = QLineEdit(self)
        self.script_contact_input.setPlaceholderText('Contact')
        self.script_contact_input.hide()
        layout.addWidget(self.script_contact_input)
        
        row_layout = QHBoxLayout()
        
        self.script_groups_input = QLineEdit(self)
        self.script_groups_input.setPlaceholderText('Groups')
        self.script_groups_input.setValidator(QIntValidator(1, 100))
        self.script_groups_input.hide()
        row_layout.addWidget(self.script_groups_input, 1)
        
        self.script_names_select = QComboBox(self)
        self.script_names_select.addItems([x.display for x in self.manager.names])
        self.script_names_select.hide()
        row_layout.addWidget(self.script_names_select, 1)
        layout.addLayout(row_layout)

        self.run_script_button = QPushButton('Run Script', self)
        self.run_script_button.clicked.connect(self.toggle_run_script)
        self.is_running_script = False
        layout.addWidget(self.run_script_button)
        
        self.cancel_run_script_button = QPushButton('Cancel', self)
        self.cancel_run_script_button.clicked.connect(self.toggle_run_script)
        self.cancel_run_script_button.hide()
        layout.addWidget(self.cancel_run_script_button)        
        
        self.create_button = QPushButton('Create Session', self)
        self.create_button.clicked.connect(self.toggle_create_session_view)
        layout.addWidget(self.create_button)

        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.clicked.connect(self.toggle_create_session_view)
        self.cancel_button.hide()
        layout.addWidget(self.cancel_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
    def start_polling(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_table)
        self.timer.start(consts.UI_REFRESH_RATE)
        
    def create_table(self):
        self.table.setRowCount(0)
        self.table.setRowCount(len(self.manager.sessions))
        self.table.setHorizontalHeaderLabels(['Session', 'Number', 'Running', 'Logged In', 'Context', None])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._buttons = []
        self._checkboxes = []
        for i, session in enumerate(self.manager.sessions):
            try:
                session.lock.acquire()
                name = session.name
                number = session.number
                running = session.running
                logged_in = session.logged_in
                context = session.context
                button = ExecuteButton(session)
            finally:
                session.lock.release()
                
            name_item = QTableWidgetItem(name) 
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)              
            self.table.setItem(i, 0, name_item)
            
            number_item = QTableWidgetItem(number)
            number_item.setTextAlignment(Qt.AlignCenter)
            number_item.setFlags(number_item.flags() & ~Qt.ItemIsEditable)   
            self.table.setItem(i, 1, number_item)
            self.table.setColumnWidth(1, 150)
            
            self._update_session_row(i, running, logged_in, context)            
            
            action_layout = QHBoxLayout()        
            checkbox = QCheckBox()
            action_layout.addWidget(checkbox)    
            action_layout.addWidget(button.btn)
            action_layout.setAlignment(Qt.AlignCenter)
            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            
            self.table.setCellWidget(i, 5, action_widget)
            self.table.setRowHeight(i, button.btn.sizeHint().height()*2)     
            
            self._buttons.append(button)
            self._checkboxes.append(checkbox)            
        
    def update_table(self):
        for i, session in enumerate(self.manager.sessions):
            try:
                session.lock.acquire()
                running = session.running
                logged_in = session.logged_in
                context = session.context
            finally:
                session.lock.release()
            
            self._update_session_row(i, running, logged_in, context)
            self._buttons[i].update_state(running)        
            
    def _update_session_row(self, i, running: bool, logged_in: bool, context: WhatsAppContext):
        running = "Yes" if running else "No"
        logged_in = "Yes" if logged_in else "No" if logged_in is not None else "Unknown"
        context = context.name
        
        running_item = QTableWidgetItem(running)
        running_item.setTextAlignment(Qt.AlignCenter)
        running_item.setFlags(running_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(i, 2, running_item)
        
        logged_in_item = QTableWidgetItem(logged_in)
        logged_in_item.setTextAlignment(Qt.AlignCenter)
        logged_in_item.setFlags(logged_in_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(i, 3, logged_in_item)

        context_item = QTableWidgetItem(context)
        context_item.setTextAlignment(Qt.AlignCenter)
        context_item.setFlags(context_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(i, 4, context_item)
        self.table.setColumnWidth(4, 200)
            
    def save_session(self):
        session_name = self.name_input.text()
        session_number = self.number_input.text()
        if session_name != '' and session_number != '' and all(session_name != s.name for s in self.manager.sessions) and re.match(r'^\w+$', session_name):
            self.manager.create_session(session_name, session_number)
            self.name_input.clear()
            self.number_input.clear()
            self.create_table()
            self.toggle_create_session_view()
        
    def toggle_create_session_view(self):
        if self.is_creating_session:
            self.name_input.hide()
            self.number_input.hide()
            self.cancel_button.hide()
            self.run_script_button.show()
            self.create_button.setText('Create Session')
            self.create_button.clicked.disconnect()
            self.create_button.clicked.connect(self.toggle_create_session_view)
        else:
            self.name_input.show()
            self.number_input.show()
            self.cancel_button.show()
            self.run_script_button.hide()
            self.create_button.setText('Save')
            self.create_button.clicked.disconnect()
            self.create_button.clicked.connect(self.save_session)
        self.is_creating_session = not self.is_creating_session
        
    def toggle_run_script(self):
        if self.is_running_script:
            self.script_contact_input.hide()
            self.script_groups_input.hide()
            self.script_names_select.hide()
            self.cancel_run_script_button.hide()
            self.create_button.show()
            self.run_script_button.setText('Run Script')
            self.run_script_button.clicked.disconnect()
            self.run_script_button.clicked.connect(self.toggle_run_script)
        else:
            self.script_contact_input.show()
            self.script_groups_input.show()
            self.script_names_select.show()
            self.cancel_run_script_button.show()
            self.create_button.hide()
            self.run_script_button.setText('Execute')
            self.run_script_button.clicked.disconnect()
            self.run_script_button.clicked.connect(self.run_script)
        self.is_running_script = not self.is_running_script

    def run_script(self):
        sessions = []
        for i, session in enumerate(self.manager.sessions):
            if self._checkboxes[i].isChecked():
                sessions.append(session)
        contact = self.script_contact_input.text()
        group_name = self.script_names_select.currentText()
        num_groups = int(self.script_groups_input.text())                
        options = Options(sessions, contact, group_name, num_groups)
        self.manager.run_script(options)
    
    def _handle_master_checkbox(self):
        new_state = self._master_checkbox.isChecked()
        for i, _ in enumerate(self.manager.sessions):
            self._checkboxes[i].setChecked(new_state)