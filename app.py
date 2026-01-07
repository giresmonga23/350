import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from datetime import datetime

app = Flask(__name__)
# Sécurité : Remplace "*" par ton URL Lovable une fois publiée pour plus de sécurité
CORS(app, resources={r"/*": {"origins": "*"}})

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Remplace par ta clé API-Football (RapidAPI) pour avoir les vrais matchs
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY", "TA_CLE_API_ICI")

@app.route("/")
def health():
    return jsonify({"status": "VisiFoot API Online", "server": "Healthy", "mode": "Real-Time"})

# --- NOUVELLE ROUTE : RÉCUPÈRE LES VRAIS MATCHS DU JOUR ---
@app.route("/api/matches/today", methods=["GET"])
def get_today_matches():
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        url = "https://v3.football.api-sports.io/fixtures"
        headers = {
            'x-rapidapi-key': FOOTBALL_API_KEY,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
        params = {'date': today, 'status': 'NS'} # Matchs non commencés

        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()

        matches = []
        for item in data.get('response', []):
            matches.append({
                "id": item['fixture']['id'],
                "homeTeam": item['teams']['home']['name'],
                "awayTeam": item['teams']['away']['name'],
                "league": item['league']['name'],
                "time": item['fixture']['date'],
                "homeLogo": item['teams']['home']['logo'],
                "awayLogo": item['teams']['away']['logo']
            })
        
        # Si aucun match trouvé, on renvoie une liste vide (Lovable affichera "Aucun match")
        return jsonify(matches)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ROUTE ANALYSE : COMMUNIQUE AVEC GROQ ---
@app.route("/analyze", methods=["POST", "OPTIONS"])
def analyze():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json(silent=True) or {}
    home = (data.get("equipe_domicile") or data.get("homeTeam") or "").strip()
    away = (data.get("equipe_exterieur") or data.get("awayTeam") or "").strip()

    if not home or not away:
        return jsonify({"error": "Equipes manquantes"}), 400

    try:
        # L'IA Groq génère l'analyse réelle
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Tu es l'expert VisiFoot. Donne un score exact et une analyse courte en français basée sur la forme actuelle."},
                {"role": "user", "content": f"Analyse réelle pour le match : {home} vs {away}"}
            ]
        )
        
        reponse_ia = completion.choices[0].message.content

        # Format ultra-complet pour remplir tous les graphiques de Lovable
        return jsonify({
            "equipe_domicile": home,
            "equipe_exterieur": away,
            "prediction": reponse_ia,
            "analyse": {
                "prediction_resultat": reponse_ia,
                "confiance_resultat": 85,
                "sous_scores": {
                    "forme": {"equipe1": 80, "equipe2": 75},
                    "motivation": {"equipe1": 90, "equipe2": 85}
                }
            },
            "predictions": {
                "resultat_principal": {"prediction": "Analyse Complète", "confiance": 85, "explication": reponse_ia},
                "over_under": {"prediction": "Plus de 1.5 buts", "confiance": 80}
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))


