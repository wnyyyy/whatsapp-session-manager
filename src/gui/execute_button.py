from PyQt5.QtWidgets import QPushButton, QStyle


class ExecuteButton:
    def __init__(self, session):
        self.btn = QPushButton()
        icon = self.btn.style().standardIcon(getattr(QStyle, 'SP_MediaPlay'))
        self.btn.setIcon(icon)
        self.btn.setMinimumSize(30, 30)
        self.btn.clicked.connect(lambda: self.handleExecute(session))    
        self.playing = False                
        
    def update_state(self, playing):
        if playing:
            self.playing = True
            icon = self.btn.style().standardIcon(getattr(QStyle, 'SP_MediaStop'))
            self.btn.setIcon(icon)
        else:
            self.playing = False
            icon = self.btn.style().standardIcon(getattr(QStyle, 'SP_MediaPlay'))
            self.btn.setIcon(icon)            
        
    def handleExecute(self, session):
        if session is not None:
            if self.playing:
                if session.running:
                    session.quit()
            else:
                if not session.running:
                    session.run()
        self.update_state(self.playing)
