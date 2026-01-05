import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
# Débloque la connexion entre Lovable et Koyeb
CORS(app, resources={r"/*": {"origins": "*"}})

# Utilise la clé API que tu as configurée dans Koyeb
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route("/")
def health():
    return {"status": "VisiFoot API Online", "server": "Healthy"}

@app.route("/analyze", methods=["POST", "OPTIONS"])
def analyze():
    # Gère la pré-vérification de sécurité du navigateur
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json(silent=True) or {}
    
    # Récupère les noms envoyés par ton nouveau fichier api.ts
    home = data.get("equipe_domicile")
    away = data.get("equipe_exterieur")

    if not home or not away:
        return jsonify({"error": "Noms des équipes manquants"}), 400

    try:
        # Demande l'analyse à l'IA Groq
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": "Tu es VisiFoot, expert en pronostics. Analyse le match et donne un score exact."
                },
                {"role": "user", "content": f"Analyse complète pour : {home} vs {away}"}
            ]
        )
        
        reponse_ia = completion.choices[0].message.content

        # Structure de réponse compatible avec ton interface Lovable
        return jsonify({
            "equipe_domicile": home,
            "equipe_exterieur": away,
            "analyse": {
                "scores": {"equipe1": 0, "equipe2": 0, "difference": 0},
                "sous_scores": {
                    "forme": {"equipe1": 80, "equipe2": 70},
                    "domicile_exterieur": {"domicile": 75, "exterieur": 65},
                    "h2h": {"score_equipe1": 0, "score_equipe2": 0, "avantage": "Nul"},
                    "motivation": {"score_equipe1": 90, "score_equipe2": 85},
                    "tendance": {"score_equipe1": 0, "score_equipe2": 0, "tendance_buts": "Moyenne"}
                },
                "prediction_resultat": reponse_ia,
                "confiance_resultat": 85
            },
            "predictions": {
                "resultat_principal": {"prediction": reponse_ia, "confiance": 85, "explication": "Analyse IA"},
                "scores_exacts": {
                    "scores_probables": ["2-1", "1-0", "1-1"],
                    "score_le_plus_probable": "2-1",
                    "confiance_score": 70
                },
                "paris_recommandes": [{"type": "Victoire", "confiance": 80, "niveau": "Élevé"}],
                "over_under": {"prediction": "Plus de 2.5", "confiance": 75, "explication": "Attaque forte"},
                "btts": {"prediction": "Oui", "confiance": 70, "explication": "Les deux marquent"},
                "double_chance": {"type": "1X", "confiance": 90, "cote_estimee": 1.30, "recommandation": "Sûr"}
            },
            "recommandations": [{"type": "Conseil", "titre": "Analyse", "contenu": [reponse_ia]}],
            "score_confiance": 85
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Port dynamique pour Koyeb
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)


