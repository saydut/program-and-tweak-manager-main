from flask import Flask, render_template

app = Flask(__name__)

# Program Yöneticisi'nin detaylarını tanımlıyoruz
PROGRAM_YONETICISI_DATA = {
    "name": "Program Yöneticisi",
    "description": "Format sonrası bilgisayarını tek tıkla kur. Programları yükle, güncelle ve sistem ayarlarını otomatik yap.",
    "version": "v2.0",
    # İndirme linki artık Netlify üzerinden
    "download_url": "https://saydut.netlify.app/ProgramYonetici.exe",
    "page_title": "Program Yöneticisi - İncele ve İndir"
}

# 1. Ana Sayfa
@app.route('/')
def home():
    return render_template('index.html')

# 2. Program Detay Sayfası
@app.route('/apps/program-yoneticisi/')
def program_yoneticisi_detail():
    return render_template('program_detail.html', program=PROGRAM_YONETICISI_DATA)