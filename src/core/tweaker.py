import os
import subprocess
import requests
import zipfile
import io
import tempfile

class Tweaker:
    def apply_tweak(self, tweak_data):
        """
        JSON'dan gelen tweak verisine göre işlemi yönlendirir.
        """
        tweak_type = tweak_data.get("type")
        name = tweak_data.get("name")
        
        print(f"İşlem başlatılıyor: {name} ({tweak_type})")
        
        try:
            if tweak_type == "script":
                self._run_powershell(tweak_data.get("command"))
            
            elif tweak_type == "external_exe":
                self._download_and_run_exe(tweak_data.get("url"))
                
            elif tweak_type == "external_zip":
                self._download_extract_run(tweak_data.get("url"), tweak_data.get("exe_inside"))
            
            elif tweak_type == "winget":
                subprocess.run(f"winget install {tweak_data.get('id')}", shell=True)
                
            elif tweak_type == "local_exe":
                # Proje içindeki assets klasöründen çalıştırır
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                exe_path = os.path.join(base_path, tweak_data.get("path"))
                if os.path.exists(exe_path):
                    subprocess.Popen([exe_path], shell=True)
                else:
                    print(f"Dosya bulunamadı: {exe_path}")

        except Exception as e:
            print(f"Tweak hatası ({name}): {e}")
            return False
        
        return True

    def _run_powershell(self, command):
        subprocess.run(["powershell", "-Command", command], shell=True)

    def _download_and_run_exe(self, url):
        filename = url.split('/')[-1]
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        
        # İndir
        response = requests.get(url)
        with open(temp_path, 'wb') as f:
            f.write(response.content)
            
        # Çalıştır
        subprocess.Popen([temp_path], shell=True)

    def _download_extract_run(self, url, exe_name_inside):
        # İndir
        response = requests.get(url)
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            extract_path = os.path.join(tempfile.gettempdir(), "SaydutTweaks", exe_name_inside.replace(".exe", ""))
            z.extractall(extract_path)
            
            # Exe'yi bul ve çalıştır
            # Bazen zip içinde klasör olur, o yüzden walk ile arıyoruz
            target_exe = None
            for root, dirs, files in os.walk(extract_path):
                if exe_name_inside in files:
                    target_exe = os.path.join(root, exe_name_inside)
                    break
            
            if target_exe:
                subprocess.Popen([target_exe], shell=True)
            else:
                print("Zip içinde hedef exe bulunamadı.")