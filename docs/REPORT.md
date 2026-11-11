# CEN445 - Introduction to Data Visualization
## Project Final Report: European Football Intelligence & Match Dynamics Dashboard

**Submission Date:** November 2026  
**Team Members:**  
- Member 1: *[Name - Student ID]* (Data Preprocessing, Sankey Flow, Treemap, Network Graph)  
- Member 2: *[Name - Student ID]* (Parallel Coordinates, Choropleth Map, ML Clustering, UI Implementation)  
- Member 3: *[Name - Student ID]* (2D Density Plot, Heatmaps, ML Classification, Documentation & Report)  

**GitHub Repository:** `https://github.com/celal-ay/cen445-football-viz`

---

### 1. Dataset Context, Source & Preprocessing
This project investigates match dynamics, goal productivity, and betting market efficiency across major European football leagues. The dataset comprises **5,420 rigorously cleaned official matches** spanning the **2023–2024 and 2024–2025 seasons** from eight prominent leagues: England (Premier League), Spain (La Liga), Germany (Bundesliga), Italy (Serie A), France (Ligue 1), Netherlands (Eredivisie), Portugal (Primeira Liga), and Turkey (Süper Lig).

**Data Preprocessing:**
- Cleaned missing values in match scores and odds lines.
- Enriched raw records with ISO-3 country codes, goal differentials, binary flags (Over/Under 2.5, Both Teams to Score), and halftime-to-fulltime momentum transitions (Comebacks).
- Normalized bookmaker closing odds to remove margins, yielding fair implied probabilities ($P = \frac{1/\text{odds}}{\sum 1/\text{odds}}$).

---

### 2. Main Goals of the Analysis
1. **Competitive Landscape:** Compare goal volume and home advantage across distinct European leagues.
2. **Match Momentum:** Trace how halftime leads dictate final outcomes and detect rare comeback flows.
3. **Market Efficiency:** Evaluate bookmaker predictive accuracy against empirical match results.
4. **Predictive Modeling:** Cluster clubs into tactical tiers and model match outcomes via machine learning.

---

### 3. Visualization Techniques (9 Distinct Methods, 6 Advanced)
1. **Geographical Choropleth Map (Advanced):** Visualizes goal frequency and home win percentages on an interactive European map using Natural Earth projection.
2. **Hierarchical Treemap (Advanced):** Displays goal distribution and win counts across nested league and club structures.
3. **Sankey Diagram (Advanced):** Traces momentum transitions from Half-Time (HT) to Full-Time (FT) outcomes, highlighting comebacks.
4. **Parallel Coordinates (Advanced):** Explores multi-dimensional relationships across Home, Draw, Away, and Over 2.5 odds mapped to match results.
5. **Head-to-Head Network Graph (Advanced):** Visualizes directed dominance structures among elite clubs within selected leagues.
6. **2D Odds Density & Contour Plot (Advanced):** Identifies betting market density clusters and reveals pricing zones prone to upsets.
7. **Scoreline Heatmap Matrix:** Displays the empirical frequencies of exact fulltime scores (0–5 goals).
8. **Value Bet Calibration Scatter Plot:** Assesses market efficiency by plotting implied probabilities against observed win rates with a 45° calibration benchmark.
9. **Violin & Box Distribution Plots:** Illustrates league-specific total goal distributions, medians, interquartile ranges, and extreme outlier matches.

---

### 4. Machine Learning Integration
- **K-Means Clustering:** Grouped 150+ teams into three interpretable tactical tiers (*Elite Dominators*, *Balanced Competitors*, *Relegation Strugglers*) based on attacking output, defensive vulnerability, and win percentages.
- **Multinomial Logistic Regression:** Modeled match outcomes (Home/Draw/Away) from market odds, achieving ~56.2% accuracy (significantly surpassing random guessing baseline of 33.3%). A live simulation widget enables real-time probability inference.

---

### 5. Key Insights & Findings
- **Home Advantage Persists Across Europe:** Across all eight leagues (5,420 matches), home teams won 43.4% of encounters, draws accounted for 25.5%, and away wins totaled 31.1%. Süper Lig recorded the highest home win percentage (46.5%), while Serie A saw the highest draw percentage (29.0%).
- **Tactical Dichotomy in Goal Output:** Bundesliga (3.18) and Eredivisie (3.11) exhibited the highest goal outputs per game with over 60% of matches ending in Over 2.5 goals. In contrast, La Liga (2.63) and Serie A (2.59) were characterized by tighter tactical battles, with under 50% Over 2.5 rates.
- **Halftime Predictability & Comeback Rarity:** A team leading at halftime converted that advantage into a fulltime victory in 75.5% of fixtures (1,394 out of 1,846 matches). True comebacks (overcoming a halftime deficit to win at fulltime) occurred in only 5.6% of all fixtures (302 matches).
