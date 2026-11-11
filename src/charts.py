"""
charts.py - CEN445 Football Analytics & Visualization Engine
Contains 9 distinct visualizations (6 Advanced + 3 Standard/Analytical)
Fully interactive with hover tooltips, zoom/pan, consistent theming.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import networkx as nx

# Consistent theme & color palette
THEME_TEMPLATE = "plotly_dark"
COLOR_PALETTE = {
    'home': '#3B82F6',       # Blue
    'draw': '#F59E0B',       # Amber
    'away': '#EF4444',       # Red
    'neutral': '#64748B',    # Slate
    'highlight': '#10B981',  # Emerald
    'bg': '#0F172A',
    'paper_bg': '#1E293B'
}

# ==============================================================================
# 1. ADVANCED: Geographical Choropleth Map (Avrupa Haritası)
# Insight: Shows average goals per match and home advantage across European leagues.
# ==============================================================================
def create_choropleth_map(df: pd.DataFrame) -> go.Figure:
    country_stats = df.groupby(['country_iso3', 'country', 'league_name']).agg(
        total_matches=('id', 'count'),
        avg_goals=('total_goals', 'mean'),
        home_win_pct=('ftr', lambda x: (x == 'H').mean() * 100),
        draw_pct=('ftr', lambda x: (x == 'D').mean() * 100),
        away_win_pct=('ftr', lambda x: (x == 'A').mean() * 100)
    ).reset_index()

    country_stats['avg_goals'] = country_stats['avg_goals'].round(2)
    country_stats['home_win_pct'] = country_stats['home_win_pct'].round(1)

    fig = px.choropleth(
        country_stats,
        locations='country_iso3',
        color='avg_goals',
        hover_name='country',
        hover_data={
            'country_iso3': False,
            'league_name': True,
            'total_matches': True,
            'avg_goals': ':.2f',
            'home_win_pct': ':.1f%'
        },
        labels={'avg_goals': 'Avg Goals / Match', 'league_name': 'League'},
        color_continuous_scale='Viridis',
        scope='europe',
        title="🌍 1. European League Landscape: Average Goals & Home Advantage"
    )

    fig.update_layout(
        template=THEME_TEMPLATE,
        geo=dict(
            bgcolor='rgba(0,0,0,0)',
            showcoastlines=True,
            showcountries=True,
            showland=True,
            landcolor='#1E293B',
            lakecolor='#0F172A',
            projection_type='natural earth'
        ),
        margin=dict(l=10, r=10, t=50, b=10),
        height=450
    )
    return fig

# ==============================================================================
# 2. ADVANCED: Hierarchical Treemap (Lig -> Takım Hiyerarşisi)
# Insight: Visualizes goal productivity and match volume across league hierarchies.
# ==============================================================================
def create_treemap(df: pd.DataFrame) -> go.Figure:
    # Team level goals
    home_g = df.groupby(['league_name', 'home_team'])['fthg'].sum().reset_index()
    home_g.columns = ['league_name', 'team', 'goals']
    away_g = df.groupby(['league_name', 'away_team'])['ftag'].sum().reset_index()
    away_g.columns = ['league_name', 'team', 'goals']
    
    team_goals = pd.concat([home_g, away_g]).groupby(['league_name', 'team'])['goals'].sum().reset_index()
    
    # Wins calculation
    home_w = df[df['ftr'] == 'H'].groupby(['league_name', 'home_team']).size().reset_index(name='wins')
    home_w.columns = ['league_name', 'team', 'wins']
    away_w = df[df['ftr'] == 'A'].groupby(['league_name', 'away_team']).size().reset_index(name='wins')
    away_w.columns = ['league_name', 'team', 'wins']
    team_wins = pd.concat([home_w, away_w]).groupby(['league_name', 'team'])['wins'].sum().reset_index()

    merged = pd.merge(team_goals, team_wins, on=['league_name', 'team'], how='left').fillna(0)

    fig = px.treemap(
        merged,
        path=[px.Constant("All Selected Leagues"), 'league_name', 'team'],
        values='goals',
        color='wins',
        color_continuous_scale='Blues',
        hover_data={'goals': True, 'wins': True},
        title="🌳 2. Goal Dominance & Wins Treemap (League & Team Hierarchy)"
    )

    fig.update_layout(
        template=THEME_TEMPLATE,
        margin=dict(l=10, r=10, t=50, b=10),
        height=500
    )
    return fig

# ==============================================================================
# 3. ADVANCED: Sankey Diagram (HT Sonucu -> FT Sonucu Akışı & Comeback Analizi)
# Insight: Visualizes match momentum transitions (e.g. halftime deficit to win).
# ==============================================================================
def create_sankey_diagram(df: pd.DataFrame) -> go.Figure:
    # Nodes:
    # 0: HT Home Win, 1: HT Draw, 2: HT Away Win
    # 3: FT Home Win, 4: FT Draw, 5: FT Away Win
    label_map = {
        'H': ('HT: Home Lead', 'FT: Home Win'),
        'D': ('HT: Draw', 'FT: Draw'),
        'A': ('HT: Away Lead', 'FT: Away Win')
    }

    flows = df.groupby(['htr', 'ftr']).size().reset_index(name='count')
    
    node_labels = [
        "HT: Home Lead", "HT: Draw", "HT: Away Lead",
        "FT: Home Win", "FT: Draw", "FT: Away Win"
    ]
    node_colors = [
        "#3B82F6", "#F59E0B", "#EF4444",
        "#2563EB", "#D97706", "#DC2626"
    ]

    source_idx = {'H': 0, 'D': 1, 'A': 2}
    target_idx = {'H': 3, 'D': 4, 'A': 5}

    sources = [source_idx[r['htr']] for _, r in flows.iterrows()]
    targets = [target_idx[r['ftr']] for _, r in flows.iterrows()]
    values = flows['count'].tolist()

    # Flow colors: highlight comebacks with vibrant colors
    link_colors = []
    for _, r in flows.iterrows():
        if r['htr'] == 'A' and r['ftr'] == 'H':
            link_colors.append("rgba(16, 185, 129, 0.7)") # Emerald comeback
        elif r['htr'] == 'H' and r['ftr'] == 'A':
            link_colors.append("rgba(244, 63, 94, 0.7)")  # Rose away comeback
        elif r['htr'] == r['ftr']:
            link_colors.append("rgba(59, 130, 246, 0.35)")
        else:
            link_colors.append("rgba(148, 163, 184, 0.25)")

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=18,
            thickness=22,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors
        )
    )])

    fig.update_layout(
        title="🌊 3. Half-Time to Full-Time Result Momentum (Sankey Flow)",
        template=THEME_TEMPLATE,
        height=450,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig

# ==============================================================================
# 4. ADVANCED: Parallel Coordinates (Çok Boyutlu Bahis Oranları Analizi)
# Insight: Unveils how bookmaker odds coordinates map into distinct match outcomes.
# ==============================================================================
def create_parallel_coordinates(df: pd.DataFrame, max_samples: int = 1500) -> go.Figure:
    sample_df = df.sample(min(len(df), max_samples), random_state=42).copy()
    
    # Encode result to numerical for coloring: Home=1, Draw=2, Away=3
    outcome_code = {'H': 1, 'D': 2, 'A': 3}
    sample_df['outcome_num'] = sample_df['ftr'].map(outcome_code)

    fig = go.Figure(data=go.Parcoords(
        line=dict(
            color=sample_df['outcome_num'],
            colorscale=[[0, '#3B82F6'], [0.5, '#F59E0B'], [1, '#EF4444']],
            showscale=True,
            colorbar=dict(
                title="Result",
                tickvals=[1, 2, 3],
                ticktext=["Home Win", "Draw", "Away Win"]
            )
        ),
        dimensions=[
            dict(range=[1, 10], label='Home Odds', values=sample_df['home_odds']),
            dict(range=[1, 8], label='Draw Odds', values=sample_df['draw_odds']),
            dict(range=[1, 12], label='Away Odds', values=sample_df['away_odds']),
            dict(range=[1, 4], label='Over 2.5 Odds', values=sample_df['over_25_odds'].fillna(2.0)),
            dict(range=[0, 8], label='Total Goals', values=sample_df['total_goals'])
        ]
    ))

    fig.update_layout(
        title="📈 4. Multi-Dimensional Betting Odds & Outcome Profile (Parallel Coordinates)",
        template=THEME_TEMPLATE,
        height=450,
        margin=dict(l=50, r=50, t=50, b=20)
    )
    return fig

# ==============================================================================
# 5. ADVANCED: Network Graph (Takımlar Arası Üstünlük Ağı)
# Insight: Directed dominance network among top teams in the selected league.
# ==============================================================================
def create_network_graph(df: pd.DataFrame, selected_league: str = 'Premier League', top_n: int = 8) -> go.Figure:
    sub_df = df[df['league_name'] == selected_league]
    if sub_df.empty:
        sub_df = df

    # Find top N teams by total wins
    top_teams = sub_df[sub_df['ftr'] == 'H']['home_team'].value_counts().head(top_n).index.tolist()
    filtered = sub_df[(sub_df['home_team'].isin(top_teams)) & (sub_df['away_team'].isin(top_teams))]

    G = nx.DiGraph()
    for team in top_teams:
        G.add_node(team)

    for _, row in filtered.iterrows():
        if row['ftr'] == 'H':
            winner, loser = row['home_team'], row['away_team']
            if G.has_edge(winner, loser):
                G[winner][loser]['weight'] += 1
            else:
                G.add_edge(winner, loser, weight=1)
        elif row['ftr'] == 'A':
            winner, loser = row['away_team'], row['home_team']
            if G.has_edge(winner, loser):
                G[winner][loser]['weight'] += 1
            else:
                G.add_edge(winner, loser, weight=1)

    pos = nx.circular_layout(G)

    # Edge traces
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.2, color='rgba(148, 163, 184, 0.4)'),
        hoverinfo='none',
        mode='lines'
    )

    # Node traces
    node_x, node_y, node_text, node_size = [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        out_deg = G.out_degree(node, weight='weight')
        in_deg = G.in_degree(node, weight='weight')
        node_text.append(f"<b>{node}</b><br>Wins: {out_deg}<br>Losses: {in_deg}")
        node_size.append(20 + out_deg * 3)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[n for n in G.nodes()],
        textposition="top center",
        hovertext=node_text,
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=node_size,
            color=[G.out_degree(n, weight='weight') for n in G.nodes()],
            colorbar=dict(thickness=12, title="Total Wins", xanchor="left"),
            line=dict(width=2, color='#FFFFFF')
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title=f"🕸️ 5. Head-to-Head Dominance Network ({selected_league} Top Teams)",
        template=THEME_TEMPLATE,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=50),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=480
    )
    return fig

# ==============================================================================
# 6. ADVANCED: 2D Contour / Density Plot (Bahis Oranları Yoğunluk Yüzeyi)
# Insight: Uncovers market odds clusters and identifies upset sweet-spots.
# ==============================================================================
def create_odds_contour_density(df: pd.DataFrame) -> go.Figure:
    clean = df[(df['home_odds'] <= 6.0) & (df['away_odds'] <= 8.0)].copy()

    fig = px.density_contour(
        clean,
        x='home_odds',
        y='away_odds',
        color='result_label',
        color_discrete_map={'Home Win': '#3B82F6', 'Draw': '#F59E0B', 'Away Win': '#EF4444'},
        title="🌌 6. Market Odds Density Landscape & Upset Clusters (2D Contour)"
    )

    fig.update_traces(contours_coloring="lines", line_width=1.5)
    fig.update_layout(
        template=THEME_TEMPLATE,
        xaxis_title="Home Closing Odds",
        yaxis_title="Away Closing Odds",
        height=450,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig

# ==============================================================================
# 7. ANALYTICAL: Exact Scoreline Heatmap
# Insight: Most frequent goal combinations (Home Goals vs Away Goals).
# ==============================================================================
def create_score_heatmap(df: pd.DataFrame) -> go.Figure:
    sub = df[(df['fthg'] <= 5) & (df['ftag'] <= 5)]
    score_matrix = pd.crosstab(sub['fthg'], sub['ftag'])

    fig = px.imshow(
        score_matrix,
        labels=dict(x="Away Goals", y="Home Goals", color="Match Frequency"),
        x=score_matrix.columns,
        y=score_matrix.index,
        color_continuous_scale="Magma",
        text_auto=True,
        title="🔥 7. Exact Scoreline Distribution Matrix (0-5 Goals)"
    )

    fig.update_layout(
        template=THEME_TEMPLATE,
        height=420,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig

# ==============================================================================
# 8. ANALYTICAL: Calibration Scatter Plot (Value Bet & Bookmaker Accuracy)
# Insight: Implied probability vs observed win rate with calibration baseline.
# ==============================================================================
def create_calibration_scatter(df: pd.DataFrame) -> go.Figure:
    clean = df.dropna(subset=['prob_home', 'ftr']).copy()
    clean['prob_bin'] = pd.cut(clean['prob_home'], bins=np.linspace(0.1, 0.9, 17))
    
    calib = clean.groupby('prob_bin', observed=False).agg(
        expected_prob=('prob_home', 'mean'),
        actual_win_rate=('ftr', lambda x: (x == 'H').mean()),
        match_count=('id', 'count')
    ).reset_index().dropna()

    fig = go.Figure()

    # Perfect calibration 45-deg line
    fig.add_trace(go.Scatter(
        x=[0.1, 0.9], y=[0.1, 0.9],
        mode='lines',
        name='Perfect Calibration (1:1)',
        line=dict(dash='dash', color='#64748B', width=2)
    ))

    # Observed data points
    fig.add_trace(go.Scatter(
        x=calib['expected_prob'],
        y=calib['actual_win_rate'],
        mode='markers+lines',
        name='Observed Market Win Rate',
        marker=dict(
            size=calib['match_count'] / 25 + 6,
            color='#10B981',
            line=dict(width=1.5, color='#FFFFFF')
        ),
        text=[f"Matches: {c}<br>Expected: {e:.1%}<br>Actual: {a:.1%}" 
              for c, e, a in zip(calib['match_count'], calib['expected_prob'], calib['actual_win_rate'])],
        hoverinfo='text'
    ))

    fig.update_layout(
        title="🎯 8. Market Efficiency & Calibration (Expected vs Actual Win Rate)",
        xaxis_title="Implied Probability (1 / Fair Odds)",
        yaxis_title="Empirical Win Rate",
        template=THEME_TEMPLATE,
        height=420,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig

# ==============================================================================
# 9. ANALYTICAL: League Goal Distribution (Violin & Box Plot with Outliers)
# Insight: Detects variance, goal inflation and extreme high-scoring outliers.
# ==============================================================================
def create_league_goals_violin(df: pd.DataFrame) -> go.Figure:
    fig = px.violin(
        df,
        x='league_name',
        y='total_goals',
        color='league_name',
        box=True,
        points='outliers',
        hover_data=['home_team', 'away_team', 'match_date'],
        title="🎻 9. League Total Goal Distributions & Outlier Matches"
    )

    fig.update_layout(
        template=THEME_TEMPLATE,
        showlegend=False,
        xaxis_title="League",
        yaxis_title="Total Goals in Match",
        height=450,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig
