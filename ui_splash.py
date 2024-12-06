# ui_splash.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt

class Ui_SplashScreen(QWidget):
    def setup_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(600, 400)
        self.setWindowTitle("Yükleniyor...")
        self.setWindowIcon(QIcon('resources/icons/splash_icon.png'))
    
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
    
        # Logo
        self.logo = QLabel(self)
        pixmap = QPixmap('resources/icons/splash_icon.png')
        self.logo.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(self.logo)
    
        # Application Name
        self.app_name = QLabel("Yoklama Sistemi", self)
        self.app_name.setAlignment(Qt.AlignCenter)
        self.app_name.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.app_name)
    
        # Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFixedWidth(300)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
    
        self.setLayout(layout)
    
    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)
