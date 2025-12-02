import sys
import ctypes
import os

def is_admin():
    """Kullanıcının yönetici olup olmadığını kontrol eder."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def restart_as_admin():
    """Programı yönetici haklarıyla yeniden başlatır."""
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )

def is_dark_mode():
    """Windows'un karanlık modda olup olmadığını kontrol eder."""
    try:
        registry_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
        value_name = 'AppsUseLightTheme'
        key = ctypes.c_void_p()

        result = ctypes.windll.advapi32.RegOpenKeyExW(
            ctypes.c_uint32(0x80000001),  # HKEY_CURRENT_USER
            ctypes.c_wchar_p(registry_path),
            0,
            0x20019,  # KEY_READ
            ctypes.byref(key)
        )

        if result != 0:
            return False

        value = ctypes.c_uint32()
        value_size = ctypes.c_uint32(ctypes.sizeof(value))
        ctypes.windll.advapi32.RegQueryValueExW(
            key, ctypes.c_wchar_p(value_name), None, None, ctypes.byref(value), ctypes.byref(value_size)
        )
        ctypes.windll.advapi32.RegCloseKey(key)
        
        # 0 = Dark, 1 = Light. Biz Dark mode mu diye bakıyoruz.
        return value.value == 0
    except Exception as e:
        print(f"Tema algılama hatası: {e}")
        return False