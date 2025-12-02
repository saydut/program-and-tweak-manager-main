import requests
import os
import sys
import subprocess
import time

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
            
            # Tarayıcı gibi görünmek için User-Agent ekliyoruz
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url_with_timestamp, headers=headers, timeout=10)
            
            # 404 veya 500 hatası varsa exception fırlatır
            response.raise_for_status()
            
            data = response.json()
            
            self.new_version = data.get("version")
            self.download_url = data.get("download_url")
            self.release_notes = data.get("changelog", "Yenilik notu bulunamadı.")
            
            print(f"Sunucu versiyonu: {self.new_version}, Mevcut: {self.current_version}")

            # Versiyon karşılaştırması
            if self.new_version and self.new_version != self.current_version:
                return True, self.new_version, self.release_notes
            else:
                return False, self.current_version, "Program güncel."
                
        except requests.exceptions.HTTPError as e:
            return False, None, f"HTTP Hatası: {e}"
        except requests.exceptions.ConnectionError:
            return False, None, "İnternet bağlantısı yok veya sunucuya ulaşılamıyor."
        except Exception as e:
            return False, None, f"Beklenmeyen hata: {str(e)}"

    def download_and_install(self):
        """Yeni sürümü indirir ve güvenli geçişi başlatır."""
        
        # Script modunda (geliştirme) güncellemeyi engelle
        if not getattr(sys, 'frozen', False):
            print("GÜVENLİK UYARISI: Script modunda güncelleme engellendi.")
            return False, "Geliştirme ortamında (IDE) güncelleme yapılamaz. Lütfen EXE dosyasını kullanın."

        if not self.download_url:
            return False, "İndirme linki bulunamadı."

        try:
            current_exe_path = os.path.abspath(sys.argv[0])
            current_dir = os.path.dirname(current_exe_path)
            temp_filename = "Update_New.exe"
            download_path = os.path.join(current_dir, temp_filename)
            
            # Dosyayı indir
            print(f"İndiriliyor: {self.download_url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.download_url, headers=headers, stream=True)
            response.raise_for_status()
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            if os.path.getsize(download_path) < 1024:
                return False, "İndirilen dosya hatalı veya çok küçük."

            print("İndirme tamamlandı. Geçiş yapılıyor...")
            self._create_and_run_safe_bat(current_exe_path, download_path)
            
            return True, "Güncelleme başlatılıyor..."

        except Exception as e:
            print(f"İndirme/Kurulum hatası: {e}")
            return False, str(e)

    def _create_and_run_safe_bat(self, current_exe, new_exe):
        current_dir = os.path.dirname(current_exe)
        exe_name = os.path.basename(current_exe)
        backup_name = exe_name + ".old"
        new_exe_name = os.path.basename(new_exe)
        batch_script_path = os.path.join(current_dir, "update_installer.bat")

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

        subprocess.Popen([batch_script_path], shell=True)
        sys.exit()