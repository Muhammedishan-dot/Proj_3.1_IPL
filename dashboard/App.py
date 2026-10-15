import sqlite3
import math

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="IPL Cricket Analytics | Teams & Venues",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DB = r"C:\Users\ishan\OneDrive\Desktop\project_3.1\data\raw\ipl.db"

# Premium dark theme: midnight navy, slate panels, restrained orange accent
BG = "#0B1220"
NAVY = "#16243A"
NAVY_2 = "#213B5B"
ORANGE = "#F2A541"
TEAL = "#4E9B83"
LIGHT_BLUE = "#91A8C7"
GREY = "#536174"
INK = "#E8EEF7"
MUTED = "#A7B4C7"
BORDER = "#29384D"
PANEL = "#111C2D"
WHITE = "#111C2D"
PALETTE = [
    "#1F3A5F", "#D98324", "#3F7F6E", "#7A5C8E", "#A64B4B",
    "#4A7AA8", "#8C8C3A", "#5B6770", "#B08D57", "#2F6F8F",
    "#8A5A44", "#6B8E4E",
] * 4


# ============================================================
# DATA AND CHART HELPERS
# ============================================================
@st.cache_data(show_spinner=False)
def q(sql, params=()):
    """Run a read-only dashboard query and cache its result."""
    with sqlite3.connect(DB) as con:
        return pd.read_sql_query(sql, con, params=params)


def look(fig, x_title, y_title, height=420, legend=False, legend_title=""):
    """Apply a consistent, readable chart style."""
    fig.update_layout(
        xaxis_title=x_title,
        yaxis_title=y_title,
        height=height,
        showlegend=legend,
        legend_title_text=legend_title,
        plot_bgcolor=PANEL,
        paper_bgcolor=PANEL,
        coloraxis_showscale=False,
        font=dict(color=INK, size=12, family="Arial"),
        margin=dict(t=48, b=28, l=12, r=24),
        hoverlabel=dict(bgcolor="#1B2A40", font_color="#F8FAFC"),
        xaxis=dict(title_font=dict(size=13), automargin=True, zeroline=False),
        yaxis=dict(title_font=dict(size=13), automargin=True, zeroline=False),
    )
    fig.update_xaxes(showgrid=False, linecolor=BORDER, tickfont=dict(color=INK))
    fig.update_yaxes(gridcolor="#26354A", tickfont=dict(color=INK))
    return fig


def section_heading(title, subtitle=None):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.caption(subtitle)


def chart_card_title(title, note=None):
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    if note:
        st.caption(note)


def safe_int(value):
    return int(0 if pd.isna(value) else value)


def download_csv(data, filename, label="Download CSV"):
    """Offer a downloadable copy of the currently displayed result table."""
    if data is not None and not data.empty:
        st.download_button(
            label=label,
            data=data.to_csv(index=False).encode("utf-8-sig"),
            file_name=filename,
            mime="text/csv",
            key=f"download_{filename.replace('.', '_')}",
        )


# ============================================================
# STYLING
# ============================================================
st.markdown(
    f"""
    <style>
    :root {{
        color-scheme: dark;
    }}
    .stApp {{
        background: {BG};
        color: {INK};
    }}
    [data-testid="stHeader"] {{
        background: rgba(11,18,32,0.92);
    }}
    .block-container {{
        max-width: 1480px;
        padding-top: 1.4rem;
        padding-bottom: 3rem;
    }}
    .stPlotlyChart {{
        border: 1px solid {BORDER};
        border-radius: 13px;
        overflow: hidden;
        background: {PANEL};
        padding: 5px;
    }}
    div[data-testid="stDownloadButton"] button {{
        border: 1px solid #40536C;
        border-radius: 9px;
        color: #EAF0F8;
        background: #16243A;
        font-weight: 650;
    }}
    div[data-testid="stDownloadButton"] button:hover {{
        border-color: {ORANGE};
        color: {ORANGE};
    }}
    .presentation-note {{
        border: 1px solid {BORDER};
        border-left: 4px solid {ORANGE};
        background: {PANEL};
        border-radius: 8px;
        padding: 10px 14px;
        color: {MUTED};
        font-size: 12px;
        margin: 8px 0 16px 0;
    }}
    .hero {{
        background: linear-gradient(120deg, #142238 0%, #1B3553 60%, #234666 100%);
        border: 1px solid #304763;
        padding: 30px 34px;
        border-radius: 16px;
        color: #F8FAFC;
        margin-bottom: 22px;
        box-shadow: 0 14px 34px rgba(0,0,0,0.22);
        position: relative;
        overflow: hidden;
    }}
    .hero:after {{
        content: "";
        position: absolute;
        top: 0;
        right: 0;
        width: 7px;
        height: 100%;
        background: {ORANGE};
    }}
    .hero-kicker {{
        color: {ORANGE};
        text-transform: uppercase;
        letter-spacing: 2.2px;
        font-size: 11px;
        font-weight: 800;
        margin-bottom: 9px;
    }}
    .hero-title {{
        color: #FFFFFF;
        font-size: 34px;
        line-height: 1.12;
        font-weight: 780;
        margin-bottom: 9px;
    }}
    .hero-subtitle {{
        color: #C8D4E3;
        font-size: 14px;
        margin: 0;
        max-width: 850px;
    }}
    .section-title {{
        font-size: 20px;
        font-weight: 750;
        color: #F1F5F9;
        border-left: 4px solid {ORANGE};
        padding-left: 12px;
        margin: 26px 0 13px 0;
        letter-spacing: -0.2px;
    }}
    .chart-title {{
        color: #EAF0F8;
        font-size: 15px;
        font-weight: 700;
        margin: 3px 0 6px 0;
    }}
    .small-note {{
        color: {MUTED};
        font-size: 12px;
    }}
    [data-testid="stMetric"] {{
        background: linear-gradient(145deg, #142136, #111C2D);
        border: 1px solid {BORDER};
        border-top: 3px solid {ORANGE};
        padding: 17px 19px;
        border-radius: 13px;
        box-shadow: 0 7px 20px rgba(0,0,0,0.12);
        min-height: 112px;
    }}
    [data-testid="stMetricLabel"] {{
        color: {MUTED};
        font-size: 13px;
        font-weight: 600;
    }}
    [data-testid="stMetricValue"] {{
        color: #F8FAFC;
        font-size: 29px;
        font-weight: 760;
    }}
    [data-testid="stMetricDelta"] {{
        color: {ORANGE};
    }}
    [data-testid="stTabs"] [data-baseweb="tab-list"] {{
        gap: 8px;
        border-bottom: 1px solid {BORDER};
        background: transparent;
    }}
    [data-testid="stTabs"] [data-baseweb="tab"] {{
        background: transparent;
        padding: 12px 20px;
        font-weight: 650;
        color: {MUTED};
    }}
    [data-testid="stTabs"] [aria-selected="true"] {{
        color: #FFFFFF !important;
        border-bottom: 3px solid {ORANGE} !important;
    }}
    [data-testid="stCaptionContainer"], .stMarkdown p, label {{
        color: {MUTED};
    }}
    [data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 10px;
        overflow: hidden;
    }}
    div[data-testid="stAlert"] {{
        background: #17263A;
        border: 1px solid #31445D;
        color: {INK};
        border-radius: 10px;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {PANEL};
        border-color: {BORDER};
        border-radius: 14px;
    }}
    [data-baseweb="select"] > div, [data-baseweb="input"] > div {{
        background: #111C2D;
        border-color: {BORDER};
    }}
    .stSlider [data-baseweb="slider"] div {{
        color: {ORANGE};
    }}
    hr {{
        border-color: {BORDER};
    }}
    </style>

    <div class="hero">
        <div class="hero-kicker">IPL · Domain D</div>
        <div class="hero-title">Cricket Analytics</div>
        <p class="hero-subtitle">Teams &amp; Venues — performance intelligence for understanding team results, ground conditions, and match strategy.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## 🏏 Dashboard guide")
    st.caption("IPL Cricket Analytics · Teams & Venues")
    st.markdown("**Overview**")
    st.caption("League-wide team wins, venue activity, batting-first trends, sixes, and seasonal ground coverage.")
    st.markdown("**Venue**")
    st.caption("Choose a ground to inspect scoring conditions, batting-first versus chasing results, and seasonal scoring.")
    st.markdown("**Team**")
    st.caption("Choose a team to review season performance, opponent records, batting-order results, and team comparisons.")
    st.divider()
    st.markdown("**Reading the analysis**")
    st.caption("Check the match count alongside every percentage. Small samples can make a venue or team look unusually strong or weak.")

presentation_mode = st.toggle(
    "Presentation mode",
    value=False,
    help="Hides helper captions and adds breathing room for screenshots or live presentations.",
)
if presentation_mode:
    st.markdown(
        """
        <style>
        [data-testid="stCaptionContainer"] { display: none; }
        .block-container { max-width: 1600px; padding-top: 1.8rem; }
        [data-testid="stMetric"] { min-height: 125px; }
        </style>
        <div class="presentation-note">Presentation mode is on. Use the same filters and charts; helper captions are hidden for a cleaner view.</div>
        """,
        unsafe_allow_html=True,
    )

# Shared data used throughout the tabs
venues = q("""
    SELECT venue_clean AS ground, COUNT(*) AS matches
    FROM matches_clean
    GROUP BY venue_clean
    ORDER BY matches DESC, venue_clean
""")

teams = q("""
    SELECT team1 AS t FROM matches
    UNION
    SELECT team2 FROM matches
    ORDER BY t
""")["t"].tolist()

if venues.empty or not teams:
    st.error("The database did not return any grounds or teams. Check the database path and tables.")
    st.stop()

TEAM_COLORS = dict(zip(teams, PALETTE))
GROUND_COLORS = dict(zip(venues["ground"], PALETTE))

# Shared filter value: used consistently in Overview and Venue tabs.
if "min_matches" not in st.session_state:
    st.session_state.min_matches = 20

tab1, tab2, tab3 = st.tabs(["Overview", "Venue analysis", "Team analysis"])


# ============================================================
# TAB 1: OVERVIEW
# ============================================================
with tab1:
    n_teams = safe_int(q("""
        SELECT COUNT(*) AS n
        FROM (SELECT team1 FROM matches UNION SELECT team2 FROM matches)
    """).iloc[0]["n"])
    n_grounds = safe_int(q("SELECT COUNT(DISTINCT venue_clean) AS n FROM matches_clean").iloc[0]["n"])
    n_raw = safe_int(q("SELECT COUNT(DISTINCT venue) AS n FROM matches").iloc[0]["n"])
    n_matches = safe_int(q("SELECT COUNT(*) AS n FROM matches_clean").iloc[0]["n"])

    chase = q("SELECT COUNT(*) AS decided, SUM(chase_won) AS wins FROM v_match_totals")
    decided = safe_int(chase.iloc[0]["decided"])
    chase_wins = safe_int(chase.iloc[0]["wins"])

    if decided:
        p = chase_wins / decided
        se = math.sqrt(p * (1 - p) / decided)
        low, high = 100 * (p - 1.96 * se), 100 * (p + 1.96 * se)
        z = (p - 0.5) / math.sqrt(0.25 / decided)
        p_value = math.erfc(abs(z) / math.sqrt(2))
        p_text = "p < 0.001" if p_value < 0.001 else f"p = {p_value:.3f}"
        chase_pct = f"{100 * p:.1f}%"
    else:
        p = se = z = p_value = 0
        low = high = 0
        p_text = "not available"
        chase_pct = "N/A"

    section_heading("League at a glance", "A quick summary of the data and the chasing result.")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Teams", f"{n_teams:,}")
    k2.metric("Matches played", f"{n_matches:,}")
    k3.metric("Cleaned grounds", f"{n_grounds:,}")
    k4.metric("Chasing win rate", chase_pct, help="Share of decided matches won by the side chasing.")
    st.caption(
        f"Venue standardisation: {n_grounds} cleaned grounds represent {n_raw} distinct raw venue spellings. "
        f"Chasing won {chase_wins:,} of {decided:,} decided matches."
    )
    if decided:
        st.info(
            f"Chasing win rate: 95% interval {low:.1f}%–{high:.1f}%. "
            f"Test against a 50% win rate: z = {z:.2f}, {p_text}. "
            + ("The result differs significantly from 50%." if p_value < 0.05
               else "The observed difference from 50% is not statistically significant.")
        )

    # Display filters only control chart density; totals and source data remain unchanged.
    section_heading("Dashboard filters", "Adjust how many teams and grounds are displayed in the overview charts.")
    filter_a, filter_b = st.columns(2)
    with filter_a:
        top_teams = st.slider(
            "Teams to display in win chart",
            min_value=5, max_value=max(5, len(teams)), value=min(14, max(5, len(teams))),
            step=1, help="Limits the number of bars shown; it does not change the underlying calculations.",
        )
    with filter_b:
        top_grounds = st.slider(
            "Grounds to display in venue chart",
            min_value=5, max_value=max(5, len(venues)), value=min(20, max(5, len(venues))),
            step=1, help="Limits the number of grounds displayed, sorted by match count.",
        )

    # Matches won by team
    section_heading("Team and venue performance", "Compare team results with how frequently each ground has hosted matches.")
    wins = q("""
        SELECT t.team,
               COUNT(*) AS played,
               SUM(CASE WHEN mc.match_winner = t.team THEN 1 ELSE 0 END) AS won
        FROM (
            SELECT match_id, team1 AS team FROM matches
            UNION ALL
            SELECT match_id, team2 AS team FROM matches
        ) t
        JOIN matches_clean mc ON mc.match_id = t.match_id
        GROUP BY t.team
        ORDER BY won DESC
    """)
    wins["label"] = (
        wins["won"].astype(int).astype(str) + " won of " + wins["played"].astype(int).astype(str)
        + " played (" + (100 * wins["won"] / wins["played"]).round(0).astype(int).astype(str) + "%)"
    )
    wins_chart = wins.head(top_teams).copy()
    chart_card_title("Matches won by team", f"Showing top {len(wins_chart)} of {len(wins)} teams. Labels include matches played.")
    fig = px.bar(
        wins_chart, x="won", y="team", orientation="h", text="label",
        color_discrete_sequence=["#7196C7"],
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_yaxes(categoryorder="total ascending", title="")
    fig.update_xaxes(range=[0, max(1, wins["won"].max()) * 1.35])
    look(fig, "Matches won", "Team", height=max(360, 31 * len(wins_chart)))
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"{wins.iloc[0]['team']} have the most wins: "
        f"{int(wins.iloc[0]['won'])} of {int(wins.iloc[0]['played'])} matches."
    )
    download_csv(wins[["team", "played", "won"]], "ipl_team_wins.csv", "Download team wins")

    min_matches = st.slider(
        "Minimum matches to assess a ground",
        min_value=5, max_value=50, value=int(st.session_state.min_matches), step=1,
        key="overview_min_matches",
        help="Grounds below this number are shown as having too few matches for a confident comparison.",
    )
    st.session_state.min_matches = min_matches

    grounds = venues.copy()
    grounds["enough"] = grounds["matches"].apply(
        lambda x: "Enough to judge" if x >= min_matches else "Too few to judge"
    )
    n_enough = int((grounds["matches"] >= min_matches).sum())

    grounds_chart = grounds.head(top_grounds).copy()
    chart_card_title(
        "Matches hosted by ground",
        f"Showing {len(grounds_chart)} of {len(grounds)} grounds · {n_enough} grounds overall meet the {min_matches}-match threshold."
    )
    fig = px.bar(
        grounds_chart, x="matches", y="ground", orientation="h", text="matches", color="enough",
        color_discrete_map={"Enough to judge": TEAL, "Too few to judge": "#657286"},
    )
    fig.add_vline(
        x=min_matches, line_dash="dash", line_color=ORANGE,
        annotation_text=f"minimum {min_matches}"
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_yaxes(categoryorder="total ascending", title="")
    fig.update_xaxes(range=[0, max(1, grounds["matches"].max()) * 1.12])
    look(fig, "Matches hosted", "Ground", height=max(420, 25 * len(grounds_chart)), legend=True)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Grounds are ordered by match count. Green indicates the selected threshold is met; "
        "grey indicates fewer matches."
    )
    download_csv(grounds[["ground", "matches", "enough"]], "ipl_ground_matches.csv", "Download ground matches")

    # Batting first by ground
    section_heading("Match conditions", "Ground-level results are shown only where the sample meets your selected threshold.")
    bat = q("""
        SELECT venue_clean AS ground,
               COUNT(*) AS decided,
               ROUND(100.0 * SUM(1 - chase_won) / COUNT(*), 1) AS bat_pct
        FROM v_match_totals
        WHERE venue_clean IN (
            SELECT venue_clean FROM matches_clean
            GROUP BY venue_clean HAVING COUNT(*) >= ?
        )
        GROUP BY venue_clean
        ORDER BY bat_pct DESC
    """, (min_matches,))
    league_bat_df = q("""
        SELECT ROUND(100.0 * SUM(1 - chase_won) / COUNT(*), 1) AS pct
        FROM v_match_totals
    """)
    league_bat = float(league_bat_df.iloc[0]["pct"]) if not league_bat_df.empty and pd.notna(league_bat_df.iloc[0]["pct"]) else 0.0

    if bat.empty:
        st.info("No ground meets the selected threshold. Lower the minimum-match setting.")
    else:
        bat["vs league"] = bat["bat_pct"].apply(lambda x: "Above league" if x > league_bat else "At or below league")
        bat["label"] = bat["bat_pct"].astype(str) + "% · n=" + bat["decided"].astype(str)
        fig = px.bar(
            bat, x="ground", y="bat_pct", text="label", color="vs league",
            color_discrete_map={"Above league": ORANGE, "At or below league": NAVY},
        )
        fig.add_hline(y=league_bat, line_dash="dash", line_color=INK,
                      annotation_text=f"league {league_bat}%")
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_yaxes(range=[0, 112])
        fig.update_xaxes(tickangle=-35)
        look(fig, "Ground", "Batting-first win rate (%)", height=490, legend=True)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Orange bars are above the league batting-first win rate. n is the number of decided matches.")
        download_csv(bat, "ipl_batting_first_by_ground.csv", "Download ground win rates")

    # Sixes by team
    section_heading("Batting and tournament footprint", "Big-hitting totals and the number of grounds used over time.")
    sixes = q("""
        SELECT batting_team AS team,
               SUM(CASE WHEN batter_runs = 6 THEN 1 ELSE 0 END) AS sixes
        FROM v_ball
        GROUP BY batting_team
        ORDER BY sixes DESC
    """)
    with st.container(border=True):
        chart_card_title("Total sixes by team", "Totals across all seasons; teams with more matches had more opportunities.")
        fig = px.bar(sixes, x="sixes", y="team", orientation="h", text="sixes",
                     color_discrete_sequence=["#7196C7"])
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_yaxes(categoryorder="total ascending", title="")
        fig.update_xaxes(range=[0, max(1, sixes["sixes"].max()) * 1.15])
        look(fig, "Total sixes", "Team", height=max(400, 28 * len(sixes)))
        st.plotly_chart(fig, use_container_width=True)
        if not sixes.empty:
            st.caption(f"{sixes.iloc[0]['team']} have hit the most sixes: {int(sixes.iloc[0]['sixes']):,}.")
        download_csv(sixes, "ipl_team_sixes.csv", "Download sixes by team")

    gs = q("""
        SELECT season_year AS season, COUNT(DISTINCT venue_clean) AS grounds
        FROM matches_clean
        GROUP BY season_year
        ORDER BY season_year
    """)
    if not gs.empty:
        span = max(1, gs["grounds"].max() - gs["grounds"].min())
        shade = (gs["grounds"] - gs["grounds"].min()) / span
        fills = px.colors.sample_colorscale("Blues", list(shade * 0.8 + 0.15))
        fig = go.Figure(go.Table(
            header=dict(
                values=["Measure"] + gs["season"].astype(str).tolist(),
                fill_color=NAVY_2, font=dict(color="white", size=12),
                align="center", height=34,
                line_color=BORDER,
            ),
            cells=dict(
                values=[["Grounds used"]] + [[int(v)] for v in gs["grounds"]],
                fill_color=[[NAVY]] + [[c] for c in fills],
                font=dict(color=[["#F8FAFC"]] + [["white" if s > 0.55 else INK] for s in shade], size=12),
                align="center", height=38, line_color=BORDER,
            ),
        ))
        fig.update_layout(height=110, margin=dict(t=2, b=2, l=2, r=2), paper_bgcolor=PANEL)
        first, last = gs.iloc[0], gs.iloc[-1]
        most = int(gs["grounds"].max())
        most_years = ", ".join(gs.loc[gs["grounds"] == most, "season"].astype(str))
        st.markdown(
            f'<div class="chart-title">Grounds used by season</div>'
            f'<div class="small-note">{int(first["grounds"])} in {int(first["season"])} · '
            f'{int(last["grounds"])} in {int(last["season"])} · peak {most} ({most_years})</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, use_container_width=True)
        download_csv(gs, "ipl_grounds_by_season.csv", "Download seasonal ground counts")


# ============================================================
# TAB 2: VENUE ANALYSIS
# ============================================================
with tab2:
    section_heading("Venue analysis", "Select grounds to compare scoring patterns and match outcomes.")
    default_ground = venues.iloc[0]["ground"]
    chosen = st.multiselect(
        "Grounds to compare (ordered by match count)",
        options=venues["ground"].tolist(),
        default=[default_ground],
    )
    if not chosen:
        chosen = [default_ground]
        st.info(f"No ground selected, so showing {default_ground}.")

    marks = ",".join("?" for _ in chosen)
    held = venues[venues["ground"].isin(chosen)].copy()
    held["Enough to judge?"] = held["matches"].apply(
        lambda x: "Yes" if x >= int(st.session_state.min_matches) else "No — too few"
    )
    held.columns = ["Ground", "Matches held", "Enough to judge?"]
    few = held.loc[held["Matches held"] < int(st.session_state.min_matches), "Ground"].tolist()

    a, b = st.columns([1.2, 2.8])
    with a:
        chart_card_title("Selected-ground summary")
        st.dataframe(
            held.astype({"Matches held": str}),
            hide_index=True, use_container_width=True,
            column_config={
                "Ground": st.column_config.TextColumn("Ground"),
                "Matches held": st.column_config.TextColumn("Matches held"),
                "Enough to judge?": st.column_config.TextColumn("Enough to judge?"),
            },
        )
        if few:
            st.warning(
                f"Fewer than {int(st.session_state.min_matches)} matches at: {', '.join(few)}. "
                "Treat the comparisons below cautiously."
            )
        download_csv(held, "ipl_selected_ground_summary.csv", "Download ground summary")
    with b:
        score = q(f"""
            SELECT mc.venue_clean AS ground, ROUND(AVG(i.runs), 1) AS avg_runs
            FROM v_innings i
            JOIN matches_clean mc ON mc.match_id = i.match_id
            WHERE i.innings = 1 AND mc.venue_clean IN ({marks})
            GROUP BY mc.venue_clean
            ORDER BY avg_runs DESC
        """, tuple(chosen))
        league_avg_df = q("SELECT ROUND(AVG(runs), 1) AS a FROM v_innings WHERE innings = 1")
        league_avg = float(league_avg_df.iloc[0]["a"]) if not league_avg_df.empty and pd.notna(league_avg_df.iloc[0]["a"]) else 0.0
        chart_card_title("Average first-innings score", "Dashed line represents the league-wide average.")
        if not score.empty:
            fig = px.bar(score, x="ground", y="avg_runs", text="avg_runs", color="ground",
                         color_discrete_map=GROUND_COLORS)
            fig.add_hline(y=league_avg, line_dash="dash", line_color=INK,
                          annotation_text=f"league average {league_avg}")
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_yaxes(range=[0, max(float(score["avg_runs"].max()), league_avg, 1) * 1.2])
            fig.update_xaxes(tickangle=-25)
            look(fig, "Selected ground", "Average first-innings score (runs)", height=410)
            st.plotly_chart(fig, use_container_width=True)
            top = score.iloc[0]
            gap = float(top["avg_runs"]) - league_avg
            st.caption(
                f"{top['ground']} has the highest average among selected grounds: {top['avg_runs']} runs, "
                f"{abs(gap):.1f} {'above' if gap >= 0 else 'below'} the league average."
            )
        else:
            st.info("No first-innings score data is available for the selected grounds.")

    section_heading("Batting first or chasing?", "Shares are calculated from decided matches at each selected ground.")
    vc = q(f"""
        SELECT venue_clean AS ground, COUNT(*) AS decided, SUM(chase_won) AS chase_wins
        FROM v_match_totals
        WHERE venue_clean IN ({marks})
        GROUP BY venue_clean
        ORDER BY decided DESC
    """, tuple(chosen))

    if vc.empty:
        st.info("No decided matches at the selected grounds.")
    else:
        vc["axis"] = vc["ground"] + "<br>(" + vc["decided"].astype(str) + " decided)"
        vc["Batting first won"] = 100 * (vc["decided"] - vc["chase_wins"]) / vc["decided"]
        vc["Chasing won"] = 100 * vc["chase_wins"] / vc["decided"]
        outcome = vc.melt(
            id_vars="axis",
            value_vars=["Batting first won", "Chasing won"],
            var_name="Result", value_name="Share",
        )
        fig = px.bar(
            outcome, x="axis", y="Share", color="Result", barmode="group", text="Share",
            color_discrete_map={"Batting first won": ORANGE, "Chasing won": "#7196C7"},
        )
        fig.add_hline(y=50, line_dash="dash", line_color=INK, annotation_text="50% (equal)")
        fig.update_traces(texttemplate="%{y:.0f}%", textposition="outside", cliponaxis=False)
        fig.update_yaxes(range=[0, 112])
        fig.update_xaxes(tickangle=-20)
        look(fig, "Ground (decided-match count shown below)", "Share of decided matches (%)", height=430, legend=True, legend_title="Result")
        st.plotly_chart(fig, use_container_width=True)
        bat_better = int((vc["Batting first won"] > vc["Chasing won"]).sum())
        chase_better = int((vc["Chasing won"] > vc["Batting first won"]).sum())
        if len(vc) == 1:
            who = "Batting first" if bat_better else ("Chasing" if chase_better else "Neither side")
            st.caption(f"{who} wins more often at {vc.iloc[0]['ground']}.")
        else:
            st.caption(
                f"Batting first wins more often at {bat_better} of {len(vc)} selected grounds; "
                f"chasing wins more often at {chase_better}."
            )

    vs = q(f"""
        SELECT mc.venue_clean AS ground, mc.season_year AS season,
               COUNT(*) AS matches, ROUND(AVG(i.runs), 1) AS avg_runs
        FROM v_innings i
        JOIN matches_clean mc ON mc.match_id = i.match_id
        WHERE i.innings = 1 AND mc.venue_clean IN ({marks})
        GROUP BY mc.venue_clean, mc.season_year
        ORDER BY mc.season_year
    """, tuple(chosen))
    if not vs.empty:
        vs["season"] = vs["season"].astype(str)
        fig = px.line(
            vs, x="season", y="avg_runs", color="ground", markers=True,
            hover_data=["matches"], color_discrete_map=GROUND_COLORS,
        )
        fig.add_hline(y=league_avg, line_dash="dash", line_color=INK,
                      annotation_text=f"league average {league_avg}")
        fig.update_traces(line_width=3, marker_size=7)
        fig.update_xaxes(type="category", categoryorder="array", categoryarray=sorted(vs["season"].unique()))
        look(fig, "Season (year)", "Average first-innings score (runs)", height=430, legend=True, legend_title="Ground")
        section_heading("Scoring trend by season", "Hover over a point to see the number of matches behind the average.")
        st.plotly_chart(fig, use_container_width=True)
        download_csv(vs, "ipl_ground_scoring_by_season.csv", "Download seasonal scoring")
    else:
        st.info("No seasonal scoring data is available for the selected grounds.")


# ============================================================
# TAB 3: TEAM ANALYSIS
# ============================================================
with tab3:
    section_heading("Team analysis", "Choose a team and season range to update every metric and chart.")
    filter1, filter2 = st.columns([1, 2])
    with filter1:
        team = st.selectbox("Select a team", teams)
    seasons = [int(x) for x in q(
        "SELECT DISTINCT season_year AS s FROM matches_clean ORDER BY s"
    )["s"].dropna()]
    if not seasons:
        st.warning("No season values are available in matches_clean.")
        st.stop()
    with filter2:
        lo, hi = st.select_slider(
            "Seasons to include", options=seasons, value=(seasons[0], seasons[-1])
        )
    st.caption(f"All team statistics below cover seasons {lo}–{hi}.")

    rec = q("""
        SELECT COUNT(*) AS played,
               SUM(CASE WHEN match_winner = ? THEN 1 ELSE 0 END) AS won
        FROM matches_clean
        WHERE match_id IN (
            SELECT match_id FROM matches WHERE team1 = ? OR team2 = ?
        )
        AND season_year BETWEEN ? AND ?
    """, (team, team, team, lo, hi))
    played = safe_int(rec.iloc[0]["played"])
    won = safe_int(rec.iloc[0]["won"])
    if played == 0:
        st.warning(f"{team} played no matches between {lo} and {hi}. Widen the season range.")
        st.stop()

    section_heading("Selected team summary")
    m1, m2, m3 = st.columns(3)
    m1.metric("Matches played", f"{played:,}")
    m2.metric("Matches won", f"{won:,}")
    m3.metric("Win rate", f"{100 * won / played:.1f}%")

    with st.expander("Compare with another team", expanded=False):
        other_teams = [name for name in teams if name != team]
        compare_team = st.selectbox(
            "Comparison team",
            other_teams,
            key="compare_team_select",
            help="Compare win rates across the same selected season range.",
        )
        compare_row = q("""
            SELECT COUNT(*) AS played,
                   SUM(CASE WHEN match_winner = ? THEN 1 ELSE 0 END) AS won
            FROM matches_clean
            WHERE match_id IN (
                SELECT match_id FROM matches WHERE team1 = ? OR team2 = ?
            )
            AND season_year BETWEEN ? AND ?
        """, (compare_team, compare_team, compare_team, lo, hi))
        compare_played = safe_int(compare_row.iloc[0]["played"])
        compare_won = safe_int(compare_row.iloc[0]["won"])
        compare_rate = 100 * compare_won / compare_played if compare_played else 0.0
        comp1, comp2, comp3 = st.columns(3)
        comp1.metric(f"{team} win rate", f"{100 * won / played:.1f}%")
        comp2.metric(f"{compare_team} win rate", f"{compare_rate:.1f}%")
        gap = (100 * won / played) - compare_rate
        comp3.metric("Win-rate difference", f"{gap:+.1f} pp")
        if compare_played == 0:
            st.info(f"{compare_team} has no matches in the selected season range.")
        else:
            compare_df = pd.DataFrame({
                "Team": [team, compare_team],
                "Matches played": [played, compare_played],
                "Matches won": [won, compare_won],
                "Win rate (%)": [round(100 * won / played, 1), round(compare_rate, 1)],
            })
            compare_fig = px.bar(
                compare_df, x="Team", y="Win rate (%)", text="Win rate (%)",
                color="Team",
                color_discrete_map={team: ORANGE, compare_team: "#7196C7"},
            )
            compare_fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside", cliponaxis=False)
            compare_fig.update_yaxes(range=[0, 112])
            look(compare_fig, "Team", "Win rate (%)", height=320, legend=False)
            st.plotly_chart(compare_fig, use_container_width=True)
            download_csv(compare_df, "ipl_team_comparison.csv", "Download team comparison")

    ts = q("""
        SELECT mc.season_year AS season, COUNT(*) AS played,
               ROUND(100.0 * SUM(CASE WHEN mc.match_winner = ? THEN 1 ELSE 0 END) / COUNT(*), 1) AS win_pct
        FROM matches_clean mc
        WHERE mc.match_id IN (
            SELECT match_id FROM matches WHERE team1 = ? OR team2 = ?
        )
        AND mc.season_year BETWEEN ? AND ?
        GROUP BY mc.season_year
        ORDER BY mc.season_year
    """, (team, team, team, lo, hi))
    if not ts.empty:
        ts["season"] = ts["season"].astype(str)
        ts["label"] = ts["win_pct"].round(0).astype(int).astype(str) + "% (n=" + ts["played"].astype(str) + ")"
        fig = px.line(ts, x="season", y="win_pct", markers=True, text="label",
                      color_discrete_sequence=[ORANGE])
        fig.add_hline(y=50, line_dash="dash", line_color=INK, annotation_text="50%")
        fig.update_traces(textposition="top center", line_width=3.5, marker_size=8)
        fig.update_xaxes(type="category")
        fig.update_yaxes(range=[0, 112])
        look(fig, "Season", "Win rate (%)", height=410)
        best = ts.sort_values("win_pct").iloc[-1]
        worst = ts.sort_values("win_pct").iloc[0]
        section_heading("Win rate by season", f"Best: {best['season']} ({best['win_pct']}%). Weakest: {worst['season']} ({worst['win_pct']}%).")
        st.plotly_chart(fig, use_container_width=True)
        download_csv(ts, "ipl_selected_team_season_win_rate.csv", "Download seasonal win rate")

    opp = q("""
        SELECT CASE WHEN m.team1 = ? THEN m.team2 ELSE m.team1 END AS opponent,
               COUNT(*) AS played,
               SUM(CASE WHEN mc.match_winner = ? THEN 1 ELSE 0 END) AS won,
               ROUND(100.0 * SUM(CASE WHEN mc.match_winner = ? THEN 1 ELSE 0 END) / COUNT(*), 1) AS win_pct
        FROM matches m
        JOIN matches_clean mc ON mc.match_id = m.match_id
        WHERE (m.team1 = ? OR m.team2 = ?)
          AND mc.season_year BETWEEN ? AND ?
        GROUP BY opponent
        ORDER BY win_pct DESC, played DESC
    """, (team, team, team, team, team, lo, hi))

    section_heading("Head-to-head performance", "Win percentage against each opponent in the selected seasons.")
    if not opp.empty:
        opp["label"] = (
            opp["win_pct"].astype(str) + "% (" + opp["won"].fillna(0).astype(int).astype(str)
            + "/" + opp["played"].astype(str) + ")"
        )
        fig = px.bar(
            opp, x="win_pct", y="opponent", orientation="h", text="label",
            color="win_pct",
            color_continuous_scale=["#C76B70", "#35445A", TEAL],
            range_color=[0, 100],
        )
        fig.add_vline(x=50, line_dash="dash", line_color=INK, annotation_text="50%")
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_yaxes(categoryorder="total ascending", title="")
        fig.update_xaxes(range=[0, 135])
        look(fig, "Win rate against opponent (%)", "Opponent", height=max(390, 34 * len(opp)))
        st.plotly_chart(fig, use_container_width=True)
        best_opp = opp.iloc[0]
        worst_opp = opp.iloc[-1]
        st.caption(
            f"Highest listed win rate: {best_opp['opponent']} ({best_opp['win_pct']}%). "
            f"Lowest listed win rate: {worst_opp['opponent']} ({worst_opp['win_pct']}%). "
            "Match counts are shown in each bar label."
        )
        download_csv(opp, "ipl_head_to_head.csv", "Download head-to-head results")
    else:
        st.info("No opponent records are available for this team and season range.")

    tb = q("""
        SELECT CASE WHEN vt.bat_first_team = ? THEN 'Batting first' ELSE 'Chasing' END AS batting_order,
               COUNT(*) AS played,
               SUM(CASE WHEN vt.match_winner = ? THEN 1 ELSE 0 END) AS won
        FROM v_match_totals vt
        JOIN matches m ON m.match_id = vt.match_id
        WHERE (m.team1 = ? OR m.team2 = ?)
          AND vt.season_year BETWEEN ? AND ?
        GROUP BY batting_order
    """, (team, team, team, team, lo, hi))
    section_heading("Performance by batting order", "Compare the team's win rate when setting a target and when chasing.")
    if not tb.empty:
        tb["win_pct"] = (100 * tb["won"] / tb["played"]).round(1)
        tb["label"] = (
            tb["win_pct"].astype(str) + "% (" + tb["won"].fillna(0).astype(int).astype(str)
            + " won of " + tb["played"].astype(str) + ")"
        )
        fig = px.bar(
            tb, x="batting_order", y="win_pct", text="label", color="batting_order",
            color_discrete_map={"Batting first": ORANGE, "Chasing": "#7196C7"},
        )
        fig.add_hline(y=50, line_dash="dash", line_color=INK, annotation_text="50%")
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_yaxes(range=[0, 112])
        look(fig, "Batting order", "Win rate (%)", height=390, legend=False)
        st.plotly_chart(fig, use_container_width=True)
        better = tb.sort_values("win_pct").iloc[-1]
        st.caption(f"{team} have the higher win rate when {better['batting_order'].lower()} ({better['win_pct']}%).")
        download_csv(tb, "ipl_batting_order_performance.csv", "Download batting-order results")
    else:
        st.info("No batting-order result data is available for this team and season range.")

st.markdown(
    f'<div style="text-align:center;color:{MUTED};font-size:11px;padding-top:22px;'
    f'border-top:1px solid {BORDER};margin-top:24px;">IPL Cricket Analytics · Teams &amp; Venues</div>',
    unsafe_allow_html=True,
)

