from flask import Flask, render_template

app = Flask(__name__)

# Program Yöneticisi Verileri
PROGRAM_YONETICISI_DATA = {
    "name": "Program Yöneticisi",
    "description": "Format sonrası bilgisayarını tek tıkla kur. Programları yükle, güncelle ve sistem ayarlarını otomatik yap.",
    "version": "v2.0",
    "download_url": "https://saydut.netlify.app/ProgramYonetici.exe",
    "page_title": "Program Yöneticisi - İncele ve İndir"
}

# YENİ: Dosya Ayırıcı Verileri (Netlify Linki ile)
DOSYA_AYIRICI_DATA = {
    "name": "Dosya Ayırıcı & Karşılaştırıcı",
    "description": "Klasörleri karşılaştırın, kopya dosyaları hash analizi ile bulun ve ayıklayın.",
    "version": "v1.0",
    # Buraya Netlify'e yüklediğin exe'nin linkini yazacaksın:
    "download_url": "https://saydut.netlify.app/DosyaAyirici.exe", 
    "page_title": "Dosya Ayırıcı - İncele ve İndir"
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/apps/program-yoneticisi/')
def program_yoneticisi_detail():
    return render_template('program_detail.html', program=PROGRAM_YONETICISI_DATA)

# EKSİK OLAN KISIM BURASIYDI (EKLENDİ)
@app.route('/apps/dosya-ayirici/')
def dosya_ayirici():
    # Veriyi (linki vs.) sayfaya gönderiyoruz
    return render_template('dosya_ayirici.html', program=DOSYA_AYIRICI_DATA)

if __name__ == '__main__':
    app.run(debug=True)