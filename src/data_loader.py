import sqlite3
import csv
import os

LEAGUE_METADATA = {
    'E0': {'league': 'Premier League', 'country': 'England', 'iso3': 'GBR', 'flag': '🏴󠁧󠁢󠁥󠁮󠁧󠁿'},
    'F1': {'league': 'Ligue 1', 'country': 'France', 'iso3': 'FRA', 'flag': '🇫🇷'},
    'D1': {'league': 'Bundesliga', 'country': 'Germany', 'iso3': 'DEU', 'flag': '🇩🇪'},
    'I1': {'league': 'Serie A', 'country': 'Italy', 'iso3': 'ITA', 'flag': '🇮🇹'},
    'N1': {'league': 'Eredivisie', 'country': 'Netherlands', 'iso3': 'NLD', 'flag': '🇳🇱'},
    'P1': {'league': 'Primeira Liga', 'country': 'Portugal', 'iso3': 'PRT', 'flag': '🇵🇹'},
    'T1': {'league': 'Süper Lig', 'country': 'Turkey', 'iso3': 'TUR', 'flag': '🇹🇷'},
    'SP1': {'league': 'La Liga', 'country': 'Spain', 'iso3': 'ESP', 'flag': '🇪🇸'}
}

TARGET_SEASONS = ['2023-2024', '2024-2025']

def extract_and_clean_data(
    raw_db_path: str = "c:/Users/Gaming/Documents/antigravity/cen445-football-viz/data/raw/odds_analysis_copy.db",
    output_dir: str = "c:/Users/Gaming/Documents/antigravity/cen445-football-viz/data"
):
    if not os.path.exists(raw_db_path):
        raise FileNotFoundError(f"Database not found at {raw_db_path}")

    conn = sqlite3.connect(raw_db_path)
    cur = conn.cursor()
    
    div_keys = list(LEAGUE_METADATA.keys())
    placeholders = ",".join(["?"] * len(div_keys))
    season_placeholders = ",".join(["?"] * len(TARGET_SEASONS))
    
    query = f"""
    SELECT 
        id, division, season, match_date,
        home_team, away_team,
        fthg, ftag, ftr,
        hthg, htag, htr,
        home_odds, draw_odds, away_odds,
        over_25_odds, under_25_odds
    FROM matches
    WHERE division IN ({placeholders})
      AND season IN ({season_placeholders})
    ORDER BY match_date ASC
    """
    
    cur.execute(query, div_keys + TARGET_SEASONS)
    rows = cur.fetchall()
    conn.close()
    
    print(f"Loaded raw records: {len(rows)}")

    result_map = {'H': 'Home Win', 'D': 'Draw', 'A': 'Away Win'}

    headers = [
        'id', 'division', 'league_name', 'country', 'country_iso3', 'season', 'match_date',
        'home_team', 'away_team', 'fthg', 'ftag', 'ftr', 'result_label',
        'hthg', 'htag', 'htr', 'ht_result_label',
        'total_goals', 'goal_diff', 'is_over_25', 'btts', 'match_flow',
        'home_odds', 'draw_odds', 'away_odds', 'over_25_odds', 'under_25_odds',
        'prob_home', 'prob_draw', 'prob_away'
    ]

    cleaned_data = []

    for r in rows:
        (m_id, div, season, m_date, h_team, a_team,
         fthg, ftag, ftr, hthg, htag, htr,
         h_odds, d_odds, a_odds, o25_odds, u25_odds) = r

        # Validation: must have essential results and odds
        if fthg is None or ftag is None or not ftr or h_odds is None or d_odds is None or a_odds is None:
            continue
        if hthg is None or htag is None or not htr:
            continue
        if h_odds <= 0 or d_odds <= 0 or a_odds <= 0:
            continue

        meta = LEAGUE_METADATA[div]
        league_name = meta['league']
        country = meta['country']
        iso3 = meta['iso3']

        total_goals = fthg + ftag
        goal_diff = fthg - ftag
        is_over_25 = 1 if total_goals > 2.5 else 0
        btts = 1 if (fthg > 0 and ftag > 0) else 0

        res_lbl = result_map.get(ftr, 'Unknown')
        ht_res_lbl = result_map.get(htr, 'Unknown')

        # Match Flow
        if htr == 'A' and ftr == 'H':
            flow = 'Home Comeback (Lost HT -> Won FT)'
        elif htr == 'H' and ftr == 'A':
            flow = 'Away Comeback (Lost HT -> Won FT)'
        elif htr == 'D' and ftr != 'D':
            flow = f"Draw HT to {'Home' if ftr=='H' else 'Away'} FT"
        elif htr == ftr:
            flow = 'Lead/Draw Maintained'
        else:
            flow = 'Other Flow'

        # Fair probabilities (margin normalized)
        raw_h, raw_d, raw_a = 1.0 / h_odds, 1.0 / d_odds, 1.0 / a_odds
        margin = raw_h + raw_d + raw_a
        p_home = round(raw_h / margin, 4)
        p_draw = round(raw_d / margin, 4)
        p_away = round(raw_a / margin, 4)

        cleaned_data.append([
            m_id, div, league_name, country, iso3, season, m_date,
            h_team, a_team, fthg, ftag, ftr, res_lbl,
            hthg, htag, htr, ht_res_lbl,
            total_goals, goal_diff, is_over_25, btts, flow,
            round(h_odds, 2), round(d_odds, 2), round(a_odds, 2),
            round(o25_odds, 2) if o25_odds else None,
            round(u25_odds, 2) if u25_odds else None,
            p_home, p_draw, p_away
        ])

    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "processed_matches.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(cleaned_data)

    print(f"Data successfully cleaned and exported!")
    print(f" - Valid rows: {len(cleaned_data)}")
    print(f" - Features count: {len(headers)}")
    print(f" - File: {csv_path} ({os.path.getsize(csv_path) / 1024:.1f} KB)")

if __name__ == "__main__":
    extract_and_clean_data()
