# ================================================================
# ================================================================
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import (
    classification_report, accuracy_score, f1_score,
    precision_score, recall_score, balanced_accuracy_score,
    matthews_corrcoef, confusion_matrix, roc_curve, auc,
)
from xgboost import XGBClassifier
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")
import altair as alt

from theme import COLORS, FONTS, FONT_SIZES, SPACING, BORDER_RADIUS
from ui_styles import (
    load_global_css, card, metric_display, section_header,
    signal_badge, live_price_banner, hero_section,
    kpi_card, success_banner, footer,
)
from components import (
    chart_container, create_candlestick_chart, confusion_matrix_chart,
    signal_timeline_chart, probability_bars, roc_curves_chart,
    backtest_comparison_chart, data_split_cards,
)

# ================================================================
# PAGE CONFIG (must be first Streamlit command)
# ================================================================
st.set_page_config(
    page_title="Trade with Machine Learning",
    page_icon="💲",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_global_css()

# ================================================================
# CORE LOGIC
# ================================================================

def _merge(df_main: pd.DataFrame, ta_obj):
    if isinstance(ta_obj, pd.DataFrame):
        return pd.concat([df_main, ta_obj], axis=1)
    return pd.concat([df_main, ta_obj.rename(ta_obj.name)], axis=1)


def add_indicators(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()
    for length in [5, 10, 15]:
        df[f"rsi_{length}"] = ta.rsi(df["Close"], length=length)
    df["roc_10"] = ta.roc(df["Close"], length=10)
    df["mom_10"] = ta.mom(df["Close"], length=10)
    df = _merge(df, ta.stochrsi(df["Close"]))
    df["cci_20"] = ta.cci(df["High"], df["Low"], df["Close"], length=20)
    df["wr_14"] = ta.willr(df["High"], df["Low"], df["Close"], length=14)
    df = _merge(df, ta.kst(df["Close"]))
    df["macd"] = ta.macd(df["Close"])["MACD_12_26_9"]
    for length in [5, 10, 20]:
        df[f"sma_{length}"] = ta.sma(df["Close"], length=length)
        df[f"ema_{length}"] = ta.ema(df["Close"], length=length)
    df["vwma_20"] = ta.vwma(df["Close"], df["Volume"], length=20)
    df = _merge(df, ta.bbands(df["Close"], length=20))
    df["atr_14"] = ta.atr(df["High"], df["Low"], df["Close"], length=14)
    df = _merge(df, ta.kc(df["High"], df["Low"], df["Close"], length=20))
    df["obv"] = ta.obv(df["Close"], df["Volume"])
    df["ad"] = ta.ad(df["High"], df["Low"], df["Close"], df["Volume"])
    df["efi"] = ta.efi(df["Close"], df["Volume"])
    df["nvi"] = ta.nvi(df["Close"], df["Volume"])
    df = _merge(df, ta.pvi(df["Close"], df["Volume"]))
    return df


def generate_label(data, lookahead=5, thresh=0.01, col="Close"):
    future_mean = (
        data[col].shift(-lookahead)
        .rolling(window=lookahead, min_periods=lookahead)
        .mean()
    )
    pct_change = (future_mean - data[col]) / data[col]
    labels = np.select(
        [pct_change >= thresh, pct_change <= -thresh],
        [2, 1], default=0,
    )
    return pd.Series(labels, index=data.index)


def selective_predict_proba(proba, thr1=0.55, thr2=0.55):
    pred = np.zeros(len(proba), dtype=int)
    mask1 = (proba[:, 1] >= thr1) & (proba[:, 1] > proba[:, 2])
    pred[mask1] = 1
    mask2 = (proba[:, 2] >= thr2) & (proba[:, 2] > proba[:, 1])
    pred[mask2] = 2
    return pred


def get_feature_cols(df):
    exclude = {"Open", "High", "Low", "Close", "Adj Close", "Volume"}
    return [c for c in df.columns if c not in exclude and not c.startswith("label_")]


# ================================================================
# SIDEBAR
# ================================================================
with st.sidebar:
    st.markdown("Trading Strategies")
    st.caption("With Machine Learning and Quant Analysis")

    st.divider()

    st.markdown(f"""
    <div class="qf-card-shiny" style="padding: 15px; text-align: center;">
        <div style="font-size: 0.75rem; color: {COLORS['text_tertiary']}; letter-spacing: 1.5px; margin-bottom: 5px; font-weight: 600; text-transform: uppercase;">Designed & Developed by</div>
        <div style="font-size: 1.2rem; font-weight: 800; color: {COLORS['text_primary']}; margin-bottom: 2px; text-transform: uppercase;">Engineer</div>
        <div style="font-size: 0.85rem; color: {COLORS['text_secondary']}; font-family: monospace;">contact : ggengineerco@gmail.com</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("#### ⚙️ Configure your Strategy")

    symbol = st.selectbox(
        "Asset Symbol",
        ["^NSEI", "^BSESN", "^NSEBANK", "^NIFTYFINANCIALS", "ES=F", "BTC-USD"],
        help="Select trading instrument",
    )

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=pd.Timestamp("2020-01-01"))
    with col2:
        lookback = st.number_input("Lookback", min_value=100, max_value=5000, value=1000)

    best_label_override = st.selectbox(
        "Labelling Strategy",
        ["auto (best F1-macro)", "label_la2_th0.010", "label_la2_th0.020",
         "label_la4_th0.010", "label_la4_th0.020",
         "label_la6_th0.010", "label_la6_th0.020",
         "label_la8_th0.010", "label_la8_th0.020",
         "label_la10_th0.010", "label_la10_th0.020"],
    )

    st.markdown("#### 🎯 Signal Thresholds")
    thresh_bear = st.slider("Bearish Threshold", 0.40, 0.90, 0.55, 0.05, format="%.2f")
    thresh_bull = st.slider("Bullish Threshold", 0.40, 0.90, 0.55, 0.05, format="%.2f")

    st.markdown("#### ⚡ Training and ML")
    run_gridsearch = st.toggle("Hyper-Parameter Search", value=False, help="Enable GridSearchCV (Slow)")
    run_walkforward = st.toggle("Walk-Forward Validation", value=False)

    st.divider()
    run_btn = st.button("Execute Strategy", type="primary", use_container_width=True)

# ================================================================
# LANDING PAGE
# ================================================================
if not run_btn:
    hero_section(
        title="Trading with AI & ML",
        subtitle="Institutional-grade XGBoost ML trading analysis with 33 technical indicators",
        icon="💲💲💲",
    )

    ""  # spacer

    cols = st.columns(4)
    features = [
        ("✅", "XGboost Classifier", "Multi-class prediction engine trained on Indian Stock Market Data"),
        ("✅", "Indicators (Total 33)", "Including Momentum, Volatility, Trend, Oscillators, & Volume indicators"),
        ("✅", "SHAP Explainability", "Highlighting the important features used in the model"),
        ("✅", "Real-Time Signals", "Live BUY/SELL recommendations"),
    ]
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            card(f"{icon} {title}", desc)

    st.markdown(f"""
    <div class="qf-card-shiny" style="
        padding: 24px; 
        text-align: center; 
        border-radius: {BORDER_RADIUS['lg']};
        margin-top: 30px;
        margin-bottom: 30px;
        cursor: pointer;
    ">
        <div style="font-size: 1.25rem; color: #e2e8f0; font-weight: 800; letter-spacing: 0.5px; text-shadow: 0 2px 4px rgba(0,0,0,0.5); font-family: {FONTS['primary']}; margin-bottom: 12px;">
            Configure your strategy in the sidebar and click <span style="background: {COLORS['danger']}90; border: 1px solid {COLORS['danger']}; color: white; padding: 4px 10px; border-radius: 6px; margin: 0 4px; box-shadow: 0 2px 8px {COLORS['danger']}40;">Execute Strategy</span> to begin analysis.
        </div>
        <div style="font-size: 0.95rem; color: {COLORS['danger']}; font-weight: 700; letter-spacing: 0.5px; font-family: {FONTS['primary']};">
            ⚠️Kindly note that this is an educational project and not financial advice⚠️
        </div>
    </div>
    """, unsafe_allow_html=True)
    footer()
    st.stop()


# ================================================================
# PIPELINE EXECUTION
# ================================================================

# ─── DATA DOWNLOAD ───────────────────────────────────────────────
section_header("MARKET DATA ACQUISITION")

with st.spinner("📡 Connecting to Yahoo Finance..."):
    df_raw = yf.download(symbol, start=str(start_date), end=None)
    if df_raw is None or df_raw.empty:
        st.error(f"Failed to fetch data for {symbol}.")
        st.stop()
    if isinstance(df_raw.columns, pd.MultiIndex):
        df_raw.columns = df_raw.columns.get_level_values(0)

live_price = df_raw['Close'].iloc[-1]
live_date = pd.to_datetime(df_raw.index[-1]).strftime("%Y-%m-%d %H:%M:%S")
live_change = (live_price - df_raw['Close'].iloc[-2]) / df_raw['Close'].iloc[-2] * 100

live_price_banner(symbol, live_price, f"Last Updated: {live_date}")

cols = st.columns(4)
with cols[0]:
    metric_display("Current Price", f"₹{live_price:,.2f}", live_change, "percentage")
with cols[1]:
    vol_chg = (df_raw['Volume'].iloc[-1] - df_raw['Volume'].iloc[-2]) / df_raw['Volume'].iloc[-2] * 100
    metric_display("Volume", f"{df_raw['Volume'].iloc[-1]:,.0f}", vol_chg, "percentage")
with cols[2]:
    metric_display("Day High", f"₹{df_raw['High'].iloc[-1]:,.2f}")
with cols[3]:
    metric_display("Day Low", f"₹{df_raw['Low'].iloc[-1]:,.2f}")

fig_price = create_candlestick_chart(df_raw, f"{symbol} — Historical Price Action")
chart_container(fig_price, height=500)


# ─── FEATURE ENGINEERING ─────────────────────────────────────────
section_header("FEATURE ENGINEERING")

with st.spinner("Computing..."):
    df_ta = add_indicators(df_raw)

feature_cols = get_feature_cols(df_ta)

cat_cols = st.columns(4)
categories = [
    ("Momentum", [c for c in feature_cols if any(x in c for x in ['rsi', 'roc', 'mom'])]),
    ("Oscillators", [c for c in feature_cols if any(x in c for x in ['stoch', 'cci', 'wr', 'kst', 'macd'])]),
    ("Trend", [c for c in feature_cols if any(x in c for x in ['sma', 'ema', 'vwma'])]),
    ("Volatility", [c for c in feature_cols if any(x in c for x in ['bband', 'atr', 'kc'])]),
]
for col, (cat_name, feats) in zip(cat_cols, categories):
    with col:
        feat_text = ", ".join(feats[:3])
        extra = f" +{len(feats)-3} more" if len(feats) > 3 else ""
        count_html = f"<span style='color: {COLORS['text_primary']}; font-weight: 700; font-size: 1.1em;'>{len(feats)}</span>"
        card(f"✅  {cat_name}", f"{count_html} indicators &middot; {feat_text}{extra}")


# ─── LABEL GENERATION ────────────────────────────────────────────
section_header("LABEL GENERATION")

with st.spinner("🏷️ Generating labels..."):
    for la in [2, 4, 6, 8, 10]:
        for th in [0.01, 0.02]:
            df_ta[f"label_la{la}_th{th:.3f}"] = generate_label(df_ta, lookahead=la, thresh=th)
    df_ta.dropna(inplace=True)

label_cols = [c for c in df_ta.columns if c.startswith("label_")]

with st.container(border=True):
    st.markdown("### Class Distribution")
    dist_data = {}
    for lc in label_cols:
        vc = df_ta[lc].value_counts().sort_index()
        dist_data[lc] = {"Neutral": vc.get(0, 0), "Bearish": vc.get(1, 0), "Bullish": vc.get(2, 0)}
    dist_df = pd.DataFrame(dist_data).T
    st.dataframe(
        dist_df.style
        .background_gradient(cmap='RdYlGn', subset=["Bullish"], axis=0)
        .background_gradient(cmap='Reds', subset=["Bearish"], axis=0),
        use_container_width=True,
    )


# ─── DATA SPLIT ──────────────────────────────────────────────────
section_header("DATA SPLITTING")

split_idx = int(len(df_ta) * 0.6)
split_idx_val = int(len(df_ta) * 0.8)
train_df = df_ta.iloc[:split_idx].copy()
test_df = df_ta.iloc[split_idx:split_idx_val].copy()
val_df = df_ta.iloc[split_idx_val:].copy()

data_split_cards(
    train_size=len(train_df), val_size=len(test_df), test_size=len(val_df),
    train_dates=f"{train_df.index[0].date()} → {train_df.index[-1].date()}",
    val_dates=f"{test_df.index[0].date()} → {test_df.index[-1].date()}",
    test_dates=f"{val_df.index[0].date()} → {val_df.index[-1].date()}",
)


# ─── BASELINE SCAN ───────────────────────────────────────────────
section_header("MODEL BASELINE ANALYSIS")

results = []
progress_bar = st.progress(0, text="Initializing baseline models...")

for i, label_col in enumerate(label_cols):
    X_tr, y_tr = train_df[feature_cols], train_df[label_col]
    X_te, y_te = test_df[feature_cols], test_df[label_col]

    mdl = XGBClassifier(
        n_estimators=300, max_depth=6, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.8,
        objective="multi:softprob", num_class=3,
        n_jobs=-1, eval_metric="mlogloss", seed=42,
    )
    mdl.fit(X_tr, y_tr)
    preds = mdl.predict(X_te)
    results.append({
        "Strategy": label_col,
        "Accuracy": accuracy_score(y_te, preds),
        "F1-Macro": f1_score(y_te, preds, average="macro"),
        "Precision": precision_score(y_te, preds, average="macro", zero_division=0),
    })
    progress_bar.progress((i + 1) / len(label_cols), text=f"Training {label_col}... ({i+1}/{len(label_cols)})")

progress_bar.empty()
results_df = pd.DataFrame(results).sort_values("F1-Macro", ascending=False)

with st.container(border=True):
    st.dataframe(
        results_df.style
        .highlight_max(subset=["Accuracy", "F1-Macro"], color=COLORS['primary'])
        .background_gradient(subset=["Accuracy", "F1-Macro"], cmap='viridis'),
        use_container_width=True,
    )

if best_label_override.startswith("auto"):
    best_label = results_df.iloc[0]["Strategy"]
else:
    best_label = best_label_override

st.success(f"🏆 Optimal Strategy: **{best_label}** (F1: {results_df.iloc[0]['F1-Macro']:.3f})")


# ─── MODEL TRAINING ──────────────────────────────────────────────
X_train, y_train = train_df[feature_cols], train_df[best_label]
X_test, y_test = test_df[feature_cols], test_df[best_label]
X_val, y_val = val_df[feature_cols], val_df[best_label]

if run_gridsearch:
    section_header("HYPER-PARAMETER OPTIMIZATION")
    with st.spinner("⏳ Running GridSearchCV..."):
        param_grid = {
            "n_estimators": [200, 400, 600],
            "max_depth": [4, 6, 8],
            "learning_rate": [0.01, 0.05, 0.1],
            "subsample": [0.8, 1.0],
            "colsample_bytree": [0.6, 0.8, 1.0],
        }
        tscv = TimeSeriesSplit(n_splits=5)
        grid = GridSearchCV(
            estimator=XGBClassifier(
                objective="multi:softprob", num_class=3,
                n_jobs=-1, eval_metric="mlogloss", seed=42,
            ),
            param_grid=param_grid, cv=tscv,
            scoring="f1_macro", verbose=0, n_jobs=-1,
        )
        grid.fit(X_train, y_train)
        best_model = grid.best_estimator_

    param_cols = st.columns(len(grid.best_params_))
    for (param, value), col in zip(grid.best_params_.items(), param_cols):
        with col:
            card(param.replace('_', ' ').title(), f"<b style='color:{COLORS['primary']};font-size:1.5rem;'>{value}</b>")
    st.metric("Cross-Validation F1", f"{grid.best_score_:.4f}", delta="Optimized")
else:
    section_header("MODEL TRAINING")
    best_model = XGBClassifier(
        n_estimators=600, max_depth=4, learning_rate=0.01,
        subsample=1.0, colsample_bytree=0.6,
        objective="multi:softprob", num_class=3,
        n_jobs=-1, eval_metric="mlogloss", seed=42,
        tree_method='hist',
    )
    with st.spinner("🧠 Training XGBoost Classifier..."):
        best_model.fit(X_train, y_train)
    st.success("✅ Training Complete — using optimized default hyperparameters")


# ─── EVALUATION ──────────────────────────────────────────────────
section_header("MODEL PERFORMANCE")

y_pred = best_model.predict(X_test)
y_proba = best_model.predict_proba(X_test)

with st.container(border=True):
    st.markdown("### Classification Report (Test Set)")
    report_dict = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    report_df = pd.DataFrame(report_dict).transpose()
    st.dataframe(
        report_df.style.background_gradient(cmap='RdYlGn', subset=['f1-score'], axis=0),
        use_container_width=True,
    )

st.markdown("### Key Performance Indicators")
metrics = st.columns(6)
metric_values = [
    ("Accuracy", accuracy_score(y_test, y_pred)),
    ("Balanced Acc", balanced_accuracy_score(y_test, y_pred)),
    ("Macro F1", f1_score(y_test, y_pred, average="macro")),
    ("Precision", precision_score(y_test, y_pred, average="macro", zero_division=0)),
    ("Recall", recall_score(y_test, y_pred, average="macro", zero_division=0)),
    ("MCC", matthews_corrcoef(y_test, y_pred)),
]
for col, (name, val) in zip(metrics, metric_values):
    with col:
        kpi_card(name, f"{val:.4f}")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Confusion Matrix")
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2])
    cmn = cm / cm.sum(axis=1, keepdims=True)
    fig_cm = confusion_matrix_chart(cmn)
    st.plotly_chart(fig_cm, use_container_width=True, key="cm_test")

with col2:
    st.markdown("### ROC Curves")
    fpr_d, tpr_d, roc_auc_d = {}, {}, {}
    for c in range(3):
        fpr_d[c], tpr_d[c], _ = roc_curve((y_test == c).astype(int), y_proba[:, c])
        roc_auc_d[c] = auc(fpr_d[c], tpr_d[c])
    fig_roc = roc_curves_chart(fpr_d, tpr_d, roc_auc_d)
    st.plotly_chart(fig_roc, use_container_width=True, key="roc_test")


# ─── VALIDATION ──────────────────────────────────────────────────
section_header("VALIDATION RESULTS")

val_pred = best_model.predict(X_val)
val_proba = best_model.predict_proba(X_val)

val_metrics = st.columns(4)
val_values = [
    ("Validation Accuracy", accuracy_score(y_val, val_pred)),
    ("Balanced Accuracy", balanced_accuracy_score(y_val, val_pred)),
    ("Macro F1", f1_score(y_val, val_pred, average="macro")),
    ("MCC", matthews_corrcoef(y_val, val_pred)),
]
for col, (name, val) in zip(val_metrics, val_values):
    with col:
        kpi_card(name, f"{val:.4f}")


# ─── THRESHOLDED PREDICTIONS ────────────────────────────────────
section_header("PROBABILITY THRESHOLDING")

st.markdown(f"""
> **Active Thresholds:** Bearish ≥ {thresh_bear} | Bullish ≥ {thresh_bull}
""")

sel_test = selective_predict_proba(best_model.predict_proba(X_test), thresh_bear, thresh_bull)
test_df["sel_preds"] = sel_test
sel_val = selective_predict_proba(val_proba, thresh_bear, thresh_bull)
val_df["sel_preds"] = sel_val

thresh_cols = st.columns(2)
with thresh_cols[0]:
    st.markdown("**Test Set (Thresholded)**")
    st.code(classification_report(y_test, sel_test, digits=4, zero_division=0))
with thresh_cols[1]:
    st.markdown("**Validation Set (Thresholded)**")
    st.code(classification_report(y_val, sel_val, digits=4, zero_division=0))


# ─── SIGNAL CHART ────────────────────────────────────────────────
section_header("LIVE SIGNAL VISUALIZATION")

chart_len = st.slider("View Window (days)", 50, len(val_df), min(200, len(val_df)), 10)
chart_start = st.slider("Historical Offset", 0, max(0, len(val_df) - chart_len), 0)

df_slice = val_df.iloc[chart_start:chart_start + chart_len].copy().reset_index()
date_col = "Date" if "Date" in df_slice.columns else "index"
offset = (df_slice["High"] - df_slice["Low"]).mean() * 0.15

fig_sig = signal_timeline_chart(df_slice, date_col, "sel_preds", offset)
chart_container(fig_sig, height=600)


# ─── SHAP ────────────────────────────────────────────────────────
section_header("MODEL INTERPRETABILITY")

with st.spinner("🔍 Computing SHAP values..."):
    explainer = shap.TreeExplainer(best_model)
    shap_values = explainer.shap_values(X_val)

fig_shap, ax = plt.subplots(figsize=(10, 8))
shap.summary_plot(shap_values, X_val, plot_type="bar", show=False)
plt.gcf().set_facecolor(COLORS['bg_primary'])
ax.set_facecolor(COLORS['bg_primary'])
ax.tick_params(colors=COLORS['text_primary'])
ax.xaxis.label.set_color(COLORS['text_primary'])
ax.yaxis.label.set_color(COLORS['text_primary'])
st.pyplot(fig_shap, clear_figure=True)


# ─── WALK-FORWARD (optional) ────────────────────────────────────
if run_walkforward:
    section_header("WALK-FORWARD ANALYSIS")

    n_splits = 5
    tscv = TimeSeriesSplit(n_splits=n_splits)
    fold_metrics = []
    wf_progress = st.progress(0, text="Initializing walk-forward validation...")

    for fold, (tr_idx, te_idx) in enumerate(tscv.split(df_ta)):
        tr = df_ta.iloc[tr_idx]
        te = df_ta.iloc[te_idx]
        wf_model = XGBClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.9, colsample_bytree=0.8,
            objective="multi:softprob", num_class=3,
            n_jobs=-1, eval_metric="mlogloss", seed=42,
        )
        wf_model.fit(tr[feature_cols], tr[best_label])
        wf_pred = wf_model.predict(te[feature_cols])

        fold_metrics.append({
            "Fold": fold + 1,
            "Period": f"{te.index[0].date()} to {te.index[-1].date()}",
            "Accuracy": accuracy_score(te[best_label], wf_pred),
            "F1-macro": f1_score(te[best_label], wf_pred, average="macro"),
        })
        wf_progress.progress((fold + 1) / n_splits, text=f"Fold {fold+1}/{n_splits} complete...")

    wf_progress.empty()
    wf_df = pd.DataFrame(fold_metrics)

    with st.container(border=True):
        st.dataframe(
            wf_df.style.highlight_max(subset=["Accuracy", "F1-macro"], color=COLORS['primary']),
            use_container_width=True,
        )

    st.markdown("### Model Stability")
    stability_cols = st.columns(2)
    for col, metric in zip(stability_cols, ["Accuracy", "F1-macro"]):
        with col:
            mean_v = wf_df[metric].mean()
            std_v = wf_df[metric].std()
            arrow_html = f"<span style='color: {COLORS['success']};'>&uarr; &plusmn; {std_v:.4f} &sigma;</span>"
            st.markdown(f"""
            <div class="qf-card-shiny qf-metric-height">
                <div style="font-size: 0.85rem; color: {COLORS['text_tertiary']}; font-weight: 600; margin-bottom: 0.3rem;">{metric} Mean</div>
                <div style="font-size: 2.2rem; font-weight: 700; color: {COLORS['text_primary']}; margin-bottom: 0.3rem;">{mean_v:.4f}</div>
                <div style="font-size: 0.9rem; font-weight: 600;">{arrow_html}</div>
            </div>
            """, unsafe_allow_html=True)


# ─── LIVE PREDICTION ─────────────────────────────────────────────
section_header("LIVE TRADING SIGNAL")

latest_row = df_ta[feature_cols].iloc[[-1]]
live_proba = best_model.predict_proba(latest_row)[0]
live_sel = selective_predict_proba(live_proba.reshape(1, -1), thresh_bear, thresh_bull)[0]

signal_cols = st.columns([1, 2, 1])
with signal_cols[1]:
    confidence = max(live_proba)
    signal_badge(live_sel, confidence)

st.markdown("### Signal Confidence Breakdown")
fig_prob = probability_bars(live_proba)
st.plotly_chart(fig_prob, use_container_width=True, key="prob_bars")

with st.expander("📊 Technical Indicator Snapshot (Latest)"):
    snap = df_ta[feature_cols].iloc[-1].to_frame("Value")
    snap["Z-Score"] = ((snap["Value"] - df_ta[feature_cols].mean()) / df_ta[feature_cols].std()).round(2)
    st.dataframe(
        snap.style.background_gradient(cmap='RdYlGn', subset=["Z-Score"]),
        use_container_width=True,
    )


# ─── BACKTEST ────────────────────────────────────────────────────
section_header("STRATEGY BACKTEST")

bt_df = val_df.copy()
bt_df["signal"] = sel_val
bt_df["daily_return"] = bt_df["Close"].pct_change()
bt_df["strategy_return"] = 0.0
bt_df.loc[bt_df["signal"] == 2, "strategy_return"] = bt_df["daily_return"]
bt_df.loc[bt_df["signal"] == 1, "strategy_return"] = -bt_df["daily_return"]
bt_df["cum_market"] = (1 + bt_df["daily_return"]).cumprod()
bt_df["cum_strategy"] = (1 + bt_df["strategy_return"]).cumprod()

fig_bt = backtest_comparison_chart(bt_df)
chart_container(fig_bt, height=500)

total_trades = (bt_df["signal"] != 0).sum()
winning_days = ((bt_df["strategy_return"] > 0) & (bt_df["signal"] != 0)).sum()
strat_total = bt_df["cum_strategy"].iloc[-1] - 1
market_total = bt_df["cum_market"].iloc[-1] - 1
win_rate = winning_days / total_trades if total_trades > 0 else 0
alpha = strat_total - market_total

bt_cols = st.columns(5)
bt_metrics = [
    ("Total Signals", f"{total_trades}", None),
    ("Win Rate", f"{win_rate:.1%}", COLORS['primary'] if win_rate > 0.5 else None),
    ("Strategy Return", f"{strat_total:.2%}", COLORS['success'] if strat_total > 0 else COLORS['danger']),
    ("Market Return", f"{market_total:.2%}", None),
    ("Alpha", f"{alpha:.2%}", COLORS['success'] if alpha > 0 else COLORS['danger']),
]
for col, (name, val, color) in zip(bt_cols, bt_metrics):
    with col:
        kpi_card(name, val, color)


# ─── DONE ────────────────────────────────────────────────────────
success_banner("All models trained, validated, and backtested successfully.")
footer()
