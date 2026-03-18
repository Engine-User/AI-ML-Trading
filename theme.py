# ================================================================
# THEME.PY — Global Design Tokens
# ================================================================

COLORS = {
    'primary':        '#615fff',
    'primary_light':  'rgba(97, 95, 255, 0.12)',
    'bg_primary':     '#1d293d',
    'bg_secondary':   '#0f172b',
    'bg_card':        '#1e293b',
    'text_primary':   '#e2e8f0',
    'text_secondary': '#94a3b8',
    'text_tertiary':  '#64748b',
    'border':         '#314158',
    'success':        '#10b981',
    'danger':         '#ef4444',
    'warning':        '#f59e0b',
    'info':           '#3b82f6',
    'neutral':        '#6b7280',
}

FONTS = {
    'primary':   '"Space Grotesk", sans-serif',
    'secondary': '"JetBrains Mono", monospace',
    'google_fonts_url': (
        'https://fonts.googleapis.com/css2?'
        'family=Space+Grotesk:wght@300;400;500;600;700&'
        'family=JetBrains+Mono:wght@400;500;600;700&display=swap'
    ),
}

FONT_SIZES = {
    'display_lg': '2.5rem',
    'h1':         '2rem',
    'h2':         '1.75rem',
    'h3':         '1.5rem',
    'h4':         '1.25rem',
    'body':       '1rem',
    'body_sm':    '0.875rem',
    'body_xs':    '0.75rem',
}

SPACING = {
    '1': '0.25rem',
    '2': '0.5rem',
    '3': '0.75rem',
    '4': '1rem',
    '5': '1.25rem',
    '6': '1.5rem',
    '8': '2rem',
}

BORDER_RADIUS = {
    'sm':   '0.375rem',
    'md':   '0.5rem',
    'lg':   '0.75rem',
    'xl':   '1rem',
    'full': '9999px',
}

CHART_COLORS = ['#615fff', '#10b981', '#ef4444', '#f59e0b', '#ec4899', '#8b5cf6', '#3b82f6']


def get_signal_color(signal: int) -> str:
    """Return color for signal: 0=neutral, 1=bearish, 2=bullish."""
    return {0: COLORS['neutral'], 1: COLORS['danger'], 2: COLORS['success']}.get(signal, COLORS['neutral'])


def get_signal_label(signal: int) -> str:
    """Return label for signal class."""
    return {0: 'NEUTRAL', 1: 'BEARISH', 2: 'BULLISH'}.get(signal, 'NEUTRAL')


def apply_chart_theme(fig):
    """Apply dark theme to a Plotly figure."""
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        #font=dict(family=FONTS['primary'], color=COLORS['text_primary'], size=12),
        xaxis=dict(gridcolor=COLORS['border'], zerolinecolor=COLORS['border']),
        yaxis=dict(gridcolor=COLORS['border'], zerolinecolor=COLORS['border']),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig
