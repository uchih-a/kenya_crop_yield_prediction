# 🌾 AgriYield Kenya — Crop Yield Prediction System

> **Agricultural Productivity & Crop Yield Prediction using LSTM Deep Learning**  
> Bachelor of Science in Data Science · Meru University of Science and Technology  
> Researcher: CT204/109423/22 — Purity Jeptoo Kemboi

---

## Overview

A production-grade Streamlit web application for predicting crop yields across Kenya's seven
agro-ecological regions using a Bidirectional LSTM neural network trained on 30,492 records
spanning 2016–2024.

---

## Project Structure

```
agri_app/
├── app.py                          # Main entry point (router + global CSS)
├── requirements.txt
├── supabase_schema.sql             # Run this in Supabase SQL editor
├── assets/
│   └── kenya_crop_yield.csv        # Dataset (30,492 records)
├── model/                          # Drop your exported models here
│   ├── linear_regression_model.pkl # (optional) from notebook
│   └── lr_scaler.pkl               # (optional) from notebook
├── pages/
│   ├── auth_page.py                # Login + Signup
│   ├── home_page.py                # Landing page
│   ├── prediction_page.py          # Prediction + trend chart
│   └── dashboard_page.py           # 3-chart interactive dashboard
├── utils/
│   ├── auth.py                     # Password hashing + session management
│   ├── database.py                 # Supabase CRUD operations
│   ├── predictor.py                # ML inference (uses dataset-trained model)
│   ├── report.py                   # PDF report generation
│   └── theme.py                    # Shared Plotly theme + color palette
└── .streamlit/
    ├── config.toml                 # Theme & server settings
    └── secrets.toml.example        # Copy → secrets.toml and fill in values
```

---

## Quick Start

### 1. Install dependencies

```bash
cd agri_app
pip install -r requirements.txt
```

### 2. Set up Supabase

1. Create a free project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run the contents of `supabase_schema.sql`
3. Copy your **Project URL** and **anon/public key** from  
   Settings → API

### 3. Configure secrets

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml`:

```toml
SUPABASE_URL      = "https://xxxx.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUz..."
```

> ⚠️ **Never commit `secrets.toml` to git.** Add it to `.gitignore`.

### 4. Run the app

```bash
streamlit run app.py
```

---

## Using Your Trained Models

The app ships with a **Ridge Regression fallback** trained on the dataset so predictions
work out of the box. To use your notebook-trained models:

### Export from Google Colab

Add these cells at the end of your notebook:

```python
import joblib

# Export LR model + scaler
joblib.dump(lr_model,  DRIVE_OUTPUT_DIR + 'linear_regression_model.pkl')
joblib.dump(scaler_lr, DRIVE_OUTPUT_DIR + 'lr_scaler.pkl')

# If you want to export the LSTM model:
lstm_model.save(DRIVE_OUTPUT_DIR + 'lstm_model.h5')
```

### Place files in the `model/` directory

```
agri_app/model/
├── linear_regression_model.pkl
└── lr_scaler.pkl
```

The `utils/predictor.py` automatically detects and loads these files at startup.

---

## Pages

| Page        | Route        | Description |
|-------------|-------------|-------------|
| Auth        | `auth`       | Login & Signup with password strength indicator and validation |
| Home        | `home`       | Project overview, KPIs, architecture summary, dataset preview |
| Prediction  | `prediction` | Input form → predicted yield + trend chart + recent predictions |
| Dashboard   | `dashboard`  | 3 interactive charts with region/crop filters + PDF export |

---

## Features

- **Authentication** — bcrypt-hashed passwords, email/username login, live password strength meter, field-level validation
- **Prediction** — climate + soil inputs → yield in tons/acre with 95% confidence interval + 12-month trend chart
- **Dashboard** — fully interactive, 3 distinct charts matching the notebook analysis, region & crop filters
- **Recent Predictions** — toggle to view all-user or personal prediction history from Supabase
- **PDF Report** — export filtered dashboard data as a formatted PDF
- **Supabase** — persistent users + predictions tables with Row Level Security

---

## Dashboard Charts

1. **Rainfall vs Yield (colour by temperature)** — scatter plot with Pearson correlation and trend line
2. **Average Yield by Region & Crop** — grouped bar chart, adapts when a single crop is selected
3. **Soil pH Distribution & Yield Relationship** — dual-axis: histogram frequency + average yield line with optimal pH band

---

## Environment Variables

| Key                | Where         | Required |
|--------------------|---------------|----------|
| `SUPABASE_URL`     | secrets.toml  | Yes      |
| `SUPABASE_ANON_KEY`| secrets.toml  | Yes      |

---

## Tech Stack

| Layer        | Technology |
|-------------|-----------|
| Frontend     | Streamlit 1.35 |
| Charts       | Plotly 5.22 |
| ML / Stats   | Scikit-learn, NumPy, Pandas |
| Deep Learning | TensorFlow / Keras (LSTM) |
| Database     | Supabase (PostgreSQL) |
| Auth         | bcrypt |
| PDF Export   | fpdf2 |
| Deployment   | Streamlit Community Cloud / Docker |

---

## Deployment (Streamlit Community Cloud)

1. Push your repo to GitHub (exclude `secrets.toml` and model files)
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Set **Main file**: `app.py`
4. Under **Advanced settings → Secrets**, paste your `secrets.toml` content

---

*Meru University of Science and Technology · Department of Computer Science · 2026*
