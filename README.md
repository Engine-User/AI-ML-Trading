# 💲 AI/ML Trading Strategies with XGBoost
<img width="940" height="412" alt="image" src="https://github.com/user-attachments/assets/5dc70879-f417-4467-aa01-9e758c35f102" />

An institutional-grade, educational **Streamlit** application that applies **XGBoost machine learning** to historical market data for multi-class trading signal generation. The system computes **33+ technical indicators**, auto-selects the best labelling strategy, evaluates model performance, explains predictions with **SHAP**, and backtests the resulting signals.

> ⚠️ **Disclaimer:** This project is for educational and informational purposes only. It is **not financial advice**. Always do your own research before making investment decisions.

---

## Features

### Core ML Pipeline
- **Data Acquisition** – Pulls OHLCV data from Yahoo Finance for Indian indices, futures, and crypto assets.
- **Feature Engineering** – Builds 33+ technical indicators across momentum, oscillators, trend, volatility, and volume categories.
- **Automated Labelling** – Generates bullish / bearish / neutral labels across multiple lookahead windows and thresholds.
- **Baseline Scan** – Trains a quick XGBoost model for every label strategy and ranks them by macro-F1.
- **Hyper-Parameter Optimization** – Optional `GridSearchCV` with time-series cross-validation.
- **Walk-Forward Validation** – Optional out-of-sample validation across multiple time folds.
<img width="940" height="464" alt="image" src="https://github.com/user-attachments/assets/0ff9de71-9deb-485f-ba3b-44b9a865f775" />

### Model Interpretability & Evaluation
- **Classification Reports** – Accuracy, balanced accuracy, macro-F1, precision, recall, MCC.
- **Confusion Matrix** – Normalised heatmap of predicted vs actual classes.
- **ROC Curves** – One-vs-rest ROC/AUC for each class.
- **SHAP Summary** – Global feature importance to understand what drives predictions.

### Signals & Backtesting
- **Probability Thresholding** – User-defined bullish / bearish thresholds to reduce false signals.
- **Live Trading Signal** – Latest prediction with confidence breakdown.
- **Signal Timeline Chart** – Candlestick chart overlaid with BUY / SELL markers.
- **Strategy Backtest** – Compares cumulative strategy return vs buy-and-hold market return.
- **Risk Metrics** – Win rate, alpha, total signals, and market return.
<img width="940" height="471" alt="image" src="https://github.com/user-attachments/assets/ba7c8f3b-0fc7-4dc8-9916-48380da26849" />

### UI/UX
- Modern dark-themed interface using custom design tokens (`theme.py`).
- Reusable chart components (`components.py`) and styled cards (`ui_styles.py`).
- Landing page with feature overview and clear call-to-action.

---

## Tech Stack

| Layer | Libraries |
|-------|-----------|
| App Framework | [Streamlit](https://streamlit.io/) |
| Data | [yfinance](https://pypi.org/project/yfinance/), [pandas](https://pandas.pydata.org/), [numpy](https://numpy.org/) |
| Technical Indicators | [pandas-ta](https://github.com/twopirllc/pandas-ta) |
| Machine Learning | [XGBoost](https://xgboost.readthedocs.io/), [scikit-learn](https://scikit-learn.org/) |
| Explainability | [SHAP](https://shap.readthedocs.io/) |
| Visualisation | [Plotly](https://plotly.com/python/), [Matplotlib](https://matplotlib.org/), [Altair](https://altair-viz.github.io/) |

---

## Installation

1. **Clone or navigate to the project folder:**

   ```bash
   cd "XGboost ML"
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

Run the Streamlit application from the project root:

```bash
streamlit run p1.py
```

Then open your browser at `http://localhost:8501`.

### Workflow
1. Select an asset symbol in the sidebar (e.g. `^NSEI`, `^BSESN`, `BTC-USD`).
2. Set the start date and lookback window.
3. Choose a labelling strategy or leave it on **auto**.
4. Adjust bullish / bearish probability thresholds.
5. Optionally enable **Hyper-Parameter Search** or **Walk-Forward Validation**.
6. Click **Execute Strategy** to train the model and view results.

---

## Model Details

- **Algorithm:** `XGBClassifier` with `multi:softprob` objective for 3-class classification.
- **Classes:**
  - `0` – Neutral
  - `1` – Bearish
  - `2` – Bullish
- **Default Hyperparameters:**
  - `n_estimators=600`
  - `max_depth=4`
  - `learning_rate=0.01`
  - `subsample=1.0`
  - `colsample_bytree=0.6`
  - `tree_method='hist'`
- **Data Split:** 60% train / 20% validation / 20% test (chronological).

---

## 📊 Indicators Used

| Category | Indicators |
|----------|------------|
| Momentum | RSI(5, 10, 15), ROC(10), MOM(10) |
| Oscillators | Stochastic RSI, CCI(20), Williams %R(14), KST, MACD |
| Trend | SMA(5, 10, 20), EMA(5, 10, 20), VWMA(20) |
| Volatility | Bollinger Bands, ATR(14), Keltner Channel |
| Volume | OBV, A/D Line, EFI, NVI, PVI |

---

## Author

**Engineer**  
📧 contact: [ggengineerco@gmail.com](mailto:ggengineerco@gmail.com)

---

## 📜 License

This project is released for educational purposes. Use at your own risk.
