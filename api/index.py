from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import io

# Relative imports
from .analysis import (
    load_data, 
    get_stats, 
    compare_players_logic, 
    predict_winner_logic, 
    generate_text_report
)

app = Flask(__name__, template_folder='../')
CORS(app)

df = load_data()

@app.route('/')
def index():
    teams = sorted(df['Team'].unique().tolist())
    players = sorted(df['Batter'].unique().tolist())
    venues = sorted(df['venue'].unique().tolist())
    return render_template('index.html', teams=teams, players=players, venues=venues)

@app.route('/api/stats')
def stats_api():
    try:
        team = request.args.get('team', 'All Teams')
        data = get_stats(df, team)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/compare')
def compare_api():
    try:
        p1 = request.args.get('p1')
        p2 = request.args.get('p2')
        if not p1 or not p2:
            return jsonify({"error": "Missing player parameters"}), 400
        return jsonify(compare_players_logic(df, p1, p2))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict')
def predict_api():
    try:
        t1 = request.args.get('t1')
        t2 = request.args.get('t2')
        v = request.args.get('v')
        if not t1 or not t2 or not v:
            return jsonify({"error": "Missing match parameters"}), 400
        winner, prob = predict_winner_logic(df, t1, t2, v)
        return jsonify({'winner': winner, 'probability': prob})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download_report')
def download_report():
    try:
        team = request.args.get('team', 'All Teams')
        t1 = request.args.get('t1', '')
        t2 = request.args.get('t2', '')
        venue = request.args.get('v', '')
        p1 = request.args.get('p1', '')
        p2 = request.args.get('p2', '')
        
        stats = get_stats(df, team)
        
        # Safe checks to run logic only if parameters exist
        ai_info = None
        if t1 and t2 and venue:
            winner, prob = predict_winner_logic(df, t1, t2, venue)
            ai_info = {'winner': winner, 'probability': prob, 'venue': venue}
        
        comp_info = None
        if p1 and p2:
            comp_info = compare_players_logic(df, p1, p2)
            
        report_text = generate_text_report(stats, team, ai_info, comp_info)
        
        # RAM memory bytes data download stream (anti-crash on serverless Vercel)
        mem_file = io.BytesIO()
        mem_file.write(report_text.encode('utf-8'))
        mem_file.seek(0)
        
        return send_file(
            mem_file, 
            as_attachment=True, 
            download_name="psl_analysis_report.txt",
            mimetype="text/plain"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)