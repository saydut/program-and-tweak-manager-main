import json
import os
import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QScrollArea, 
                             QPushButton, QHBoxLayout, QMessageBox, QLabel, 
                             QGridLayout, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from src.utils.helpers import get_base_path  # Helper fonksiyonu import ettik

# --- İŞ PARÇACIĞI (THREAD) ---
class InstallerThread(QThread):
    """
    Kurulum işlemlerini arka planda yapar, arayüzün donmasını engeller.
    """
    progress_signal = pyqtSignal(str)  # Anlık durum mesajı
    finished_signal = pyqtSignal()     # İşlem bitti sinyali

    def __init__(self, install_list):
        super().__init__()
        self.install_list = install_list

    def run(self):
        total = len(self.install_list)
        for index, program_id in enumerate(self.install_list):
            self.progress_signal.emit(f"[{index+1}/{total}] Kuruluyor: {program_id}...")
            
            try:
                # Winget komutu: Onay sormadan (-e --silent), tüm lisansları kabul ederek kur
                cmd = f"winget install --id {program_id} -e --silent --accept-package-agreements --accept-source-agreements"
                
                # subprocess ile komutu çalıştır (shell=True, cmd penceresi açılmasın diye creationflags eklenebilir)
                creationflags = 0x08000000 if os.name == 'nt' else 0
                subprocess.run(cmd, shell=True, check=True, creationflags=creationflags)
                
                self.progress_signal.emit(f"✅ {program_id} başarıyla kuruldu.")
            except subprocess.CalledProcessError:
                self.progress_signal.emit(f"❌ {program_id} kurulamadı (Hata).")
            except Exception as e:
                self.progress_signal.emit(f"❌ {program_id} hatası: {str(e)}")
        
        self.finished_signal.emit()

# --- ARAYÜZ ---
class ProgramsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.checkboxes = []
        self.programs_data = []
        
        self.load_data()
        self.init_ui()
        self.setLayout(self.layout)

    def load_data(self):
        # data/programs.json yolunu EXE uyumlu dinamik bul
        try:
            base_dir = get_base_path() # Helpers'dan gelen fonksiyon
            json_path = os.path.join(base_dir, 'data', 'programs.json')
            
            with open(json_path, 'r', encoding='utf-8') as f:
                self.programs_data = json.load(f)
        except Exception as e:
            print(f"JSON Yükleme Hatası: {e}")
            self.programs_data = []

    def init_ui(self):
        # 1. Başlık
        header_layout = QVBoxLayout()
        title = QLabel("Popüler Programlar (Winget)")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #3b82f6;")
        desc = QLabel("Resmi Winget kaynağını kullanarak en güncel sürümleri güvenle kurun.")
        desc.setStyleSheet("color: #94a3b8; margin-bottom: 10px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(desc)
        self.layout.addLayout(header_layout)

        # 2. Kaydırılabilir Alan (Scroll Area)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;") 
        
        # Grid Layout
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15) 
        grid_layout.setContentsMargins(5, 5, 5, 5)

        if not self.programs_data:
            grid_layout.addWidget(QLabel("Program listesi (data/programs.json) bulunamadı!"), 0, 0)
        else:
            row = 0
            col = 0
            max_columns = 3 

            for prog in self.programs_data:
                # Kart Yapısı
                card = QFrame()
                card.setProperty("class", "card")
                card.setMinimumHeight(100)
                card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(15, 15, 15, 15)
                
                # Checkbox
                cb = QCheckBox(prog.get("name", "Bilinmeyen"))
                cb.setStyleSheet("font-weight: bold; font-size: 14px; border: none; background: transparent;")
                cb.setProperty("winget_id", prog.get("id"))
                self.checkboxes.append(cb)
                
                # Açıklama
                desc_text = prog.get("description", "Açıklama yok.")
                desc_lbl = QLabel(desc_text)
                desc_lbl.setWordWrap(True)
                desc_lbl.setStyleSheet("color: #94a3b8; font-size: 11px; border: none; background: transparent;")
                
                card_layout.addWidget(cb)
                card_layout.addWidget(desc_lbl)
                card_layout.addStretch() 
                
                grid_layout.addWidget(card, row, col)
                
                col += 1
                if col >= max_columns:
                    col = 0
                    row += 1

        scroll_widget.setLayout(grid_layout)
        scroll_area.setWidget(scroll_widget)
        self.layout.addWidget(scroll_area)

        # 3. Durum Çubuğu (Log)
        self.lbl_status = QLabel("Hazır")
        self.lbl_status.setStyleSheet("color: #10b981; font-weight: bold; margin-left: 5px;")
        self.layout.addWidget(self.lbl_status)

        # 4. Alt Butonlar
        action_bar = QFrame()
        action_bar.setStyleSheet("background-color: transparent; border-top: 1px solid #334155; margin-top: 5px;")
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(0, 10, 0, 0)
        
        self.btn_select_all = QPushButton("Tümünü Seç")
        self.btn_select_all.setProperty("class", "secondary")
        self.btn_select_all.setFixedWidth(120)
        self.btn_select_all.clicked.connect(self.toggle_select_all)
        
        self.btn_install = QPushButton("Seçilenleri Kur")
        self.btn_install.setProperty("class", "success")
        self.btn_install.setMinimumHeight(45)
        self.btn_install.setMinimumWidth(200)
        self.btn_install.clicked.connect(self.install_selected)
        
        action_layout.addWidget(self.btn_select_all)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_install)
        
        self.layout.addWidget(action_bar)

    def toggle_select_all(self):
        any_unchecked = any(not cb.isChecked() for cb in self.checkboxes)
        for cb in self.checkboxes:
            cb.setChecked(any_unchecked)

    def install_selected(self):
        to_install = []
        for cb in self.checkboxes:
            if cb.isChecked():
                to_install.append(cb.property("winget_id"))
        
        if not to_install:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir program seçin.")
            return

        confirm = QMessageBox.question(self, "Onay", f"{len(to_install)} program kurulacak. Onaylıyor musunuz?", 
                                       QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            self.btn_install.setEnabled(False)
            self.btn_select_all.setEnabled(False)
            self.lbl_status.setText("Kurulum başlatılıyor...")
            
            # Thread Başlatma
            self.thread = InstallerThread(to_install)
            self.thread.progress_signal.connect(self.update_status)
            self.thread.finished_signal.connect(self.on_install_finished)
            self.thread.start()

    def update_status(self, message):
        self.lbl_status.setText(message)

    def on_install_finished(self):
        self.lbl_status.setText("Tüm işlemler tamamlandı.")
        self.btn_install.setEnabled(True)
        self.btn_select_all.setEnabled(True)
        QMessageBox.information(self, "Başarılı", "Seçilen programların kurulumu tamamlandı!")