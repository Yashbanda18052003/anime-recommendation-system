from flask import Flask, render_template, request
import pickle
import os
import json
import urllib.parse
import pandas as pd

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
anime_path = os.path.join(BASE_DIR, 'anime.pkl')
similarity_path = os.path.join(BASE_DIR, 'similarity.pkl')
demo_path = os.path.join(BASE_DIR, 'demo_data.json')

DEMO_MODE = False
anime = None
similarity = None
demo_data = {}

if os.path.exists(anime_path) and os.path.exists(similarity_path):
    print("Loading full anime dataset and similarity matrix (18,400+ records)...")
    anime = pickle.load(open(anime_path, 'rb'))
    similarity = pickle.load(open(similarity_path, 'rb'))
    print("Full model loaded successfully! Ready to serve.")
else:
    DEMO_MODE = True
    print("\n" + "="*60)
    print("NOTICE: 'anime.pkl' or 'similarity.pkl' not found.")
    print("Running in DEMO MODE with built-in sample data (demo_data.json).")
    print("Anyone cloning from GitHub can test recommendations immediately!")
    print("="*60 + "\n")
    if os.path.exists(demo_path):
        with open(demo_path, 'r', encoding='utf-8') as f:
            demo_data = json.load(f)

# Recommendation function
def recommend(anime_name):
    anime_name = anime_name.lower().strip()
    
    if not DEMO_MODE:
        if anime_name not in anime['Name'].str.lower().values:
            return None, []

        selected_row = anime[anime['Name'].str.lower() == anime_name].iloc[0]
        r_val = selected_row.get('Rating')
        try:
            rating_str = f"{float(r_val):.2f}" if pd.notnull(r_val) else "N/A"
        except:
            rating_str = "N/A"

        selected_info = {
            'name': str(selected_row.get('Name', '')),
            'studio': "" if str(selected_row.get('Studio', '')).lower() == 'nan' else str(selected_row.get('Studio', '')).strip(),
            'type': "" if str(selected_row.get('Type', '')).lower() == 'nan' else str(selected_row.get('Type', '')).strip(),
            'rating': rating_str
        }

        index = anime[anime['Name'].str.lower() == anime_name].index[0]
        distances = similarity[index]
        anime_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]

        recommendations = []
        for rank_idx, i in enumerate(anime_list, 1):
            row = anime.iloc[i[0]]
            raw_tags = str(row.get('Tags', ''))
            tags_list = [t.strip() for t in raw_tags.split(',') if t.strip() and t.strip().lower() != 'nan'][:4]
            
            val = row.get('Rating')
            try:
                r_formatted = f"{float(val):.2f}" if pd.notnull(val) else "N/A"
            except:
                r_formatted = "N/A"
                
            ep_val = row.get('Episodes')
            try:
                episodes_str = str(int(float(ep_val))) if pd.notnull(ep_val) else ""
            except:
                episodes_str = ""
                
            yr_val = row.get('Release_year')
            try:
                year_str = str(int(float(yr_val))) if pd.notnull(yr_val) else ""
            except:
                year_str = ""
                
            desc_val = str(row.get('Description', ''))
            if desc_val.lower() == 'nan' or not desc_val.strip():
                desc_cleaned = "No synopsis available for this title."
            else:
                desc_cleaned = desc_val.strip("'\" \n\r\t").replace("?Ts", "'s")
                desc_cleaned = " ".join(desc_cleaned.split())
                if len(desc_cleaned) > 210:
                    desc_cleaned = desc_cleaned[:207] + "..."
                    
            sim_score = round(float(i[1]) * 100, 1)

            recommendations.append({
                'rank': rank_idx,
                'name': str(row.get('Name', '')),
                'japanese_name': "" if str(row.get('Japanese_name', '')).lower() == 'nan' else str(row.get('Japanese_name', '')),
                'type': "" if str(row.get('Type', '')).lower() == 'nan' else str(row.get('Type', '')).strip(),
                'episodes': episodes_str,
                'studio': "" if str(row.get('Studio', '')).lower() == 'nan' else str(row.get('Studio', '')).strip(),
                'tags': tags_list,
                'rating': r_formatted,
                'year': year_str,
                'description': desc_cleaned,
                'similarity': sim_score,
                'search_query': urllib.parse.quote(str(row.get('Name', '')))
            })
        return selected_info, recommendations

    else:
        # DEMO MODE (using built-in demo_data.json)
        if anime_name in demo_data:
            entry = demo_data[anime_name]
            return entry['info'], entry['recommendations']
        else:
            return None, []

# Routes
@app.route('/')
def home():
    if not DEMO_MODE:
        titles = anime['Name'].values
    else:
        titles = [v['info']['name'] for v in demo_data.values()]
    return render_template('index.html', anime_list=titles, recommendations=None, demo_mode=DEMO_MODE)

@app.route('/recommend', methods=['POST'])
def recommend_route():
    selected_anime = request.form.get('anime', '').strip()
    selected_info, recommendations = recommend(selected_anime)
    if not DEMO_MODE:
        titles = anime['Name'].values
    else:
        titles = [v['info']['name'] for v in demo_data.values()]
    return render_template('index.html',
                           anime_list=titles,
                           selected_anime=selected_anime,
                           selected_info=selected_info,
                           recommendations=recommendations,
                           demo_mode=DEMO_MODE)

if __name__ == '__main__':
    print("Starting Flask web server on http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=False)
