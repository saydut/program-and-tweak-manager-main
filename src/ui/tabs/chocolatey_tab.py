import json
import os
import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QScrollArea, 
                             QPushButton, QHBoxLayout, QMessageBox, QLabel,
                             QGridLayout, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# --- CHOCCO THREAD ---
class ChocoInstallerThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, package_list):
        super().__init__()
        self.package_list = package_list

    def run(self):
        # Toplu kurulum komutu: choco install paket1 paket2 -y
        packages_str = " ".join(self.package_list)
        self.progress_signal.emit(f"Paketler indiriliyor: {packages_str}...")
        
        try:
            cmd = f"choco install {packages_str} -y --force"
            
            # Konsol penceresini gizle
            creationflags = 0x08000000 if os.name == 'nt' else 0
            
            # İşlemi başlat ve bekle
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                    text=True, creationflags=creationflags)
            
            # Çıktıları okuyabiliriz (Basit versiyon için bekleme yeterli)
            proc.wait()
            
            if proc.returncode == 0:
                self.progress_signal.emit("✅ Kurulum başarıyla tamamlandı.")
            else:
                self.progress_signal.emit("⚠️ Bazı paketlerde sorun oluşmuş olabilir.")
                
        except Exception as e:
            self.progress_signal.emit(f"❌ Hata: {str(e)}")
            
        self.finished_signal.emit()

# --- ARAYÜZ ---
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
        """Chocolatey'nin sistemde olup olmadığını kontrol eder."""
        try:
            creationflags = 0x08000000 if os.name == 'nt' else 0
            subprocess.run(["choco", "--version"], capture_output=True, check=True, creationflags=creationflags)
            return True
        except:
            return False

    def load_data(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            json_path = os.path.join(base_dir, 'data', 'chocolatey.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                self.choco_data = json.load(f)
        except:
            self.choco_data = []

    def init_ui(self):
        # 1. Başlık ve Durum
        header_layout = QHBoxLayout()
        title = QLabel("Chocolatey Paketleri")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #3b82f6;")
        
        status_text = "✔️ Yüklü" if self.is_choco_installed else "❌ Yüklü Değil"
        status_color = "#10b981" if self.is_choco_installed else "#ef4444"
        
        self.lbl_choco_status = QLabel(f"Durum: {status_text}")
        self.lbl_choco_status.setStyleSheet(f"color: {status_color}; font-weight: bold; font-size: 14px;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_choco_status)
        self.layout.addLayout(header_layout)

        # Eğer choco yoksa yükleme butonu göster
        if not self.is_choco_installed:
            self.btn_install_core = QPushButton("Chocolatey'i Şimdi Yükle (Gerekli)")
            self.btn_install_core.setProperty("class", "danger")
            self.btn_install_core.clicked.connect(self.install_chocolatey_core)
            self.layout.addWidget(self.btn_install_core)

        # 2. Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(5, 5, 5, 5)
        
        if not self.choco_data:
            grid_layout.addWidget(QLabel("Veri yok (data/chocolatey.json)!"), 0, 0)
        else:
            row = 0
            col = 0
            max_columns = 4 

            for item in self.choco_data:
                card = QFrame()
                card.setProperty("class", "card")
                card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(15, 15, 15, 15)
                
                cb = QCheckBox(item.get("name", "Bilinmeyen"))
                cb.setStyleSheet("font-weight: bold; font-size: 14px; border: none; background: transparent;")
                cb.setProperty("choco_package", item.get("package"))
                
                # Choco yoksa seçimleri engelle
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

        # 3. İşlem Durum Logu
        self.lbl_process_status = QLabel("Hazır")
        self.lbl_process_status.setStyleSheet("color: #64748b; font-weight: bold; margin-left: 5px;")
        self.layout.addWidget(self.lbl_process_status)

        # 4. Alt Buton
        action_bar = QFrame()
        action_bar.setStyleSheet("background-color: transparent; border-top: 1px solid #334155; margin-top: 5px;")
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
        """Chocolatey'i sisteme kurar."""
        cmd = "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
        try:
            QMessageBox.information(self, "Kurulum", "Chocolatey kurulumu başlıyor. Bu işlem internet hızına göre sürebilir.\nLütfen bekleyin...")
            
            creationflags = 0x08000000 if os.name == 'nt' else 0
            subprocess.run(["powershell", "-Command", cmd], shell=True, check=True, creationflags=creationflags)
            
            QMessageBox.information(self, "Başarılı", "Chocolatey kuruldu! Programı yeniden başlatmanız gerekiyor.")
            self.btn_install_core.setEnabled(False)
            self.btn_install_core.setText("Kurulum Tamamlandı (Yeniden Başlatın)")
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

        self.btn_install.setEnabled(False)
        self.lbl_process_status.setText("İşlem başlatılıyor...")
        
        self.thread = ChocoInstallerThread(packages)
        self.thread.progress_signal.connect(self.lbl_process_status.setText)
        self.thread.finished_signal.connect(self.on_process_finished)
        self.thread.start()

    def on_process_finished(self):
        self.btn_install.setEnabled(True)
        self.lbl_process_status.setText("Tüm işlemler bitti.")
        QMessageBox.information(self, "Bilgi", "Seçilen Chocolatey paketleri kuruldu.")