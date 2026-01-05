import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)

# Configuration CORS ultra-large pour ne plus avoir de "Failed to fetch"
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route("/")
def health():
    return {"status": "VisiFoot API Online"}

@app.route("/analyze", methods=["POST", "OPTIONS"])
def analyze():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json(silent=True) or {}
    
    # On récupère le match peu importe le nom que Lovable lui donne
    home = data.get("homeTeam") or data.get("equipe_domicile") or data.get("home")
    away = data.get("awayTeam") or data.get("equipe_exterieur") or data.get("away")
    full_match = data.get("match")

    if full_match:
        match_query = full_match
    elif home and away:
        match_query = f"{home} vs {away}"
    else:
        return jsonify({"error": "Données de match manquantes"}), 400

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es VisiFoot, expert en paris sportifs. Donne un score exact et une confiance en %."
                },
                {"role": "user", "content": f"Analyse : {match_query}"}
            ],
            temperature=0.4
        )

        # On renvoie un format que Lovable comprendra toujours
        result = response.choices[0].message.content
        return jsonify({
            "status": "success",
            "analysis": result,
            "prediction": result # Doublon pour la sécurité
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)


