import os
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

# Initialisation sécurisée du client Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route("/")
def health():
    return {"status": "ok"}

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True)
    if not data or "match" not in data:
        return jsonify({"error": "Match non fourni"}), 400

    match = data["match"]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es VisiFoot, une IA experte en paris sportifs football. "
                        "Analyse data-driven, value betting, probabilités, absences, contexte."
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
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
