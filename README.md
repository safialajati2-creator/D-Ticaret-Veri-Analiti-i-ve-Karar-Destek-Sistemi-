# 📊 Foreign Trade Decision Support System

<p align="center">
  <b>English</b> | <a href="README_TR.md">Türkçe</a>
</p>

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?logo=scikitlearn&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas&logoColor=white)
![Status](https://img.shields.io/badge/Status-Portfolio%20Project-success)

An interactive foreign trade analytics and decision support application built with **Python** and **Streamlit**. The system cleans trade data, calculates key economic indicators, visualizes export/import trends, produces machine-learning forecasts, generates rule-based decision-support insights, and exports analytical results as PDF reports.

## 🖥️ Application Screenshots

<p align="center">
  <img src="Sonu%C3%A7%20%C3%A7%C4%B1kt%C4%B1lar%C4%B1/1.jpeg" width="48%" />
  <img src="Sonu%C3%A7%20%C3%A7%C4%B1kt%C4%B1lar%C4%B1/2.jpeg" width="48%" />
</p>
<p align="center">
  <img src="Sonu%C3%A7%20%C3%A7%C4%B1kt%C4%B1lar%C4%B1/3.jpeg" width="48%" />
  <img src="Sonu%C3%A7%20%C3%A7%C4%B1kt%C4%B1lar%C4%B1/4.jpeg" width="48%" />
</p>

<details>
<summary><b>More screenshots</b></summary>
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

## 🎓 Academic Background

The project was developed alongside the academic study **“Python Tabanlı Dış Ticaret Veri Analitiği ve Karar Destek Sistemi Tasarımı”** at **Beykoz University, Faculty of Engineering and Architecture – Software Engineering**.

📄 **Academic report (Turkish):** [Dış Ticaret Makalesı.pdf](Makale/D%C4%B1%C5%9F%20Ticaret%20Makales%C4%B1.pdf)

The study covers Turkish foreign-trade data analysis, preprocessing, indicator calculation, machine-learning forecasting, rule-based decision support, and system evaluation. The repository's `app.py` is the portfolio-oriented application version of this work.

## ✨ Key Features

- CSV upload with support for multiple encodings and separators
- Cleaning of missing, negative, invalid, and duplicate records
- Export, import, foreign-trade balance, and total trade-volume analysis
- Export/import coverage ratio and annual change calculations
- Interactive Streamlit dashboard
- Linear Regression and Random Forest Regressor
- Lag features (`Lag-1`, `Lag-2`) and 3-period moving average (`MA-3`)
- Chronological train/test split
- Model evaluation using R² and MAE
- Random Forest feature importance analysis
- Recursive future-period forecasting
- Rule-based decision-support recommendations
- Automatic PDF reporting with ReportLab

## 🧰 Tech Stack

| Technology | Usage |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web interface |
| Pandas | Data cleaning and analysis |
| NumPy | Numerical operations and feature engineering |
| Matplotlib | Data visualization |
| Scikit-learn | Regression models and evaluation metrics |
| ReportLab | PDF report generation |

## 🧠 System Workflow

1. Upload a CSV file or use the built-in sample dataset.
2. Normalize column names and validate the data.
3. Clean missing and invalid records.
4. Calculate trade balance, trade volume, coverage ratio, and change rates.
5. Display analytical results through tables and charts.
6. Select the forecasting target and model.
7. Evaluate the model using a chronological training/test split.
8. Generate future-period forecasts.
9. Interpret indicators using the rule-based decision-support module.
10. Export analytical results as a PDF report.

## 🤖 Machine Learning

The application provides two regression models:

- **Linear Regression**
- **Random Forest Regressor** — `200` trees, `max_depth=5`, `random_state=42`

Model inputs include the year, one- and two-period lag values of the target series, and a three-period moving average. Performance is evaluated with **R²** and **MAE**.

> Model metrics can have high variance on small annual datasets. Forecasts are intended for academic and analytical demonstration and should not be interpreted as financial or economic advice.

## 💡 Decision Support Module

The rule-based module evaluates indicators including:

- Export/import coverage ratio
- Foreign trade deficit
- Latest export change
- Latest import change
- Trade volume relative to historical levels

It produces automated analytical observations designed to demonstrate data-driven decision-support logic rather than professional policy or investment advice.

## 📄 PDF Reporting

The application uses ReportLab to generate downloadable PDF reports containing summary indicators, analytical charts, decision-support observations, and forecasting performance when available.

## 📚 Dataset

The CSV included in the repository contains **18 years of sample foreign-trade data from 2005 to 2022**. The application's built-in demo uses a more recent example series. Users can also upload their own CSV containing `Yil`, `Ihracat`, and `Ithalat` columns.

> The included dataset is intended for portfolio and academic demonstration. Current and verified official data should be used for real-world analysis.

## 🚀 Installation

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

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

## 📁 Project Structure

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

## 🎯 Project Purpose

This project demonstrates practical skills in **data analysis, data cleaning, feature engineering, machine learning, data visualization, Streamlit application development, decision-support logic, and automated reporting** within a single end-to-end software project.
