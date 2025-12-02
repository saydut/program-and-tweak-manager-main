import json
import os
import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QScrollArea, 
                             QPushButton, QHBoxLayout, QMessageBox, QLabel)
from PyQt5.QtCore import Qt

class ProgramsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.checkboxes = []
        self.programs_data = []
        
        # JSON verisini yükle
        self.load_data()
        
        # Arayüzü oluştur
        self.init_ui()
        self.setLayout(self.layout)

    def load_data(self):
        """data/programs.json dosyasını okur."""
        # Dosya yolunu bul (main.py'ın olduğu yere göre data/programs.json)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        json_path = os.path.join(base_dir, 'data', 'programs.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.programs_data = json.load(f)
        except FileNotFoundError:
            self.programs_data = []
            print(f"HATA: {json_path} bulunamadı!")

    def init_ui(self):
        # Başlık
        title = QLabel("Kurulacak Programları Seçin (Winget)")
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        self.layout.addWidget(title)

        # Kaydırma Alanı (Scroll Area)
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # JSON'dan gelen her program için bir CheckBox oluştur
        if not self.programs_data:
            scroll_layout.addWidget(QLabel("Program listesi yüklenemedi! data/programs.json dosyasını kontrol edin."))
        else:
            for prog in self.programs_data:
                # Görünen isim (name) ve arka plandaki ID (id)
                cb = QCheckBox(prog.get("name", "Bilinmeyen Program"))
                cb.setToolTip(prog.get("description", "")) # Fareyle üzerine gelince açıklama çıkar
                # ID bilgisini checkbox nesnesine saklayalım
                cb.setProperty("winget_id", prog.get("id"))
                self.checkboxes.append(cb)
                scroll_layout.addWidget(cb)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)
        self.layout.addWidget(scroll_area)

        # Butonlar
        btn_layout = QHBoxLayout()
        
        self.btn_install = QPushButton("Seçilenleri Kur")
        self.btn_install.setMinimumHeight(40)
        self.btn_install.clicked.connect(self.install_selected)
        
        btn_layout.addWidget(self.btn_install)
        self.layout.addLayout(btn_layout)

    def install_selected(self):
        to_install = []
        for cb in self.checkboxes:
            if cb.isChecked():
                to_install.append(cb.property("winget_id"))
        
        if not to_install:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir program seçin.")
            return

        # Şimdilik kurulumu basitçe gösterelim (İleride Thread yapısına geçeceğiz)
        confirm = QMessageBox.question(self, "Onay", f"{len(to_install)} adet program kurulacak. Onaylıyor musunuz?", 
                                       QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            # Burada normalde Thread başlatacağız. Şimdilik komutu yazdıralım.
            cmd = f"winget install {' '.join(to_install)}"
            print(f"Çalıştırılacak komut: {cmd}")
            # Örnek tekli kurulum (Test amaçlı):
            # subprocess.run(f"winget install {to_install[0]}", shell=True)
            QMessageBox.information(self, "Bilgi", "Kurulum işlemi arka planda başlatılacak (Sonraki adımda eklenecek).")