# ================================================================
# COMPONENTS.PY — Chart & Visualization Components
# ================================================================
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from theme import COLORS, FONTS, FONT_SIZES, SPACING, BORDER_RADIUS, CHART_COLORS, apply_chart_theme, get_signal_color


def chart_container(fig, height: int = 450):
    """Display a themed Plotly chart."""
    fig = apply_chart_theme(fig)
    fig.update_layout(height=height)
    st.plotly_chart(fig, use_container_width=True)


def create_candlestick_chart(df, title: str = "Price", height: int = 450):
    """Create a candlestick chart from OHLCV dataframe."""
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        increasing_line_color=COLORS['success'],
        decreasing_line_color=COLORS['danger'],
    )])
    fig.update_layout(
        title=title,
        xaxis_rangeslider_visible=False,
        xaxis_title="", yaxis_title="Price",
    )
    return fig


def confusion_matrix_chart(cmn):
    """Heatmap for normalised confusion matrix (3×3)."""
    labels = ['Neutral', 'Bearish', 'Bullish']
    text = [[f"{cmn[i][j]:.2f}" for j in range(3)] for i in range(3)]

    fig = go.Figure(data=go.Heatmap(
        z=cmn, x=labels, y=labels,
        text=text, texttemplate="%{text}",
        colorscale=[[0, COLORS['bg_secondary']], [1, COLORS['primary']]],
        showscale=False,
    ))
    fig.update_layout(
        xaxis_title="Predicted", yaxis_title="Actual",
        yaxis=dict(autorange='reversed'),
    )
    return fig


def signal_timeline_chart(df, date_col: str, signal_col: str, offset: float = 0):
    """Candlestick with buy/sell markers overlaid."""
    fig = go.Figure(data=[go.Candlestick(
        x=df[date_col],
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        increasing_line_color=COLORS['success'],
        decreasing_line_color=COLORS['danger'],
        name='Price',
    )])

    bull = df[df[signal_col] == 2]
    bear = df[df[signal_col] == 1]

    if not bull.empty:
        fig.add_trace(go.Scatter(
            x=bull[date_col], y=bull['Low'] - offset,
            mode='markers', name='BUY',
            marker=dict(symbol='triangle-up', size=10, color=COLORS['success']),
        ))
    if not bear.empty:
        fig.add_trace(go.Scatter(
            x=bear[date_col], y=bear['High'] + offset,
            mode='markers', name='SELL',
            marker=dict(symbol='triangle-down', size=10, color=COLORS['danger']),
        ))

    fig.update_layout(
        title="Signal Timeline",
        xaxis_rangeslider_visible=False,
        xaxis_title="", yaxis_title="Price",
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
    )
    return fig


def probability_bars(proba):
    """Horizontal bar chart for class probabilities [neutral, bearish, bullish]."""
    labels = ['Neutral', 'Bearish', 'Bullish']
    colors = [COLORS['neutral'], COLORS['danger'], COLORS['success']]

    fig = go.Figure(data=[go.Bar(
        x=list(proba),
        y=labels,
        orientation='h',
        marker_color=colors,
        text=[f"{p:.1%}" for p in proba],
        textposition='auto',
    )])
    fig.update_layout(
        xaxis=dict(range=[0, 1], title='Probability'),
        yaxis_title="",
        height=200,
    )
    return fig


def roc_curves_chart(fpr_d, tpr_d, roc_auc_d):
    """ROC curves for 3 classes."""
    class_names = ['Neutral', 'Bearish', 'Bullish']
    colors = [COLORS['neutral'], COLORS['danger'], COLORS['success']]

    fig = go.Figure()
    for c in range(3):
        fig.add_trace(go.Scatter(
            x=fpr_d[c], y=tpr_d[c],
            name=f"{class_names[c]} (AUC={roc_auc_d[c]:.3f})",
            line=dict(color=colors[c]),
        ))
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        line=dict(dash='dash', color=COLORS['text_tertiary']),
        showlegend=False,
    ))
    fig.update_layout(
        xaxis_title='False Positive Rate',
        yaxis_title='True Positive Rate',
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
    )
    return fig


def backtest_comparison_chart(bt_df):
    """Strategy vs Market cumulative returns."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=bt_df.index, y=bt_df['cum_strategy'],
        name='Strategy', line=dict(color=COLORS['primary'], width=2),
    ))
    fig.add_trace(go.Scatter(
        x=bt_df.index, y=bt_df['cum_market'],
        name='Market', line=dict(color=COLORS['text_tertiary'], width=1, dash='dot'),
    ))
    fig.update_layout(
        title='Cumulative Returns: Strategy vs Market',
        xaxis_title='', yaxis_title='Cumulative Return',
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
    )
    return fig


def data_split_cards(train_size, val_size, test_size,
                     train_dates="", val_dates="", test_dates=""):
    """Show train/val/test split as styled metrics."""
    total = train_size + val_size + test_size
    cols = st.columns(3)

    splits = [
        ("Train", train_size, train_dates, COLORS['primary']),
        ("Validation", val_size, val_dates, COLORS['warning']),
        ("Test", test_size, test_dates, COLORS['success']),
    ]

    for col, (name, size, dates, color) in zip(cols, splits):
        pct = size / total * 100 if total else 0
        with col:
            st.markdown(f"""
            <div style="
                text-align:center; padding:{SPACING['4']};
                background:{COLORS['bg_card']}; border:1px solid {COLORS['border']};
                border-radius:{BORDER_RADIUS['lg']}; border-top:3px solid {color};
            ">
                <div style="font-size:{FONT_SIZES['body_xs']}; color:{COLORS['text_tertiary']}; text-transform:uppercase;">{name}</div>
                <div style="font-size:{FONT_SIZES['h3']}; font-weight:700; color:{color}; font-family:{FONTS['secondary']};">{size:,}</div>
                <div style="font-size:{FONT_SIZES['body_xs']}; color:{COLORS['text_tertiary']};">{pct:.0f}% · {dates}</div>
            </div>
            """, unsafe_allow_html=True)
