import psutil
import platform
import socket
import subprocess
import os

# PyOpenCL opsiyonel olarak kalsın, varsa kullanırız
try:
    import pyopencl as cl
    HAS_OPENCL = True
except ImportError:
    HAS_OPENCL = False

class SystemInfo:
    def get_full_report(self):
        """Tüm sistem raporunu metin olarak döndürür."""
        report = []
        report.append("=== SİSTEM BİLGİLERİ ===")
        report.append(f"İşletim Sistemi: {platform.system()} {platform.release()} ({platform.version()})")
        report.append(f"Bilgisayar Adı: {socket.gethostname()}")
        report.append("-" * 40)
        
        report.append(self.get_cpu_info())
        report.append("-" * 40)
        
        report.append(self.get_memory_info())
        report.append("-" * 40)
        
        report.append(self.get_disk_info())
        report.append("-" * 40)
        
        report.append(self.get_network_info())
        report.append("-" * 40)
        
        report.append(self.get_gpu_info())
        
        return "\n".join(report)

    def get_cpu_info(self):
        lines = ["=== İŞLEMCİ (CPU) ==="]
        lines.append(f"İşlemci Modeli: {platform.processor()}")
        lines.append(f"Fiziksel Çekirdek: {psutil.cpu_count(logical=False)}")
        lines.append(f"Mantıksal İş Parçacığı: {psutil.cpu_count(logical=True)}")
        try:
            freq = psutil.cpu_freq()
            if freq:
                lines.append(f"Maks Frekans: {freq.max:.2f} Mhz")
        except:
            pass
        return "\n".join(lines)

    def get_memory_info(self):
        mem = psutil.virtual_memory()
        total = round(mem.total / (1024**3), 2)
        available = round(mem.available / (1024**3), 2)
        percent = mem.percent
        return f"=== BELLEK (RAM) ===\nToplam: {total} GB\nKullanılabilir: {available} GB\nKullanım Oranı: %{percent}"

    def get_disk_info(self):
        lines = ["=== DEPOLAMA (C: Sürücüsü) ==="]
        try:
            # Windows'ta genelde C: ana disktir
            disk = psutil.disk_usage('C:\\')
            total = round(disk.total / (1024**3), 2)
            used = round(disk.used / (1024**3), 2)
            free = round(disk.free / (1024**3), 2)
            lines.append(f"Toplam Alan: {total} GB")
            lines.append(f"Kullanılan: {used} GB")
            lines.append(f"Boş Alan: {free} GB")
        except:
            lines.append("C: Sürücüsü bilgisi alınamadı.")
        return "\n".join(lines)
    
    def get_network_info(self):
        lines = ["=== AĞ BİLGİLERİ ==="]
        if_addrs = psutil.net_if_addrs()
        for interface_name, interface_addresses in if_addrs.items():
            for address in interface_addresses:
                if str(address.family) == 'AddressFamily.AF_INET':
                    lines.append(f"Arayüz: {interface_name}")
                    lines.append(f"  IP: {address.address}")
        return "\n".join(lines)

    def get_gpu_info(self):
        """
        Ekran kartı bilgisini almak için önce WMIC (Windows),
        yoksa PyOpenCL dener.
        """
        lines = ["=== EKRAN KARTI (GPU) ==="]
        
        # Yöntem 1: WMIC (En hafif ve garanti yöntem - Windows için)
        if os.name == 'nt':
            try:
                creationflags = 0x08000000 # Pencere gizleme
                cmd = "wmic path win32_videocontroller get name"
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True, creationflags=creationflags)
                gpus = [line.strip() for line in result.stdout.split('\n') if line.strip() and "Name" not in line]
                
                if gpus:
                    for i, gpu in enumerate(gpus):
                        lines.append(f"GPU {i+1}: {gpu}")
                    return "\n".join(lines)
            except:
                pass # Hata olursa diğer yönteme geç

        # Yöntem 2: PyOpenCL (Varsa)
        if HAS_OPENCL:
            try:
                platforms = cl.get_platforms()
                for p in platforms:
                    devices = p.get_devices(device_type=cl.device_type.GPU)
                    for d in devices:
                        lines.append(f"Model (OpenCL): {d.name}")
                        lines.append(f"  Sürücü: {d.driver_version}")
                return "\n".join(lines)
            except:
                pass
            
        lines.append("Ekran kartı bilgisi alınamadı.")
        return "\n".join(lines)