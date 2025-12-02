import sys
import os
import ctypes
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from src.ui.main_window import MainWindow
from src.utils.logger import setup_logging
from src.utils.helpers import check_and_request_admin

def main():
    # 1. Loglamayı Başlat
    setup_logging()

    # 2. Admin Kontrolü (Yönetici değilse ister ve yeniden başlar)
    check_and_request_admin()

    # 3. Windows Taskbar İkon Düzeltmesi
    # Görev çubuğunda python ikonu değil, kendi ikonun görünsün
    myappid = 'saydut.programyoneticisi.v2.0'
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    # 4. Uygulamayı Başlat
    app = QApplication(sys.argv)
    
    # 5. Uygulama İkonunu Ayarla
    app_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "favicon.ico")
    if os.path.exists(app_icon_path):
        app.setWindowIcon(QIcon(app_icon_path))

    # 6. Stil (Sadece Fusion kullanıyoruz, ekstra renk kodlarını kaldırdık)
    app.setStyle("Fusion")

    # Pencereyi oluştur ve göster
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()