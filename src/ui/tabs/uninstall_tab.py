import winreg
import subprocess
import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QPushButton, 
                             QMessageBox, QLabel, QLineEdit, QHBoxLayout, QFrame)

class UninstallTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.init_ui()
        self.setLayout(self.layout)
        # Sekme ilk açıldığında listeyi doldur
        self.refresh_list()

    def init_ui(self):
        # Başlık
        title = QLabel("Yüklü Programları Kaldır")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ef4444;") # Kırmızı başlık
        self.layout.addWidget(title)

        # Arama
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Program ara...")
        self.search_input.textChanged.connect(self.filter_list)
        self.layout.addWidget(self.search_input)

        # Liste
        self.list_widget = QListWidget()
        # Tema dosyasındaki stil otomatik uygulanır
        self.layout.addWidget(self.list_widget)

        # Butonlar
        action_bar = QFrame()
        action_bar.setStyleSheet("background-color: transparent; border-top: 1px solid #334155; margin-top: 10px;")
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(0, 10, 0, 0)
        
        self.btn_refresh = QPushButton("Listeyi Yenile")
        self.btn_refresh.setProperty("class", "secondary")
        self.btn_refresh.clicked.connect(self.refresh_list)
        
        self.btn_uninstall = QPushButton("Seçili Programı Kaldır")
        self.btn_uninstall.setProperty("class", "danger")
        self.btn_uninstall.setMinimumHeight(45)
        self.btn_uninstall.clicked.connect(self.uninstall_selected)
        
        action_layout.addWidget(self.btn_refresh)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_uninstall)
        
        self.layout.addWidget(action_bar)

    def get_installed_programs(self):
        """Windows Kayıt Defteri'nden yüklü programları çeker."""
        program_list = set()
        
        # Taranacak kayıt defteri yolları (Uninstall anahtarları)
        registry_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        
        # HKEY_LOCAL_MACHINE ve HKEY_CURRENT_USER köklerini tara
        hives = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
        
        for hive in hives:
            for path in registry_paths:
                try:
                    # Anahtarı aç (Sadece okuma izni yeterli)
                    # 64-bit sistemde 32-bit ve 64-bit görünümleri için KEY_WOW64 bayrakları gerekebilir
                    # Ancak basit okuma genellikle yeterlidir.
                    with winreg.OpenKey(hive, path) as key:
                        for i in range(winreg.QueryInfoKey(key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        # DisplayName değerini al
                                        name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                        if name:
                                            program_list.add(name)
                                    except OSError:
                                        pass # DisplayName yoksa geç
                            except OSError:
                                continue
                except OSError:
                    continue
                    
        return sorted(list(program_list))

    def refresh_list(self):
        self.list_widget.clear()
        self.list_widget.addItem("Listeleniyor... Lütfen bekleyin.")
        self.btn_refresh.setEnabled(False)
        
        # Arayüz donmasın diye processEvents (basit çözüm)
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()
        
        programs = self.get_installed_programs()
        
        self.list_widget.clear()
        if not programs:
            self.list_widget.addItem("Program bulunamadı veya erişim hatası.")
        else:
            self.list_widget.addItems(programs)
            
        self.btn_refresh.setEnabled(True)

    def filter_list(self):
        search_text = self.search_input.text().lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(search_text not in item.text().lower())

    def uninstall_selected(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Uyarı", "Lütfen kaldırılacak bir program seçin.")
            return
            
        program_name = current_item.text()
        
        confirm = QMessageBox.question(self, "Kaldırma Onayı", 
                                       f"'{program_name}' programını kaldırmak istediğinize emin misiniz?\n\n"
                                       "Not: Bu işlem Winget kullanılarak denenecektir.",
                                       QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            # Winget uninstall komutunu çalıştır
            # Konsol penceresini kullanıcıya gösteriyoruz ki süreci görsün
            cmd = f'winget uninstall --name "{program_name}"'
            
            # Start cmd /k ile komut satırını açık tutuyoruz
            full_cmd = f'start cmd /k "echo {program_name} kaldiriliyor... && {cmd} && echo. && echo Islem tamamlandi, pencereyi kapatabilirsiniz."'
            
            try:
                subprocess.run(full_cmd, shell=True)
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"İşlem başlatılamadı: {e}")