"""
ml_engine.py - CEN445 Machine Learning Integration
Implements two machine learning algorithms:
1. K-Means Clustering: Team Tactical & Performance Profiling
2. Logistic Regression: Match Outcome Prediction & Feature Importance
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
import plotly.express as px
import plotly.graph_objects as go

THEME_TEMPLATE = "plotly_dark"

# ==============================================================================
# 1. K-MEANS CLUSTERING: Team Tactical Profiles
# ==============================================================================
def run_team_clustering(df: pd.DataFrame, n_clusters: int = 3):
    """
    Computes per-team statistics across matches and clusters them using K-Means.
    Returns: (team_df, scatter_plot_figure)
    """
    # 1. Aggregate Team Statistics
    home_stats = df.groupby('home_team').agg(
        matches=('id', 'count'),
        goals_for=('fthg', 'sum'),
        goals_against=('ftag', 'sum'),
        wins=('ftr', lambda x: (x == 'H').sum())
    )
    
    away_stats = df.groupby('away_team').agg(
        matches=('id', 'count'),
        goals_for=('ftag', 'sum'),
        goals_against=('fthg', 'sum'),
        wins=('ftr', lambda x: (x == 'A').sum())
    )
    
    teams = home_stats.add(away_stats, fill_value=0)
    teams = teams[teams['matches'] >= 15] # Minimum matches threshold
    
    teams['goals_per_match'] = (teams['goals_for'] / teams['matches']).round(2)
    teams['conceded_per_match'] = (teams['goals_against'] / teams['matches']).round(2)
    teams['win_rate'] = (teams['wins'] / teams['matches'] * 100).round(1)
    teams['goal_diff_per_match'] = (teams['goals_per_match'] - teams['conceded_per_match']).round(2)
    
    features = ['goals_per_match', 'conceded_per_match', 'win_rate']
    X = teams[features]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    teams['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Meaningful cluster labels sorted by win rate
    cluster_order = teams.groupby('cluster')['win_rate'].mean().sort_values(ascending=False).index
    label_map = {
        cluster_order[0]: "Elite Dominators",
        cluster_order[1]: "Balanced Competitors",
        cluster_order[2]: "Relegation Strugglers"
    }
    if n_clusters > 3:
        for i, c_idx in enumerate(cluster_order):
            label_map[c_idx] = f"Tier {i+1} Teams"
            
    teams['cluster_label'] = teams['cluster'].map(label_map)
    teams['team_name'] = teams.index
    
    # Visualization: Goals Scored vs Conceded colored by Cluster
    fig = px.scatter(
        teams.reset_index(),
        x='goals_per_match',
        y='conceded_per_match',
        color='cluster_label',
        size='win_rate',
        hover_name='team_name',
        hover_data={'goals_per_match': ':.2f', 'conceded_per_match': ':.2f', 'win_rate': ':.1f%'},
        labels={
            'goals_per_match': 'Avg Goals Scored / Match',
            'conceded_per_match': 'Avg Goals Conceded / Match',
            'cluster_label': 'Team Profile Tier'
        },
        color_discrete_map={
            "Elite Dominators": "#10B981",       # Emerald
            "Balanced Competitors": "#3B82F6",   # Blue
            "Relegation Strugglers": "#EF4444"   # Red
        },
        title=f"🤖 ML 1: Team Tactical Clustering (K-Means, k={n_clusters})"
    )
    
    fig.update_layout(
        template=THEME_TEMPLATE,
        yaxis=dict(autorange="reversed"), # Top is lower conceded (better defense)
        height=480,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return teams, fig

# ==============================================================================
# 2. CLASSIFICATION: Match Outcome Prediction & Feature Importance
# ==============================================================================
def train_match_classifier(df: pd.DataFrame):
    """
    Trains a Logistic Regression model to predict match outcomes (H, D, A)
    from market odds and derived probabilities.
    Returns: (accuracy, model, scaler, cm_fig, importance_fig)
    """
    clean_df = df.dropna(subset=['prob_home', 'prob_draw', 'prob_away', 'ftr']).copy()
    
    features = ['prob_home', 'prob_draw', 'prob_away', 'home_odds', 'draw_odds', 'away_odds']
    X = clean_df[features]
    y = clean_df['ftr'] # 'H', 'D', 'A'
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    
    # 1. Confusion Matrix Figure
    labels = ['H', 'D', 'A']
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    cm_df = pd.DataFrame(cm, index=['Actual Home', 'Actual Draw', 'Actual Away'],
                             columns=['Pred Home', 'Pred Draw', 'Pred Away'])
    
    cm_fig = px.imshow(
        cm_df,
        text_auto=True,
        color_continuous_scale='Blues',
        title=f"🤖 ML 2: Confusion Matrix (Accuracy: {acc:.1%})"
    )
    cm_fig.update_layout(template=THEME_TEMPLATE, height=380, margin=dict(l=10, r=10, t=50, b=10))
    
    # 2. Feature Importance Figure (Home Win Coefficients)
    home_idx = list(model.classes_).index('H')
    coefs = model.coef_[home_idx]
    feat_df = pd.DataFrame({'Feature': features, 'Weight': coefs}).sort_values('Weight', ascending=True)
    
    imp_fig = px.bar(
        feat_df,
        x='Weight',
        y='Feature',
        orientation='h',
        color='Weight',
        color_continuous_scale='Tealrose',
        title="🤖 ML 2: Feature Weights Driving Home Win Prediction"
    )
    imp_fig.update_layout(template=THEME_TEMPLATE, height=380, margin=dict(l=10, r=10, t=50, b=10))
    
    return acc, model, scaler, cm_fig, imp_fig
