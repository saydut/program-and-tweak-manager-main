import json
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QScrollArea, 
                             QPushButton, QHBoxLayout, QMessageBox, QLabel, 
                             QGridLayout, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt

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
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        json_path = os.path.join(base_dir, 'data', 'programs.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.programs_data = json.load(f)
        except FileNotFoundError:
            self.programs_data = []

    def init_ui(self):
        # Başlık ve Açıklama
        header_layout = QVBoxLayout()
        title = QLabel("Kurulacak Programları Seçin (Winget)")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #3b82f6;")
        desc = QLabel("Aşağıdaki listeden kurmak istediğiniz programları seçin ve 'Kur' butonuna basın.")
        desc.setStyleSheet("color: #94a3b8; margin-bottom: 10px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(desc)
        self.layout.addLayout(header_layout)

        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;") 
        
        # Grid Layout (Izgara)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15) 
        grid_layout.setContentsMargins(5, 5, 5, 5)

        if not self.programs_data:
            grid_layout.addWidget(QLabel("Program listesi yüklenemedi!"), 0, 0)
        else:
            row = 0
            col = 0
            # 3 sütunlu yapı, geniş ekranlarda daha iyi
            max_columns = 3 

            for prog in self.programs_data:
                # KART (Frame)
                card = QFrame()
                card.setProperty("class", "card") # Tema dosyasındaki stili uygula
                card.setMinimumHeight(100)
                card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                
                # Kart İç Düzeni
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(15, 15, 15, 15)
                
                # Checkbox (Başlık)
                cb = QCheckBox(prog.get("name", "Bilinmeyen"))
                cb.setStyleSheet("font-weight: bold; font-size: 14px; border: none; background: transparent;")
                cb.setProperty("winget_id", prog.get("id"))
                self.checkboxes.append(cb)
                
                # Açıklama (Alt metin)
                desc_text = prog.get("description", "Açıklama yok.")
                desc_lbl = QLabel(desc_text)
                desc_lbl.setWordWrap(True) # ÖNEMLİ: Metin sığmazsa aşağı kayar
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

        # Alt Buton Paneli
        action_bar = QFrame()
        action_bar.setStyleSheet("background-color: transparent; border-top: 1px solid #334155; margin-top: 10px;")
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

        confirm = QMessageBox.question(self, "Onay", f"{len(to_install)} adet program kurulacak. Onaylıyor musunuz?", 
                                       QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            cmd = f"winget install {' '.join(to_install)}"
            print(f"Komut: {cmd}")
            QMessageBox.information(self, "Bilgi", "Kurulum işlemi başlatılıyor...")