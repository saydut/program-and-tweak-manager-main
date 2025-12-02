import requests
import os
import sys
import subprocess
import tempfile
import json
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
            response = requests.get(self.remote_json_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            self.new_version = data.get("version")
            self.download_url = data.get("download_url")
            self.release_notes = data.get("changelog", "Yenilik notu bulunamadı.")
            
            # Basit versiyon karşılaştırması (String olarak)
            # Daha gelişmişi için packaging.version kullanılabilir ama şimdilik yeterli.
            if self.new_version > self.current_version:
                return True, self.new_version, self.release_notes
            else:
                return False, self.current_version, "Program güncel."
                
        except Exception as e:
            print(f"Güncelleme hatası: {e}")
            return False, None, str(e)

    def download_and_install(self):
        """Yeni sürümü indirir ve değişimi başlatır."""
        if not self.download_url:
            return False

        try:
            # 1. Dosyayı İndir (Temp klasörüne değil, exe'nin yanına indiriyoruz ki taşıması kolay olsun)
            current_exe_path = os.path.abspath(sys.argv[0])
            current_dir = os.path.dirname(current_exe_path)
            temp_filename = "Update_Temp.exe"
            download_path = os.path.join(current_dir, temp_filename)
            
            print(f"İndiriliyor: {self.download_url}")
            response = requests.get(self.download_url, stream=True)
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print("İndirme tamamlandı. Yeniden başlatılıyor...")
            
            # 2. Bat Scripti Oluştur (Değişimi yapacak tetikçi)
            self._create_and_run_bat(current_exe_path, download_path)
            
            return True

        except Exception as e:
            print(f"İndirme/Kurulum hatası: {e}")
            return False

    def _create_and_run_bat(self, old_exe, new_exe):
        """
        Eski exe'yi silip yeni exe'yi onun yerine koyan ve uygulamayı yeniden başlatan .bat dosyası.
        """
        batch_script_path = os.path.join(os.path.dirname(old_exe), "update_swapper.bat")
        exe_name = os.path.basename(old_exe)
        new_exe_name = os.path.basename(new_exe) # Update_Temp.exe

        # Bat script içeriği
        # 1. 2 saniye bekle (Programın kapanması için)
        # 2. Eski exe'yi sil
        # 3. Yeni inen dosyayı eski isme (ProgramYonetici.exe) çevir
        # 4. Programı başlat
        # 5. Bat dosyasını sil
        
        script_content = f"""
@echo off
timeout /t 2 /nobreak > NUL
del "{exe_name}"
rename "{new_exe_name}" "{exe_name}"
start "" "{exe_name}"
del "%~f0"
"""
        with open(batch_script_path, "w") as bat_file:
            bat_file.write(script_content)

        # 3. Programı kapat ve scripti çalıştır
        subprocess.Popen([batch_script_path], shell=True)
        sys.exit()