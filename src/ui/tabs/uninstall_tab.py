import winreg
import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QPushButton, 
                             QMessageBox, QLabel, QLineEdit, QHBoxLayout)

class UninstallTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.init_ui()
        self.setLayout(self.layout)
        
        # Sekme ilk açıldığında listeyi doldur
        self.refresh_list()

    def init_ui(self):
        title = QLabel("Yüklü Programları Kaldır")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(title)

        # Arama Çubuğu
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Program ara...")
        self.search_input.textChanged.connect(self.filter_list)
        self.layout.addWidget(self.search_input)

        # Liste
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        # Butonlar
        btn_layout = QHBoxLayout()
        
        self.btn_refresh = QPushButton("Listeyi Yenile")
        self.btn_refresh.clicked.connect(self.refresh_list)
        btn_layout.addWidget(self.btn_refresh)
        
        self.btn_uninstall = QPushButton("Seçili Programı Kaldır")
        self.btn_uninstall.setStyleSheet("background-color: #d32f2f; color: white;")
        self.btn_uninstall.clicked.connect(self.uninstall_selected)
        btn_layout.addWidget(self.btn_uninstall)
        
        self.layout.addLayout(btn_layout)

    def get_installed_programs(self):
        """Windows Kayıt Defterinden (Registry) program listesini çeker."""
        program_set = set()
        
        # Taranacak yollar
        registry_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        
        # Ana kökler (Hem makine geneli hem kullanıcıya özel)
        roots = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
        
        # Erişim modları: Standart, 64-bit zorla, 32-bit zorla
        # Bu sayede sistem ne olursa olsun tüm anahtarları görmeye çalışırız
        access_modes = [
            winreg.KEY_READ, 
            winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
            winreg.KEY_READ | winreg.KEY_WOW64_32KEY
        ]

        for root in roots:
            for path in registry_paths:
                for access_mode in access_modes:
                    try:
                        with winreg.OpenKey(root, path, 0, access_mode) as key:
                            # Alt anahtar sayısını al
                            num_subkeys = winreg.QueryInfoKey(key)[0]
                            for i in range(num_subkeys):
                                try:
                                    subkey_name = winreg.EnumKey(key, i)
                                    # HATA DÜZELTİLDİ: Artık tam yol yerine sadece subkey_name kullanıyoruz
                                    # çünkü 'key' zaten o dizini işaret ediyor.
                                    with winreg.OpenKey(key, subkey_name, 0, access_mode) as subkey:
                                        try:
                                            name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                                            if name and name.strip():
                                                program_set.add(name)
                                        except FileNotFoundError:
                                            pass # DisplayName yoksa geç
                                except Exception:
                                    continue
                    except Exception:
                        continue # Erişim hatası olursa diğer moda geç
        
        return sorted(list(program_set))

    def refresh_list(self):
        self.list_widget.clear()
        programs = self.get_installed_programs()
        if not programs:
            self.list_widget.addItem("Hiçbir program bulunamadı veya erişim reddedildi.")
        else:
            self.list_widget.addItems(programs)
        
    def filter_list(self):
        search_text = self.search_input.text().lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(search_text not in item.text().lower())

    def uninstall_selected(self):
        current_item = self.list_widget.currentItem()
        if not current_item or current_item.text() == "Hiçbir program bulunamadı veya erişim reddedildi.":
            QMessageBox.warning(self, "Uyarı", "Lütfen kaldırılacak geçerli bir program seçin.")
            return

        program_name = current_item.text()
        
        confirm = QMessageBox.question(self, "Onay", f"'{program_name}' programını kaldırmak istediğinize emin misiniz?\n(Bu işlem Winget kullanılarak denenecek)", 
                                       QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            # Kullanıcı görsün diye yeni pencerede işlemi başlatıyoruz
            cmd = f'winget uninstall --name "{program_name}"'
            full_cmd = f'start cmd /k "echo {program_name} kaldiriliyor... && {cmd} && echo. && echo Islem bitti, pencereyi kapatabilirsiniz."'
            
            try:
                subprocess.run(full_cmd, shell=True)
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"İşlem başlatılamadı: {e}")