import os
import sys
import json
import logging
import psutil
import platform
import socket
import subprocess
import requests
import threading
import ctypes
import winreg
from datetime import datetime

# --- YARDIMCI FONKSİYONLAR ---

def get_base_path():
    """Çalışma dizinini bulur (EXE veya .py)"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def setup_logging():
    log_dir = os.path.join(get_base_path(), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y-%m-%d')}.txt")
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_and_request_admin():
    if is_admin():
        return True
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return False
    except:
        return False

def load_json_data(filename):
    """Data klasöründeki JSON dosyalarını okur"""
    try:
        path = os.path.join(get_base_path(), 'data', filename)
        if not os.path.exists(path):
            return []
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"JSON okuma hatası ({filename}): {e}")
        return []

# --- SİSTEM BİLGİLERİ ---

class SystemInfo:
    def get_report(self):
        info = f"--- SİSTEM RAPORU ---\n"
        info += f"PC Adı: {socket.gethostname()}\n"
        info += f"OS: {platform.system()} {platform.release()} ({platform.version()})\n"
        info += f"İşlemci: {platform.processor()}\n"
        info += f"Çekirdek: {psutil.cpu_count(logical=False)} Fiziksel / {psutil.cpu_count(logical=True)} Mantıksal\n"
        
        mem = psutil.virtual_memory()
        info += f"RAM: {round(mem.total / (1024**3), 2)} GB (Kullanılan: {mem.percent}%)\n"
        
        # Diskler
        info += "\n--- DİSKLER ---\n"
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                info += f"{part.device} ({part.fstype}): {round(usage.total / (1024**3), 1)} GB Toplam\n"
            except: pass
            
        return info

# --- TWEAK VE İŞLEMLER ---

class Tweaker:
    def apply_tweak(self, tweak_data, log_callback=None):
        name = tweak_data.get("name")
        t_type = tweak_data.get("type")
        
        if log_callback: log_callback(f"İşlem başlatılıyor: {name}...")
        
        try:
            if t_type == "script":
                cmd = tweak_data.get("command")
                subprocess.run(["powershell", "-Command", cmd], shell=True, creationflags=0x08000000)
            
            elif t_type == "winget":
                subprocess.run(f"winget install --id {tweak_data.get('id')} -e --silent", shell=True, creationflags=0x08000000)
                
            elif t_type == "external_exe" or t_type == "external_zip":
                url = tweak_data.get("url")
                if log_callback: log_callback(f"{name} indiriliyor (Simülasyon)...")
                # Gerçek indirme ve çalıştırma kodları buraya eklenebilir.
                
            if log_callback: log_callback(f"✅ {name} tamamlandı.")
            return True
        except Exception as e:
            if log_callback: log_callback(f"❌ Hata: {str(e)}")
            return False

# --- WINGET İŞLEMLERİ ---

class WingetManager:
    def install_program(self, app_id, callback):
        def _run():
            try:
                callback(f"Kuruluyor: {app_id}...")
                cmd = f"winget install --id {app_id} -e --silent --accept-package-agreements --accept-source-agreements"
                subprocess.run(cmd, shell=True, check=True, creationflags=0x08000000)
                callback(f"✅ {app_id} Kuruldu!")
            except:
                callback(f"❌ {app_id} Hatası!")
        
        threading.Thread(target=_run, daemon=True).start()

    def check_updates(self, result_callback):
        def _scan():
            try:
                cmd = "winget upgrade --include-unknown"
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True, encoding='utf-8', errors='ignore', creationflags=0x08000000)
                lines = result.stdout.splitlines()
                
                updates = []
                start_parsing = False
                for line in lines:
                    if "Name" in line and "Id" in line:
                        start_parsing = True
                        continue
                    if start_parsing and "-----" in line:
                        continue
                    if start_parsing and len(line) > 10:
                        parts = line.split()
                        if len(parts) >= 3:
                            updates.append(line)
                            
                result_callback(updates)
            except Exception as e:
                result_callback([f"Hata: {e}"])
        
        threading.Thread(target=_scan, daemon=True).start()

# --- PROGRAM KALDIRMA YÖNETİCİSİ ---

class UninstallManager:
    def get_installed_programs(self):
        """Windows Kayıt Defteri'nden yüklü programları çeker."""
        programs = set()
        registry_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        
        hives = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
        
        for hive in hives:
            for path in registry_paths:
                try:
                    with winreg.OpenKey(hive, path) as key:
                        for i in range(winreg.QueryInfoKey(key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                        if name:
                                            programs.add(name)
                                    except OSError:
                                        pass
                            except OSError:
                                continue
                except OSError:
                    continue
        return sorted(list(programs))

    def uninstall_program(self, program_name, callback):
        """Seçili programı Winget üzerinden kaldırmayı dener."""
        def _run():
            try:
                callback(f"Kaldırılıyor: {program_name}...")
                # Winget uninstall komutu
                cmd = f'winget uninstall --name "{program_name}" --silent --accept-source-agreements'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=0x08000000)
                
                if result.returncode == 0:
                    callback(f"✅ {program_name} başarıyla kaldırıldı.")
                else:
                    callback(f"⚠️ {program_name} kaldırılamadı (Manuel müdahale gerekebilir).")
            except Exception as e:
                callback(f"❌ Hata: {str(e)}")
        
        threading.Thread(target=_run, daemon=True).start()

# --- CHOCOLATEY YÖNETİCİSİ ---

class ChocolateyManager:
    def is_installed(self):
        try:
            subprocess.run(["choco", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08000000)
            return True
        except FileNotFoundError:
            return False

    def install_choco(self, callback):
        def _run():
            callback("Chocolatey indiriliyor ve kuruluyor...")
            cmd = "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
            try:
                subprocess.run(["powershell", "-Command", cmd], shell=True, check=True, creationflags=0x08000000)
                callback("✅ Chocolatey kuruldu! Programı yeniden başlatın.")
            except Exception as e:
                callback(f"❌ Kurulum hatası: {e}")
        
        threading.Thread(target=_run, daemon=True).start()

    def install_packages(self, package_list, callback):
        def _run():
            packages_str = " ".join(package_list)
            callback(f"Paketler kuruluyor: {packages_str}...")
            try:
                cmd = f"choco install {packages_str} -y --force"
                subprocess.run(cmd, shell=True, creationflags=0x08000000)
                callback("✅ İşlem tamamlandı.")
            except Exception as e:
                callback(f"❌ Hata: {e}")
        
        threading.Thread(target=_run, daemon=True).start()