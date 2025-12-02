# Bu dosya uygulamanın tüm görsel stillerini içerir.
# Renk paleti: Modern Dark (VS Code / Tailwind tarzı) ve Light Tema

# --- KARANLIK TEMA (DEFAULT) ---
DARK_THEME_STYLESHEET = """
/* Genel Pencere Ayarları */
QMainWindow, QWidget {
    background-color: #0f172a; /* Çok Koyu Lacivert */
    color: #e2e8f0; /* Açık Gri Yazı */
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

/* ScrollBar (Kaydırma Çubuğu) */
QScrollBar:vertical {
    border: none;
    background: #1e293b;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #475569;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Tab Widget (Sekmeler) */
QTabWidget::pane {
    border: 1px solid #334155;
    background: #1e293b;
    border-radius: 8px;
    margin-top: 15px; /* Sekmeler ile içerik arası boşluk */
}

QTabWidget::tab-bar {
    left: 5px; /* İlk sekme için sol boşluk */
}

/* SEKME TASARIMI (Burayı Genişlettik) */
QTabBar::tab {
    background: #0f172a;
    color: #94a3b8;
    
    /* Yükseklik ve Genişlik Ayarları */
    min-width: 130px; /* Sekmelerin minimum genişliği */
    min-height: 35px; /* Sekmelerin yüksekliği */
    padding: 5px 15px; /* Metin çevresindeki boşluk */
    
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 5px; /* Sekmeler arası boşluk */
    font-weight: bold;
    font-size: 15px; /* Sekme yazı boyutu */
    border: 1px solid transparent;
}

QTabBar::tab:selected {
    background: #1e293b;
    color: #3b82f6; /* Parlak Mavi */
    border-bottom: 3px solid #3b82f6; /* Alt çizgi kalınlığı */
}

QTabBar::tab:hover {
    background: #1e293b;
    color: #ffffff;
}

/* Butonlar */
QPushButton {
    background-color: #3b82f6;
    color: white;
    border: 1px solid #2563eb;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: bold;
    min-height: 30px;
}

QPushButton:hover {
    background-color: #2563eb;
    border-color: #1d4ed8;
}

QPushButton:pressed {
    background-color: #1d4ed8;
}

QPushButton:disabled {
    background-color: #334155;
    color: #64748b;
    border: 1px solid #334155;
}

/* Kırmızı Buton (Tehlikeli İşlemler) */
QPushButton[class="danger"] {
    background-color: #ef4444;
    border: 1px solid #dc2626;
}
QPushButton[class="danger"]:hover {
    background-color: #dc2626;
}

/* Yeşil Buton (Onay/Başarılı) */
QPushButton[class="success"] {
    background-color: #10b981;
    border: 1px solid #059669;
}
QPushButton[class="success"]:hover {
    background-color: #059669;
}

/* Gri Buton (Nötr) */
QPushButton[class="secondary"] {
    background-color: #475569;
    border: 1px solid #334155;
}
QPushButton[class="secondary"]:hover {
    background-color: #334155;
}

/* Input ve Arama Kutuları */
QLineEdit, QTextEdit {
    background-color: #1e293b;
    border: 1px solid #334155;
    color: white;
    padding: 8px;
    border-radius: 6px;
}
QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #3b82f6;
}

/* Checkbox */
QCheckBox {
    spacing: 8px;
    color: #e2e8f0;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #475569;
    background: #0f172a;
}
QCheckBox::indicator:checked {
    background-color: #3b82f6;
    border-color: #3b82f6;
}

/* Tablolar */
QTableWidget, QListWidget {
    background-color: #1e293b;
    border: 1px solid #334155;
    gridline-color: #334155;
    border-radius: 8px;
    alternate-background-color: #252f40; /* Satır arası renk */
}
QTableWidget::item, QListWidget::item {
    padding: 5px;
}
QTableWidget::item:selected, QListWidget::item:selected {
    background-color: #3b82f6;
    color: white;
}
QHeaderView::section {
    background-color: #0f172a;
    color: #cbd5e1;
    padding: 8px;
    border: none;
    font-weight: bold;
}

/* KART TASARIMI (QFrame) */
QFrame[class="card"] {
    background-color: #1e293b;
    border-radius: 12px;
    border: 1px solid #334155;
}
QFrame[class="card"]:hover {
    border: 1px solid #3b82f6;
    background-color: #263345;
}

/* Menü Bar */
QMenuBar {
    background-color: #0f172a;
    color: #e2e8f0;
    padding: 5px;
}
QMenuBar::item {
    padding: 5px 10px;
    background-color: transparent;
}
QMenuBar::item:selected {
    background-color: #1e293b;
    border-radius: 4px;
}
QMenu {
    background-color: #1e293b;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 5px;
}
QMenu::item {
    padding: 5px 20px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #3b82f6;
}
"""

# --- AYDINLIK TEMA (LIGHT) ---
LIGHT_THEME_STYLESHEET = """
/* Genel Pencere Ayarları */
QMainWindow, QWidget {
    background-color: #f8fafc;
    color: #1e293b;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

/* ScrollBar */
QScrollBar:vertical {
    border: none;
    background: #e2e8f0;
    width: 10px;
}
QScrollBar::handle:vertical {
    background: #94a3b8;
    border-radius: 5px;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #cbd5e1;
    background: #ffffff;
    border-radius: 8px;
    margin-top: 15px;
}

QTabWidget::tab-bar {
    left: 5px;
}

/* SEKME TASARIMI (LIGHT) */
QTabBar::tab {
    background: #f1f5f9;
    color: #64748b;
    
    /* Yükseklik ve Genişlik */
    min-width: 130px;
    min-height: 35px;
    padding: 5px 15px;
    
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 5px;
    font-weight: bold;
    font-size: 15px;
}

QTabBar::tab:selected {
    background: #ffffff;
    color: #2563eb;
    border-bottom: 3px solid #2563eb;
}

QTabBar::tab:hover {
    background: #e2e8f0;
    color: #1e293b;
}

/* Butonlar */
QPushButton {
    background-color: #2563eb;
    color: white;
    border: 1px solid #1d4ed8;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: bold;
    min-height: 30px;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:disabled {
    background-color: #cbd5e1;
    color: #94a3b8;
    border: 1px solid #cbd5e1;
}

/* Kırmızı Buton */
QPushButton[class="danger"] {
    background-color: #ef4444;
    border: 1px solid #dc2626;
}
QPushButton[class="danger"]:hover {
    background-color: #dc2626;
}

/* Yeşil Buton */
QPushButton[class="success"] {
    background-color: #10b981;
    border: 1px solid #059669;
}
QPushButton[class="success"]:hover {
    background-color: #059669;
}

/* Gri Buton (Nötr) */
QPushButton[class="secondary"] {
    background-color: #e2e8f0;
    border: 1px solid #cbd5e1;
    color: #475569;
}
QPushButton[class="secondary"]:hover {
    background-color: #cbd5e1;
}

/* Inputlar */
QLineEdit, QTextEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    color: #1e293b;
    padding: 8px;
    border-radius: 6px;
}
QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #2563eb;
}

/* Checkbox */
QCheckBox {
    spacing: 8px;
    color: #1e293b;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #cbd5e1;
    background: #ffffff;
}
QCheckBox::indicator:checked {
    background-color: #2563eb;
    border-color: #2563eb;
}

/* Tablolar */
QTableWidget, QListWidget {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    gridline-color: #e2e8f0;
    border-radius: 8px;
    alternate-background-color: #f8fafc;
}
QTableWidget::item:selected, QListWidget::item:selected {
    background-color: #2563eb;
    color: white;
}
QHeaderView::section {
    background-color: #f1f5f9;
    color: #475569;
    padding: 8px;
    border: none;
    font-weight: bold;
}

/* KART TASARIMI */
QFrame[class="card"] {
    background-color: #ffffff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}
QFrame[class="card"]:hover {
    border: 1px solid #2563eb;
    background-color: #f8fafc;
}

/* Menü Bar */
QMenuBar {
    background-color: #ffffff;
    color: #1e293b;
    padding: 5px;
}
QMenuBar::item {
    padding: 5px 10px;
    background-color: transparent;
}
QMenuBar::item:selected {
    background-color: #f1f5f9;
    border-radius: 4px;
}
QMenu {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 5px;
}
QMenu::item {
    padding: 5px 20px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #eff6ff; 
}
"""