from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QMessageBox, QCheckBox, QHBoxLayout, QProgressBar, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import subprocess
import sys

class CheckUpdatesThread(QThread):
    """
    Güncellemeleri arka planda kontrol eden iş parçacığı.
    Programın donmasını engeller.
    """
    updates_found = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def run(self):
        try:
            # Winget komutunu çalıştır (UTF-8 encoding ile Türkçe karakter sorununu çözer)
            # --include-unknown: Sürümü bilinmeyenleri de listele
            creationflags = 0x08000000 if sys.platform == "win32" else 0  # Konsol penceresi açılmasın
            result = subprocess.run(
                ["winget", "upgrade", "--include-unknown"],
                capture_output=True,
                text=True,
                encoding='utf-8', 
                errors='ignore',
                creationflags=creationflags
            )

            if result.returncode != 0 and "No installed package found matching input criteria" not in result.stderr:
                # Winget bazen hata kodu döndürse de çıktı verebilir, o yüzden stderr kontrolü önemli
                if not result.stdout:
                    self.error_occurred.emit(f"Hata oluştu: {result.stderr}")
                    return

            output_lines = result.stdout.splitlines()
            parsed_data = self.parse_winget_output(output_lines)
            self.updates_found.emit(parsed_data)

        except Exception as e:
            self.error_occurred.emit(str(e))

    def parse_winget_output(self, lines):
        """Winget çıktısını tablo verisine dönüştürür."""
        apps = []
        header_found = False
        col_indices = {}

        for line in lines:
            # Başlık satırını bul (Name, Id, Version... içerir)
            # Winget sürümüne göre başlıklar değişebilir, bu yüzden esnek olmalı
            lower_line = line.lower()
            if "name" in lower_line and "id" in lower_line and "version" in lower_line:
                header_found = True
                # Sütunların başlangıç yerlerini tespit et
                col_indices['Name'] = line.find("Name") if "Name" in line else line.find("Ad")
                col_indices['Id'] = line.find("Id")
                col_indices['Version'] = line.find("Version") if "Version" in line else line.find("Sürüm")
                col_indices['Available'] = line.find("Available") if "Available" in line else line.find("Mevcut")
                col_indices['Source'] = line.find("Source") if "Source" in line else line.find("Kaynak")
                continue
            
            # Ayırıcı çizgileri (------) atla
            if "-----" in line:
                continue

            # Veri satırlarını işle
            if header_found and line.strip():
                try:
                    # Satırı sütunlara böl
                    # İndekslerin geçerliliğini kontrol et
                    name_idx = col_indices.get('Name', 0)
                    id_idx = col_indices.get('Id', 20)
                    ver_idx = col_indices.get('Version', 40)
                    avail_idx = col_indices.get('Available', 60)
                    source_idx = col_indices.get('Source', 80)

                    name = line[name_idx:id_idx].strip()
                    app_id = line[id_idx:ver_idx].strip()
                    current_ver = line[ver_idx:avail_idx].strip()
                    new_ver = line[avail_idx:source_idx].strip()
                    
                    # Eğer anlamlı bir veri varsa listeye ekle
                    if name and app_id and "..." not in app_id: # ... olanlar genelde kesilmiş satırlardır
                        apps.append({
                            "name": name,
                            "id": app_id,
                            "current": current_ver,
                            "new": new_ver
                        })
                except:
                    continue # Hatalı satırı atla
        return apps

class UpdateRunnerThread(QThread):
    """
    Seçilen programları sırayla güncelleyen iş parçacığı.
    """
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, app_ids):
        super().__init__()
        self.app_ids = app_ids

    def run(self):
        total = len(self.app_ids)
        for index, app_id in enumerate(self.app_ids):
            self.log_signal.emit(f"[{index+1}/{total}] Güncelleniyor: {app_id}...")
            
            creationflags = 0x08000000 if sys.platform == "win32" else 0
            # --accept-source-agreements --accept-package-agreements: Onay istemeden kurması için
            cmd = ["winget", "upgrade", "--id", app_id, "--accept-source-agreements", "--accept-package-agreements", "--silent"]
            
            try:
                proc = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True, 
                    encoding='utf-8', 
                    errors='ignore',
                    creationflags=creationflags
                )
                
                # Çıktıyı bekle
                stdout, stderr = proc.communicate()
                
                if proc.returncode == 0:
                    self.log_signal.emit(f"✅ {app_id} başarıyla güncellendi.")
                else:
                    self.log_signal.emit(f"❌ {app_id} güncellenemedi. Hata kodu: {proc.returncode}")
            except Exception as e:
                self.log_signal.emit(f"❌ {app_id} hata: {str(e)}")
        
        self.finished_signal.emit()

class UpdatesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Üst Bilgi
        title = QLabel("Yazılım Güncellemeleri")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #3b82f6;")
        desc = QLabel("Bilgisayarınızdaki güncellemeleri kontrol edin ve seçtiklerinizi güvenle yükleyin.")
        desc.setStyleSheet("color: #94a3b8; margin-bottom: 10px;")
        
        layout.addWidget(title)
        layout.addWidget(desc)

        # Kontrol Butonu
        self.btn_check = QPushButton("Güncellemeleri Tara")
        self.btn_check.setMinimumHeight(40)
        self.btn_check.clicked.connect(self.start_check_updates)
        layout.addWidget(self.btn_check)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Sonsuz döngü (Marquee)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: none; background: #334155; height: 5px; border-radius: 2px; }
            QProgressBar::chunk { background: #3b82f6; border-radius: 2px; }
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Seç", "Program Adı", "Mevcut Sürüm", "Yeni Sürüm"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 50)
        self.table.verticalHeader().setVisible(False)
        # Tema dosyasındaki stiller otomatik uygulanacak
        layout.addWidget(self.table)

        # Alt Butonlar
        action_bar = QFrame()
        action_bar.setStyleSheet("background-color: transparent; border-top: 1px solid #334155; margin-top: 10px;")
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(0, 10, 0, 0)
        
        self.lbl_status = QLabel("Hazır")
        self.lbl_status.setStyleSheet("color: #64748b; font-weight: bold;")
        
        self.btn_update = QPushButton("Seçilenleri Güncelle")
        self.btn_update.setProperty("class", "success")
        self.btn_update.setMinimumHeight(45)
        self.btn_update.setEnabled(False)
        self.btn_update.clicked.connect(self.start_update_process)
        
        action_layout.addWidget(self.lbl_status)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_update)
        
        layout.addWidget(action_bar)
        self.setLayout(layout)

    def start_check_updates(self):
        self.table.setRowCount(0)
        self.btn_check.setEnabled(False)
        self.btn_update.setEnabled(False)
        self.progress_bar.show()
        self.lbl_status.setText("Güncellemeler taranıyor... Bu işlem biraz sürebilir.")
        
        self.check_thread = CheckUpdatesThread()
        self.check_thread.updates_found.connect(self.on_updates_found)
        self.check_thread.error_occurred.connect(self.on_error)
        self.check_thread.start()

    def on_updates_found(self, apps):
        self.progress_bar.hide()
        self.btn_check.setEnabled(True)
        
        if not apps:
            self.lbl_status.setText("Tüm programlar güncel!")
            QMessageBox.information(self, "Durum", "Harika! Güncellenecek program bulunamadı.")
            return

        self.lbl_status.setText(f"{len(apps)} adet güncelleme bulundu.")
        self.table.setRowCount(len(apps))
        
        for row, app in enumerate(apps):
            # 1. Checkbox
            chk_box = QCheckBox()
            chk_box.setChecked(True)
            cell_widget = QWidget()
            chk_layout = QHBoxLayout(cell_widget)
            chk_layout.addWidget(chk_box)
            chk_layout.setAlignment(Qt.AlignCenter)
            chk_layout.setContentsMargins(0,0,0,0)
            self.table.setCellWidget(row, 0, cell_widget)
            
            # Program ID'sini checkbox'a ekle
            chk_box.setProperty("app_id", app['id'])

            # 2. Bilgiler
            self.table.setItem(row, 1, QTableWidgetItem(app['name']))
            self.table.setItem(row, 2, QTableWidgetItem(app['current']))
            self.table.setItem(row, 3, QTableWidgetItem(app['new']))

        self.btn_update.setEnabled(True)

    def on_error(self, message):
        self.progress_bar.hide()
        self.btn_check.setEnabled(True)
        self.lbl_status.setText("Hata oluştu.")
        QMessageBox.warning(self, "Hata", message)

    def start_update_process(self):
        selected_ids = []
        for row in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(row, 0)
            if cell_widget:
                checkbox = cell_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    selected_ids.append(checkbox.property("app_id"))

        if not selected_ids:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir program seçin.")
            return

        confirm = QMessageBox.question(self, "Onay", f"{len(selected_ids)} program güncellenecek. Devam edilsin mi?", 
                                       QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            self.btn_check.setEnabled(False)
            self.btn_update.setEnabled(False)
            self.progress_bar.show()
            
            self.update_thread = UpdateRunnerThread(selected_ids)
            self.update_thread.log_signal.connect(self.update_status_log)
            self.update_thread.finished_signal.connect(self.on_update_finished)
            self.update_thread.start()

    def update_status_log(self, message):
        self.lbl_status.setText(message)

    def on_update_finished(self):
        self.progress_bar.hide()
        self.lbl_status.setText("İşlem tamamlandı.")
        self.btn_check.setEnabled(True)
        QMessageBox.information(self, "Tamamlandı", "Seçilen güncellemeler tamamlandı!")
        self.table.setRowCount(0)