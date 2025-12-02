import json
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QCheckBox, QMessageBox, QHBoxLayout, QScrollArea, 
                             QGridLayout, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from src.utils.helpers import create_restore_point
from src.core.tweaker import Tweaker  # <--- Tweaker sınıfını import ettik

class TweakRunnerThread(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, tweaks):
        super().__init__()
        self.tweaks = tweaks
        self.tweaker = Tweaker() # <--- Tweaker nesnesi oluşturduk

    def run(self):
        total = len(self.tweaks)
        for index, tweak in enumerate(self.tweaks):
            name = tweak.get('name', 'Bilinmeyen İşlem')
            self.log_signal.emit(f"[{index+1}/{total}] Uygulanıyor: {name}...")
            
            # Tweaker sınıfındaki apply_tweak fonksiyonunu kullanıyoruz
            success = self.tweaker.apply_tweak(tweak)
            
            if success:
                self.log_signal.emit(f"✅ {name} başarıyla uygulandı.")
            else:
                self.log_signal.emit(f"❌ {name} sırasında hata oluştu.")
                
        self.finished_signal.emit()

class TweaksTab(QWidget):
    def __init__(self):
        super().__init__()
        self.tweaks_data = self.load_tweaks()
        self.checkboxes = [] 
        self.init_ui()

    def load_tweaks(self):
        try:
            # src/ui/tabs/tweaks_tab.py -> ../../../data/tweaks.json
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            json_path = os.path.join(base_dir, 'data', 'tweaks.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Tweak dosyası okunamadı: {e}")
            return []

    def init_ui(self):
        layout = QVBoxLayout()

        # Üst Bilgi
        info_title = QLabel("Sistem İyileştirmeleri (Tweaks)")
        info_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #3b82f6;")
        
        info_desc = QLabel("Sistem performansını artırmak için aşağıdaki ayarları kullanabilirsiniz.\n"
                           "DİKKAT: İşlem öncesi otomatik olarak Sistem Geri Yükleme Noktası oluşturulacaktır.")
        info_desc.setStyleSheet("color: #94a3b8; margin-bottom: 10px;")
        
        layout.addWidget(info_title)
        layout.addWidget(info_desc)

        # Scroll Area & Grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(5, 5, 5, 5)

        row = 0
        col = 0
        max_columns = 2 

        if not self.tweaks_data:
             grid_layout.addWidget(QLabel("Tweak verisi bulunamadı! data/tweaks.json dosyasını kontrol edin."), 0, 0)
        else:
            for tweak in self.tweaks_data:
                # KART YAPISI
                card = QFrame()
                card.setProperty("class", "card")
                card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(15, 15, 15, 15)
                
                # Checkbox
                cb = QCheckBox(tweak.get('name', 'Bilinmeyen'))
                cb.setStyleSheet("font-weight: bold; font-size: 15px; border: none; background: transparent;")
                # Tüm tweak verisini checkbox'a özellik olarak ekliyoruz
                cb.setProperty("tweak_data", tweak)
                self.checkboxes.append(cb)
                
                # Açıklama
                desc = QLabel(tweak.get('description', ''))
                desc.setWordWrap(True)
                desc.setStyleSheet("color: #94a3b8; font-size: 12px; border: none; background: transparent;")
                
                # Tip Bilgisi
                t_type = tweak.get('type', 'script')
                type_text = "Script (PowerShell)"
                if t_type == "external_exe": type_text = "İndir ve Çalıştır (EXE)"
                elif t_type == "external_zip": type_text = "İndir ve Çalıştır (ZIP)"
                elif t_type == "local_exe": type_text = "Dahili Araç"
                elif t_type == "winget": type_text = "Winget Kurulumu"

                type_lbl = QLabel(f"Tür: {type_text}")
                type_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-style: italic; border: none; background: transparent;")
                type_lbl.setAlignment(Qt.AlignRight)

                card_layout.addWidget(cb)
                card_layout.addWidget(desc)
                card_layout.addWidget(type_lbl)
                
                grid_layout.addWidget(card, row, col)
                
                col += 1
                if col >= max_columns:
                    col = 0
                    row += 1

        scroll_widget.setLayout(grid_layout)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Durum Çubuğu
        self.lbl_status = QLabel("Hazır")
        self.lbl_status.setStyleSheet("color: #64748b; font-weight: bold; margin-top: 5px;")
        layout.addWidget(self.lbl_status)

        # Alt Buton Paneli
        action_bar = QFrame()
        action_bar.setStyleSheet("background-color: transparent; border-top: 1px solid #334155; margin-top: 5px;")
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(0, 10, 0, 0)

        self.btn_select_all = QPushButton("Tümünü Seç")
        self.btn_select_all.setFixedWidth(120)
        self.btn_select_all.setProperty("class", "secondary")
        self.btn_select_all.clicked.connect(self.toggle_select_all)

        self.btn_apply = QPushButton("Seçilenleri Uygula")
        self.btn_apply.setProperty("class", "danger")
        self.btn_apply.setMinimumHeight(45)
        self.btn_apply.setMinimumWidth(200)
        self.btn_apply.clicked.connect(self.start_apply_process)
        
        action_layout.addWidget(self.btn_select_all)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_apply)

        layout.addWidget(action_bar)
        self.setLayout(layout)

    def toggle_select_all(self):
        any_unchecked = any(not cb.isChecked() for cb in self.checkboxes)
        for cb in self.checkboxes:
            cb.setChecked(any_unchecked)

    def start_apply_process(self):
        selected_tweaks = []
        for cb in self.checkboxes:
            if cb.isChecked():
                selected_tweaks.append(cb.property("tweak_data"))

        if not selected_tweaks:
            QMessageBox.warning(self, "Uyarı", "Lütfen uygulanacak en az bir ayar seçin.")
            return

        reply = QMessageBox.question(self, "Güvenlik Önlemi", 
                                   f"{len(selected_tweaks)} adet sistem ayarı değiştirilecek.\n\n"
                                   "SİSTEM GERİ YÜKLEME NOKTASI oluşturulsun mu?\n(Önerilir)",
                                   QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

        if reply == QMessageBox.Cancel:
            return

        if reply == QMessageBox.Yes:
            self.lbl_status.setText("⏳ Sistem Geri Yükleme Noktası oluşturuluyor...")
            # Not: Geri yükleme noktası oluşturma işlemi uzun sürebilir,
            # kullanıcı arayüzü donmasın diye bunu da thread içine almak daha iyi olurdu
            # ama şimdilik helper fonksiyonunu çağırıyoruz.
            success, msg = create_restore_point()
            if success:
                QMessageBox.information(self, "Bilgi", msg)
            else:
                QMessageBox.warning(self, "Uyarı", f"Geri yükleme noktası oluşturulamadı: {msg}\nİşleme devam ediliyor.")

        self.run_tweaks(selected_tweaks)

    def run_tweaks(self, tweaks):
        self.btn_apply.setEnabled(False)
        self.thread = TweakRunnerThread(tweaks)
        self.thread.log_signal.connect(self.lbl_status.setText)
        self.thread.finished_signal.connect(self.on_finished)
        self.thread.start()

    def on_finished(self):
        self.btn_apply.setEnabled(True)
        self.lbl_status.setText("İşlem tamamlandı.")
        QMessageBox.information(self, "Başarılı", "Seçilen işlemler tamamlandı.")