import json
import os
import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QScrollArea, 
                             QPushButton, QHBoxLayout, QMessageBox, QLabel,
                             QGridLayout, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt

class ChocolateyTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.checkboxes = []
        self.choco_data = []
        self.is_choco_installed = self.check_choco_installed()
        
        self.load_data()
        self.init_ui()
        self.setLayout(self.layout)

    def check_choco_installed(self):
        try:
            subprocess.run(["choco", "--version"], capture_output=True, check=True, creationflags=0x08000000)
            return True
        except:
            return False

    def load_data(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        json_path = os.path.join(base_dir, 'data', 'chocolatey.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.choco_data = json.load(f)
        except:
            self.choco_data = []

    def init_ui(self):
        # Başlık ve Durum
        header_layout = QHBoxLayout()
        title = QLabel("Chocolatey Paketleri")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #3b82f6;")
        
        status_label = QLabel()
        if self.is_choco_installed:
            status_label.setText("Durum: ✔️ Yüklü")
            status_label.setStyleSheet("color: #10b981; font-weight: bold; font-size: 14px;")
        else:
            status_label.setText("Durum: ❌ Yüklü Değil")
            status_label.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 14px;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(status_label)
        self.layout.addLayout(header_layout)

        if not self.is_choco_installed:
            install_btn = QPushButton("Chocolatey'i Şimdi Yükle")
            install_btn.setProperty("class", "danger")
            install_btn.clicked.connect(self.install_chocolatey_core)
            self.layout.addWidget(install_btn)

        # Kart Alanı
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(5, 5, 5, 5)
        
        if not self.choco_data:
            grid_layout.addWidget(QLabel("Veri yok!"), 0, 0)
        else:
            row = 0
            col = 0
            max_columns = 4 # İsimler kısa olduğu için 4 sütun olabilir

            for item in self.choco_data:
                card = QFrame()
                card.setProperty("class", "card")
                card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(15, 15, 15, 15)
                
                cb = QCheckBox(item.get("name", "Bilinmeyen"))
                cb.setStyleSheet("font-weight: bold; font-size: 14px; border: none; background: transparent;")
                cb.setProperty("choco_package", item.get("package"))
                if not self.is_choco_installed:
                    cb.setEnabled(False)
                
                self.checkboxes.append(cb)
                
                card_layout.addWidget(cb)
                grid_layout.addWidget(card, row, col)
                
                col += 1
                if col >= max_columns:
                    col = 0
                    row += 1

        scroll_widget.setLayout(grid_layout)
        scroll_area.setWidget(scroll_widget)
        self.layout.addWidget(scroll_area)

        # Alt Buton
        action_bar = QFrame()
        action_bar.setStyleSheet("background-color: transparent; border-top: 1px solid #334155; margin-top: 10px;")
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(0, 10, 0, 0)
        
        self.btn_install = QPushButton("Seçilenleri Kur")
        self.btn_install.setProperty("class", "success")
        self.btn_install.setMinimumHeight(45)
        self.btn_install.clicked.connect(self.install_selected)
        if not self.is_choco_installed:
            self.btn_install.setEnabled(False)
            
        action_layout.addStretch()
        action_layout.addWidget(self.btn_install)
        self.layout.addWidget(action_bar)

    def install_chocolatey_core(self):
        cmd = "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
        try:
            QMessageBox.information(self, "Kurulum", "Chocolatey kurulumu başlıyor...")
            subprocess.run(["powershell", "-Command", cmd], shell=True, check=True)
            QMessageBox.information(self, "Başarılı", "Chocolatey kuruldu! Programı yeniden başlatın.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kurulum başarısız: {e}")

    def install_selected(self):
        packages = []
        for cb in self.checkboxes:
            if cb.isChecked():
                packages.append(cb.property("choco_package"))
        
        if not packages:
            QMessageBox.warning(self, "Uyarı", "Paket seçmelisiniz.")
            return

        cmd = f"choco install {' '.join(packages)} -y"
        print(f"Komut: {cmd}")
        QMessageBox.information(self, "Bilgi", "Kurulum başlıyor...")