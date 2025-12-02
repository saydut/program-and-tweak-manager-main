from flask import Flask, render_template, url_for

app = Flask(__name__)

# Program Yöneticisi'nin detaylarını tanımlıyoruz
# Not: Programı güncellediğinde sadece buradaki 'version' bilgisini değiştirmen yeterli olur.
PROGRAM_YONETICISI_DATA = {
    "name": "Program Yöneticisi",
    "description": "Format sonrası bilgisayarını tek tıkla kur. Programları yükle, güncelle ve sistem ayarlarını otomatik yap.",
    "version": "v2.0",
    # İndirme linki, PythonAnywhere'deki static dosya ayarına göre oluşur.
    "download_url":"/static/apps/programyonetici/ProgramYonetici.exe", # .zip yerine .exe öneriyorum (Madde 1 gereği)
    "page_title": "Program Yöneticisi - İncele ve İndir"
}

# 1. Ana Sayfa Rotası
@app.route('/')
def home():
    # index.html'i yükle
    return render_template('index.html')

# 2. Program Detay Sayfası Rotası (İndirme/Tanıtım Sayfası)
@app.route('/apps/program-yoneticisi/')
def program_yoneticisi_detail():
    """
    Program Yöneticisi'nin detay sayfasını yükler ve veriyi sayfaya gönderir.
    """
    return render_template('program_detail.html', program=PROGRAM_YONETICISI_DATA)