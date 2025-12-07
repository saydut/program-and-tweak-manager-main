import sys
import os
import ctypes
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from src.ui.main_window import MainWindow
from src.utils.logger import setup_logging
# get_base_path fonksiyonunu import etmeyi unutma!
from src.utils.helpers import check_and_request_admin, get_base_path

def main():
    # 1. Loglamayı Başlat
    setup_logging()

    # 2. Admin Kontrolü
    check_and_request_admin()

    # 3. Taskbar İkon Düzeltmesi (Windows için)
    myappid = 'saydut.programyoneticisi.v2.0'
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    # 4. Uygulamayı Başlat
    app = QApplication(sys.argv)
    
    # 5. Uygulama İkonunu Ayarla (EXE uyumlu hale getirildi)
    # get_base_path() sayesinde EXE içindeki geçici klasörden ikonu bulur.
    base_path = get_base_path()
    app_icon_path = os.path.join(base_path, "favicon.ico")
    
    if os.path.exists(app_icon_path):
        app.setWindowIcon(QIcon(app_icon_path))

    # 6. Stil
    app.setStyle("Fusion")

    # Pencereyi oluştur ve göster
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()