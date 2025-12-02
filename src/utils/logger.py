import sys
import os
import logging
from datetime import datetime

def setup_logging():
    """
    Program genelinde loglama sistemini başlatır.
    Hem ekrana (konsol) hem de dosyaya çıktı verir.
    """
    # 1. Log klasörünü belirle (Programın ana dizininde 'logs' klasörü)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_dir = os.path.join(base_dir, "logs")
    
    # Klasör yoksa oluştur
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception as e:
            print(f"Log klasörü oluşturulamadı: {e}")
            return # Yazma izni yoksa loglamayı pas geç

    # 2. Log dosyasının adı (Örn: log_2025-12-02.txt)
    log_filename = f"log_{datetime.now().strftime('%Y-%m-%d')}.txt"
    log_path = os.path.join(log_dir, log_filename)

    # 3. Ayarları Yap
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'), # Dosyaya yaz
            logging.StreamHandler(sys.stdout)                # Ekrana da yaz (CMD açıkken görmek için)
        ]
    )

    # 4. Yakalanmayan Hataları (Crash) Yakala
    # Bu kısım çok önemli: Program çökerse hatayı log dosyasına yazar.
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logging.critical("BEKLENMEYEN HATA (CRASH):", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception
    
    logging.info("--- Program Başlatıldı ---")
    logging.info(f"Sürüm Kontrolü: Log sistemi aktif. Dosya: {log_path}")