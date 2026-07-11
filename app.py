from flask import Flask, render_template, jsonify, request, send_file
from analysis import (
    load_data, 
    get_stats, 
    compare_players_logic, 
    predict_winner_logic, 
    generate_pdf_report
)

# template_folder='.' lagane se Flask HTML ko main directory mein dhoondega
app = Flask(__name__, template_folder='.')
df = load_data()

@app.route('/')
def index():
    teams = sorted(df['Team'].unique().tolist())
    players = sorted(df['Batter'].unique().tolist())
    venues = sorted(df['venue'].unique().tolist())
    return render_template('index.html', teams=teams, players=players, venues=venues)

@app.route('/api/stats')
def stats_api():
    team = request.args.get('team', 'All Teams')
    return jsonify(get_stats(df, team))

@app.route('/api/compare')
def compare_api():
    p1 = request.args.get('p1')
    p2 = request.args.get('p2')
    return jsonify(compare_players_logic(df, p1, p2))

@app.route('/api/predict')
def predict_api():
    t1 = request.args.get('t1')
    t2 = request.args.get('t2')
    v = request.args.get('v')
    winner, prob = predict_winner_logic(df, t1, t2, v)
    return jsonify({'winner': winner, 'probability': prob})

@app.route('/download_report')
def download_report():
    team = request.args.get('team', 'All Teams')
    t1 = request.args.get('t1')
    t2 = request.args.get('t2')
    venue = request.args.get('v')
    p1 = request.args.get('p1')
    p2 = request.args.get('p2')
    
    stats = get_stats(df, team)
    winner, prob = predict_winner_logic(df, t1, t2, venue)
    ai_info = {'winner': winner, 'probability': prob, 'venue': venue}
    
    comp_info = None
    if p1 and p2:
        comp_info = compare_players_logic(df, p1, p2)
        
    pdf_path = generate_pdf_report(stats, team, ai_info, comp_info)
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)