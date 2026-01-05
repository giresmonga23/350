import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
# Autorisation totale pour Lovable
CORS(app, resources={r"/*": {"origins": "*"}})

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route("/")
def health():
    return {"status": "VisiFoot API Online", "server": "Healthy"}

@app.route("/analyze", methods=["POST", "OPTIONS"])
def analyze():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

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
                {"role": "user", "content": f"Donne le score exact et les buteurs pour {home} vs {away}."}
            ]
        )
        
        reponse_ia = completion.choices[0].message.content

        return jsonify({
            "equipe_domicile": home,
            "equipe_



