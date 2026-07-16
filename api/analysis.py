import pandas as pd
import os
from fpdf import FPDF

def load_data():
    # Vercel par crash se bachne ke liye absolute relative path ka istemaal
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

def generate_pdf_report(stats, team_name, ai_data=None, comp_data=None):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Design
    pdf.set_fill_color(30, 30, 40)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(190, 25, txt="PSL AI ELITE REPORT", ln=True, align='C')
    
    # Summary Details
    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, txt=f"Analysis Context: {team_name}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.cell(95, 10, txt=f"Total Runs: {stats['total_runs']}")
    pdf.cell(95, 10, txt=f"Total Wickets: {stats['total_wickets']}", ln=True)
    
    if ai_data:
        pdf.ln(10)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(190, 10, txt=" AI Match Prediction Analysis", ln=True, fill=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(190, 8, txt=f"Winner: {ai_data['winner']} ({ai_data['probability']}% Probability) at {ai_data['venue']}")

    if comp_data:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(190, 10, txt=" Player Head-to-Head Comparison", ln=True)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(60, 10, "Player", border=1)
        pdf.cell(60, 10, "Runs", border=1)
        pdf.cell(60, 10, "SR", border=1, ln=True)
        for p_name, p_stats in comp_data.items():
            pdf.cell(60, 10, p_name, border=1)
            pdf.cell(60, 10, str(p_stats['Runs']), border=1)
            pdf.cell(60, 10, str(p_stats['SR']), border=1, ln=True)

    # Serverless runtime temporary directory path for saving PDFs safely on Vercel
    report_path = "/tmp/psl_report.pdf"
    pdf.output(report_path)
    return report_path