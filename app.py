import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)

# Configuration CORS complète pour accepter les requêtes de Lovable
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Clé API Groq depuis variables d’environnement
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route("/")
def health():
    return {"status": "FootBrain API online"}

@app.route("/analyze", methods=["POST", "OPTIONS"])
def analyze():
    # Gestion indispensable de la requête de vérification OPTIONS (CORS)
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    # Récupération des données envoyées par Lovable
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"error": "Données non fournies"}), 400
    
    # Adaptation au format de Lovable (clé 'match' ou les deux équipes)
    match = data.get("match") or f"{data.get('equipe_domicile')} vs {data.get('equipe_exterieur')}"

    try:
        # Appel à l'IA Llama 3.3 via Groq
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es VisiFoot, une IA experte en paris sportifs football. "
                        "Analyse data-driven, value betting, probabilités, absences, contexte. "
                        "Donne un pronostic précis avec score exact et pourcentage de confiance."
                    )
                },
                {"role": "user", "content": f"Analyse ce match : {match}"}
            ],
            temperature=0.4
        )

        # Renvoi de la réponse à l'application
        return jsonify({
            "status": "success",
            "analysis": response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Koyeb utilise le port 8000 par défaut
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

