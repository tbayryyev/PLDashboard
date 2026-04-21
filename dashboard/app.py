import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd

# ── Load & clean data ────────────────────────────────────────────────────────
df = pd.read_csv("PL_team_stats.csv")
df.columns = df.columns.str.strip()
df["Squad"] = df["Squad"].str.strip()

df["Non-PK Goals"] = df["Gls"] - df["PK"]
df["Shots Off Target"] = df["Sh"] - df["SoT"]
pd.set_option("future.no_silent_downcasting", True)
pk_conv = df["PK"] / df["PKatt"].replace(0, pd.NA) * 100
df["PK Conversion%"] = pd.to_numeric(pk_conv, errors="coerce").fillna(0).round(1)
df = df.sort_values("Gls", ascending=False).reset_index(drop=True)

# ── Design tokens ────────────────────────────────────────────────────────────
TEAM_COLORS = {
    "Arsenal": "#EF0107", "Aston Villa": "#670E36", "Bournemouth": "#DA291C",
    "Brentford": "#e30613", "Brighton": "#0057B8", "Burnley": "#6C1D45",
    "Chelsea": "#034694", "Crystal Palace": "#1B458F", "Everton": "#003399",
    "Fulham": "#555555", "Leeds United": "#FFCD00", "Liverpool": "#C8102E",
    "Manchester City": "#6CABDD", "Manchester Utd": "#DA291C",
    "Newcastle United": "#444444", "Nottingham Forest": "#DD0000",
    "Sunderland": "#EB172B", "Tottenham Hotspur": "#132257",
    "West Ham United": "#7A263A", "Wolves": "#FDB913",
}

BG = "#06080d"
SURFACE = "rgba(255,255,255,0.03)"
CARD_BG = "rgba(255,255,255,0.04)"
CARD_BORDER = "rgba(255,255,255,0.06)"
TEXT_PRIMARY = "#f0f0f5"
TEXT_SECONDARY = "#7a7d8e"
TEXT_MUTED = "#4a4d5e"
ACCENT = "#5463ed"
ACCENT_DIM = "rgba(129,140,248,0.15)"
GRID_COLOR = "rgba(255,255,255,0.04)"
DIVIDER = "rgba(255,255,255,0.06)"

FONT = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"

# ── Custom CSS ───────────────────────────────────────────────────────────────
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* { box-sizing: border-box; }

body {
    margin: 0;
    background: #06080d;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.15); }

/* Dropdown overrides */
.Select-control { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 10px !important; }
.Select-control:hover { border-color: rgba(129,140,248,0.3) !important; }
.Select-menu-outer { background: #12141c !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 10px !important; margin-top: 4px !important; }
.Select-option { background: transparent !important; color: #f0f0f5 !important; }
.Select-option:hover, .Select-option.is-focused { background: rgba(129,140,248,0.1) !important; }
.Select-value-label, .Select-placeholder, .Select-input > input { color: #f0f0f5 !important; }
.Select-multi-value-wrapper .Select-value { background: rgba(129,140,248,0.15) !important; border: 1px solid rgba(129,140,248,0.25) !important; border-radius: 6px !important; color: #818cf8 !important; }
.Select-value-icon { border-right-color: rgba(129,140,248,0.25) !important; }
.Select-arrow-zone .Select-arrow { border-top-color: #7a7d8e !important; }
.Select.is-open .Select-arrow { border-bottom-color: #7a7d8e !important; }
.Select-clear-zone { color: #7a7d8e !important; }

/* Dash graph container */
.js-plotly-plot .plotly .modebar { display: none !important; }

/* KPI hover */
.kpi-card { transition: all 0.2s ease; }
.kpi-card:hover { transform: translateY(-2px); border-color: rgba(129,140,248,0.2) !important; background: rgba(255,255,255,0.06) !important; }

/* Table row hover */
.stats-row { transition: background 0.15s ease; }
.stats-row:hover { background: rgba(129,140,248,0.06) !important; }
"""

# ── App setup ────────────────────────────────────────────────────────────────
app = dash.Dash(__name__)
app.title = "PL 25/26 Shooting Stats"

app.index_string = '''<!DOCTYPE html>
<html>
<head>
{%metas%}
<title>{%title%}</title>
{%favicon%}
{%css%}
<style>''' + CUSTOM_CSS + '''</style>
</head>
<body>
{%app_entry%}
<footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>'''

STAT_OPTIONS = [
    {"label": "Goals", "value": "Gls"},
    {"label": "Shots", "value": "Sh"},
    {"label": "Shots on Target", "value": "SoT"},
    {"label": "SoT %", "value": "SoT%"},
    {"label": "Shots / 90", "value": "Sh/90"},
    {"label": "Goals / Shot", "value": "G/Sh"},
    {"label": "Goals / SoT", "value": "G/SoT"},
    {"label": "Non-PK Goals", "value": "Non-PK Goals"},
]

# ── Components───────────────────────────────────────────────────────────────
def kpi_card(icon, title, value, subtitle="", accent_color=ACCENT):
    return html.Div(className="kpi-card", children=[
        html.Div([
            html.Div(icon, style={
                "width": "36px", "height": "36px", "borderRadius": "10px",
                "background": f"linear-gradient(135deg, {accent_color}22, {accent_color}08)",
                "display": "flex", "alignItems": "center", "justifyContent": "center",
                "fontSize": "16px", "marginBottom": "16px",
                "border": f"1px solid {accent_color}22",
            }),
            html.P(title, style={
                "margin": "0", "fontSize": "11px", "fontWeight": "500",
                "color": TEXT_SECONDARY, "textTransform": "uppercase",
                "letterSpacing": "1.2px",
            }),
            html.H2(value, style={
                "margin": "8px 0 4px", "fontSize": "30px", "fontWeight": "700",
                "color": TEXT_PRIMARY, "letterSpacing": "-0.5px", "lineHeight": "1",
            }),
            html.P(subtitle, style={
                "margin": "0", "fontSize": "12px", "color": TEXT_SECONDARY, "fontWeight": "400",
            }),
        ]),
    ], style={
        "background": CARD_BG, "borderRadius": "16px", "padding": "24px",
        "flex": "1", "minWidth": "185px",
        "border": f"1px solid {CARD_BORDER}",
        "backdropFilter": "blur(20px)",
    })


def section_card(title, children, subtitle=None):
    header = [
        html.H3(title, style={
            "margin": "0", "fontSize": "14px", "fontWeight": "600",
            "color": TEXT_PRIMARY, "letterSpacing": "-0.2px",
        }),
    ]
    if subtitle:
        header.append(html.P(subtitle, style={
            "margin": "4px 0 0", "fontSize": "12px", "color": TEXT_MUTED,
        }))
    return html.Div([
        html.Div(header, style={"marginBottom": "4px"}),
        *children,
    ], style={
        "background": CARD_BG, "borderRadius": "16px", "padding": "24px",
        "border": f"1px solid {CARD_BORDER}", "flex": "1",
        "backdropFilter": "blur(20px)", "overflow": "hidden",
    })


def apply_chart_theme(fig, height=420, show_xgrid=True, show_ygrid=True):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_SECONDARY, family=FONT, size=11),
        margin=dict(l=8, r=16, t=16, b=40),
        height=height,
        xaxis=dict(
            gridcolor=GRID_COLOR if show_xgrid else "rgba(0,0,0,0)",
            showgrid=show_xgrid, zeroline=False,
            tickfont=dict(size=11, color=TEXT_MUTED),
            title_font=dict(size=12, color=TEXT_SECONDARY),
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR if show_ygrid else "rgba(0,0,0,0)",
            showgrid=show_ygrid, zeroline=False,
            tickfont=dict(size=11, color=TEXT_SECONDARY),
            title_font=dict(size=12, color=TEXT_SECONDARY),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=TEXT_SECONDARY),
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        ),
        hoverlabel=dict(
            bgcolor="#1a1d29", font_size=12, font_family=FONT,
            font_color=TEXT_PRIMARY, bordercolor="rgba(255,255,255,0.1)",
        ),
    )
    return fig


# ── Layout ───────────────────────────────────────────────────────────────────
app.layout = html.Div(style={
    "background": BG, "minHeight": "100vh",
    "padding": "40px 48px 60px", "fontFamily": FONT,
    "maxWidth": "1440px", "margin": "0 auto",
}, children=[


    # Header
    html.Div([
        html.Div([
            html.Div([
                html.Span("PL", style={
                    "fontSize": "11px", "fontWeight": "700", "color": ACCENT,
                    "background": ACCENT_DIM, "padding": "4px 10px",
                    "borderRadius": "6px", "letterSpacing": "1px",
                    "border": f"1px solid {ACCENT}33",
                }),
                html.Span("2025/26 Season", style={
                    "fontSize": "12px", "color": TEXT_MUTED, "marginLeft": "10px",
                }),
            ], style={"marginBottom": "12px"}),
            html.H1("Shooting Stats", style={
                "margin": "0", "fontSize": "32px", "fontWeight": "800",
                "color": TEXT_PRIMARY, "letterSpacing": "-1px", "lineHeight": "1.1",
            }),
            html.P("Premier League team shooting performance analysis", style={
                "margin": "8px 0 0", "color": TEXT_MUTED, "fontSize": "14px",
                "fontWeight": "400",
            }),
        ]),
    ], style={"marginBottom": "36px"}),

    # KPI row
    html.Div(id="kpi-cards", style={
        "display": "flex", "gap": "14px", "flexWrap": "wrap", "marginBottom": "32px",
    }),

    # Thin divider
    html.Hr(style={"border": "none", "borderTop": f"1px solid {DIVIDER}", "margin": "0 0 32px"}),

    # Controls
    html.Div([
        html.Div([
            html.Label("Compare stat", style={
                "fontSize": "11px", "color": TEXT_MUTED, "marginBottom": "6px",
                "display": "block", "textTransform": "uppercase",
                "letterSpacing": "1px", "fontWeight": "500",
            }),
            dcc.Dropdown(
                id="stat-picker", options=STAT_OPTIONS, value="Gls", clearable=False,
                style={"width": "200px"},
            ),
        ]),
        html.Div([
            html.Label("Highlight teams", style={
                "fontSize": "11px", "color": TEXT_MUTED, "marginBottom": "6px",
                "display": "block", "textTransform": "uppercase",
                "letterSpacing": "1px", "fontWeight": "500",
            }),
            dcc.Dropdown(
                id="team-filter",
                options=[{"label": s, "value": s} for s in sorted(df["Squad"])],
                value=[], multi=True, placeholder="All teams shown",
                style={"width": "520px"},
            ),
        ]),
    ], style={
        "display": "flex", "gap": "20px", "marginBottom": "28px", "alignItems": "flex-end",
    }),

    # Row 1
    html.Div([
        html.Div([
            html.Div([
                html.H3(id="bar-title", style={
                    "margin": "0", "fontSize": "14px", "fontWeight": "600",
                    "color": TEXT_PRIMARY, "letterSpacing": "-0.2px",
                }),
            ], style={"marginBottom": "4px"}),
            dcc.Graph(id="bar-chart", config={"displayModeBar": False}),
        ], style={
            "background": CARD_BG, "borderRadius": "16px", "padding": "24px",
            "border": f"1px solid {CARD_BORDER}", "flex": "1",
            "backdropFilter": "blur(20px)", "overflow": "hidden",
        }),
        section_card("Shooting Efficiency", [dcc.Graph(id="scatter-chart", config={"displayModeBar": False})],
                     subtitle="Shots vs Goals (bubble = accuracy)"),
    ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

    # Row 2
    html.Div([
        section_card("Goal Breakdown", [dcc.Graph(id="stacked-bar", config={"displayModeBar": False})],
                     subtitle="Open play vs penalties"),
        section_card("Shot Accuracy", [dcc.Graph(id="accuracy-chart", config={"displayModeBar": False})],
                     subtitle="% of shots on target"),
    ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

    # Table
    html.Div([
        section_card("Detailed Stats", [html.Div(id="stats-table", style={"marginTop": "12px", "overflowX": "auto"})],
                     subtitle="All shooting metrics by team"),
    ], style={"marginBottom": "16px"}),

    # Footer
    html.Div([
        html.P("Data source: FBref — Premier League 2025/26 shooting statistics", style={
            "margin": "0", "fontSize": "11px", "color": TEXT_MUTED, "textAlign": "center",
        }),
    ], style={"marginTop": "40px", "paddingTop": "20px", "borderTop": f"1px solid {DIVIDER}"}),
])



# ── Callbacks ────────────────────────────────────────────────────────────────
@app.callback(
    Output("kpi-cards", "children"),
    Output("bar-title", "children"),
    Output("bar-chart", "figure"),
    Output("scatter-chart", "figure"),
    Output("stacked-bar", "figure"),
    Output("accuracy-chart", "figure"),
    Output("stats-table", "children"),
    Input("stat-picker", "value"),
    Input("team-filter", "value"),
)
def update(stat, teams):
    filtered = df if not teams else df[df["Squad"].isin(teams)]
    full = df.copy()

    def get_colors(squads, opacity=1.0):
        if opacity < 1:
            colors = []
            for s in squads:
                hex_c = TEAM_COLORS.get(s, ACCENT)
                r, g, b = int(hex_c[1:3], 16), int(hex_c[3:5], 16), int(hex_c[5:7], 16)
                colors.append(f"rgba({r},{g},{b},{opacity})")
            return colors
        return [TEAM_COLORS.get(s, ACCENT) for s in squads]

    # ── KPIs ─────────────────────────────────────────────────────────────
    top_scorer = full.loc[full["Gls"].idxmax(), "Squad"]
    top_shooter = full.loc[full["Sh"].idxmax(), "Squad"]
    most_accurate = full.loc[full["SoT%"].idxmax(), "Squad"]
    most_efficient = full.loc[full["G/Sh"].idxmax(), "Squad"]

    kpis = [
        kpi_card("G", "Total Goals", str(full["Gls"].sum()),
                 f"Top: {top_scorer} ({full['Gls'].max()})", "#818cf8"),
        kpi_card("S", "Total Shots", str(full["Sh"].sum()),
                 f"Top: {top_shooter} ({full['Sh'].max()})", "#60a5fa"),
        kpi_card("%", "Avg Accuracy", f"{full['SoT%'].mean():.1f}%",
                 f"Best: {most_accurate} ({full['SoT%'].max()}%)", "#34d399"),
        kpi_card("E", "Avg G/Shot", f"{full['G/Sh'].mean():.2f}",
                 f"Best: {most_efficient} ({full['G/Sh'].max()})", "#fbbf24"),
        kpi_card("P", "Penalties", f"{full['PK'].sum()}/{full['PKatt'].sum()}",
                 f"{full['PK'].sum()/max(full['PKatt'].sum(),1)*100:.0f}% converted", "#f472b6"),
    ]

    # ── Bar chart ────────────────────────────────────────────────────────
    bar_df = filtered.sort_values(stat, ascending=True)
    label = next(o["label"] for o in STAT_OPTIONS if o["value"] == stat)

    bar_fig = go.Figure(go.Bar(
        x=bar_df[stat], y=bar_df["Squad"], orientation="h",
        marker=dict(
            color=get_colors(bar_df["Squad"], 0.85),
            line=dict(width=0),
            cornerradius=4,
        ),
        text=bar_df[stat], textposition="outside",
        textfont=dict(size=11, color=TEXT_SECONDARY),
        hovertemplate="<b>%{y}</b><br>" + label + ": %{x}<extra></extra>",
    ))
    apply_chart_theme(bar_fig, height=max(440, len(bar_df) * 30), show_xgrid=False)
    bar_fig.update_layout(
        margin=dict(l=8, r=50, t=16, b=20),
        yaxis=dict(tickfont=dict(size=12, color=TEXT_PRIMARY)),
    )

    # ── Scatter ──────────────────────────────────────────────────────────
    scatter_fig = go.Figure()
    for _, row in filtered.iterrows():
        c = TEAM_COLORS.get(row["Squad"], ACCENT)
        r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
        scatter_fig.add_trace(go.Scatter(
            x=[row["Sh"]], y=[row["Gls"]], mode="markers+text",
            marker=dict(
                size=row["SoT%"] * 0.75 + 4,
                color=f"rgba({r},{g},{b},0.7)",
                line=dict(width=2, color=f"rgba({r},{g},{b},1)"),
            ),
            text=[row["Squad"]], textposition="top center",
            textfont=dict(size=10, color=TEXT_SECONDARY),
            name=row["Squad"], showlegend=False,
            hovertemplate=(
                f"<b>{row['Squad']}</b><br>"
                f"Shots: {row['Sh']}<br>"
                f"Goals: {row['Gls']}<br>"
                f"SoT%: {row['SoT%']}%<extra></extra>"
            ),
        ))
    apply_chart_theme(scatter_fig, height=440)
    scatter_fig.update_layout(
        xaxis_title="Total Shots", yaxis_title="Goals Scored",
        margin=dict(l=40, r=16, t=16, b=50),
    )

    # ── Stacked bar ──────────────────────────────────────────────────────
    stacked_df = filtered.sort_values("Gls", ascending=True)
    stacked_fig = go.Figure()
    stacked_fig.add_trace(go.Bar(
        y=stacked_df["Squad"], x=stacked_df["Non-PK Goals"], name="Open Play",
        orientation="h",
        marker=dict(color="rgba(129,140,248,0.75)", cornerradius=2),
        hovertemplate="<b>%{y}</b><br>Open Play: %{x}<extra></extra>",
    ))
    stacked_fig.add_trace(go.Bar(
        y=stacked_df["Squad"], x=stacked_df["PK"], name="Penalties",
        orientation="h",
        marker=dict(color="rgba(251,191,36,0.75)", cornerradius=2),
        hovertemplate="<b>%{y}</b><br>Penalties: %{x}<extra></extra>",
    ))
    apply_chart_theme(stacked_fig, height=max(440, len(stacked_df) * 30), show_xgrid=False)
    stacked_fig.update_layout(
        barmode="stack",
        margin=dict(l=8, r=16, t=30, b=20),
        yaxis=dict(tickfont=dict(size=12, color=TEXT_PRIMARY)),
    )

    # ── Accuracy ─────────────────────────────────────────────────────────
    acc_df = filtered.sort_values("SoT%", ascending=True)

    # Gradient-like effect using opacity based on value
    max_sot = acc_df["SoT%"].max()
    acc_colors = []
    for _, row in acc_df.iterrows():
        intensity = 0.4 + 0.5 * (row["SoT%"] / max_sot)
        acc_colors.append(f"rgba(52,211,153,{intensity})")

    acc_fig = go.Figure(go.Bar(
        y=acc_df["Squad"], x=acc_df["SoT%"], orientation="h",
        marker=dict(color=acc_colors, cornerradius=4, line=dict(width=0)),
        text=acc_df["SoT%"].apply(lambda v: f"{v}%"),
        textposition="outside",
        textfont=dict(size=11, color=TEXT_SECONDARY),
        hovertemplate="<b>%{y}</b><br>SoT%%: %{x}%<extra></extra>",
    ))
    apply_chart_theme(acc_fig, height=max(440, len(acc_df) * 30), show_xgrid=False)
    acc_fig.update_layout(
        xaxis=dict(range=[0, 48]),
        margin=dict(l=8, r=50, t=16, b=20),
        yaxis=dict(tickfont=dict(size=12, color=TEXT_PRIMARY)),
    )

    # ── Table ────────────────────────────────────────────────────────────
    display_cols = ["Squad", "Gls", "Sh", "SoT", "SoT%", "Sh/90", "SoT/90", "G/Sh", "G/SoT", "Non-PK Goals", "PK", "PKatt"]
    nice_names = {
        "Squad": "Team", "Gls": "Goals", "Sh": "Shots", "SoT": "On Target",
        "SoT%": "SoT%", "Sh/90": "Sh/90", "SoT/90": "SoT/90", "G/Sh": "G/Sh",
        "G/SoT": "G/SoT", "Non-PK Goals": "NPK Goals", "PK": "PK", "PKatt": "PK Att",
    }
    table_df = filtered[display_cols].sort_values("Gls", ascending=False)

    header_style = {
        "padding": "12px 16px", "fontSize": "11px", "fontWeight": "600",
        "color": TEXT_MUTED, "textAlign": "left",
        "textTransform": "uppercase", "letterSpacing": "0.8px",
        "borderBottom": f"1px solid {DIVIDER}",
        "whiteSpace": "nowrap", "background": "transparent",
    }
    cell_style = {
        "padding": "11px 16px", "fontSize": "13px", "color": TEXT_SECONDARY,
        "borderBottom": f"1px solid {DIVIDER}",
        "whiteSpace": "nowrap", "fontVariantNumeric": "tabular-nums",
    }
    team_cell_style = {
        **cell_style, "color": TEXT_PRIMARY, "fontWeight": "600", "fontSize": "13px",
    }

    # Highlight best values
    best = {col: table_df[col].max() for col in display_cols if col != "Squad"}

    def cell_content(row, col):
        val = row[col]
        if col == "Squad":
            color = TEAM_COLORS.get(val, ACCENT)
            return html.Div([
                html.Span(style={
                    "display": "inline-block", "width": "8px", "height": "8px",
                    "borderRadius": "50%", "background": color,
                    "marginRight": "10px", "flexShrink": "0",
                }),
                html.Span(val),
            ], style={"display": "flex", "alignItems": "center"})
        style = {**cell_style}
        if val == best.get(col):
            style["color"] = "#34d399"
            style["fontWeight"] = "600"
        return html.Td(val, style=style)

    table = html.Table([
        html.Thead(html.Tr([
            html.Th(nice_names.get(c, c), style=header_style) for c in display_cols
        ])),
        html.Tbody([
            html.Tr(
                [html.Td(cell_content(row, "Squad"), style=team_cell_style)] +
                [cell_content(row, c) for c in display_cols[1:]],
                className="stats-row",
                style={"background": "transparent" if i % 2 == 0 else "rgba(255,255,255,0.015)"},
            )
            for i, (_, row) in enumerate(table_df.iterrows())
        ]),
    ], style={"width": "100%", "borderCollapse": "collapse", "borderSpacing": "0"})

    return kpis, f"{label} by Team", bar_fig, scatter_fig, stacked_fig, acc_fig, table


if __name__ == "__main__":
    app.run(debug=False, port=8050)
