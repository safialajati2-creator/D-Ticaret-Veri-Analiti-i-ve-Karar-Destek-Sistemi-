# 📊 Dış Ticaret Karar Destek Sistemi

Python ve Streamlit ile geliştirilen, dış ticaret verilerini analiz eden; ihracat ve ithalat eğilimlerini görselleştiren, makine öğrenmesi modelleriyle tahmin üreten ve karar destek önerileri sunan interaktif bir veri analitiği uygulaması.

## Proje Özeti

Bu proje, ham dış ticaret verilerini karar vermeyi kolaylaştıran anlamlı göstergelere dönüştürmek amacıyla geliştirilmiştir. Kullanıcı kendi CSV verisini yükleyebilir veya örnek veri seti üzerinden sistemi inceleyebilir.

Sistem veri temizleme, temel ekonomik gösterge hesaplama, görselleştirme, tahminleme, kural tabanlı karar desteği ve otomatik PDF raporlama adımlarını tek bir Streamlit arayüzünde birleştirir.

## 🎓 Akademik Çalışma

Proje, **Beykoz Üniversitesi Mühendislik ve Mimarlık Fakültesi – Yazılım Mühendisliği** kapsamında hazırlanan **“Python Tabanlı Dış Ticaret Veri Analitiği ve Karar Destek Sistemi Tasarımı”** başlıklı akademik çalışmayla birlikte geliştirilmiştir.

Akademik çalışma; Türkiye dış ticaret verilerinin analizi, veri ön işleme, gösterge hesaplama, makine öğrenmesiyle tahminleme, kural tabanlı karar desteği ve sistemin güçlü/zayıf yönlerinin değerlendirilmesini kapsamaktadır.

📄 **Akademik rapor:** [Dış Ticaret Makalesı.pdf](Makale/D%C4%B1%C5%9F%20Ticaret%20Makales%C4%B1.pdf)

> Raporda yer alan model konfigürasyonları ve deneysel sonuçlar, çalışmanın akademik deney aşamasını yansıtmaktadır. Repository içindeki uygulama kodu daha sonra geliştirilmiş bir sürüm olabilir; bu nedenle güncel davranış için `app.py` esas alınmalıdır.

## ✨ Temel Özellikler

- CSV dosyası yükleme ve manuel veri girişi
- Farklı CSV encoding ve ayraç biçimlerini destekleyen veri okuma
- Eksik, negatif ve geçersiz kayıtların temizlenmesi
- İhracat, ithalat, dış ticaret dengesi ve ticaret hacmi analizi
- İhracatın ithalatı karşılama oranı ve yıllık değişim hesaplamaları
- İnteraktif analiz ekranları ve grafikler
- Linear Regression ve Random Forest modelleri
- Gelecek yıllara yönelik ihracat / ithalat tahmini
- R² ve MAE ile model performansı değerlendirmesi
- Random Forest özellik önemlerinin görüntülenmesi
- Kural tabanlı karar destek önerileri
- Türkçe karakter destekli otomatik PDF raporu

## 🧰 Kullanılan Teknolojiler

| Teknoloji | Kullanım |
|---|---|
| Python | Ana programlama dili |
| Streamlit | Web uygulaması ve kullanıcı arayüzü |
| Pandas | Veri işleme ve analiz |
| NumPy | Sayısal işlemler |
| Matplotlib | Veri görselleştirme |
| Scikit-learn | Linear Regression ve Random Forest modelleri |
| ReportLab | Otomatik PDF raporlama |

## 🧠 Sistem Akışı

1. Kullanıcı CSV yükler, manuel veri girer veya örnek veri setini kullanır.
2. Sistem veriyi doğrular ve temizler.
3. Dış ticaret göstergeleri otomatik hesaplanır.
4. Analiz sonuçları tablo ve grafiklerle sunulur.
5. Kullanıcı tahmin hedefini ve makine öğrenmesi modelini seçer.
6. Sistem modeli eğitir ve gelecek dönem tahminlerini üretir.
7. Karar destek modülü mevcut göstergeleri değerlendirerek öneriler oluşturur.
8. Sonuçlar PDF raporu olarak indirilebilir.

## 🤖 Tahmin Modelleri

Uygulama iki farklı regresyon yaklaşımı sunar:

- **Linear Regression**
- **Random Forest Regressor**

Tahminleme sürecinde yıl, trend ve önceki dönem ihracat/ithalat değerlerinden oluşturulan gecikmeli (lag) özellikler kullanılır. Model performansı **R²** ve **MAE** metrikleriyle gösterilir.

> Not: Tahminler analitik/akademik amaçlıdır ve gerçek yatırım veya ekonomi politikası tavsiyesi olarak değerlendirilmemelidir.

## 💡 Karar Destek Modülü

Sistem yalnızca veriyi göstermeyi değil, hesaplanan göstergeleri yorumlamayı da amaçlar. Karşılama oranı, dış ticaret açığı, ihracat/ithalat büyüme eğilimleri ve toplam ticaret hacmi gibi göstergeler üzerinden uyarı, bilgi ve olumlu durum mesajları üretir.

## 📄 PDF Raporlama

ReportLab ile oluşturulan rapor şunları içerebilir:

- Temel dış ticaret göstergeleri
- Veri tablosu
- Analiz grafikleri
- Tahmin sonuçları ve performans metrikleri
- Karar destek önerileri
- Genel sonuç özeti

Türkçe karakterlerin doğru görüntülenmesi için sistem uygun Unicode destekli fontları otomatik olarak bulmaya çalışır.

## 🚀 Kurulum ve Çalıştırma

```bash
git clone https://github.com/safialajati2-creator/D-Ticaret-Veri-Analiti-i-ve-Karar-Destek-Sistemi-.git
cd D-Ticaret-Veri-Analiti-i-ve-Karar-Destek-Sistemi-
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Bağımlılıkları yükleyin:

```bash
pip install -r requirements.txt
```

Uygulamayı başlatın:

```bash
streamlit run app.py
```

## 📁 Proje Yapısı

```text
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── Veri seti/
│   └── dis_ticaret_2015_2022.csv
├── Sonuç çıktıları/
│   └── ...
└── Makale/
    └── Dış Ticaret Makalesı.pdf
```

## 📌 Proje Amacı

Proje; veri analizi, makine öğrenmesi, veri görselleştirme, kullanıcı arayüzü geliştirme ve otomatik raporlama becerilerini tek bir uygulamada birleştiren akademik ve portföy odaklı bir çalışmadır.

## ⚠️ Kullanım Notu

Bu uygulama eğitim, akademik çalışma ve veri analitiği demonstrasyonu amacıyla geliştirilmiştir. Üretilen tahminler ve karar destek önerileri profesyonel finansal veya ekonomik danışmanlık niteliğinde değildir.
