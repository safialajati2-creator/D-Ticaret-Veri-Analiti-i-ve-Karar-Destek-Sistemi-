# 📊 Dış Ticaret Karar Destek Sistemi

<p align="center">
  <a href="README.md">English</a> | <b>Türkçe</b>
</p>

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?logo=scikitlearn&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Veri%20Analizi-150458?logo=pandas&logoColor=white)
![Status](https://img.shields.io/badge/Durum-Portf%C3%B6y%20Projesi-success)

Python ve Streamlit ile geliştirilen bu proje; dış ticaret verilerini temizleyen, temel ekonomik göstergeleri hesaplayan, ihracat ve ithalat eğilimlerini görselleştiren, makine öğrenmesiyle tahmin üreten, kural tabanlı karar destek önerileri sunan ve sonuçları PDF olarak raporlayabilen interaktif bir veri analitiği uygulamasıdır.

## 🖥️ Uygulamadan Görüntüler

<p align="center">
  <img src="Sonu%C3%A7%20%C3%A7%C4%B1kt%C4%B1lar%C4%B1/1.jpeg" width="48%" />
  <img src="Sonu%C3%A7%20%C3%A7%C4%B1kt%C4%B1lar%C4%B1/2.jpeg" width="48%" />
</p>
<p align="center">
  <img src="Sonu%C3%A7%20%C3%A7%C4%B1kt%C4%B1lar%C4%B1/3.jpeg" width="48%" />
  <img src="Sonu%C3%A7%20%C3%A7%C4%B1kt%C4%B1lar%C4%B1/4.jpeg" width="48%" />
</p>

<details>
<summary><b>Daha fazla ekran görüntüsü</b></summary>
<br>
<p align="center">
  <img src="Sonu%C3%A7%20%C3%A7%C4%B1kt%C4%B1lar%C4%B1/5.jpeg" width="48%" />
  <img src="Sonu%C3%A7%20%C3%A7%C4%B1kt%C4%B1lar%C4%B1/6.jpeg" width="48%" />
</p>
<p align="center">
  <img src="Sonu%C3%A7%20%C3%A7%C4%B1kt%C4%B1lar%C4%B1/7.jpeg" width="48%" />
  <img src="Sonu%C3%A7%20%C3%A7%C4%B1kt%C4%B1lar%C4%B1/8.jpeg" width="48%" />
</p>
</details>

## 🎓 Akademik Çalışma

Proje, **Beykoz Üniversitesi Mühendislik ve Mimarlık Fakültesi – Yazılım Mühendisliği** kapsamında hazırlanan **“Python Tabanlı Dış Ticaret Veri Analitiği ve Karar Destek Sistemi Tasarımı”** başlıklı akademik çalışmayla birlikte geliştirilmiştir.

📄 **Akademik rapor:** [Dış Ticaret Makalesı.pdf](Makale/D%C4%B1%C5%9F%20Ticaret%20Makales%C4%B1.pdf)

Akademik çalışma; Türkiye dış ticaret verilerinin analizi, veri ön işleme, gösterge hesaplama, makine öğrenmesiyle tahminleme, kural tabanlı karar desteği ve sistem değerlendirmesini kapsar. Repository içindeki `app.py`, çalışmanın portföy için düzenlenmiş uygulama sürümüdür.

## ✨ Temel Özellikler

- CSV yükleme ve farklı encoding/ayraç biçimlerini algılama
- Eksik, negatif, geçersiz ve yinelenen kayıtların temizlenmesi
- İhracat, ithalat, dış ticaret dengesi ve toplam ticaret hacmi analizi
- İhracatın ithalatı karşılama oranı ve yıllık değişim hesaplamaları
- Streamlit tabanlı interaktif dashboard
- Linear Regression ve Random Forest Regressor
- Gecikmeli değişkenler (`Lag-1`, `Lag-2`) ve 3 dönemlik hareketli ortalama (`MA-3`)
- Kronolojik train/test ayrımı
- R² ve MAE ile model değerlendirmesi
- Random Forest özellik önemleri
- Gelecek yıllara yönelik özyinelemeli tahmin
- Kural tabanlı karar destek önerileri
- ReportLab ile otomatik PDF raporu

## 🧰 Teknolojiler

| Teknoloji | Kullanım |
|---|---|
| Python | Ana programlama dili |
| Streamlit | Web arayüzü |
| Pandas | Veri temizleme ve analiz |
| NumPy | Sayısal işlemler ve özellik üretimi |
| Matplotlib | Veri görselleştirme |
| Scikit-learn | Regresyon modelleri ve performans metrikleri |
| ReportLab | PDF raporlama |

## 🧠 Sistem Akışı

1. Kullanıcı CSV yükler veya uygulamadaki örnek veri setini kullanır.
2. Sütun adları normalize edilir ve veriler doğrulanır.
3. Eksik ve geçersiz kayıtlar temizlenir.
4. Dış ticaret dengesi, ticaret hacmi, karşılama oranı ve değişim oranları hesaplanır.
5. Sonuçlar tablo ve grafiklerle gösterilir.
6. Tahmin hedefi ve model seçilir.
7. Model kronolojik olarak ayrılmış eğitim/test verisi üzerinde değerlendirilir.
8. Gelecek dönem tahminleri üretilir.
9. Kural tabanlı modül göstergeleri yorumlayarak karar destek mesajları oluşturur.
10. Sonuçlar PDF raporu olarak indirilebilir.

## 🤖 Makine Öğrenmesi

Uygulama iki regresyon modeli sunar:

- **Linear Regression**
- **Random Forest Regressor** — `200` ağaç, `max_depth=5`, `random_state=42`

Model girdileri hedef serinin yılı, bir ve iki dönem gecikmeli değerleri ile önceki üç dönemin hareketli ortalamasından oluşur. Performans **R²** ve **MAE** ile ölçülür.

> Küçük yıllık veri setlerinde model metrikleri yüksek varyans gösterebilir. Tahminler akademik/analitik demonstrasyon amaçlıdır; finansal veya ekonomik danışmanlık değildir.

## 💡 Karar Destek Modülü

Kural tabanlı modül aşağıdaki göstergeleri değerlendirir:

- İhracatın ithalatı karşılama oranı
- Dış ticaret açığı
- Son dönem ihracat değişimi
- Son dönem ithalat değişimi
- Ticaret hacminin tarihsel seviyesi

Bu bölüm otomatik analitik uyarılar üretir ve veri odaklı karar destek mantığını göstermeyi amaçlar.

## 📄 PDF Raporlama

Uygulama ReportLab kullanarak özet göstergeler, analiz grafikleri, karar destek önerileri ve mevcutsa tahmin performansını içeren PDF raporu oluşturabilir.

## 📚 Veri Seti

Repository içindeki CSV, **2005–2022** dönemine ait 18 yıllık örnek dış ticaret verisini içerir. Uygulamanın yerleşik demo verisi ise daha güncel bir örnek seri kullanır. Kullanıcı kendi `Yil`, `Ihracat`, `Ithalat` sütunlarını içeren CSV dosyasını da yükleyebilir.

> Veri dosyası portföy/akademik demonstrasyon amacıyla repository içinde tutulmaktadır. Gerçek analizlerde güncel ve doğrulanmış resmi kaynak kullanılması önerilir.

## 🚀 Kurulum

```bash
git clone https://github.com/safialajati2-creator/foreign-trade-decision-support-system.git
cd foreign-trade-decision-support-system
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
├── README_TR.md
├── .gitignore
├── Veri seti/
│   └── dis_ticaret_2015_2022.csv
├── Sonuç çıktıları/
│   └── 1.jpeg ... 8.jpeg
└── Makale/
    └── Dış Ticaret Makalesı.pdf
```

## 🎯 Proje Amacı

Bu çalışma; **veri analizi, veri temizleme, özellik mühendisliği, makine öğrenmesi, veri görselleştirme, Streamlit arayüz geliştirme, karar destek mantığı ve otomatik raporlama** becerilerini tek bir uçtan uca projede göstermeyi amaçlar.
