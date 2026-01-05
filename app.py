import os
from flask import Flask, request, jsonify
from flask_cors import CORS  # <-- LIGNE 1 : AJOUTÉE
from groq import Groq

app = Flask(__name__)
CORS(app)  # <-- LIGNE 2 : AJOUTÉE (Autorise Lovable à se connecter)

# Clé API Groq depuis variables d’environnement
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route("/")
def health():
    return {"status": "FootBrain API online"}

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True)
    
    # Lovable envoie parfois 'equipe_domicile', on s'adapte
    if not data:
        return jsonify({"error": "Données non fournies"}), 400
    
    match = data.get("match") or f"{data.get('equipe_domicile')} vs {data.get('equipe_exterieur')}"

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es VisiFoot, une IA experte en paris sportifs football. "
                        "Donne un pronostic précis avec score exact et confiance."
                    )
                },
                {"role": "user", "content": f"Analyse ce match : {match}"}
            ],
            temperature=0.4
        )

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
