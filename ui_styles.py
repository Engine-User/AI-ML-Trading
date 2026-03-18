# ================================================================
# UI_STYLES.PY — Minimal CSS & UI Components
# ================================================================
import streamlit as st
from theme import COLORS, FONTS, FONT_SIZES, SPACING, BORDER_RADIUS, get_signal_color, get_signal_label


def load_global_css():
    """Inject minimal global CSS overrides."""
    st.markdown(f"""
    <style>
        @import url('{FONTS["google_fonts_url"]}');

        /* Apply space grotesk cleanly */
        html, body, div, span, p, h1, h2, h3, h4, h5, h6, a, label, button, li {{
            font-family: {FONTS['primary']}, sans-serif;
        }}
        
        /* Protect Streamlit internal Material Icons from being overwritten */
        .material-symbols-rounded, .material-symbols-outlined, .material-icons, [class*="icon"], [class*="Icon"], i {{
            font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        }}

        /* Smooth animations */
        .qf-animate-fade {{
            animation: qfFadeIn 0.5s ease-out;
        }}
        @keyframes qfFadeIn {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Remove default padding from main block */
        .block-container {{ padding-top: 2rem; }}

        /* Enhanced Shiny Cards */
        .qf-card-shiny {{
            background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-top: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: {BORDER_RADIUS['lg']};
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5), 0 2px 4px -1px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        .qf-card-shiny::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 100%;
            background: linear-gradient(180deg, rgba(255,255,255,0.03) 0%, transparent 100%);
            pointer-events: none;
        }}
        .qf-card-shiny:hover {{
            transform: translateY(-3px);
            box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.6), 0 8px 10px -5px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);
            border-color: rgba(97, 95, 255, 0.5);
        }}

        /* Fixed Dimensions */
        .qf-metric-height {{ height: 130px; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: {SPACING['4']}; text-align: center; }}
        .qf-feature-height {{ height: 160px; display: flex; flex-direction: column; justify-content: flex-start; padding: {SPACING['5']}; }}
        .qf-kpi-height {{ height: 110px; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: {SPACING['4']}; text-align: center; }}

        /* Sidebar Styling Overrides */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #111827 0%, #0f172a 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }}
        section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
        section[data-testid="stSidebar"] input {{
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 6px !important;
            color: #ffffff !important;
        }}
        section[data-testid="stSidebar"] hr {{
            border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        }}

        /* Sleek Sidebar Radio Buttons */
        section[data-testid="stSidebar"] div[role="radiogroup"] > label {{
            background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-top: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 8px !important;
            padding: 10px 16px !important;
            margin: 4px 0 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}
        section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 12px -2px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
            border-color: rgba(97, 95, 255, 0.4) !important;
        }}
        
        /* 3D Glowing Signal Badges */
        .qf-signal-badge {{
            text-align: center;
            padding: {SPACING['8']};
            background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
            border-radius: {BORDER_RADIUS['xl']};
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            margin: {SPACING['2']} auto;
        }}
        .qf-signal-badge::before {{
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 100%;
            pointer-events: none; opacity: 0.15;
            background: radial-gradient(circle at 50% 0%, currentColor 0%, transparent 70%);
        }}
        .qf-signal-0 {{ box-shadow: 0 10px 30px -5px {COLORS['neutral']}30, inset 0 2px 4px rgba(255,255,255,0.1); border: 2px solid {COLORS['border']}; border-top-color: {COLORS['border']}; color: {COLORS['neutral']}; }}
        .qf-signal-1 {{ box-shadow: 0 10px 30px -5px {COLORS['danger']}40, inset 0 2px 4px rgba(255,255,255,0.1); border: 2px solid {COLORS['danger']}40; border-top-color: {COLORS['danger']}; color: {COLORS['danger']}; }}
        .qf-signal-2 {{ box-shadow: 0 10px 30px -5px {COLORS['success']}40, inset 0 2px 4px rgba(255,255,255,0.1); border: 2px solid {COLORS['success']}40; border-top-color: {COLORS['success']}; color: {COLORS['success']}; }}

        .qf-signal-0:hover {{ box-shadow: 0 15px 40px -5px {COLORS['neutral']}50, inset 0 2px 4px rgba(255,255,255,0.2); transform: translateY(-4px) scale(1.02); }}
        .qf-signal-1:hover {{ box-shadow: 0 15px 40px -5px {COLORS['danger']}60, inset 0 2px 4px rgba(255,255,255,0.2); transform: translateY(-4px) scale(1.02); }}
        .qf-signal-2:hover {{ box-shadow: 0 15px 40px -5px {COLORS['success']}60, inset 0 2px 4px rgba(255,255,255,0.2); transform: translateY(-4px) scale(1.02); }}

        /* Mono font class */
        .qf-mono {{ font-family: {FONTS['secondary']}; }}
    </style>
    """, unsafe_allow_html=True)


def card(title: str, body: str = ""):
    """Render a simple card with title and optional body HTML."""
    st.markdown(f"""
    <div class="qf-card-shiny qf-feature-height" style="margin-bottom: {SPACING['4']};">
        <div style="font-weight: 600; font-size: {FONT_SIZES['h4']}; margin-bottom: {SPACING['3']}; color: {COLORS['text_primary']}; display: flex; align-items: center; gap: {SPACING['2']};">
            {title}
        </div>
        <div style="font-size: {FONT_SIZES['body_sm']}; color: {COLORS['text_secondary']}; line-height: 1.6;">
            {body}
        </div>
    </div>
    """, unsafe_allow_html=True)


def metric_display(label: str, value: str, delta=None, delta_format: str = "percentage"):
    """Show a metric. Optionally with delta."""
    delta_html = ""
    if delta is not None:
        d_color = COLORS['success'] if delta >= 0 else COLORS['danger']
        d_sign = "+" if delta >= 0 else ""
        d_suffix = "%" if delta_format == "percentage" else ""
        delta_html = f'<div style="color:{d_color}; font-size:{FONT_SIZES["body_xs"]}; font-weight:600; margin-top:{SPACING["1"]}; letter-spacing: 0.5px;">{d_sign}{delta:.2f}{d_suffix}</div>'

    st.markdown(f"""
    <div class="qf-card-shiny qf-metric-height">
        <div style="font-size: {FONT_SIZES['body_xs']}; color: {COLORS['text_tertiary']}; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; margin-bottom: {SPACING['2']};">
            {label}
        </div>
        <div style="font-size: {FONT_SIZES['h3']}; font-weight: 700; color: {COLORS['text_primary']}; font-family: {FONTS['secondary']}; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">
            {value}
        </div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str):
    """Terminal-style section header."""
    st.markdown(f"""
    <div style="
        border-bottom: 1px solid {COLORS['border']};
        padding: {SPACING['3']} 0;
        margin: {SPACING['8']} 0 {SPACING['4']} 0;
    ">
        <span style="
            font-family: {FONTS['secondary']};
            font-size: {FONT_SIZES['body_xs']};
            color: {COLORS['primary']};
            letter-spacing: 1.5px;
            text-transform: uppercase;
        ">▸ {title}</span>
    </div>
    """, unsafe_allow_html=True)


def signal_badge(signal: int, confidence: float = 0.0):
    """Large 3D signal badge for live prediction."""
    color = get_signal_color(signal)
    label = get_signal_label(signal)
    emoji = {0: "⏸️", 1: "🔻", 2: "✅"}.get(signal, "✅")

    conf_html = ""
    if confidence:
        conf_html = f'<div style="font-size:{FONT_SIZES["body_sm"]}; color:{COLORS["text_secondary"]}; margin-top:{SPACING["3"]}; font-weight: 500;">Confidence: {confidence:.1%}</div>'

    st.markdown(f"""
    <div class="qf-signal-badge qf-signal-{signal}">
        <div style="font-size: 3.8rem; margin-bottom: {SPACING['3']}; text-shadow: 0 4px 10px rgba(0,0,0,0.5);">{emoji}</div>
        <div style="
            font-size: {FONT_SIZES['h1']};
            font-weight: 800;
            margin: {SPACING['2']} 0;
            letter-spacing: 4px;
            text-transform: uppercase;
            text-shadow: 0 2px 5px rgba(0,0,0,0.8);
        ">{label}</div>
        {conf_html}
    </div>
    """, unsafe_allow_html=True)


def live_price_banner(symbol: str, price: float, subtitle: str = ""):
    """Banner showing live price with golden 3D edge effect."""
    st.markdown(f"""
    <div class="qf-card-shiny" style="
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid rgba(234, 179, 8, 0.4);
        border-top: 1px solid rgba(250, 204, 21, 0.8);
        border-radius: {BORDER_RADIUS['xl']};
        padding: {SPACING['6']} {SPACING['8']};
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: {SPACING['6']};
        box-shadow: 0 10px 30px -5px rgba(234, 179, 8, 0.2), inset 0 2px 4px rgba(255, 255, 255, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        cursor: pointer;
    " onmouseover="this.style.transform='scale(1.01) translateY(-2px)'; this.style.boxShadow='0 20px 40px -5px rgba(234, 179, 8, 0.35), inset 0 2px 4px rgba(255, 255, 255, 0.2)'; this.style.borderColor='rgba(250, 204, 21, 0.8)';" onmouseout="this.style.transform='scale(1) translateY(0)'; this.style.boxShadow='0 10px 30px -5px rgba(234, 179, 8, 0.2), inset 0 2px 4px rgba(255, 255, 255, 0.1)'; this.style.borderColor='rgba(234, 179, 8, 0.4)';">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 100%; background: radial-gradient(circle at 10% 50%, rgba(250, 204, 21, 0.15) 0%, transparent 60%); pointer-events: none; z-index: 0;"></div>
        <div style="position: relative; z-index: 1;">
            <div style="font-size: 1.1rem; color: #fbbf24; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 6px; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">{symbol} <span style="font-size: 0.8rem; color: #fef08a; font-weight: 500; background: rgba(234,179,8,0.2); padding: 2px 6px; border-radius: 4px; margin-left: 8px;">ACTIVE</span></div>
            <div style="font-size: 3.2rem; font-weight: 800; color: #ffffff; font-family: {FONTS['secondary']}; text-shadow: 0 4px 10px rgba(0,0,0,0.6); line-height: 1;">
                ₹{price:,.2f}
            </div>
        </div>
        <div style="position: relative; z-index: 1; text-align: right;">
            <div style="font-size: 0.95rem; color: {COLORS['text_secondary']}; font-weight: 500; background: rgba(0,0,0,0.3); padding: {SPACING['3']} {SPACING['4']}; border-radius: {BORDER_RADIUS['md']}; border: 1px solid rgba(255,255,255,0.05);">
                {subtitle}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def hero_section(title: str, subtitle: str, icon: str = "💲"):
    """Hero landing section."""
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: {SPACING['8']} 0;
    ">
        <div style="font-size: 3.5rem; margin-bottom: {SPACING['3']};">{icon}</div>
        <h1 style="
            font-size: {FONT_SIZES['display_lg']};
            font-weight: 600;
            color: {COLORS['text_primary']};
            margin: 0 0 {SPACING['3']} 0;
        ">{title}</h1>
        <p style="
            font-size: {FONT_SIZES['body']};
            color: {COLORS['text_secondary']};
            max-width: 600px;
            margin: 0 auto;
        ">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def split_card(left_title, left_body, right_title, right_body):
    """Two-column card."""
    c1, c2 = st.columns(2)
    with c1:
        card(left_title, left_body)
    with c2:
        card(right_title, right_body)


def kpi_card(name: str, value: str, color=None):
    """Small KPI metric card."""
    c = color or COLORS['primary']
    st.markdown(f"""
    <div class="qf-card-shiny qf-kpi-height">
        <div style="font-size: {FONT_SIZES['body_xs']}; color: {COLORS['text_tertiary']}; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; margin-bottom: {SPACING['1']};">
            {name}
        </div>
        <div style="font-size: {FONT_SIZES['h3']}; color: {c}; font-weight: 700; font-family: {FONTS['secondary']}; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">
            {value}
        </div>
    </div>
    """, unsafe_allow_html=True)


def success_banner(message: str):
    """Green success completion banner."""
    st.markdown(f"""
    <div style="
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid {COLORS['success']};
        border-radius: {BORDER_RADIUS['lg']};
        padding: {SPACING['5']};
        text-align: center;
        margin: {SPACING['6']} 0;
    ">
        <span style="font-size: 1.5rem;">✅</span>
        <span style="color: {COLORS['success']}; font-weight: 500; margin-left: {SPACING['2']};">
            {message}
        </span>
    </div>
    """, unsafe_allow_html=True)


def footer(brand: str = "AI Enabled Stock Market Analysis", version: str = "V1.2"):
    """Minimal footer."""
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: {SPACING['6']} 0 {SPACING['4']} 0;
        margin-top: {SPACING['8']};
        border-top: 1px solid {COLORS['border']};
        font-size: {FONT_SIZES['body_xs']};
        color: {COLORS['text_tertiary']};
    ">
        {brand} {version}
    </div>
    """, unsafe_allow_html=True)
