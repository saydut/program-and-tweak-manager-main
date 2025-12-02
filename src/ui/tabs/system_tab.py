from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
from PyQt5.QtGui import QFont
from src.core.sys_info import SystemInfo

class SystemTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.sys_info = SystemInfo()
        
        self.init_ui()
        self.setLayout(self.layout)
        
        # Sekme açıldığında otomatik yükle
        self.refresh_info()

    def init_ui(self):
        title = QLabel("Donanım ve Sistem Raporu")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(title)

        # Rapor Alanı
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        # Kod fontu gibi görünmesi için Consolas
        self.text_area.setFont(QFont("Consolas", 10))
        self.layout.addWidget(self.text_area)

        # Yenile Butonu
        self.btn_refresh = QPushButton("Bilgileri Yenile")
        self.btn_refresh.clicked.connect(self.refresh_info)
        self.layout.addWidget(self.btn_refresh)

    def refresh_info(self):
        self.text_area.setText("Sistem taranıyor, lütfen bekleyin...")
        # İşlemi gerçekleştirelim
        # Not: Eğer GPU sorgusu çok uzun sürerse burası Thread içine alınabilir.
        # Şimdilik basit tutuyoruz.
        try:
            report = self.sys_info.get_full_report()
            self.text_area.setText(report)
        except Exception as e:
            self.text_area.setText(f"Bir hata oluştu: {str(e)}")