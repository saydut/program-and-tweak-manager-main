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
            url_with_timestamp = f"{self.remote_json_url}?t={int(time.time())}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            
            response = requests.get(url_with_timestamp, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.new_version = data.get("version")
            self.download_url = data.get("download_url")
            self.release_notes = data.get("changelog", "Yenilik notu bulunamadı.")
            
            if self.new_version and self.new_version != self.current_version:
                return True, self.new_version, self.release_notes
            else:
                return False, self.current_version, "Program güncel."
        except Exception as e:
            return False, None, f"Hata: {str(e)}"

    def download_and_install(self):
        """
        Güncelleme işlemini başlatır.
        Program kapanır ve görünür bir CMD penceresi (BAT dosyası) işlemleri devralır.
        """
        if not getattr(sys, 'frozen', False):
            return False, "Geliştirme ortamında (IDE) güncelleme yapılamaz."

        if not self.download_url:
            return False, "İndirme linki bulunamadı."

        try:
            current_exe = os.path.abspath(sys.argv[0])
            current_dir = os.path.dirname(current_exe)
            temp_filename = "Update_New.exe"
            new_exe_path = os.path.join(current_dir, temp_filename)
            
            # Görünür BAT dosyasını oluştur ve çalıştır
            self._create_and_run_visible_updater(current_exe, new_exe_path, self.download_url)
            
            return True, "Güncelleme penceresi açılıyor..."

        except Exception as e:
            return False, str(e)

    def _create_and_run_visible_updater(self, current_exe, new_exe_path, url):
        """
        Kullanıcının görebileceği (konsol açık) bir güncelleme scripti oluşturur.
        """
        current_dir = os.path.dirname(current_exe)
        batch_script_path = os.path.join(current_dir, "update_visible.bat")
        
        # Windows CMD Scripti (Görünür Mod)
        # curl ile indir, sil, taşı, başlat.
        
        script_content = f"""
@echo off
title Saydut Program Yoneticisi Guncelleme
color 1F
mode con: cols=80 lines=25
cls

echo ========================================================
echo      SAYDUT PROGRAM YONETICISI - GUNCELLEME
echo ========================================================
echo.
echo  Lutfen bekleyin, program kapatiliyor...
timeout /t 3 /nobreak > NUL

echo.
echo  Yeni surum sunucudan indiriliyor...
echo  Link: {url}
echo.

:: Curl ile indirme (İlerleme çubuğu görünür)
curl -L -o "{new_exe_path}" "{url}"

if errorlevel 1 (
    color 4F
    cls
    echo ========================================================
    echo      HATA: INDIRME BASARISIZ OLDU!
    echo ========================================================
    echo.
    echo  Sunucuya erisilemedi veya dosya bulunamadi.
    echo  Lutfen internet baglantinizi kontrol edin.
    echo.
    echo  Eski surumunuz guvende. Cikmak icin bir tusa basin.
    pause >nul
    del "%~f0"
    exit
)

if not exist "{new_exe_path}" (
    color 4F
    echo HATA: Dosya yazilamadi!
    pause
    del "%~f0"
    exit
)

echo.
echo  Eski surum kaldiriliyor...
if exist "{current_exe}" del /f /q "{current_exe}"

echo.
echo  Yeni surum yukleniyor...
move /y "{new_exe_path}" "{current_exe}"

echo.
echo  Guncelleme tamamlandi! Program baslatiliyor...
timeout /t 2 /nobreak > NUL
start "" "{current_exe}"

:: Script kendini temizler
(goto) 2>nul & del "%~f0"
"""
        try:
            with open(batch_script_path, "w") as bat_file:
                bat_file.write(script_content)

            # BAT dosyasını GÖRÜNÜR şekilde yeni pencerede çalıştır
            # CREATE_NEW_CONSOLE bayrağı, yeni ve bağımsız bir CMD penceresi açar.
            creationflags = subprocess.CREATE_NEW_CONSOLE
            subprocess.Popen([batch_script_path], shell=True, creationflags=creationflags)
            
            # Programı anında kapat
            sys.exit(0)
            
        except Exception as e:
            print(f"Script oluşturma hatası: {e}")