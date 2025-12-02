from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QMessageBox, QCheckBox, QHBoxLayout, QProgressBar)
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
            if "Name" in line and "Id" in line and "Version" in line:
                header_found = True
                # Sütunların başlangıç yerlerini tespit et
                col_indices['Name'] = 0
                col_indices['Id'] = line.find("Id")
                col_indices['Version'] = line.find("Version")
                col_indices['Available'] = line.find("Available")
                col_indices['Source'] = line.find("Source")
                continue
            
            # Ayırıcı çizgileri (------) atla
            if "-----" in line:
                continue

            # Veri satırlarını işle
            if header_found and line.strip():
                try:
                    # Satırı sütunlara böl
                    name = line[col_indices['Name']:col_indices['Id']].strip()
                    app_id = line[col_indices['Id']:col_indices['Version']].strip()
                    current_ver = line[col_indices['Version']:col_indices['Available']].strip()
                    new_ver = line[col_indices['Available']:col_indices['Source']].strip()
                    
                    # Eğer anlamlı bir veri varsa listeye ekle
                    if name and app_id:
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
            cmd = ["winget", "upgrade", "--id", app_id, "--accept-source-agreements", "--accept-package-agreements"]
            
            proc = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                encoding='utf-8', 
                errors='ignore',
                creationflags=creationflags
            )
            
            # Çıktıyı anlık okuyabiliriz ama basitlik için bekleyelim
            stdout, stderr = proc.communicate()
            
            if proc.returncode == 0:
                self.log_signal.emit(f"✅ {app_id} başarıyla güncellendi.")
            else:
                self.log_signal.emit(f"❌ {app_id} güncellenemedi.")
        
        self.finished_signal.emit()

class UpdatesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # --- Üst Bilgi ve Buton ---
        info_label = QLabel("Bilgisayarınızdaki güncellemeleri kontrol edin ve seçtiklerinizi güvenle yükleyin.")
        info_label.setStyleSheet("color: #aaa; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(info_label)

        btn_layout = QHBoxLayout()
        self.btn_check = QPushButton("Güncellemeleri Denetle")
        self.btn_check.setFixedHeight(40)
        self.btn_check.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; color: white; border-radius: 5px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        self.btn_check.clicked.connect(self.start_check_updates)
        btn_layout.addWidget(self.btn_check)
        layout.addLayout(btn_layout)

        # --- Yükleniyor Göstergesi ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Sonsuz döngü animasyonu
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # --- Tablo ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Seç", "Program Adı", "Mevcut Sürüm", "Yeni Sürüm"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch) # İsim kısmı uzasın
        self.table.setColumnWidth(0, 40) # Checkbox sütunu dar olsun
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1e293b; color: #e2e8f0; gridline-color: #334155; border: none;
            }
            QHeaderView::section {
                background-color: #0f172a; color: #94a3b8; padding: 5px; border: none; font-weight: bold;
            }
            QTableWidget::item { padding: 5px; }
        """)
        layout.addWidget(self.table)

        # --- Alt Aksiyon Alanı ---
        action_layout = QHBoxLayout()
        
        self.lbl_status = QLabel("Hazır")
        self.lbl_status.setStyleSheet("color: #64748b;")
        action_layout.addWidget(self.lbl_status)
        
        action_layout.addStretch()
        
        self.btn_update_selected = QPushButton("Seçilenleri Güncelle")
        self.btn_update_selected.setEnabled(False) # Başta pasif
        self.btn_update_selected.setFixedHeight(40)
        self.btn_update_selected.setStyleSheet("""
            QPushButton {
                background-color: #16a34a; color: white; border-radius: 5px; font-weight: bold; padding: 0 20px;
            }
            QPushButton:hover { background-color: #15803d; }
            QPushButton:disabled { background-color: #334155; color: #94a3b8; }
        """)
        self.btn_update_selected.clicked.connect(self.start_update_process)
        action_layout.addWidget(self.btn_update_selected)
        
        layout.addLayout(action_layout)
        self.setLayout(layout)

    def start_check_updates(self):
        """Kontrol işlemini başlatır."""
        self.table.setRowCount(0)
        self.btn_check.setEnabled(False)
        self.btn_update_selected.setEnabled(False)
        self.progress_bar.show()
        self.lbl_status.setText("Güncellemeler taranıyor (Winget)... Bu işlem biraz sürebilir.")
        
        self.check_thread = CheckUpdatesThread()
        self.check_thread.updates_found.connect(self.on_updates_found)
        self.check_thread.error_occurred.connect(self.on_error)
        self.check_thread.start()

    def on_updates_found(self, apps):
        """Bulunan güncellemeleri tabloya ekler."""
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
            chk_box.setChecked(True) # Varsayılan olarak seçili gelsin
            # Checkbox'ı ortalamak için bir widget içine koyuyoruz
            cell_widget = QWidget()
            chk_layout = QHBoxLayout(cell_widget)
            chk_layout.addWidget(chk_box)
            chk_layout.setAlignment(Qt.AlignCenter)
            chk_layout.setContentsMargins(0,0,0,0)
            self.table.setCellWidget(row, 0, cell_widget)
            
            # Program ID'sini checkbox'a gizli veri olarak ekleyelim ki sonra bulalım
            chk_box.setProperty("app_id", app['id'])

            # 2. İsim, Mevcut, Yeni
            self.table.setItem(row, 1, QTableWidgetItem(app['name']))
            self.table.setItem(row, 2, QTableWidgetItem(app['current']))
            self.table.setItem(row, 3, QTableWidgetItem(app['new']))

        self.btn_update_selected.setEnabled(True)

    def on_error(self, message):
        self.progress_bar.hide()
        self.btn_check.setEnabled(True)
        self.lbl_status.setText("Hata oluştu.")
        QMessageBox.warning(self, "Hata", message)

    def start_update_process(self):
        """Seçilenleri güncelleme işlemini başlatır."""
        selected_ids = []
        
        # Tabloyu gez ve seçili olanların ID'sini al
        for row in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(row, 0)
            # Widget hiyerarşisi: Widget -> Layout -> Checkbox
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
            self.btn_update_selected.setEnabled(False)
            self.progress_bar.show()
            
            self.update_thread = UpdateRunnerThread(selected_ids)
            self.update_thread.log_signal.connect(self.update_status_log)
            self.update_thread.finished_signal.connect(self.on_update_finished)
            self.update_thread.start()

    def update_status_log(self, message):
        self.lbl_status.setText(message)

    def on_update_finished(self):
        self.progress_bar.hide()
        self.lbl_status.setText("İşlem tamamlandı. Listeyi yenileyebilirsiniz.")
        self.btn_check.setEnabled(True)
        QMessageBox.information(self, "Tamamlandı", "Seçilen güncellemeler tamamlandı!")
        # Listeyi temizle
        self.table.setRowCount(0)
        self.btn_update_selected.setEnabled(False)