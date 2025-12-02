from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QAction, QMenu
from PyQt5.QtGui import QIcon
import json
import os

from src.ui.tabs.programs_tab import ProgramsTab
from src.ui.tabs.tweaks_tab import TweaksTab
from src.ui.tabs.system_tab import SystemTab
from src.ui.tabs.chocolatey_tab import ChocolateyTab
from src.ui.tabs.uninstall_tab import UninstallTab
from src.ui.tabs.updates_tab import UpdatesTab
from src.utils.updater import Updater
from src.ui.theme import DARK_THEME_STYLESHEET, LIGHT_THEME_STYLESHEET
from src.utils.helpers import get_base_path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Saydut Program Yöneticisi v2.0")
        self.setGeometry(100, 100, 1100, 750) 
        
        self.config = self.load_config()
        self.current_version = self.config.get("version", "2.0.0")
        
        self.current_theme = self.config.get("theme", "dark")
        self.apply_theme(self.current_theme)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.setCentralWidget(self.tabs)
        
        self.create_menus()
        self.setup_tabs()

    def load_config(self):
        try:
            base_dir = get_base_path()
            config_path = os.path.join(base_dir, 'config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def save_config(self):
        try:
            import sys
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = get_base_path()
                
            config_path = os.path.join(base_dir, 'config.json')
            current_conf = self.load_config()
            current_conf.update(self.config)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(current_conf, f, indent=4)
        except Exception as e:
            print(f"Config kaydedilemedi: {e}")

    def apply_theme(self, theme_name):
        if theme_name == "light":
            self.setStyleSheet(LIGHT_THEME_STYLESHEET)
            self.current_theme = "light"
        else:
            self.setStyleSheet(DARK_THEME_STYLESHEET)
            self.current_theme = "dark"
        
        self.config["theme"] = self.current_theme
        self.save_config()

    def create_menus(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('Dosya')
        exit_action = QAction('Çıkış', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        view_menu = menubar.addMenu('Görünüm')
        theme_menu = view_menu.addMenu('Tema Seç')
        
        dark_action = QAction('Karanlık Tema', self)
        dark_action.triggered.connect(lambda: self.apply_theme("dark"))
        theme_menu.addAction(dark_action)
        
        light_action = QAction('Aydınlık Tema', self)
        light_action.triggered.connect(lambda: self.apply_theme("light"))
        theme_menu.addAction(light_action)

        help_menu = menubar.addMenu('Yardım')
        update_action = QAction('Güncellemeleri Kontrol Et', self)
        update_action.triggered.connect(self.check_updates)
        help_menu.addAction(update_action)
        
        about_action = QAction('Hakkında', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_tabs(self):
        self.programs_tab = ProgramsTab()
        self.tabs.addTab(self.programs_tab, "Programlar")
        
        self.choco_tab = ChocolateyTab()
        self.tabs.addTab(self.choco_tab, "Chocolatey")
        
        self.updates_tab = UpdatesTab()
        self.tabs.addTab(self.updates_tab, "Güncelle")
        
        self.uninstall_tab = UninstallTab()
        self.tabs.addTab(self.uninstall_tab, "Kaldır")
        
        self.tweaks_tab = TweaksTab()
        self.tabs.addTab(self.tweaks_tab, "Tweakler")
        
        self.system_tab = SystemTab()
        self.tabs.addTab(self.system_tab, "Sistem")

    def check_updates(self):
        remote_url = self.config.get("remote_version_url", "")
        if not remote_url:
            QMessageBox.warning(self, "Hata", "Config dosyasında güncelleme URL'si bulunamadı!")
            return

        updater = Updater(self.current_version, remote_json_url=remote_url)
        has_update, new_ver, notes = updater.check_for_updates()
        
        if has_update:
            msg = f"Yeni sürüm mevcut: {new_ver}\n\nDeğişiklikler:\n{notes}\n\nŞimdi indirip güncellemek ister misiniz?"
            reply = QMessageBox.question(self, "Güncelleme Mevcut", msg, QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                QMessageBox.information(self, "İndiriliyor", "Güncelleme indiriliyor, program kapanıp yeniden açılacak...")
                success, message = updater.download_and_install()
                if not success:
                    QMessageBox.critical(self, "Hata", message)
        else:
            # HATA YAKALAMA KISMI BURASI
            if new_ver is None:
                # Eğer versiyon None dönmüşse bir hata olmuştur (404, Connection Error vb.)
                # Eğer notes boş gelirse diye varsayılan bir mesaj ekleyelim
                hata_mesaji = notes if notes else "Bilinmeyen bir ağ hatası oluştu."
                QMessageBox.warning(self, "Bağlantı Hatası", f"Sunucuya bağlanırken hata oluştu:\n{hata_mesaji}")
            else:
                QMessageBox.information(self, "Bilgi", f"Programınız güncel ({self.current_version}).")

    def show_about(self):
        QMessageBox.about(self, "Hakkında", 
                          f"Saydut Program Yöneticisi\nSürüm: {self.current_version}\n\nModern ve Açık Kaynaklı Yönetim Aracı")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Çıkış', 'Programdan çıkmak istediğinize emin misiniz?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()