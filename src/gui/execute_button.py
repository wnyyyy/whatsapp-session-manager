from PyQt5.QtWidgets import QPushButton, QStyle


class ExecuteButton:
    def __init__(self, session):
        self.btn = QPushButton()
        icon = self.btn.style().standardIcon(getattr(QStyle, 'SP_MediaPlay'))
        self.btn.setIcon(icon)
        self.btn.setMinimumSize(30, 30)
        self.btn.clicked.connect(lambda: self._handleExecute(session))    
        self.playing = False                
        
    def swap_state(self, playing):
        if playing:
            self.playing = True
            icon = self.btn.style().standardIcon(getattr(QStyle, 'SP_MediaStop'))
            self.btn.setIcon(icon)
        else:
            self.playing = False
            icon = self.btn.style().standardIcon(getattr(QStyle, 'SP_MediaPlay'))
            self.btn.setIcon(icon)            
        
    def _handleExecute(self, session):
        if self.playing:
            if session.running:
                session.quit()
        else:
            if not session.running:
                session.run()            
        self.swap_state(self.playing)
