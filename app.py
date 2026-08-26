# ╔══════════════════════════════════════════════════════════════════════╗
# ║         DIŞ TİCARET KARAR DESTEK SİSTEMİ                           ║
# ║         Foreign Trade Decision Support System                        ║
# ║  Versiyon  : 2.1  |  Türkçe font düzeltmesi + orijinal efektler     ║
# ╚══════════════════════════════════════════════════════════════════════╝

# ─── KÜTÜPHANE İMPORTLARI ──────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io, warnings, datetime, os
warnings.filterwarnings("ignore")

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, Image as RLImage, PageBreak, HRFlowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ─── TÜRKÇE FONT KAYDI ────────────────────────────────────────────────────────
# ReportLab varsayılan fontları Türkçe karakterleri desteklemez.
# Bu bölüm Windows / Linux / macOS üzerinde DejaVuSans veya Arial gibi Türkçe
# destekli TTF fontları arar. Font bulunamazsa PDF üretimini durdurur;
# Helvetica'ya düşmez. Böylece Ş, Ğ, İ, ı, Ö, Ü, Ç harfleri kare çıkmaz.
import glob
from matplotlib import font_manager


def _find_font_file(names):
    candidates = []
    for n in names:
        candidates += glob.glob(n)
    try:
        candidates.append(font_manager.findfont("DejaVu Sans", fallback_to_default=False))
    except Exception:
        pass
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


_FONT_REG = _find_font_file([
    r"C:/Windows/Fonts/DejaVuSans.ttf",
    r"C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/Library/Fonts/Arial.ttf",
])
_FONT_BOLD = _find_font_file([
    r"C:/Windows/Fonts/DejaVuSans-Bold.ttf",
    r"C:/Windows/Fonts/arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]) or _FONT_REG
_FONT_IT = _find_font_file([
    r"C:/Windows/Fonts/DejaVuSans-Oblique.ttf",
    r"C:/Windows/Fonts/ariali.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
    "/Library/Fonts/Arial Italic.ttf",
]) or _FONT_REG

if not _FONT_REG:
    raise RuntimeError("Türkçe PDF fontu bulunamadı. Lütfen matplotlib kurulu olsun veya Windows Fonts klasöründe Arial bulunsun.")

pdfmetrics.registerFont(TTFont("TR", _FONT_REG))
pdfmetrics.registerFont(TTFont("TR-Bold", _FONT_BOLD))
pdfmetrics.registerFont(TTFont("TR-Italic", _FONT_IT))
pdfmetrics.registerFontFamily("TR", normal="TR", bold="TR-Bold", italic="TR-Italic", boldItalic="TR-Bold")
_F, _FB, _FI = "TR", "TR-Bold", "TR-Italic"

# ─── SAYFA YAPILANDIRMASI ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dış Ticaret Karar Destek Sistemi",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ─── ÖZEL CSS STİLLERİ ────────────────────────────────────────────────────────
def inject_custom_css():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a1628 100%);
        color: #e2e8f0;
    }
    .main-header {
        background: linear-gradient(90deg, #1a3a5c 0%, #0f2744 40%, #1a3a5c 100%);
        border: 1px solid #2563eb44;
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 24px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #2563eb, #06b6d4, #2563eb);
        animation: shimmer 3s infinite;
    }
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    .main-header h1 {
        font-size: 2.1rem;
        font-weight: 800;
        color: #e2e8f0;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 6px 0 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #162d4a 100%);
        border: 1px solid #2563eb33;
        border-radius: 14px;
        padding: 20px 22px;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px #2563eb22;
        border-color: #2563eb66;
    }
    .metric-card .label {
        font-size: 0.78rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #60a5fa;
    }
    .metric-card .delta { font-size: 0.82rem; margin-top: 4px; }
    .delta-pos { color: #34d399; }
    .delta-neg { color: #f87171; }
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #60a5fa;
        border-left: 4px solid #2563eb;
        padding-left: 12px;
        margin: 20px 0 14px;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1b2a 0%, #0a1628 100%);
        border-right: 1px solid #1e3a5f;
    }
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 { color: #60a5fa; }
    .stButton > button {
        background: linear-gradient(135deg, #1d4ed8, #2563eb);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        transform: translateY(-1px);
        box-shadow: 0 4px 14px #2563eb44;
    }
    .footer {
        text-align: center;
        color: #475569;
        font-size: 0.78rem;
        padding: 20px;
        border-top: 1px solid #1e3a5f;
        margin-top: 40px;
    }
    </style>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# BÖLÜM 1: VERİ YÜKLEME VE TEMİZLEME
# ══════════════════════════════════════════════════════════════════════════════
def load_sample_data() -> pd.DataFrame:
    years = list(range(2000, 2024))
    exports = [
        27.3, 31.3, 36.1, 47.3, 63.1, 73.5, 85.5, 107.2, 132.0, 102.1,
        113.9, 134.9, 152.5, 151.8, 157.6, 143.8, 142.5, 156.9, 167.9, 180.5,
        169.5, 225.4, 254.2, 255.3
    ]
    imports = [
        54.5, 41.4, 51.6, 69.3, 97.5, 116.8, 139.6, 170.1, 201.8, 140.9,
        185.5, 240.8, 236.5, 251.7, 242.2, 207.2, 198.6, 233.8, 223.0, 210.3,
        219.5, 271.4, 364.0, 362.4
    ]
    return pd.DataFrame({"Yil": years, "Ihracat": exports, "Ithalat": imports})


def _normalize_col_name(text: str) -> str:
    text = str(text).strip().lower()
    tr_map = str.maketrans({
        "ı": "i", "İ": "i", "ğ": "g", "Ğ": "g",
        "ü": "u", "Ü": "u", "ş": "s", "Ş": "s",
        "ö": "o", "Ö": "o", "ç": "c", "Ç": "c",
    })
    text = text.translate(tr_map)
    return text.replace(" ", "_").replace("-", "_")


def read_csv_smart(uploaded_file) -> pd.DataFrame:
    raw = uploaded_file.getvalue()
    last_error = None
    for enc in ["utf-8-sig", "utf-8", "cp1254", "latin1"]:
        for sep in [None, ";", ",", "\t"]:
            try:
                df = pd.read_csv(io.BytesIO(raw), encoding=enc, sep=sep, engine="python")
                if len(df.columns) >= 3:
                    return df
            except Exception as e:
                last_error = e
    raise ValueError(f"CSV okunamadı. Dosyanın sütunları Yil, Ihracat, Ithalat olmalı. Detay: {last_error}")


def clean_data(df: pd.DataFrame) -> tuple:
    uyarilar = []
    baslangic_satir = len(df)
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    col_map = {}
    for col in df.columns:
        cl = _normalize_col_name(col)
        if cl in ["yil", "year", "tarih"] or "yil" in cl or "year" in cl:
            col_map[col] = "Yil"
        elif "ihracat" in cl or "export" in cl:
            col_map[col] = "Ihracat"
        elif "ithalat" in cl or "import" in cl:
            col_map[col] = "Ithalat"
    df = df.rename(columns=col_map)
    eksik = [c for c in ["Yil", "Ihracat", "Ithalat"] if c not in df.columns]
    if eksik:
        mevcut = ", ".join(map(str, df.columns))
        raise ValueError(f"CSV içinde gerekli sütunlar bulunamadı: {', '.join(eksik)}. Mevcut sütunlar: {mevcut}")
    for col in ["Yil", "Ihracat", "Ithalat"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    once = len(df)
    df = df.dropna(subset=["Yil", "Ihracat", "Ithalat"])
    if len(df) < once:
        uyarilar.append(f"⚠️ {once - len(df)} satır eksik değer içerdiği için kaldırıldı.")
    once2 = len(df)
    df = df[(df["Ihracat"] >= 0) & (df["Ithalat"] >= 0)]
    if len(df) < once2:
        uyarilar.append(f"⚠️ {once2 - len(df)} satır negatif değer içerdiği için kaldırıldı.")
    once3 = len(df)
    df = df[(df["Yil"] >= 1900) & (df["Yil"] <= 2100)]
    if len(df) < once3:
        uyarilar.append(f"⚠️ {once3 - len(df)} satır geçersiz yıl değeri içerdiği için kaldırıldı.")
    df["Yil"] = df["Yil"].astype(int)
    df = df.sort_values("Yil").reset_index(drop=True)
    df = df.drop_duplicates(subset=["Yil"], keep="last")
    toplam_kaldirilan = baslangic_satir - len(df)
    if toplam_kaldirilan > 0:
        uyarilar.append(f"ℹ️ Toplam {toplam_kaldirilan} hatalı satır kaldırıldı. {len(df)} temiz kayıt.")
    return df, uyarilar


# ══════════════════════════════════════════════════════════════════════════════
# BÖLÜM 2: GÖSTERGE HESAPLAMA
# ══════════════════════════════════════════════════════════════════════════════
def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Dis_Ticaret_Dengesi"] = df["Ihracat"] - df["Ithalat"]
    df["Ticaret_Hacmi"] = df["Ihracat"] + df["Ithalat"]
    df["Karsilama_Orani"] = (df["Ihracat"] / df["Ithalat"]) * 100
    df["Ihracat_Degisim"] = df["Ihracat"].pct_change() * 100
    df["Ithalat_Degisim"] = df["Ithalat"].pct_change() * 100
    df["Hacim_Degisim"] = df["Ticaret_Hacmi"].pct_change() * 100
    return df


# ══════════════════════════════════════════════════════════════════════════════
# BÖLÜM 3: TAHMİNLEME MODELLERİ
# ══════════════════════════════════════════════════════════════════════════════
def prepare_features(df: pd.DataFrame):
    d = df.copy().reset_index(drop=True)
    d["Lag1_Ihracat"] = d["Ihracat"].shift(1)
    d["Lag2_Ihracat"] = d["Ihracat"].shift(2)
    d["Lag1_Ithalat"] = d["Ithalat"].shift(1)
    d["Lag2_Ithalat"] = d["Ithalat"].shift(2)
    d["Trend"] = range(len(d))
    d = d.dropna()
    X = d[["Yil", "Lag1_Ihracat", "Lag2_Ihracat", "Lag1_Ithalat", "Lag2_Ithalat", "Trend"]].values
    return X, d["Ihracat"].values, d["Ithalat"].values


def train_and_forecast(df: pd.DataFrame, hedef: str, model_adi: str, tahmin_yili: int) -> dict:
    X, y_ihracat, y_ithalat = prepare_features(df)
    y = y_ihracat if hedef == "Ihracat" else y_ithalat
    split = max(1, int(len(X) * 0.2)) if len(X) >= 5 else 1
    X_train, X_test = X[:-split], X[-split:]
    y_train, y_test = y[:-split], y[-split:]
    model = (LinearRegression() if model_adi == "Linear Regression"
             else RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
    model.fit(X_train, y_train)
    y_pred_test = model.predict(X_test)
    r2 = round(r2_score(y_test, y_pred_test), 4)
    mae = round(mean_absolute_error(y_test, y_pred_test), 2)
    feature_importance = None
    if model_adi == "Random Forest":
        fn = ["Yıl", "Lag1-İhracat", "Lag2-İhracat", "Lag1-İthalat", "Lag2-İthalat", "Trend"]
        feature_importance = dict(zip(fn, model.feature_importances_))
    l1i = df["Ihracat"].iloc[-1]; l2i = df["Ihracat"].iloc[-2]
    l1t = df["Ithalat"].iloc[-1]; l2t = df["Ithalat"].iloc[-2]
    trend0 = len(df) - 1
    gelecek_yillar, tahmin_degerleri = [], []
    for i in range(1, tahmin_yili + 1):
        yil = df["Yil"].iloc[-1] + i
        Xf = np.array([[yil, l1i, l2i, l1t, l2t, trend0 + i]])
        pred = max(model.predict(Xf)[0], 0)
        gelecek_yillar.append(yil)
        tahmin_degerleri.append(round(pred, 2))
        if hedef == "Ihracat": l2i, l1i = l1i, pred
        else: l2t, l1t = l1t, pred
    return {
        "model": model, "r2": r2, "mae": mae,
        "gelecek_yillar": gelecek_yillar, "tahmin_degerleri": tahmin_degerleri,
        "feature_importance": feature_importance,
        "y_test": y_test, "y_pred_test": y_pred_test,
    }


# ══════════════════════════════════════════════════════════════════════════════
# BÖLÜM 4: GÖRSELLEŞTİRME
# ══════════════════════════════════════════════════════════════════════════════
PALETTE = {
    "ihracat":"#3b82f6","ithalat":"#f87171","hacim":"#a78bfa",
    "denge_pos":"#34d399","denge_neg":"#f87171","karsilama":"#fbbf24",
    "tahmin":"#fb923c","bg":"#0d1b2a","grid":"#1e3a5f","text":"#cbd5e1","spine":"#1e3a5f",
}


def apply_dark_theme(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(PALETTE["bg"])
    ax.tick_params(colors=PALETTE["text"], labelsize=9)
    ax.xaxis.label.set_color(PALETTE["text"])
    ax.yaxis.label.set_color(PALETTE["text"])
    ax.title.set_color("#e2e8f0")
    for spine in ax.spines.values():
        spine.set_color(PALETTE["spine"])
    ax.grid(True, color=PALETTE["grid"], linewidth=0.6, linestyle="--", alpha=0.6)
    if title: ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
    if xlabel: ax.set_xlabel(xlabel, fontsize=9)
    if ylabel: ax.set_ylabel(ylabel, fontsize=9)


def fig_trend(df):
    fig, ax = plt.subplots(figsize=(10, 4)); fig.patch.set_facecolor(PALETTE["bg"])
    ax.plot(df["Yil"], df["Ihracat"], color=PALETTE["ihracat"], lw=2.5, marker="o", ms=4, label="İhracat")
    ax.plot(df["Yil"], df["Ithalat"], color=PALETTE["ithalat"], lw=2.5, marker="s", ms=4, label="İthalat")
    ax.fill_between(df["Yil"], df["Ihracat"], df["Ithalat"], alpha=0.12, color="#94a3b8")
    ax.legend(facecolor="#0f2744", edgecolor=PALETTE["spine"], labelcolor=PALETTE["text"], fontsize=9)
    apply_dark_theme(ax, "İhracat / İthalat Trendi", "Yıl", "Milyar $")
    fig.tight_layout(); return fig


def fig_denge(df):
    fig, ax = plt.subplots(figsize=(10, 4)); fig.patch.set_facecolor(PALETTE["bg"])
    renkler = [PALETTE["denge_pos"] if v >= 0 else PALETTE["denge_neg"] for v in df["Dis_Ticaret_Dengesi"]]
    ax.bar(df["Yil"], df["Dis_Ticaret_Dengesi"], color=renkler, alpha=0.85, width=0.7, edgecolor="#0d1b2a")
    ax.axhline(0, color="#64748b", lw=1.2)
    apply_dark_theme(ax, "Dış Ticaret Dengesi", "Yıl", "Milyar $")
    fig.tight_layout(); return fig


def fig_karsilama(df):
    fig, ax = plt.subplots(figsize=(10, 4)); fig.patch.set_facecolor(PALETTE["bg"])
    ax.plot(df["Yil"], df["Karsilama_Orani"], color=PALETTE["karsilama"], lw=2.5, marker="D", ms=4)
    ax.fill_between(df["Yil"], df["Karsilama_Orani"], 100, where=[v < 100 for v in df["Karsilama_Orani"]], alpha=0.15, color=PALETTE["denge_neg"])
    ax.axhline(100, color="#64748b", lw=1.2, ls="--", label="Denge (%100)")
    ax.legend(facecolor="#0f2744", edgecolor=PALETTE["spine"], labelcolor=PALETTE["text"], fontsize=9)
    apply_dark_theme(ax, "İhracatın İthalatı Karşılama Oranı (%)", "Yıl", "%")
    fig.tight_layout(); return fig


def fig_degisim(df):
    df2 = df.dropna(subset=["Ihracat_Degisim", "Ithalat_Degisim"])
    fig, ax = plt.subplots(figsize=(10, 4)); fig.patch.set_facecolor(PALETTE["bg"])
    x = np.arange(len(df2)); w = 0.35
    ax.bar(x - w/2, df2["Ihracat_Degisim"], w, label="İhracat %", color=PALETTE["ihracat"], alpha=0.85, edgecolor="#0d1b2a")
    ax.bar(x + w/2, df2["Ithalat_Degisim"], w, label="İthalat %", color=PALETTE["ithalat"], alpha=0.85, edgecolor="#0d1b2a")
    ax.set_xticks(x); ax.set_xticklabels(df2["Yil"].astype(str), rotation=45, ha="right", fontsize=8)
    ax.axhline(0, color="#64748b", lw=1)
    ax.legend(facecolor="#0f2744", edgecolor=PALETTE["spine"], labelcolor=PALETTE["text"], fontsize=9)
    apply_dark_theme(ax, "Yıllık Değişim Oranları (%)", "Yıl", "%")
    fig.tight_layout(); return fig


def fig_tahmin(df, sonuc, hedef):
    fig, ax = plt.subplots(figsize=(10, 4)); fig.patch.set_facecolor(PALETTE["bg"])
    renk = PALETTE["ihracat"] if hedef == "Ihracat" else PALETTE["ithalat"]
    ax.plot(df["Yil"], df[hedef], color=renk, lw=2.5, marker="o", ms=4, label=f"Gerçek {hedef}")
    ax.plot(sonuc["gelecek_yillar"], sonuc["tahmin_degerleri"], color=PALETTE["tahmin"], lw=2.5, marker="*", ms=8, ls="--", label="Tahmin")
    ax.plot([df["Yil"].iloc[-1], sonuc["gelecek_yillar"][0]], [df[hedef].iloc[-1], sonuc["tahmin_degerleri"][0]], color=PALETTE["tahmin"], lw=1.5, ls="--")
    ax.legend(facecolor="#0f2744", edgecolor=PALETTE["spine"], labelcolor=PALETTE["text"], fontsize=9)
    apply_dark_theme(ax, f"{hedef} Tahmin Grafiği", "Yıl", "Milyar $")
    fig.tight_layout(); return fig


def fig_feature_importance(sonuc):
    fi = sonuc["feature_importance"]
    if not fi: return None
    fig, ax = plt.subplots(figsize=(7, 3.5)); fig.patch.set_facecolor(PALETTE["bg"])
    keys, vals = zip(*sorted(zip(fi.values(), fi.keys())))
    ax.barh(vals, keys, color=PALETTE["hacim"], alpha=0.85, edgecolor="#0d1b2a")
    apply_dark_theme(ax, "Random Forest – Özellik Önemi", "Önem Skoru", "Özellik")
    fig.tight_layout(); return fig


# ══════════════════════════════════════════════════════════════════════════════
# BÖLÜM 5: KARAR DESTEK SİSTEMİ
# ══════════════════════════════════════════════════════════════════════════════
def generate_recommendations(df: pd.DataFrame) -> list:
    oneriler = []
    son = df.iloc[-1]; son_3 = df.tail(3)
    k = son["Karsilama_Orani"]
    if k < 60:
        oneriler.append({"seviye":"error","baslik":"🚨 Kritik: Düşük Karşılama Oranı", "aciklama":f"İhracatın ithalatı karşılama oranı **%{k:.1f}** ile kritik seviyenin altındadır (%60). Döviz rezervlerinde ciddi baskı oluşabilir. Acil ihracat teşvik programları değerlendirilmelidir."})
    elif k < 80:
        oneriler.append({"seviye":"warning","baslik":"⚠️ Uyarı: Zayıf Karşılama Oranı", "aciklama":f"Karşılama oranı **%{k:.1f}** ile zayıf seviyededir. İhracatın artırılması ve ithalat bağımlılığının azaltılması önerilir."})
    elif k >= 100:
        oneriler.append({"seviye":"success","baslik":"✅ Dış Ticaret Fazlası", "aciklama":f"İhracat ithalatı **%{k:.1f}** oranında karşılamaktadır. Dış ticaret dengesi olumlu seyretmektedir."})
    else:
        oneriler.append({"seviye":"info","baslik":"ℹ️ Makul Karşılama Oranı", "aciklama":f"Karşılama oranı **%{k:.1f}** olup kabul edilebilir aralıktadır."})
    if len(df) >= 3:
        it = son_3["Ithalat"].pct_change().mean() * 100
        if it > 10:
            oneriler.append({"seviye":"warning","baslik":"⚠️ İthalat Hızla Artıyor", "aciklama":f"Son 3 yılda ithalat ortalama **%{it:.1f}** büyümektedir. Yerli ikame araştırılmalıdır."})
        ih = son_3["Ihracat"].pct_change().mean() * 100
        if ih < 0:
            oneriler.append({"seviye":"error","baslik":"🚨 İhracat Düşüş Eğiliminde", "aciklama":f"Son 3 yılda ihracat ortalama **%{abs(ih):.1f}** gerilemiştir. Pazar çeşitlendirmesi şarttır."})
        elif ih > 15:
            oneriler.append({"seviye":"success","baslik":"📈 İhracatta Güçlü Büyüme", "aciklama":f"Son 3 yılda ihracat ortalama **%{ih:.1f}** büyümüştür. Lojistik altyapı güçlendirilmelidir."})
    if len(df) >= 2:
        hd = df["Ticaret_Hacmi"].pct_change().iloc[-1] * 100
        if hd > 0:
            oneriler.append({"seviye":"info","baslik":"📊 Ticaret Hacmi Artıyor", "aciklama":f"Toplam ticaret hacmi son yılda **%{hd:.1f}** büyümüştür ({son['Ticaret_Hacmi']:.1f} Milyar $)."})
    acik_oran = abs(son["Dis_Ticaret_Dengesi"]) / son["Ticaret_Hacmi"] * 100
    if acik_oran > 20 and son["Dis_Ticaret_Dengesi"] < 0:
        oneriler.append({"seviye":"warning","baslik":"⚠️ Yüksek Ticaret Açığı", "aciklama":f"Dış ticaret açığı **{abs(son['Dis_Ticaret_Dengesi']):.1f} Milyar $** – ticaret hacminin **%{acik_oran:.1f}**'ini oluşturmaktadır."})
    return oneriler


# ══════════════════════════════════════════════════════════════════════════════
# BÖLÜM 6: PDF RAPOR
# ══════════════════════════════════════════════════════════════════════════════
def fig_to_image(fig, dpi=150):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor()); buf.seek(0); return buf.read()

_C = {
    "title":colors.HexColor("#0f4c75"),"head1":colors.HexColor("#1b6ca8"),"head2":colors.HexColor("#1a936f"),"head3":colors.HexColor("#117a65"),
    "row_a":colors.HexColor("#eaf4fb"),"row_b":colors.white,"grid":colors.HexColor("#b0cce4"),"rule":colors.HexColor("#1b6ca8"),
    "err_c":colors.HexColor("#c1121f"),"err_bg":colors.HexColor("#fff0f0"),"warn_c":colors.HexColor("#d97706"),"warn_bg":colors.HexColor("#fffbeb"),
    "ok_c":colors.HexColor("#2d6a4f"),"ok_bg":colors.HexColor("#f0faf5"),"info_c":colors.HexColor("#1b6ca8"),"info_bg":colors.HexColor("#f0f7ff"),
}


def _pdf_safe_text(text):
    repl = {"🚨":"", "⚠️":"", "✅":"", "ℹ️":"", "📈":"", "📊":"", "💡":"", "📄":""}
    text = str(text)
    for a, b in repl.items(): text = text.replace(a, b)
    return text


def _P(text, style): return Paragraph(_pdf_safe_text(text), style)


def create_pdf_report(df, oneriler, tahmin_sonuc, hedef, model_adi) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    S = getSampleStyleSheet()
    def sty(name, parent="Normal", fn=None, **kw): return ParagraphStyle(name, parent=S[parent], fontName=(fn or _F), **kw)
    title_sty = sty("T","Title",fn=_FB,fontSize=20,textColor=_C["title"],alignment=TA_CENTER,spaceAfter=6)
    sub_sty = sty("Sub","Normal",fontSize=10,textColor=colors.HexColor("#555555"),alignment=TA_CENTER,spaceAfter=4)
    h2_sty = sty("H2","Normal",fn=_FB,fontSize=13,textColor=_C["title"],spaceBefore=14,spaceAfter=6)
    body_sty = sty("BD","Normal",fontSize=9.5,leading=14,spaceAfter=5)
    cap_sty = sty("CP","Normal",fn=_FI,fontSize=8,textColor=colors.HexColor("#6b7280"),alignment=TA_CENTER,spaceAfter=8)
    th_sty = sty("TH","Normal",fn=_FB,fontSize=9,textColor=colors.white,alignment=TA_CENTER)
    td_sty = sty("TD","Normal",fontSize=9,alignment=TA_CENTER)
    def make_table(rows, col_widths, hdr_color=None, row_colors=None):
        hdr_color = hdr_color or _C["head1"]; row_colors = row_colors or [_C["row_a"], _C["row_b"]]
        pdf_rows = [[_P(cell, th_sty) for cell in rows[0]]]
        for row in rows[1:]: pdf_rows.append([_P(cell, td_sty) for cell in row])
        t = Table(pdf_rows, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),hdr_color),("ROWBACKGROUNDS",(0,1),(-1,-1),row_colors),("GRID",(0,0),(-1,-1),0.4,_C["grid"]),("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6)])); return t
    story=[]; now=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"); son=df.iloc[-1]
    story += [Spacer(1,1.5*cm),_P("DIŞ TİCARET",title_sty),_P("KARAR DESTEK SİSTEMİ RAPORU",title_sty),Spacer(1,.4*cm),HRFlowable(width="100%",thickness=2,color=_C["rule"]),Spacer(1,.4*cm),_P(f"Veri Aralığı : {df['Yil'].min()} – {df['Yil'].max()}",sub_sty),_P(f"Kayıt Sayısı : {len(df)}",sub_sty),_P(f"Rapor Tarihi : {now}",sub_sty),Spacer(1,1.5*cm)]
    story.append(make_table([["Gösterge","Değer"],["Son Yıl İhracat",f"{son['Ihracat']:.1f} Milyar $"],["Son Yıl İthalat",f"{son['Ithalat']:.1f} Milyar $"],["Denge",f"{son['Dis_Ticaret_Dengesi']:+.1f} Milyar $"],["Karşılama Oranı",f"%{son['Karsilama_Orani']:.1f}"],["Ticaret Hacmi",f"{son['Ticaret_Hacmi']:.1f} Milyar $"]],[7*cm,7*cm],hdr_color=_C["head2"],row_colors=[_C["ok_bg"],colors.white])); story.append(PageBreak())
    story += [_P("1. Veri Tablosu",h2_sty),_P("Analiz kapsamındaki ham ve hesaplanmış göstergeler.",body_sty)]
    rows=[["Yıl","İhracat ($M)","İthalat ($M)","Denge ($M)","Karş. %","Hacim ($M)"]]
    for _,r in df.iterrows(): rows.append([str(int(r["Yil"])),f"{r['Ihracat']:.1f}",f"{r['Ithalat']:.1f}",f"{r['Dis_Ticaret_Dengesi']:+.1f}",f"%{r['Karsilama_Orani']:.1f}",f"{r['Ticaret_Hacmi']:.1f}"])
    story.append(make_table(rows,[1.8*cm,2.8*cm,2.8*cm,2.8*cm,2.8*cm,2.8*cm])); story.append(PageBreak())
    story.append(_P("2. Grafikler",h2_sty))
    for fn,cap in [(fig_trend,"Şekil 1: İhracat / İthalat Trendi"),(fig_denge,"Şekil 2: Dış Ticaret Dengesi"),(fig_karsilama,"Şekil 3: Karşılama Oranı"),(fig_degisim,"Şekil 4: Yıllık Değişim Oranları")]:
        f=fn(df); story.append(RLImage(io.BytesIO(fig_to_image(f)),width=16*cm,height=6.5*cm)); story.append(_P(cap,cap_sty)); plt.close(f)
    story.append(PageBreak())
    if tahmin_sonuc:
        story += [_P("3. Tahminleme Sonuçları",h2_sty),_P(f"Model: {model_adi}  |  Hedef: {hedef}",body_sty)]
        story.append(make_table([["Metrik","Değer"],["R² Skoru",f"{tahmin_sonuc['r2']:.4f}"],["MAE (Milyar $)",f"{tahmin_sonuc['mae']:.2f}"]],[8*cm,6*cm],hdr_color=_C["head3"],row_colors=[_C["ok_bg"],colors.white]))
        story.append(Spacer(1,.4*cm)); pred_rows=[["Yıl",f"Tahmini {hedef} (Milyar $")]]+[[str(y),f"{p:.2f}"] for y,p in zip(tahmin_sonuc["gelecek_yillar"],tahmin_sonuc["tahmin_degerleri"])]
        story.append(make_table(pred_rows,[5*cm,8*cm])); ft=fig_tahmin(df,tahmin_sonuc,hedef); story += [Spacer(1,.3*cm),RLImage(io.BytesIO(fig_to_image(ft)),width=16*cm,height=6.5*cm),_P("Şekil 5: Tahmin Grafiği",cap_sty)]; plt.close(ft); story.append(PageBreak())
    story.append(_P("4. Karar Destek Önerileri",h2_sty)); sev_map={"error":(_C["err_c"],_C["err_bg"]),"warning":(_C["warn_c"],_C["warn_bg"]),"success":(_C["ok_c"],_C["ok_bg"]),"info":(_C["info_c"],_C["info_bg"])}
    for o in oneriler:
        bc,bg=sev_map[o["seviye"]]; b_sty=sty(f"ob{o['seviye']}","Normal",fn=_FB,fontSize=10,textColor=bc); a_sty=sty(f"oa{o['seviye']}","Normal",fontSize=9)
        kutu=Table([[_P(o["baslik"],b_sty)],[_P(o["aciklama"].replace("**",""),a_sty)]],colWidths=[16*cm]); kutu.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),("BOX",(0,0),(-1,-1),.8,bc)])); story += [kutu,Spacer(1,.25*cm)]
    story.append(PageBreak()); story.append(_P("5. Sonuç",h2_sty)); story.append(_P(f"Bu rapor, {df['Yil'].min()}–{df['Yil'].max()} yılları arasındaki {len(df)} yıllık dış ticaret verisi analiz edilerek hazırlanmıştır. Son yıl ihracat <b>{son['Ihracat']:.1f}</b>, ithalat <b>{son['Ithalat']:.1f}</b> Milyar $; karşılama oranı <b>%{son['Karsilama_Orani']:.1f}</b>, denge <b>{son['Dis_Ticaret_Dengesi']:+.1f}</b> Milyar $. Sistem toplam <b>{len(oneriler)}</b> öneri üretmiştir.",body_sty))
    story += [Spacer(1,1*cm),HRFlowable(width="100%",thickness=1,color=_C["grid"]),Spacer(1,.3*cm),_P(f"Rapor {now} tarihinde Dış Ticaret Karar Destek Sistemi tarafından otomatik oluşturulmuştur.",cap_sty)]
    doc.build(story); buffer.seek(0); return buffer.read()


# ══════════════════════════════════════════════════════════════════════════════
# BÖLÜM 7: ANA UYGULAMA
# ══════════════════════════════════════════════════════════════════════════════
def initialize_session_state():
    defaults={"df_raw":None,"df_clean":None,"df_indicators":None,"uyarilar":[],"tahmin_sonuc":None,"tahmin_hedef":"Ihracat","tahmin_model":"Linear Regression","data_loaded":False}
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v


def sidebar_panel():
    with st.sidebar:
        st.markdown("""<div style='text-align:center;padding:16px 0 8px'><div style='font-size:2.5rem'>📊</div><div style='font-size:.95rem;color:#60a5fa;font-weight:700;letter-spacing:.5px'>DIŞ TİCARET</div><div style='font-size:.78rem;color:#64748b'>Karar Destek Sistemi</div></div><hr style='border-color:#1e3a5f;margin:8px 0 16px'>""",unsafe_allow_html=True)
        st.markdown("### ⚙️ Sistem Ayarları")
        if st.button("📥 Örnek Veri Yükle",use_container_width=True):
            df_raw=load_sample_data(); df_clean,uyarilar=clean_data(df_raw); df_ind=calculate_indicators(df_clean)
            st.session_state.df_raw=df_raw; st.session_state.df_clean=df_clean; st.session_state.df_indicators=df_ind; st.session_state.uyarilar=uyarilar; st.session_state.data_loaded=True; st.session_state.tahmin_sonuc=None; st.success("Örnek veri yüklendi!"); st.rerun()
        st.markdown("---")
        if st.session_state.data_loaded:
            df=st.session_state.df_indicators; st.markdown(f"""<div style='background:#14532d22;border:1px solid #22c55e44;border-radius:8px;padding:12px;font-size:.82rem;color:#86efac'>✅ <b>Veri Aktif</b><br>📅 {df['Yil'].min()} – {df['Yil'].max()}<br>📋 {len(df)} kayıt</div>""",unsafe_allow_html=True)
        else:
            st.markdown("""<div style='background:#7c2d1222;border:1px solid #f9731644;border-radius:8px;padding:12px;font-size:.82rem;color:#fdba74'>⚠️ Veri yüklenmedi</div>""",unsafe_allow_html=True)
        st.markdown("---"); st.markdown("""<div style='font-size:.75rem;color:#475569;line-height:1.6'><b>Kullanım Kılavuzu</b><br>1. <i>Veri Girişi</i> sekmesine git<br>2. CSV yükle veya veri gir<br>3. Diğer sekmeleri incele</div>""",unsafe_allow_html=True)


def sec(title): st.markdown(f'<div class="section-title">{title}</div>',unsafe_allow_html=True)


def tab_veri_girisi():
    sec("Veri Girişi"); col1,col2=st.columns(2,gap="large")
    with col1:
        st.markdown("#### 📂 CSV Dosyası Yükle"); st.markdown("""<div style='background:#1e3a5f22;border:1px solid #2563eb33;border-radius:8px;padding:12px;font-size:.82rem;color:#94a3b8;margin-bottom:12px'>CSV sütunları: <code style='color:#60a5fa'>Yil, Ihracat, Ithalat</code></div>""",unsafe_allow_html=True)
        uploaded=st.file_uploader("CSV seçin",type=["csv"],label_visibility="collapsed")
        if uploaded:
            try:
                df_raw=read_csv_smart(uploaded); df_clean,uyarilar=clean_data(df_raw); df_ind=calculate_indicators(df_clean)
                st.session_state.df_raw=df_raw; st.session_state.df_clean=df_clean; st.session_state.df_indicators=df_ind; st.session_state.uyarilar=uyarilar; st.session_state.data_loaded=True; st.session_state.tahmin_sonuc=None; st.success(f"✅ Dosya yüklendi! {len(df_clean)} kayıt.")
            except Exception as e: st.error(f"Hata: {e}")
        st.download_button("📄 Örnek CSV İndir",load_sample_data().to_csv(index=False).encode("utf-8-sig"),"ornek_dis_ticaret.csv","text/csv",use_container_width=True)
    with col2:
        st.markdown("#### ✏️ Elle Veri Girişi")
        with st.form("manual_entry"):
            yil=st.number_input("Yıl",1900,2100,2024,step=1); ihr=st.number_input("İhracat (Milyar $)",0.0,step=0.1); ith=st.number_input("İthalat (Milyar $)",0.0,step=0.1)
            if st.form_submit_button("➕ Satır Ekle",use_container_width=True):
                yeni=pd.DataFrame({"Yil":[yil],"Ihracat":[ihr],"Ithalat":[ith]}); base=(st.session_state.df_clean[["Yil","Ihracat","Ithalat"]] if st.session_state.df_clean is not None else pd.DataFrame()); df_clean,uyarilar=clean_data(pd.concat([base,yeni],ignore_index=True)); st.session_state.df_clean=df_clean; st.session_state.df_indicators=calculate_indicators(df_clean); st.session_state.uyarilar=uyarilar; st.session_state.data_loaded=True; st.session_state.tahmin_sonuc=None; st.success(f"Yıl {yil} eklendi."); st.rerun()
    for u in st.session_state.uyarilar: st.warning(u)
    if st.session_state.data_loaded:
        st.markdown("---"); sec("Veri Önizleme"); st.dataframe(st.session_state.df_clean.style.format({"Ihracat":"{:.1f}","Ithalat":"{:.1f}"}),use_container_width=True); st.download_button("💾 Temizlenmiş CSV İndir",st.session_state.df_clean.to_csv(index=False).encode("utf-8-sig"),"temiz_dis_ticaret.csv","text/csv")


def tab_veri_analizi():
    if not st.session_state.data_loaded: st.info("Lütfen önce veri yükleyin."); return
    df=st.session_state.df_indicators; son=df.iloc[-1]; sec("Özet Göstergeler"); cols=st.columns(5)
    cards=[("İhracat",f"{son['Ihracat']:.1f}","Milyar $",son.get("Ihracat_Degisim")),("İthalat",f"{son['Ithalat']:.1f}","Milyar $",son.get("Ithalat_Degisim")),("Denge",f"{son['Dis_Ticaret_Dengesi']:+.1f}","Milyar $",None),("Karş. Oranı",f"%{son['Karsilama_Orani']:.1f}","",None),("Ticaret Hacmi",f"{son['Ticaret_Hacmi']:.1f}","Milyar $",son.get("Hacim_Degisim"))]
    for col,(lbl,val,unit,delta) in zip(cols,cards):
        with col:
            d_html=""
            if delta is not None and not np.isnan(delta):
                cls="delta-pos" if delta>=0 else "delta-neg"; sign="▲" if delta>=0 else "▼"; d_html=f'<div class="delta {cls}">{sign} %{abs(delta):.1f}</div>'
            st.markdown(f'<div class="metric-card"><div class="label">{lbl}</div><div class="value">{val}</div><div style="font-size:.7rem;color:#64748b">{unit}</div>{d_html}</div>',unsafe_allow_html=True)
    sec("İstatistiksel Özet"); istat=df[["Ihracat","Ithalat","Dis_Ticaret_Dengesi","Karsilama_Orani","Ticaret_Hacmi"]].describe().T; istat.index=["İhracat","İthalat","DTD","Karş. Oranı","Hacim"]; st.dataframe(istat.style.format("{:.2f}"),use_container_width=True)
    sec("Tüm Göstergeler Tablosu"); disp=df[["Yil","Ihracat","Ithalat","Dis_Ticaret_Dengesi","Karsilama_Orani","Ticaret_Hacmi","Ihracat_Degisim","Ithalat_Degisim"]].rename(columns={"Yil":"Yıl","Ihracat":"İhracat ($M)","Ithalat":"İthalat ($M)","Dis_Ticaret_Dengesi":"DTD ($M)","Karsilama_Orani":"Karş. %","Ticaret_Hacmi":"Hacim ($M)","Ihracat_Degisim":"İhr. %","Ithalat_Degisim":"İth. %"}); st.dataframe(disp.style.format({c:"{:.1f}" for c in disp.columns if c!="Yıl"}),use_container_width=True)


def tab_grafikler():
    if not st.session_state.data_loaded: st.info("Lütfen önce veri yükleyin."); return
    df=st.session_state.df_indicators; sec("İhracat / İthalat Trendi"); st.pyplot(fig_trend(df),use_container_width=True); c1,c2=st.columns(2,gap="medium")
    with c1: sec("Dış Ticaret Dengesi"); st.pyplot(fig_denge(df),use_container_width=True)
    with c2: sec("Karşılama Oranı"); st.pyplot(fig_karsilama(df),use_container_width=True)
    sec("Yıllık Değişim Oranları"); st.pyplot(fig_degisim(df),use_container_width=True)


def tab_tahminleme():
    if not st.session_state.data_loaded: st.info("Lütfen önce veri yükleyin."); return
    df=st.session_state.df_indicators; sec("Tahminleme Ayarları"); c1,c2,c3=st.columns(3); hedef=c1.selectbox("Tahmin Hedefi",["Ihracat","Ithalat"],key="hedef_sel"); model_adi=c2.selectbox("Model",["Linear Regression","Random Forest"],key="model_sel"); n_yil=c3.slider("Kaç Yıl İleri?",1,10,5,key="tahmin_yil_sel")
    if st.button("🚀 Modeli Eğit ve Tahmin Et",use_container_width=True):
        if len(df)<5: st.error("En az 5 yıllık veri gereklidir."); return
        with st.spinner("Model eğitiliyor…"): sonuc=train_and_forecast(df,hedef,model_adi,n_yil)
        st.session_state.tahmin_sonuc=sonuc; st.session_state.tahmin_hedef=hedef; st.session_state.tahmin_model=model_adi; st.success("Model başarıyla eğitildi!")
    if st.session_state.tahmin_sonuc:
        sonuc=st.session_state.tahmin_sonuc; hedef=st.session_state.tahmin_hedef; sec("Model Performansı"); m1,m2=st.columns(2); r2_cls="delta-pos" if sonuc["r2"]>0.8 else "delta-neg"
        with m1: st.markdown(f'<div class="metric-card"><div class="label">R² Skoru</div><div class="value {r2_cls}">{sonuc["r2"]}</div><div style="font-size:.72rem;color:#64748b">0.8+ ideal</div></div>',unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="metric-card"><div class="label">MAE</div><div class="value">{sonuc["mae"]}</div><div style="font-size:.72rem;color:#64748b">Ort. Mutlak Hata (Milyar $)</div></div>',unsafe_allow_html=True)
        sec("Tahmin Sonuçları"); st.dataframe(pd.DataFrame({"Yıl":sonuc["gelecek_yillar"],f"Tahmini {hedef} (Milyar $)":sonuc["tahmin_degerleri"]}),use_container_width=True); sec("Tahmin Grafiği"); st.pyplot(fig_tahmin(df,sonuc,hedef),use_container_width=True)
        if sonuc["feature_importance"]:
            sec("Özellik Önemi"); fig_fi=fig_feature_importance(sonuc)
            if fig_fi: st.pyplot(fig_fi,use_container_width=True)


def tab_karar_destek():
    if not st.session_state.data_loaded: st.info("Lütfen önce veri yükleyin."); return
    oneriler=generate_recommendations(st.session_state.df_indicators); sec("Karar Destek Önerileri"); st.markdown(f"Sistem **{len(oneriler)}** öneri üretmiştir."); sayac={"error":0,"warning":0,"success":0,"info":0}
    for o in oneriler: sayac[o["seviye"]]+=1
    c1,c2,c3,c4=st.columns(4)
    for col,(lbl,sev,bg,brd) in zip([c1,c2,c3,c4],[("🚨 Kritik","error","#7f1d1d","#ef4444"),("⚠️ Uyarı","warning","#78350f","#f59e0b"),("✅ Olumlu","success","#14532d","#22c55e"),("ℹ️ Bilgi","info","#1e3a5f","#60a5fa")]):
        with col: st.markdown(f'<div style="background:{bg}33;border:1px solid {brd}44;border-radius:10px;padding:14px;text-align:center"><div style="font-size:1.8rem;font-weight:700;color:{brd}">{sayac[sev]}</div><div style="font-size:.78rem;color:#94a3b8">{lbl}</div></div>',unsafe_allow_html=True)
    st.markdown("---"); fn_map={"error":st.error,"warning":st.warning,"success":st.success,"info":st.info}
    for o in oneriler: fn_map[o["seviye"]](f"**{o['baslik']}**\n\n{o['aciklama']}")


def tab_pdf_rapor():
    if not st.session_state.data_loaded: st.info("Lütfen önce veri yükleyin."); return
    df=st.session_state.df_indicators; sec("PDF Rapor Oluştur"); st.markdown("Analiz, grafikler, tahmin sonuçları ve karar destek önerilerini tek bir PDF raporunda dışa aktarabilirsiniz.")
    oneriler=generate_recommendations(df); tahmin=st.session_state.tahmin_sonuc; hedef=st.session_state.tahmin_hedef; model=st.session_state.tahmin_model
    try:
        pdf=create_pdf_report(df,oneriler,tahmin,hedef,model); st.download_button("📄 PDF Raporunu İndir",pdf,"dis_ticaret_karar_destek_raporu.pdf","application/pdf",use_container_width=True)
    except Exception as e: st.error(f"PDF oluşturulamadı: {e}")


def main():
    inject_custom_css(); initialize_session_state(); sidebar_panel()
    st.markdown("""<div class='main-header'><h1>📊 Dış Ticaret Karar Destek Sistemi</h1><p>Foreign Trade Analytics • Forecasting • Decision Support • Automated Reporting</p></div>""",unsafe_allow_html=True)
    tabs=st.tabs(["📥 Veri Girişi","📊 Veri Analizi","📈 Grafikler","🤖 Tahminleme","💡 Karar Destek","📄 PDF Rapor"])
    with tabs[0]: tab_veri_girisi()
    with tabs[1]: tab_veri_analizi()
    with tabs[2]: tab_grafikler()
    with tabs[3]: tab_tahminleme()
    with tabs[4]: tab_karar_destek()
    with tabs[5]: tab_pdf_rapor()
    st.markdown("<div class='footer'>Dış Ticaret Karar Destek Sistemi • Version 2.1</div>",unsafe_allow_html=True)


if __name__ == "__main__":
    main()
