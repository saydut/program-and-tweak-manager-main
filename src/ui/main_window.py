from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QAction
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Saydut Program Yöneticisi v2.0")
        self.setGeometry(100, 100, 900, 650)
        
        self.config = self.load_config()
        self.current_version = self.config.get("version", "1.0.0")
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.create_menus()
        self.setup_tabs()

    def load_config(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(base_dir, 'config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('Dosya')
        exit_action = QAction('Çıkış', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        help_menu = menubar.addMenu('Yardım')
        update_action = QAction('Güncellemeleri Kontrol Et', self)
        update_action.triggered.connect(self.check_updates)
        help_menu.addAction(update_action)
        
        about_action = QAction('Hakkında', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_tabs(self):
        # 1. Programlar Sekmesi (Winget)
        self.programs_tab = ProgramsTab()
        self.tabs.addTab(self.programs_tab, "Programlar")
        
        # 2. Chocolatey Sekmesi
        self.choco_tab = ChocolateyTab()
        self.tabs.addTab(self.choco_tab, "Chocolatey")
        
        # 3. Program Kaldırma
        self.uninstall_tab = UninstallTab()
        self.tabs.addTab(self.uninstall_tab, "Kaldır")
        
        # 4. Güncellemeler
        self.updates_tab = UpdatesTab()
        self.tabs.addTab(self.updates_tab, "Güncelle")
        
        # 5. Tweakler Sekmesi
        self.tweaks_tab = TweaksTab()
        self.tabs.addTab(self.tweaks_tab, "Tweakler")
        
        # 6. Sistem Bilgileri Sekmesi
        self.system_tab = SystemTab()
        self.tabs.addTab(self.system_tab, "Sistem")

    def check_updates(self):
        """
        Sunucudan güncelleme kontrolü yapar ve kullanıcıya sorar.
        """
        remote_url = self.config.get("remote_version_url", "")
        if not remote_url:
            QMessageBox.warning(self, "Hata", "Config dosyasında güncelleme URL'si bulunamadı!")
            return

        updater = Updater(self.current_version, remote_url)
        
        # Updater'dan bilgi al
        has_update, new_ver, notes = updater.check_for_updates()
        
        if has_update:
            # Kullanıcıya detaylı bilgi verelim
            msg = (f"📢 <b>YENİ GÜNCELLEME MEVCUT!</b><br><br>"
                   f"Eski Sürüm: {self.current_version}<br>"
                   f"Yeni Sürüm: <b>{new_ver}</b><br><br>"
                   f"<b>Yenilikler:</b><br>{notes}<br><br>"
                   f"İndirip otomatik olarak güncellemek ister misiniz?<br>"
                   f"<i>(Program otomatik olarak kapanıp açılacaktır)</i>")
            
            reply = QMessageBox.question(self, "Güncelleme Yöneticisi", msg, 
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                QMessageBox.information(self, "İndirme Başladı", 
                                      "Güncelleme arka planda indiriliyor.\n"
                                      "Lütfen bekleyin, işlem bitince program yeniden başlayacak.")
                
                # İndirme işlemini başlat (Dönüş değeri: Başarılı mı?, Mesaj)
                success, status_msg = updater.download_and_install()
                
                if not success:
                    # Hata varsa (veya geliştirici modundaysak) uyar
                    QMessageBox.warning(self, "Güncelleme Başarısız", status_msg)
        else:
            QMessageBox.information(self, "Durum", f"Sisteminiz zaten güncel.\nMevcut Sürüm: {self.current_version}")

    def show_about(self):
        QMessageBox.about(self, "Hakkında", 
                          f"Saydut Program Yöneticisi\nSürüm: {self.current_version}\n\nProfesyonel Program Yönetim Aracı")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Çıkış', 'Programdan çıkmak istediğinize emin misiniz?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()