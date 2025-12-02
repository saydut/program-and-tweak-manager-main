from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QPushButton, 
                             QHBoxLayout, QMessageBox, QLabel)
from PyQt5.QtGui import QFont
import subprocess

class UpdatesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.init_ui()
        self.setLayout(self.layout)

    def init_ui(self):
        title = QLabel("Yazılım Güncellemeleri (Winget)")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(title)

        # Bilgi Etiketi
        info_lbl = QLabel("Sisteminizdeki güncel olmayan programları tarar ve günceller.")
        self.layout.addWidget(info_lbl)

        # Log Ekranı (Konsol gibi görünmesi için)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Consolas", 10))
        self.log_area.setPlaceholderText("Güncellemeleri denetlemek için butona basın...")
        self.layout.addWidget(self.log_area)

        # Butonlar
        btn_layout = QHBoxLayout()
        
        self.btn_check = QPushButton("Güncellemeleri Denetle")
        self.btn_check.clicked.connect(self.check_updates)
        btn_layout.addWidget(self.btn_check)
        
        self.btn_update_all = QPushButton("Tümünü Güncelle")
        self.btn_update_all.setStyleSheet("background-color: #2e7d32; color: white;") # Yeşil renk
        self.btn_update_all.clicked.connect(self.update_all)
        self.btn_update_all.setEnabled(False) # Denetleme yapılmadan aktif olmasın
        btn_layout.addWidget(self.btn_update_all)
        
        self.layout.addLayout(btn_layout)

    def check_updates(self):
        self.log_area.setText("Güncellemeler denetleniyor, lütfen bekleyin...\n(Bu işlem biraz zaman alabilir)")
        self.log_area.repaint() # Arayüzün donmaması için zorla çizdir
        
        try:
            # Windows'ta konsol penceresi açılmasın diye startupinfo ayarı
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            # 'winget upgrade' komutunu çalıştır
            process = subprocess.run(["winget", "upgrade"], capture_output=True, text=True, startupinfo=si)
            output = process.stdout
            
            self.log_area.setText(output)
            
            # Eğer çıktı içinde "No installed package found" gibi bir ifade yoksa güncelleme vardır
            # Basit bir mantıkla: Çıktı çok kısaysa güncelleme yoktur.
            if "No installed package found matching input criteria" in output or "güncelleme bulunamadı" in output.lower():
                self.btn_update_all.setEnabled(False)
                self.log_area.append("\n\nSisteminiz güncel görünüyor.")
            else:
                self.btn_update_all.setEnabled(True)
                self.log_area.append("\n\nGüncellemeler mevcut. 'Tümünü Güncelle' butonunu kullanabilirsiniz.")
                
        except Exception as e:
            self.log_area.setText(f"Hata oluştu: {str(e)}")

    def update_all(self):
        confirm = QMessageBox.question(self, "Onay", "Tüm programlar güncellenecek. Bu işlem uzun sürebilir.\nDevam edilsin mi?", 
                                       QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            # Güncelleme işlemini kullanıcının görebilmesi için ayrı bir CMD penceresinde başlatıyoruz
            cmd = 'start cmd /k "winget upgrade --all && echo. && echo Islem tamamlandi, pencereyi kapatabilirsiniz."'
            subprocess.run(cmd, shell=True)
            self.log_area.append("\n\nGüncelleme işlemi yeni pencerede başlatıldı.")