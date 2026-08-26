"""
Dış Ticaret Karar Destek Sistemi
Foreign Trade Decision Support System

Portfolio version aligned with the accompanying academic study.
"""

import io
import os
import glob
import datetime
import warnings

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from matplotlib import font_manager
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    PageBreak,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Dış Ticaret Karar Destek Sistemi",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

SAMPLE_DATA = pd.DataFrame(
    {
        "Yil": list(range(2010, 2024)),
        "Ihracat": [
            113.9, 134.9, 152.5, 151.8, 157.6, 143.8, 142.5,
            157.0, 168.0, 180.8, 169.6, 225.2, 254.2, 255.8,
        ],
        "Ithalat": [
            185.5, 240.8, 236.5, 251.7, 242.2, 207.2, 198.6,
            233.8, 223.0, 210.3, 219.5, 271.4, 363.7, 361.8,
        ],
    }
)


def inject_css():
    st.markdown(
        """
        <style>
        .stApp {background: linear-gradient(135deg,#0a0e1a,#0d1b2a 50%,#0a1628); color:#e2e8f0;}
        .main-header {background:linear-gradient(90deg,#1a3a5c,#0f2744,#1a3a5c);
            border:1px solid #2563eb44;border-radius:16px;padding:28px 36px;
            margin-bottom:24px;text-align:center;}
        .main-header h1 {font-size:2.05rem;font-weight:800;margin:0;color:#e2e8f0;}
        .main-header p {color:#94a3b8;margin:7px 0 0;}
        .metric-card {background:linear-gradient(135deg,#1e3a5f,#162d4a);
            border:1px solid #2563eb33;border-radius:14px;padding:18px;text-align:center;}
        .metric-card .label {font-size:.76rem;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;}
        .metric-card .value {font-size:1.65rem;font-weight:700;color:#60a5fa;margin-top:6px;}
        .section-title {font-size:1.2rem;font-weight:700;color:#60a5fa;
            border-left:4px solid #2563eb;padding-left:10px;margin:20px 0 14px;}
        section[data-testid="stSidebar"] {background:linear-gradient(180deg,#0d1b2a,#0a1628);
            border-right:1px solid #1e3a5f;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _normalize_col_name(text: str) -> str:
    text = str(text).strip().lower()
    text = text.translate(
        str.maketrans(
            {
                "ı": "i", "İ": "i", "ğ": "g", "Ğ": "g",
                "ü": "u", "Ü": "u", "ş": "s", "Ş": "s",
                "ö": "o", "Ö": "o", "ç": "c", "Ç": "c",
            }
        )
    )
    return text.replace(" ", "_").replace("-", "_")


def read_csv_smart(uploaded_file) -> pd.DataFrame:
    raw = uploaded_file.getvalue()
    last_error = None
    for encoding in ("utf-8-sig", "utf-8", "cp1254", "latin1"):
        for sep in (None, ";", ",", "\t"):
            try:
                df = pd.read_csv(
                    io.BytesIO(raw), encoding=encoding, sep=sep, engine="python"
                )
                if len(df.columns) >= 3:
                    return df
            except Exception as exc:
                last_error = exc
    raise ValueError(
        "CSV okunamadı. Beklenen temel sütunlar: Yil, Ihracat, Ithalat. "
        f"Detay: {last_error}"
    )


def clean_data(df: pd.DataFrame):
    warnings_list = []
    initial_count = len(df)
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    rename_map = {}
    for col in df.columns:
        normalized = _normalize_col_name(col)
        if normalized in {"yil", "year", "tarih"} or "yil" in normalized or "year" in normalized:
            rename_map[col] = "Yil"
        elif "ihracat" in normalized or "export" in normalized:
            rename_map[col] = "Ihracat"
        elif "ithalat" in normalized or "import" in normalized:
            rename_map[col] = "Ithalat"

    df = df.rename(columns=rename_map)
    required = ["Yil", "Ihracat", "Ithalat"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Eksik sütun(lar): {', '.join(missing)}")

    for col in required:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    before = len(df)
    df = df.dropna(subset=required)
    if len(df) < before:
        warnings_list.append(f"{before - len(df)} eksik/geçersiz satır kaldırıldı.")

    before = len(df)
    df = df[(df["Ihracat"] >= 0) & (df["Ithalat"] > 0)]
    if len(df) < before:
        warnings_list.append(
            f"{before - len(df)} negatif veya sıfır ithalat değeri içeren satır kaldırıldı."
        )

    df = df[(df["Yil"] >= 1900) & (df["Yil"] <= 2100)]
    df["Yil"] = df["Yil"].astype(int)
    df = (
        df.sort_values("Yil")
        .drop_duplicates(subset=["Yil"], keep="last")
        .reset_index(drop=True)
    )

    removed = initial_count - len(df)
    if removed > 0:
        warnings_list.append(f"Toplam {removed} satır temizlendi.")

    if df.empty:
        raise ValueError("Temizleme sonrasında kullanılabilir veri kalmadı.")

    return df, warnings_list


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["Dis_Ticaret_Dengesi"] = result["Ihracat"] - result["Ithalat"]
    result["Ticaret_Hacmi"] = result["Ihracat"] + result["Ithalat"]
    result["Karsilama_Orani"] = result["Ihracat"] / result["Ithalat"] * 100
    result["Ihracat_Degisim"] = result["Ihracat"].pct_change() * 100
    result["Ithalat_Degisim"] = result["Ithalat"].pct_change() * 100
    result["Hacim_Degisim"] = result["Ticaret_Hacmi"].pct_change() * 100
    return result


def _target_features(df: pd.DataFrame, target: str):
    d = df[["Yil", target]].copy()
    d["Lag1"] = d[target].shift(1)
    d["Lag2"] = d[target].shift(2)
    d["MA3"] = d[target].shift(1).rolling(3).mean()
    d = d.dropna().reset_index(drop=True)
    X = d[["Yil", "Lag1", "Lag2", "MA3"]].values
    y = d[target].values
    return X, y


def train_and_forecast(
    df: pd.DataFrame, target: str, model_name: str, forecast_years: int
) -> dict:
    X, y = _target_features(df, target)
    if len(X) < 5:
        raise ValueError("Model değerlendirmesi için en az 8 yıllık veri önerilir.")

    test_size = max(2, int(round(len(X) * 0.2)))
    if len(X) - test_size < 2:
        test_size = 2

    X_train, X_test = X[:-test_size], X[-test_size:]
    y_train, y_test = y[:-test_size], y[-test_size:]

    if model_name == "Linear Regression":
        model = LinearRegression()
    else:
        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=5,
            random_state=42,
            n_jobs=-1,
        )

    model.fit(X_train, y_train)
    test_pred = model.predict(X_test)

    r2 = float(r2_score(y_test, test_pred)) if len(y_test) >= 2 else np.nan
    mae = float(mean_absolute_error(y_test, test_pred))

    feature_importance = None
    if model_name == "Random Forest":
        feature_importance = dict(
            zip(["Yıl", "Lag-1", "Lag-2", "MA-3"], model.feature_importances_)
        )

    history = list(df[target].astype(float))
    years = []
    predictions = []
    last_year = int(df["Yil"].iloc[-1])

    for step in range(1, forecast_years + 1):
        year = last_year + step
        lag1 = history[-1]
        lag2 = history[-2]
        ma3 = float(np.mean(history[-3:]))
        pred = max(float(model.predict([[year, lag1, lag2, ma3]])[0]), 0.0)
        years.append(year)
        predictions.append(round(pred, 2))
        history.append(pred)

    return {
        "model": model,
        "r2": r2,
        "mae": mae,
        "years": years,
        "predictions": predictions,
        "feature_importance": feature_importance,
    }


def generate_recommendations(df: pd.DataFrame) -> list:
    latest = df.iloc[-1]
    previous = df.iloc[-2] if len(df) >= 2 else None
    recommendations = []

    coverage = latest["Karsilama_Orani"]
    if coverage < 60:
        recommendations.append(
            ("error", "Kritik karşılama oranı",
             f"Karşılama oranı %{coverage:.1f}. Acil ihracat artırımı ve ithal ikamesi değerlendirilmelidir.")
        )
    elif coverage < 75:
        recommendations.append(
            ("warning", "Zayıf karşılama oranı",
             f"Karşılama oranı %{coverage:.1f}. İhracat artışı ve ithalat bağımlılığının azaltılması önerilir.")
        )
    else:
        recommendations.append(
            ("success", "Karşılama oranı",
             f"Karşılama oranı %{coverage:.1f}. İzleme sürdürülmelidir.")
        )

    if latest["Dis_Ticaret_Dengesi"] < 0:
        recommendations.append(
            ("warning", "Dış ticaret açığı",
             f"Açık {abs(latest['Dis_Ticaret_Dengesi']):.1f} milyar $. Yerli üretim ve tedarik çeşitlendirmesi değerlendirilebilir.")
        )

    if previous is not None:
        if latest["Ihracat"] < previous["Ihracat"]:
            recommendations.append(
                ("warning", "İhracat geriledi",
                 "Yeni pazar ve ürün çeşitlendirme çalışmaları değerlendirilebilir.")
            )
        if latest["Ithalat"] > previous["Ithalat"]:
            recommendations.append(
                ("info", "İthalat arttı",
                 "İthalat artışının ürün/kategori bazında nedenleri ayrıca analiz edilmelidir.")
            )
        historical_max = df.iloc[:-1]["Ticaret_Hacmi"].max()
        if latest["Ticaret_Hacmi"] > historical_max:
            recommendations.append(
                ("info", "Ticaret hacmi yeni zirvede",
                 "Lojistik ve gümrük kapasitesinin artan hacme göre gözden geçirilmesi önerilir.")
            )

    return recommendations


PALETTE = {
    "export": "#3b82f6",
    "import": "#f87171",
    "forecast": "#fb923c",
    "bg": "#0d1b2a",
    "grid": "#1e3a5f",
    "text": "#cbd5e1",
}


def _theme(ax, title, ylabel):
    ax.set_facecolor(PALETTE["bg"])
    ax.figure.patch.set_facecolor(PALETTE["bg"])
    ax.tick_params(colors=PALETTE["text"])
    for spine in ax.spines.values():
        spine.set_color(PALETTE["grid"])
    ax.grid(True, color=PALETTE["grid"], linestyle="--", alpha=0.6)
    ax.set_title(title, color="#e2e8f0", fontweight="bold")
    ax.set_xlabel("Yıl", color=PALETTE["text"])
    ax.set_ylabel(ylabel, color=PALETTE["text"])


def fig_trend(df):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df["Yil"], df["Ihracat"], marker="o", label="İhracat", color=PALETTE["export"])
    ax.plot(df["Yil"], df["Ithalat"], marker="s", label="İthalat", color=PALETTE["import"])
    _theme(ax, "İhracat / İthalat Trendi", "Milyar $")
    ax.legend()
    fig.tight_layout()
    return fig


def fig_balance(df):
    fig, ax = plt.subplots(figsize=(10, 4))
    vals = df["Dis_Ticaret_Dengesi"]
    colors_ = ["#34d399" if v >= 0 else "#f87171" for v in vals]
    ax.bar(df["Yil"], vals, color=colors_)
    ax.axhline(0, color="#94a3b8", linewidth=1)
    _theme(ax, "Dış Ticaret Dengesi", "Milyar $")
    fig.tight_layout()
    return fig


def fig_coverage(df):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df["Yil"], df["Karsilama_Orani"], marker="D", color="#fbbf24")
    ax.axhline(75, color="#f87171", linestyle="--", label="%75 eşik")
    _theme(ax, "İhracatın İthalatı Karşılama Oranı", "%")
    ax.legend()
    fig.tight_layout()
    return fig


def fig_forecast(df, result, target):
    fig, ax = plt.subplots(figsize=(10, 4))
    base_color = PALETTE["export"] if target == "Ihracat" else PALETTE["import"]
    ax.plot(df["Yil"], df[target], marker="o", color=base_color, label="Gerçek")
    ax.plot(
        result["years"],
        result["predictions"],
        marker="*",
        linestyle="--",
        color=PALETTE["forecast"],
        label="Tahmin",
    )
    _theme(ax, f"{target} Tahmini", "Milyar $")
    ax.legend()
    fig.tight_layout()
    return fig


def _find_pdf_font():
    candidates = [
        r"C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    try:
        candidates.append(font_manager.findfont("DejaVu Sans", fallback_to_default=False))
    except Exception:
        pass
    for path in candidates:
        for match in glob.glob(path):
            if os.path.exists(match):
                return match
    return None


def create_pdf_report(df, recommendations, forecast_result, target, model_name):
    font_path = _find_pdf_font()
    font_name = "Helvetica"
    if font_path:
        try:
            pdfmetrics.registerFont(TTFont("TR", font_path))
            font_name = "TR"
        except Exception:
            pass

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5 * cm, leftMargin=1.5 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleTR", parent=styles["Title"], fontName=font_name,
        alignment=TA_CENTER, textColor=colors.HexColor("#0f4c75"),
    )
    body = ParagraphStyle(
        "BodyTR", parent=styles["BodyText"], fontName=font_name, leading=14,
    )

    latest = df.iloc[-1]
    story = [
        Paragraph("DIŞ TİCARET KARAR DESTEK SİSTEMİ", title),
        Spacer(1, 0.4 * cm),
        HRFlowable(width="100%", color=colors.HexColor("#1b6ca8")),
        Spacer(1, 0.4 * cm),
        Paragraph(
            f"Veri aralığı: {df['Yil'].min()}–{df['Yil'].max()} | "
            f"Rapor tarihi: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}",
            body,
        ),
        Spacer(1, 0.4 * cm),
    ]

    summary = [
        ["Gösterge", "Değer"],
        ["İhracat", f"{latest['Ihracat']:.1f} Milyar $"],
        ["İthalat", f"{latest['Ithalat']:.1f} Milyar $"],
        ["Denge", f"{latest['Dis_Ticaret_Dengesi']:+.1f} Milyar $"],
        ["Karşılama", f"%{latest['Karsilama_Orani']:.1f}"],
    ]
    table = Table(summary, colWidths=[7 * cm, 7 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b6ca8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b0cce4")),
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    story += [table, PageBreak(), Paragraph("Analiz Grafikleri", title)]

    for fig in (fig_trend(df), fig_balance(df), fig_coverage(df)):
        img = io.BytesIO()
        fig.savefig(img, format="png", dpi=130, bbox_inches="tight")
        img.seek(0)
        story.append(RLImage(img, width=16 * cm, height=6.2 * cm))
        plt.close(fig)

    story += [PageBreak(), Paragraph("Karar Destek Önerileri", title)]
    for level, heading, text in recommendations:
        story.append(Paragraph(f"<b>{heading}</b>: {text}", body))
        story.append(Spacer(1, 0.2 * cm))

    if forecast_result:
        story += [PageBreak(), Paragraph("Tahmin Sonuçları", title)]
        story.append(
            Paragraph(
                f"Model: {model_name} | Hedef: {target} | "
                f"R²: {forecast_result['r2']:.4f} | MAE: {forecast_result['mae']:.2f}",
                body,
            )
        )

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def initialize_state():
    defaults = {
        "df": None,
        "forecast": None,
        "forecast_target": "Ihracat",
        "forecast_model": "Linear Regression",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def sidebar():
    with st.sidebar:
        st.markdown("## 📊 Dış Ticaret")
        st.caption("Karar Destek Sistemi")
        if st.button("Örnek veriyi yükle", use_container_width=True):
            st.session_state.df = calculate_indicators(SAMPLE_DATA.copy())
            st.session_state.forecast = None
            st.rerun()

        if st.session_state.df is not None:
            df = st.session_state.df
            st.success(f"{df['Yil'].min()}–{df['Yil'].max()} | {len(df)} kayıt")
        else:
            st.info("Henüz veri yüklenmedi.")


def tab_input():
    section("Veri Girişi")
    left, right = st.columns(2)
    with left:
        uploaded = st.file_uploader("CSV dosyası", type=["csv"])
        if uploaded is not None:
            try:
                raw = read_csv_smart(uploaded)
                clean, notices = clean_data(raw)
                st.session_state.df = calculate_indicators(clean)
                st.session_state.forecast = None
                st.success(f"{len(clean)} kayıt yüklendi.")
                for notice in notices:
                    st.warning(notice)
            except Exception as exc:
                st.error(str(exc))

    with right:
        st.download_button(
            "Örnek CSV indir",
            SAMPLE_DATA.to_csv(index=False).encode("utf-8-sig"),
            "dis_ticaret_2010_2023.csv",
            "text/csv",
            use_container_width=True,
        )

    if st.session_state.df is not None:
        st.dataframe(st.session_state.df, use_container_width=True)


def tab_analysis():
    df = st.session_state.df
    if df is None:
        st.info("Önce veri yükleyin.")
        return

    latest = df.iloc[-1]
    section("Özet Göstergeler")
    cols = st.columns(5)
    values = [
        ("İhracat", f"{latest['Ihracat']:.1f}"),
        ("İthalat", f"{latest['Ithalat']:.1f}"),
        ("Denge", f"{latest['Dis_Ticaret_Dengesi']:+.1f}"),
        ("Karşılama", f"%{latest['Karsilama_Orani']:.1f}"),
        ("Hacim", f"{latest['Ticaret_Hacmi']:.1f}"),
    ]
    for col, (label, value) in zip(cols, values):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="label">{label}</div>'
                f'<div class="value">{value}</div></div>',
                unsafe_allow_html=True,
            )

    section("İstatistiksel Özet")
    st.dataframe(
        df[["Ihracat", "Ithalat", "Dis_Ticaret_Dengesi", "Karsilama_Orani", "Ticaret_Hacmi"]]
        .describe()
        .T,
        use_container_width=True,
    )


def tab_charts():
    df = st.session_state.df
    if df is None:
        st.info("Önce veri yükleyin.")
        return
    st.pyplot(fig_trend(df), use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        st.pyplot(fig_balance(df), use_container_width=True)
    with c2:
        st.pyplot(fig_coverage(df), use_container_width=True)


def tab_forecast():
    df = st.session_state.df
    if df is None:
        st.info("Önce veri yükleyin.")
        return

    c1, c2, c3 = st.columns(3)
    target = c1.selectbox("Tahmin hedefi", ["Ihracat", "Ithalat"])
    model_name = c2.selectbox("Model", ["Linear Regression", "Random Forest"])
    years = c3.slider("Kaç yıl ileri?", 1, 10, 3)

    if st.button("Modeli eğit ve tahmin et", use_container_width=True):
        try:
            result = train_and_forecast(df, target, model_name, years)
            st.session_state.forecast = result
            st.session_state.forecast_target = target
            st.session_state.forecast_model = model_name
        except Exception as exc:
            st.error(str(exc))

    result = st.session_state.forecast
    if result:
        m1, m2 = st.columns(2)
        m1.metric("R²", f"{result['r2']:.4f}")
        m2.metric("MAE", f"{result['mae']:.2f}")
        st.dataframe(
            pd.DataFrame(
                {"Yıl": result["years"], "Tahmin (Milyar $)": result["predictions"]}
            ),
            use_container_width=True,
        )
        st.pyplot(
            fig_forecast(df, result, st.session_state.forecast_target),
            use_container_width=True,
        )
        if result["feature_importance"]:
            st.write("**Özellik önemi**")
            st.bar_chart(pd.Series(result["feature_importance"]))


def tab_decision():
    df = st.session_state.df
    if df is None:
        st.info("Önce veri yükleyin.")
        return

    recommendations = generate_recommendations(df)
    section("Karar Destek Önerileri")
    render = {
        "error": st.error,
        "warning": st.warning,
        "success": st.success,
        "info": st.info,
    }
    for level, heading, text in recommendations:
        render[level](f"**{heading}**\n\n{text}")


def tab_pdf():
    df = st.session_state.df
    if df is None:
        st.info("Önce veri yükleyin.")
        return

    if st.button("PDF raporu oluştur", use_container_width=True):
        try:
            pdf = create_pdf_report(
                df,
                generate_recommendations(df),
                st.session_state.forecast,
                st.session_state.forecast_target,
                st.session_state.forecast_model,
            )
            st.download_button(
                "PDF indir",
                pdf,
                "dis_ticaret_karar_destek_raporu.pdf",
                "application/pdf",
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f"PDF oluşturulamadı: {exc}")


def main():
    inject_css()
    initialize_state()
    st.markdown(
        """
        <div class="main-header">
            <h1>📊 Dış Ticaret Karar Destek Sistemi</h1>
            <p>Veri Analizi · Makine Öğrenmesi · Karar Destek · PDF Raporlama</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs(
        ["📂 Veri", "📈 Analiz", "📊 Grafikler", "🤖 Tahmin", "💡 Karar Destek", "📄 PDF"]
    )
    with tabs[0]:
        tab_input()
    with tabs[1]:
        tab_analysis()
    with tabs[2]:
        tab_charts()
    with tabs[3]:
        tab_forecast()
    with tabs[4]:
        tab_decision()
    with tabs[5]:
        tab_pdf()

    sidebar()


if __name__ == "__main__":
    main()
