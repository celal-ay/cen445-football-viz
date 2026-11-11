import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

# Ensure src modules are resolvable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.charts import (
    create_choropleth_map,
    create_treemap,
    create_sankey_diagram,
    create_parallel_coordinates,
    create_network_graph,
    create_odds_contour_density,
    create_score_heatmap,
    create_calibration_scatter,
    create_league_goals_violin
)
from src.ml_engine import (
    run_team_clustering,
    train_match_classifier
)

# ------------------------------------------------------------------------------
# 1. Page Configuration & Styling
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="European Football Intelligence | CEN445",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-header {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-bottom: 1.2rem;
    }
    .kpi-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. Data Loading (Fast & Always Fresh)
# ------------------------------------------------------------------------------
def load_data():
    parquet_path = os.path.join(os.path.dirname(__file__), "data", "processed_matches.parquet")
    csv_path = os.path.join(os.path.dirname(__file__), "data", "processed_matches.csv")
    
    if os.path.exists(parquet_path):
        df = pd.read_parquet(parquet_path)
    elif os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        st.error("Dataset not found! Please check data/ directory.")
        return pd.DataFrame()
    return df

df_raw = load_data()

if df_raw.empty:
    st.stop()

# ------------------------------------------------------------------------------
# 3. Interactive Sidebar (Filters & Controls)
# ------------------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/53/53283.png", width=64)
    st.title("⚽ Control Panel")
    st.caption("CEN445 - Exploratory Data Visualization")
    st.write("---")
    
    # Filter 1: League Multiselect (Dropdown)
    all_leagues = sorted(df_raw['league_name'].unique().tolist())
    
    # Refresh button to clear any cached states
    if st.button("🔄 Reload & Reset Filters"):
        st.cache_data.clear()
        st.session_state.clear()
        st.rerun()

    selected_leagues = st.multiselect(
        "🏆 Select Leagues",
        options=all_leagues,
        default=all_leagues,
        key="selected_leagues_multiselect"
    )
    
    # Filter 2: Season Selector (Selectbox)
    all_seasons = ["All Seasons"] + sorted(df_raw['season'].unique().tolist(), reverse=True)
    selected_season = st.selectbox("📅 Select Season", options=all_seasons)
    
    # Filter 3: Total Goals Range (Slider)
    min_goals, max_goals = int(df_raw['total_goals'].min()), int(df_raw['total_goals'].max())
    goal_range = st.slider(
        "🎯 Total Goals Range",
        min_value=min_goals,
        max_value=max_goals,
        value=(min_goals, max_goals)
    )
    
    # Filter 4: Max Home Odds (Slider)
    max_odds_limit = st.slider(
        "💰 Max Home Odds Filter",
        min_value=1.0,
        max_value=15.0,
        value=15.0,
        step=0.5
    )
    
    # Filter 5: Comebacks Only (Checkbox)
    comebacks_only = st.checkbox("🔥 Show Comebacks Only (HT Deficit -> FT Win)", value=False)
    
    st.write("---")
    st.markdown("ℹ️ **Dataset Metrics:**")
    st.markdown(f"- Total Loaded: **{len(df_raw):,}** matches")
    st.markdown("- Dimensions: **30 columns**")
    st.markdown("- Coverage: **7 Leagues, 2 Seasons**")

# ------------------------------------------------------------------------------
# 4. Apply Filters to Dataset
# ------------------------------------------------------------------------------
df_filtered = df_raw.copy()

if selected_leagues:
    df_filtered = df_filtered[df_filtered['league_name'].isin(selected_leagues)]

if selected_season != "All Seasons":
    df_filtered = df_filtered[df_filtered['season'] == selected_season]

df_filtered = df_filtered[
    (df_filtered['total_goals'] >= goal_range[0]) & 
    (df_filtered['total_goals'] <= goal_range[1]) &
    (df_filtered['home_odds'] <= max_odds_limit)
]

if comebacks_only:
    df_filtered = df_filtered[
        ((df_filtered['htr'] == 'A') & (df_filtered['ftr'] == 'H')) |
        ((df_filtered['htr'] == 'H') & (df_filtered['ftr'] == 'A'))
    ]

# ------------------------------------------------------------------------------
# 5. Header & Top KPI Metrics
# ------------------------------------------------------------------------------
st.markdown('<div class="main-header">European Football Intelligence & Match Dynamics</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Interactive Exploratory Visualization Dashboard • CEN445 Assignment</div>', unsafe_allow_html=True)

# KPI Row
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
total_matches = len(df_filtered)
avg_goals = df_filtered['total_goals'].mean() if total_matches > 0 else 0
home_win_rate = (df_filtered['ftr'] == 'H').mean() * 100 if total_matches > 0 else 0
over_25_rate = (df_filtered['is_over_25'] == 1).mean() * 100 if total_matches > 0 else 0
btts_rate = (df_filtered['btts'] == 1).mean() * 100 if total_matches > 0 else 0

kpi1.metric("Matches Displayed", f"{total_matches:,}")
kpi2.metric("Avg Goals / Match", f"{avg_goals:.2f}")
kpi3.metric("Home Win Advantage", f"{home_win_rate:.1f}%")
kpi4.metric("Over 2.5 Goals", f"{over_25_rate:.1f}%")
kpi5.metric("Both Teams Scored", f"{btts_rate:.1f}%")

st.write("---")

if total_matches == 0:
    st.warning("⚠️ No matches match your filter criteria. Please broaden your selections in the sidebar.")
    st.stop()

# ------------------------------------------------------------------------------
# 6. Tabbed Visualization Layout (9 Charts across 3 Tabs + 1 ML Tab)
# ------------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🌍 1. League & Geography",
    "🌊 2. Match Momentum & Odds",
    "🔥 3. Scores & Team Networks",
    "🤖 4. Machine Learning & Predictive Insights"
])

# ------------------------------------------------------------------------------
# TAB 1: League & Geography (3 Visualizations)
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("Geographical Landscape & League Hierarchies")
    st.info("💡 **Analytical Insight:** European leagues exhibit distinct goal profiles. Use the map to compare countries and the treemap to navigate team-level productivity.")
    
    # Chart 1: Choropleth Map (Advanced)
    st.plotly_chart(create_choropleth_map(df_filtered), use_container_width=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        # Chart 2: Treemap (Advanced)
        st.plotly_chart(create_treemap(df_filtered), use_container_width=True)
    with col_b:
        # Chart 9: League Goal Distribution (Analytical - Violin/Box)
        st.plotly_chart(create_league_goals_violin(df_filtered), use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 2: Match Momentum & Odds (3 Visualizations)
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("Match Flow Dynamics & Multi-Dimensional Odds Space")
    st.info("💡 **Analytical Insight:** Explore how halftime leads translate into fulltime victories via Sankey flow, and inspect multi-dimensional betting lines with Parallel Coordinates.")
    
    # Chart 3: Sankey Diagram (Advanced)
    st.plotly_chart(create_sankey_diagram(df_filtered), use_container_width=True)
    
    col_c, col_d = st.columns(2)
    with col_c:
        # Chart 4: Parallel Coordinates (Advanced)
        st.plotly_chart(create_parallel_coordinates(df_filtered), use_container_width=True)
    with col_d:
        # Chart 6: 2D Contour Density (Advanced)
        st.plotly_chart(create_odds_contour_density(df_filtered), use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 3: Scores & Team Networks (3 Visualizations)
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("Exact Score Matrix, Calibration & Team Dominance Network")
    st.info("💡 **Analytical Insight:** Visualizing the most frequent exact scoreline combinations, bookmaker probability efficiency, and head-to-head dominance networks.")
    
    col_e, col_f = st.columns(2)
    with col_e:
        # Chart 7: Score Heatmap (Analytical)
        st.plotly_chart(create_score_heatmap(df_filtered), use_container_width=True)
    with col_f:
        # Chart 8: Calibration Scatter Plot (Analytical)
        st.plotly_chart(create_calibration_scatter(df_filtered), use_container_width=True)
        
    # Chart 5: Network Graph (Advanced)
    network_league = st.selectbox(
        "Select League for Network Dominance Analysis:",
        options=selected_leagues if selected_leagues else all_leagues,
        index=0
    )
    st.plotly_chart(create_network_graph(df_filtered, selected_league=network_league), use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 4: Machine Learning & Predictive Insights (2 ML Models)
# ------------------------------------------------------------------------------
with tab4:
    st.subheader("Machine Learning Augmentation (Clustering & Classification)")
    st.info("💡 **Analytical Insight:** Machine learning models identify underlying tactical archetypes of teams and provide probability distributions for match outcomes based on market closing lines.")
    
    # ML 1: K-Means Clustering
    st.markdown("#### 1️⃣ K-Means Clustering: Team Tactical Archetypes")
    n_clusters = st.slider("Select Number of Clusters (k):", min_value=2, max_value=5, value=3)
    teams_df, cluster_fig = run_team_clustering(df_filtered, n_clusters=n_clusters)
    st.plotly_chart(cluster_fig, use_container_width=True)
    
    with st.expander("🔍 View Clustered Team Profiles Table"):
        st.dataframe(
            teams_df[['team_name', 'cluster_label', 'matches', 'goals_per_match', 'conceded_per_match', 'win_rate']],
            use_container_width=True
        )
    
    st.write("---")
    
    # ML 2: Match Outcome Classifier
    st.markdown("#### 2️⃣ Logistic Regression: Outcome Prediction & Feature Importance")
    acc, model, scaler, cm_fig, imp_fig = train_match_classifier(df_filtered)
    
    col_g, col_h = st.columns(2)
    with col_g:
        st.plotly_chart(cm_fig, use_container_width=True)
    with col_h:
        st.plotly_chart(imp_fig, use_container_width=True)
        
    # Live Interactive Predictor
    st.markdown("##### 🔮 Live Match Prediction Simulator")
    sim_col1, sim_col2, sim_col3 = st.columns(3)
    with sim_col1:
        sim_h = st.number_input("Simulated Home Odds:", min_value=1.05, max_value=25.0, value=1.75, step=0.05)
    with sim_col2:
        sim_d = st.number_input("Simulated Draw Odds:", min_value=1.05, max_value=25.0, value=3.60, step=0.05)
    with sim_col3:
        sim_a = st.number_input("Simulated Away Odds:", min_value=1.05, max_value=25.0, value=4.50, step=0.05)
        
    # Fair probabilities
    raw_h, raw_d, raw_a = 1.0 / sim_h, 1.0 / sim_d, 1.0 / sim_a
    m = raw_h + raw_d + raw_a
    p_h, p_d, p_a = raw_h / m, raw_d / m, raw_a / m
    
    sim_input = pd.DataFrame([{
        'prob_home': p_h, 'prob_draw': p_d, 'prob_away': p_a,
        'home_odds': sim_h, 'draw_odds': sim_d, 'away_odds': sim_a
    }])
    sim_scaled = scaler.transform(sim_input)
    pred_probs = model.predict_proba(sim_scaled)[0]
    classes = list(model.classes_)
    
    prob_dict = {c: p for c, p in zip(classes, pred_probs)}
    
    pcol1, pcol2, pcol3 = st.columns(3)
    pcol1.metric("Predicted Home Win Prob", f"{prob_dict.get('H', 0):.1%}")
    pcol2.metric("Predicted Draw Prob", f"{prob_dict.get('D', 0):.1%}")
    pcol3.metric("Predicted Away Win Prob", f"{prob_dict.get('A', 0):.1%}")

# ------------------------------------------------------------------------------
# 7. Raw Data Explorer & Export
# ------------------------------------------------------------------------------
st.write("---")
with st.expander("📥 Explore Filtered Data & Export"):
    st.dataframe(df_filtered.head(100), use_container_width=True)
    csv_bytes = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv_bytes,
        file_name="filtered_matches_cen445.csv",
        mime="text/csv"
    )

# Footer
st.caption("CEN445 Introduction to Data Visualization • Team Project Dashboard • Built with Python & Streamlit")
