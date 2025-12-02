import requests
import os
import sys
import subprocess
import time
from PyQt5.QtWidgets import QMessageBox

class Updater:
    def __init__(self, current_version, remote_json_url):
        self.current_version = current_version
        self.remote_json_url = remote_json_url
        self.download_url = None
        self.new_version = None
        self.release_notes = ""

    def check_for_updates(self):
        """Sunucudaki version.json dosyasını kontrol eder."""
        try:
            print(f"Güncelleme kontrol ediliyor: {self.remote_json_url}")
            # Cache önlemek için timestamp ekliyoruz
            url_with_timestamp = f"{self.remote_json_url}?t={int(time.time())}"
            response = requests.get(url_with_timestamp, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            self.new_version = data.get("version")
            self.download_url = data.get("download_url")
            self.release_notes = data.get("changelog", "Yenilik notu bulunamadı.")
            
            # Versiyon karşılaştırması
            if self.new_version != self.current_version:
                return True, self.new_version, self.release_notes
            else:
                return False, self.current_version, "Program güncel."
                
        except Exception as e:
            print(f"Güncelleme hatası: {e}")
            return False, None, str(e)

    def download_and_install(self):
        """Yeni sürümü indirir ve güvenli geçişi başlatır."""
        
        # --- [GÜVENLİK 1] GELİŞTİRME MODU KORUMASI ---
        # Eğer program PyInstaller ile paketlenmemişse (exe değilse) çalışmayı durdur.
        if not getattr(sys, 'frozen', False):
            print("GÜVENLİK UYARISI: Script modunda güncelleme engellendi.")
            return False, "Geliştirme ortamında güncelleme yapılamaz.\nBu koruma main.py dosyanızı silinmekten kurtardı."
        # ---------------------------------------------

        if not self.download_url:
            return False, "İndirme linki bulunamadı."

        try:
            current_exe_path = os.path.abspath(sys.argv[0])
            current_dir = os.path.dirname(current_exe_path)
            temp_filename = "Update_New.exe"
            download_path = os.path.join(current_dir, temp_filename)
            
            # Dosyayı indir
            print(f"İndiriliyor: {self.download_url}")
            response = requests.get(self.download_url, stream=True)
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # İndirilen dosyanın sağlamlığını basitçe kontrol et (Boyut 0 değilse)
            if os.path.getsize(download_path) < 1024:
                return False, "İndirilen dosya hatalı veya çok küçük."

            print("İndirme tamamlandı. Geçiş yapılıyor...")
            
            # Bat scripti ile güvenli geçiş yap
            self._create_and_run_safe_bat(current_exe_path, download_path)
            
            return True, "Güncelleme başlatılıyor..."

        except Exception as e:
            print(f"İndirme/Kurulum hatası: {e}")
            return False, str(e)

    def _create_and_run_safe_bat(self, current_exe, new_exe):
        """
        Eski exe'yi yedekler, yenisini koyar ve başlatır.
        """
        current_dir = os.path.dirname(current_exe)
        exe_name = os.path.basename(current_exe)
        backup_name = exe_name + ".old"
        new_exe_name = os.path.basename(new_exe)
        batch_script_path = os.path.join(current_dir, "update_installer.bat")

        # --- [GÜVENLİK 2] YEDEKLE VE DEĞİŞTİR MANTIĞI ---
        # 1. Bekle (Program kapansın)
        # 2. Varsa eski yedeği sil
        # 3. Mevcut programın ismini .old yap (SİLME YOK, RENAME VAR)
        # 4. Yeni inen dosyayı asıl isme çevir
        # 5. Programı başlat
        # 6. Bat dosyasını temizle
        
        script_content = f"""
@echo off
timeout /t 3 /nobreak > NUL
if exist "{backup_name}" del "{backup_name}"
move "{exe_name}" "{backup_name}"
move "{new_exe_name}" "{exe_name}"
start "" "{exe_name}"
del "%~f0"
"""
        with open(batch_script_path, "w") as bat_file:
            bat_file.write(script_content)

        # Programı kapat ve scripti çalıştır
        subprocess.Popen([batch_script_path], shell=True)
        sys.exit()