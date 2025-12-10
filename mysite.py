from flask import Flask, render_template

app = Flask(__name__)

# ==========================================
# 1. PROGRAM YÖNETİCİSİ VERİLERİ
# ==========================================
PROGRAM_YONETICISI_DATA = {
    "name": "Program Yöneticisi",
    "description": "Format sonrası bilgisayarını tek tıkla kur. Programları yükle, güncelle ve sistem ayarlarını otomatik yap.",
    "version": "v2.0",
    "download_url": "https://saydut.netlify.app/ProgramYonetici.exe",
    "page_title": "Program Yöneticisi - İncele ve İndir"
}

# ==========================================
# 2. DOSYA AYIRICI VERİLERİ
# ==========================================
DOSYA_AYIRICI_DATA = {
    "name": "Dosya Ayırıcı & Karşılaştırıcı",
    "description": "Klasörleri karşılaştırın, kopya dosyaları hash analizi ile bulun ve ayıklayın.",
    "version": "v1.0",
    "download_url": "https://saydut.netlify.app/DosyaAyirici.exe", 
    "page_title": "Dosya Ayırıcı - İncele ve İndir"
}

# ==========================================
# 3. YENİ: BEKRA SYSTEM CARE VERİLERİ
# ==========================================
BEKRA_DATA = {
    "name": "Bekra System Care Pro",
    "description": "Sisteminizin gerçek potansiyelini ortaya çıkarın. Akıllı RAM yönetimi ve disk temizliği.",
    "version": "v1.0",
    # Buraya exe'yi yükleyince linkini koyarsın:
    "download_url": "https://saydut.netlify.app/BekraSystemCare.exe", 
    "page_title": "Bekra System Care - Sistem Hızlandırma"
}

# ==========================================
# ROUTE (YÖNLENDİRME) AYARLARI
# ==========================================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/apps/program-yoneticisi/')
def program_yoneticisi_detail():
    return render_template('program_detail.html', program=PROGRAM_YONETICISI_DATA)

@app.route('/apps/dosya-ayirici/')
def dosya_ayirici():
    return render_template('dosya_ayirici.html', program=DOSYA_AYIRICI_DATA)

# YENİ EKLENEN FONKSİYON
# index.html'deki {{ url_for('bekra_detail') }} buraya bakar.
@app.route('/apps/bekra-system-care/')
def bekra_detail():
    # bekra_detail.html dosyasını render ediyoruz
    # İlerde html içine {{ program.name }} koyarsan diye veriyi de gönderdim.
    return render_template('bekra_detail.html', program=BEKRA_DATA)

if __name__ == '__main__':
    app.run(debug=True)