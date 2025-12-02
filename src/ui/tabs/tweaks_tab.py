import json
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QPushButton, 
                             QHBoxLayout, QMessageBox, QLabel, QListWidgetItem)
from src.core.tweaker import Tweaker

class TweaksTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.tweaker = Tweaker()
        self.tweaks_data = []
        
        self.load_data()
        self.init_ui()
        self.setLayout(self.layout)

    def load_data(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        json_path = os.path.join(base_dir, 'data', 'tweaks.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.tweaks_data = json.load(f)
        except:
            self.tweaks_data = []

    def init_ui(self):
        title = QLabel("Sistem İnce Ayarları ve Araçlar")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(title)

        # Liste
        self.list_widget = QListWidget()
        for tweak in self.tweaks_data:
            item = QListWidgetItem(tweak.get("name"))
            item.setToolTip(tweak.get("description"))
            # Tweak verisini item'ın içine gömüyoruz
            item.setData(32, tweak) # 32 = Qt.UserRole
            self.list_widget.addItem(item)
            
        self.layout.addWidget(self.list_widget)

        # Butonlar
        btn_layout = QHBoxLayout()
        self.btn_apply = QPushButton("Seçileni Uygula / Çalıştır")
        self.btn_apply.clicked.connect(self.run_selected_tweak)
        
        btn_layout.addWidget(self.btn_apply)
        self.layout.addLayout(btn_layout)

    def run_selected_tweak(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Uyarı", "Lütfen listeden bir işlem seçin.")
            return

        tweak_data = current_item.data(32)
        
        # Onay İste
        reply = QMessageBox.question(self, "Onay", f"'{tweak_data.get('name')}' çalıştırılacak. Devam edilsin mi?", 
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.tweaker.apply_tweak(tweak_data)
            QMessageBox.information(self, "Bilgi", "İşlem başlatıldı.")