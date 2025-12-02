import sys
import os
import ctypes
from PyQt5.QtWidgets import QApplication
from src.utils.helpers import is_admin, restart_as_admin, is_dark_mode
from src.ui.main_window import MainWindow
import qdarkstyle  # Eğer yüklüyse kullanacağız

def hide_console():
    """Program çalıştığında arkadaki siyah CMD penceresini gizler."""
    try:
        # Konsol penceresinin kimliğini al
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        # Eğer bir konsol varsa (hwnd != 0), onu gizle (0 = SW_HIDE)
        if hwnd != 0:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass

def main():
    # 1. Konsolu Gizle (En başta yapıyoruz ki görünmesin)
    hide_console()

    # 2. Admin Kontrolü
    if not is_admin():
        # Admin izni yoksa iste ve yeniden başlat
        restart_as_admin()
        sys.exit()

    # 3. Uygulama Başlatma
    app = QApplication(sys.argv)
    
    # 4. Tema Ayarları
    # Windows karanlık moddaysa qdarkstyle uygula
    if is_dark_mode():
        try:
            app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
        except ImportError:
            # print("qdarkstyle modülü bulunamadı, varsayılan tema kullanılıyor.")
            pass

    # 5. Ana Pencereyi Göster
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()