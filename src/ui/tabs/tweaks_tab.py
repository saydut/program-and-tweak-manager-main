from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QCheckBox, QMessageBox, QHBoxLayout, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import json
import os
import sys

# Yeni oluşturduğumuz helper'ı import ediyoruz
from src.utils.helpers import create_restore_point, run_powershell

class TweakRunnerThread(QThread):
    """Tweakleri arka planda uygulayan iş parçacığı"""
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, tweaks):
        super().__init__()
        self.tweaks = tweaks

    def run(self):
        total = len(self.tweaks)
        for index, tweak in enumerate(self.tweaks):
            self.log_signal.emit(f"[{index+1}/{total}] Uygulanıyor: {tweak['name']}...")
            
            # Tweak komutunu çalıştır (PowerShell)
            # Not: data/tweaks.json içindeki komutların PowerShell uyumlu olduğunu varsayıyoruz.
            command = tweak.get('command', '')
            if command:
                run_powershell(command)
            
            self.log_signal.emit(f"✅ {tweak['name']} uygulandı.")
        
        self.finished_signal.emit()

class TweaksTab(QWidget):
    def __init__(self):
        super().__init__()
        self.tweaks_data = self.load_tweaks()
        self.init_ui()

    def load_tweaks(self):
        """data/tweaks.json dosyasını yükler"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            json_path = os.path.join(base_dir, 'data', 'tweaks.json')
            
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Tweak dosyası okunamadı: {e}")
            return []

    def init_ui(self):
        layout = QVBoxLayout()

        # Bilgilendirme
        info = QLabel("Sistem performansını artırmak için aşağıdaki ayarları kullanabilirsiniz.\n"
                      "DİKKAT: İşlem öncesi otomatik olarak Sistem Geri Yükleme Noktası oluşturulacaktır.")
        info.setStyleSheet("color: #aaa; margin-bottom: 10px;")
        layout.addWidget(info)

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Seç", "Tweak Adı", "Açıklama"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 40)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #1e293b; color: #e2e8f0; border: none; }
            QHeaderView::section { background-color: #0f172a; color: #94a3b8; padding: 5px; }
        """)
        
        # Tabloyu doldur
        self.table.setRowCount(len(self.tweaks_data))
        for row, tweak in enumerate(self.tweaks_data):
            # Checkbox
            chk_box = QCheckBox()
            cell_widget = QWidget()
            chk_layout = QHBoxLayout(cell_widget)
            chk_layout.addWidget(chk_box)
            chk_layout.setAlignment(Qt.AlignCenter)
            chk_layout.setContentsMargins(0,0,0,0)
            self.table.setCellWidget(row, 0, cell_widget)
            chk_box.setProperty("tweak_data", tweak)

            # Bilgiler
            self.table.setItem(row, 1, QTableWidgetItem(tweak.get('name', 'Bilinmeyen')))
            self.table.setItem(row, 2, QTableWidgetItem(tweak.get('description', '')))

        layout.addWidget(self.table)
        
        # Durum Çubuğu
        self.lbl_status = QLabel("Hazır")
        self.lbl_status.setStyleSheet("color: #64748b;")
        layout.addWidget(self.lbl_status)

        # Buton
        self.btn_apply = QPushButton("Seçilenleri Uygula")
        self.btn_apply.setFixedHeight(45)
        self.btn_apply.setStyleSheet("""
            QPushButton { background-color: #e11d48; color: white; font-weight: bold; border-radius: 5px; }
            QPushButton:hover { background-color: #be123c; }
        """)
        self.btn_apply.clicked.connect(self.start_apply_process)
        layout.addWidget(self.btn_apply)

        self.setLayout(layout)

    def start_apply_process(self):
        selected_tweaks = []
        for row in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(row, 0)
            if cell_widget:
                checkbox = cell_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    selected_tweaks.append(checkbox.property("tweak_data"))

        if not selected_tweaks:
            QMessageBox.warning(self, "Uyarı", "Lütfen uygulanacak en az bir ayar seçin.")
            return

        # 1. KULLANICIYA SOR VE GERİ YÜKLEME NOKTASI OLUŞTUR
        reply = QMessageBox.question(self, "Güvenlik Önlemi", 
                                   f"{len(selected_tweaks)} adet sistem ayarı değiştirilecek.\n\n"
                                   "Olası sorunlara karşı SİSTEM GERİ YÜKLEME NOKTASI oluşturulsun mu?\n"
                                   "(Önerilir, ancak işlem 1-2 dakika sürebilir)",
                                   QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

        if reply == QMessageBox.Cancel:
            return

        if reply == QMessageBox.Yes:
            self.lbl_status.setText("⏳ Sistem Geri Yükleme Noktası oluşturuluyor... Lütfen bekleyin...")
            self.btn_apply.setEnabled(False)
            self.table.setEnabled(False)
            
            # Arayüz donmasın diye processEvents (basit çözüm)
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()

            success, msg = create_restore_point("Saydut Tweak Öncesi Yedek")
            
            if not success:
                warn_reply = QMessageBox.warning(self, "Yedek Oluşturulamadı", 
                                               f"Geri yükleme noktası oluşturulamadı:\n{msg}\n\nYine de devam etmek istiyor musunuz?",
                                               QMessageBox.Yes | QMessageBox.No)
                if warn_reply == QMessageBox.No:
                    self.lbl_status.setText("İşlem iptal edildi.")
                    self.btn_apply.setEnabled(True)
                    self.table.setEnabled(True)
                    return
            else:
                self.lbl_status.setText("✅ Geri yükleme noktası oluşturuldu.")

        # 2. TWEAKLERİ UYGULA
        self.run_tweaks(selected_tweaks)

    def run_tweaks(self, tweaks):
        self.btn_apply.setEnabled(False)
        self.table.setEnabled(False)
        self.thread = TweakRunnerThread(tweaks)
        self.thread.log_signal.connect(self.lbl_status.setText)
        self.thread.finished_signal.connect(self.on_finished)
        self.thread.start()

    def on_finished(self):
        self.btn_apply.setEnabled(True)
        self.table.setEnabled(True)
        self.lbl_status.setText("İşlem tamamlandı.")
        QMessageBox.information(self, "Başarılı", "Seçilen ayarlar uygulandı.\nEtkilerin görülmesi için bilgisayarı yeniden başlatmanız önerilir.")