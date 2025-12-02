import sys
import os
import ctypes
import subprocess

def is_admin():
    """Programın yönetici olarak çalışıp çalışmadığını kontrol eder."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_base_path():
    """
    Programın çalıştığı ana dizini döndürür.
    PyInstaller ile derlendiğinde geçici klasörü (sys._MEIPASS),
    normal çalışırken proje ana dizinini verir.
    """
    if getattr(sys, 'frozen', False):
        # .exe içinde çalışıyorsa
        return sys._MEIPASS
    else:
        # Normal .py olarak çalışıyorsa (src/utils/helpers.py -> ../../)
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_restore_point(description="Saydut Program Yoneticisi"):
    """
    Windows Sistem Geri Yükleme Noktası oluşturur.
    PowerShell kullanır çünkü en güvenilir yöntem budur.
    """
    if not is_admin():
        return False, "Yönetici izni gerekli."

    try:
        # PowerShell komutu: Checkpoint-Computer
        # RestorePointType: MODIFY_SETTINGS (Ayarları değiştirmeden önce)
        cmd = [
            "powershell", 
            "-Command", 
            f'Checkpoint-Computer -Description "{description}" -RestorePointType "MODIFY_SETTINGS"'
        ]
        
        # Konsol penceresi açılmadan arka planda çalıştır (CREATE_NO_WINDOW)
        creationflags = 0x08000000 if sys.platform == "win32" else 0
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            creationflags=creationflags
        )

        if result.returncode == 0:
            return True, "Geri yükleme noktası başarıyla oluşturuldu."
        else:
            # Hata varsa PowerShell çıktısını döndür
            err_msg = result.stderr.strip() or "Bilinmeyen bir hata oluştu."
            return False, f"Hata: {err_msg}"

    except Exception as e:
        return False, str(e)

def run_powershell(command):
    """Verilen PowerShell komutunu çalıştırır."""
    try:
        creationflags = 0x08000000 if sys.platform == "win32" else 0
        subprocess.run(["powershell", "-Command", command], creationflags=creationflags)
        return True
    except:
        return False

def check_and_request_admin():
    """
    Program yönetici değilse, yönetici olarak yeniden başlatır.
    """
    if is_admin():
        return True

    # Yönetici değilse, yeniden başlatmayı dene
    try:
        if getattr(sys, 'frozen', False):
            # Eğer .exe ise
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        else:
            # Eğer .py script ise
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        
        sys.exit(0) # Eski (yetkisiz) programı kapat
    except Exception as e:
        print(f"Yönetici izni alınamadı: {e}")
        return False