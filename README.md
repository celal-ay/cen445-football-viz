# European Football Intelligence & Match Dynamics Dashboard
## CEN445 - Introduction to Data Visualization Course Project

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](http://localhost:8501)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An advanced, interactive exploratory data visualization dashboard built with **Python**, **Streamlit**, and **Plotly** to explore and analyze **5,421 European football matches** across 8 major leagues and 2 consecutive seasons (2023–2024 & 2024–2025).

---

### 🌐 Live Dashboard Architecture & Features

The dashboard implements **9 distinct visualization techniques (including 6 advanced types)** and **2 Machine Learning algorithms**, fulfilling and exceeding all requirements for the CEN445 assignment:

| # | Visualization Method | Category | Insight / Analytical Perspective |
|---|----------------------|----------|----------------------------------|
| 1 | **Choropleth Map** | Advanced | European geographical distribution of goal frequency and home advantage. |
| 2 | **Hierarchical Treemap** | Advanced | League $\rightarrow$ Club hierarchy partitioned by total goals and win volume. |
| 3 | **Sankey Diagram** | Advanced | Momentum transition flow from Half-Time (HT) to Full-Time (FT) outcomes, highlighting comeback matches. |
| 4 | **Parallel Coordinates** | Advanced | Multi-dimensional mapping of Home, Draw, Away, and Over 2.5 odds to match results. |
| 5 | **Head-to-Head Network Graph** | Advanced | Directed dominance network topology among top teams within any selected league. |
| 6 | **2D Density Contour Plot** | Advanced | Market odds density landscape revealing clusters and upset sweet-spots. |
| 7 | **Score Frequency Heatmap** | Analytical | Exact fulltime score combination matrix (0–5 goals). |
| 8 | **Calibration Scatter Plot** | Analytical | Market efficiency check: Implied probability ($1/\text{odds}$) vs observed win frequency. |
| 9 | **Violin & Box Plot** | Analytical | League-by-league goal distribution, medians, IQR, and high-scoring outliers. |

---

### 🤖 Machine Learning Models
1. **K-Means Clustering:** Unsupervised tactical profiling of 150+ teams into 3 tiers (*Elite Dominators*, *Balanced Competitors*, *Relegation Strugglers*) based on attacking and defensive performance metrics.
2. **Multinomial Logistic Regression:** Predictive modeling for match outcome classification (Home, Draw, Away) from closing market odds with ~56.2% accuracy. Includes an interactive live simulator for testing arbitrary odds lines.

---

### 🎛️ Interactive Controls & Filters
- **Multiselect Dropdown:** Filter by any combination of the 7 European leagues.
- **Selectbox:** Switch between seasons (*All Seasons*, *2024-2025*, *2023-2024*).
- **Range Slider:** Filter by total goals per match (0 to 10).
- **Float Slider:** Max home odds threshold filter.
- **Checkbox:** Isolate thrilling comebacks (halftime deficit turned into fulltime victory).
- **Interactive Cluster Slider:** Dynamically configure $k$ for K-Means clustering.
- **Interactive Simulator:** Live input for custom odds testing.

---

### 🚀 Quickstart & Setup

1. **Clone the repository:**
   ```bash
   git clone git@github.com:celal-ay/cen445-football-viz.git
   cd cen445-football-viz
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit Dashboard:**
   ```bash
   streamlit run app.py
   ```
   *The application will automatically open in your default browser at `http://localhost:8501`.*

---

### 📁 Project Directory Structure
```text
cen445-football-viz/
├── app.py                      # Main Streamlit dashboard application
├── requirements.txt            # Python dependencies (streamlit, plotly, scikit-learn, etc.)
├── README.md                   # Project overview & execution guide
├── .gitignore                  # Git ignore rules
│
├── .streamlit/
│   └── config.toml             # Custom theme configuration (Dark Mode, Wide Layout)
│
├── data/
│   ├── processed_matches.csv   # Cleaned dataset (4,661 rows, 30 columns)
│   ├── processed_matches.parquet # High-speed binary format
│   └── raw/                    # Raw SQLite copy (isolated from original project)
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py          # Data ingestion, cleaning & feature enrichment pipeline
│   ├── charts.py               # 9 interactive visualization generator functions
│   └── ml_engine.py            # K-Means clustering & match outcome classifier
│
└── docs/
    ├── DEVELOPMENT_LOG.md      # Comprehensive engineering & development log
    └── REPORT.md               # 1-page English summary report for CEN445 submission
```

---

### 👥 Team Contribution Matrix
*(Edit according to your team member assignments)*
* **Member 1 (Name - Student ID):** Data pipeline & feature engineering, Sankey diagram, Treemap, Network Graph.
* **Member 2 (Name - Student ID):** Parallel Coordinates, Geographical Choropleth Map, K-Means Clustering, Streamlit UI & filter panel.
* **Member 3 (Name - Student ID):** 2D Density Plot, Heatmaps, Logistic Regression Classifier, Documentation & Final Report.
