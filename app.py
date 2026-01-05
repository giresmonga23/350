
# app.py (version robuste pour CORS + OPTIONS)
import os

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
app.url_map.strict_slashes = False  # évite les redirects 308 (/analyze/ vs /analyze)

# CORS complet (IMPORTANT pour le preflight)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=86400,
)

# Filet de sécurité : force les headers CORS sur TOUTES les réponses
@app.after_request
def add_cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    return resp

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY manquant (à définir dans les variables d'environnement Koyeb).")

client = Groq(api_key=GROQ_API_KEY)

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "VisiFoot API Online", "server": "Healthy"}), 200

@app.route("/analyze", methods=["POST", "OPTIONS"])
def analyze():
    # Preflight CORS
    if request.method == "OPTIONS":
        return make_response("", 204)

    data = request.get_json(silent=True) or {}
    home = data.get("equipe_domicile")
    away = data.get("equipe_exterieur")

    if not home or not away:
        return jsonify({"error": "Noms des équipes manquants"}), 400

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Tu es l'expert VisiFoot. Réponds en français uniquement."},
                {"role": "user", "content": f"Donne le score exact et les buteurs pour {home} vs {away}."},
            ],
        )

        reponse_ia = (completion.choices[0].message.content or "").strip()

        return jsonify({
            "equipe_domicile": home,
            "equipe_exterieur": away,
            "donnees": {},
            "analyse": {
                "scores": {"equipe1": 0, "equipe2": 0, "difference": 0},
                "sous_scores": {
                    "forme": {"equipe1": 85, "equipe2": 80},
                    "domicile_exterieur": {"domicile": 75, "exterieur": 70},
                    "h2h": {"score_equipe1": 0, "score_equipe2": 0, "avantage": "Nul"},
                    "motivation": {"score_equipe1": 95, "score_equipe2": 95},
                    "tendance": {"score_equipe1": 0, "score_equipe2": 0, "tendance_buts": "Élevée"},
                },
                "prediction_resultat": reponse_ia,
                "confiance_resultat": 88,
                "analyse_detaille": [],
            },
            "predictions": {
                "resultat_principal": {"prediction": "Victoire / Nul", "confiance": 88, "explication": reponse_ia},
                "scores_exacts": {
                    "scores_probables": ["2-1", "1-1", "2-2"],
                    "score_le_plus_probable": "2-1",
                    "confiance_score": 75,
                },
                "paris_recommandes": [{"type": "Buteurs", "confiance": 70, "niveau": "Moyen"}],
                "over_under": {"prediction": "Plus de 1.5", "confiance": 90, "explication": "Match ouvert"},
                "btts": {"prediction": "Oui", "confiance": 80, "explication": "Attaques en forme"},
                "double_chance": {"type": "1X", "confiance": 85, "cote_estimee": 1.45, "recommandation": "Conseillé"},
            },
            "recommandations": [{"type": "IA Analysis", "titre": "Rapport complet", "contenu": [reponse_ia]}],
            "score_confiance": 90,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
