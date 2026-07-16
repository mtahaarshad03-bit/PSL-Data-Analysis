import pandas as pd
import os

def load_data():
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, 'PSL.csv')
    df = pd.read_csv(file_path)
    return df

def get_stats(df, team_name="All Teams"):
    temp_df = df
    if team_name != "All Teams":
        temp_df = df[df['Team'] == team_name]

    batsmen = temp_df.groupby('Batter')['Batter runs'].sum().sort_values(ascending=False).head(5).to_dict()
    bowlers = temp_df[temp_df['Wickets'] > 0].groupby('Bowler')['Wickets'].count().sort_values(ascending=False).head(5).to_dict()
    
    return {
        'batsmen': batsmen,
        'bowlers': bowlers,
        'total_runs': f"{int(temp_df['Batter runs'].sum()):,}",
        'total_wickets': f"{int(temp_df['Wickets'].sum()):,}"
    }

def compare_players_logic(df, p1, p2):
    res = {}
    for p in [p1, p2]:
        p_df = df[df['Batter'] == p]
        runs = int(p_df['Batter runs'].sum())
        balls = len(p_df)
        sr = round((runs / balls) * 100, 2) if balls > 0 else 0
        res[p] = {'Runs': runs, 'SR': sr}
    return res

def predict_winner_logic(df, team1, team2, venue):
    t1_wins = len(df[(df['Winner'] == team1) & (df['venue'] == venue)])
    t2_wins = len(df[(df['Winner'] == team2) & (df['venue'] == venue)])
    
    if t1_wins > t2_wins:
        return team1, 75
    elif t2_wins > t1_wins:
        return team2, 75
    else:
        return "Tough Competition", 50

# Fallback fake pdf generator to prevent crash on FPDF import
def generate_pdf_report(stats, team_name, ai_data=None, comp_data=None):
    report_path = "/tmp/psl_report.txt"
    with open(report_path, "w") as f:
        f.write(f"PSL Report - {team_name}\nTotal Runs: {stats['total_runs']}")
    return report_path