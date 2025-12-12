import sys
import os
import ctypes
import customtkinter as ctk
from interface import MainWindow
from logic import setup_logging, check_and_request_admin

# Windows görev çubuğu ikonunu düzeltme
try:
    myappid = 'saydut.programyoneticisi.v3.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

if __name__ == "__main__":
    # 1. Loglama
    setup_logging()

    # 2. Admin Kontrolü (İstersen aktif edebilirsin, geliştirme aşamasında kapalı kalabilir)
    # if not check_and_request_admin():
    #     sys.exit()

    # 3. Arayüz Ayarları
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")

    # 4. Başlat
    app = MainWindow()
    app.mainloop()