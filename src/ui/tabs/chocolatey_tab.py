import json
import os
import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QScrollArea, 
                             QPushButton, QHBoxLayout, QMessageBox, QLabel)
from PyQt5.QtCore import Qt

class ChocolateyTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.checkboxes = []
        self.choco_data = []
        
        # Önce Chocolatey yüklü mü diye bakalım
        self.is_choco_installed = self.check_choco_installed()
        
        self.load_data()
        self.init_ui()
        self.setLayout(self.layout)

    def check_choco_installed(self):
        """Sistemde 'choco' komutu çalışıyor mu kontrol eder."""
        try:
            subprocess.run(["choco", "--version"], capture_output=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
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
        # Başlık ve Durum Bilgisi
        header_layout = QHBoxLayout()
        title = QLabel("Chocolatey Paketleri")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title)
        
        # Duruma göre ikon/metin
        status_label = QLabel()
        if self.is_choco_installed:
            status_label.setText("Durum: ✔️ Yüklü")
            status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            status_label.setText("Durum: ❌ Yüklü Değil")
            status_label.setStyleSheet("color: red; font-weight: bold;")
        
        header_layout.addWidget(status_label)
        header_layout.addStretch()
        self.layout.addLayout(header_layout)

        # Eğer yüklü değilse "Yükle" butonu göster
        if not self.is_choco_installed:
            install_btn = QPushButton("Chocolatey'i Şimdi Yükle")
            install_btn.setStyleSheet("background-color: #d32f2f; color: white; padding: 5px;")
            install_btn.clicked.connect(self.install_chocolatey_core)
            self.layout.addWidget(install_btn)

        # Liste Alanı
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        if not self.choco_data:
            scroll_layout.addWidget(QLabel("Liste yüklenemedi! data/chocolatey.json dosyasını kontrol edin."))
        else:
            for item in self.choco_data:
                cb = QCheckBox(item.get("name", "Bilinmeyen"))
                # JSON'da paket adı 'package' anahtarı ile tutuluyor
                cb.setProperty("choco_package", item.get("package"))
                self.checkboxes.append(cb)
                scroll_layout.addWidget(cb)
                
                # Choco yüklü değilse checkboxları devre dışı bırak
                if not self.is_choco_installed:
                    cb.setEnabled(False)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)
        self.layout.addWidget(scroll_area)

        # Kurulum Butonu
        btn_layout = QHBoxLayout()
        self.btn_install = QPushButton("Seçilenleri Kur")
        self.btn_install.setMinimumHeight(40)
        self.btn_install.clicked.connect(self.install_selected)
        if not self.is_choco_installed:
            self.btn_install.setEnabled(False)
            
        btn_layout.addWidget(self.btn_install)
        self.layout.addLayout(btn_layout)

    def install_chocolatey_core(self):
        """Chocolatey'i sisteme kuran komutu çalıştırır."""
        cmd = "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
        try:
            QMessageBox.information(self, "Kurulum", "Chocolatey kurulumu başlıyor. Bu işlem biraz sürebilir, lütfen bekleyin.")
            # PowerShell ile çalıştır
            subprocess.run(["powershell", "-Command", cmd], shell=True, check=True)
            QMessageBox.information(self, "Başarılı", "Chocolatey kuruldu! Programı yeniden başlatmanız gerekebilir.")
            # Butonları aktifleştirmek için basitçe yeniden başlatma önerilir veya programı reload edebiliriz.
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kurulum başarısız oldu: {e}")

    def install_selected(self):
        packages = []
        for cb in self.checkboxes:
            if cb.isChecked():
                packages.append(cb.property("choco_package"))
        
        if not packages:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir paket seçin.")
            return

        confirm = QMessageBox.question(self, "Onay", f"{len(packages)} paket Chocolatey ile kurulacak.\nDevam edilsin mi?", 
                                       QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            # Paketleri tek komutta birleştir: choco install p1 p2 p3 -y
            packages_str = " ".join(packages)
            cmd = f"choco install {packages_str} -y"
            
            # Şimdilik direkt çalıştırıyoruz (Multithread sonraki iş)
            print(f"Komut: {cmd}")
            # subprocess.run(cmd, shell=True) # Gerçek kurulum için bu satır açılmalı
            QMessageBox.information(self, "Bilgi", f"Komut gönderildi:\n{cmd}\n\n(Arka plan işlemi daha sonra eklenecek)")