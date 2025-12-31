from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

# Ta clé API Groq pour l'intelligence artificielle
client = Groq(api_key="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")

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    match = data.get('match')
    try:
        # Utilisation du modèle Llama 3.3 pour l'analyse
        chat = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Tu es VisiFoot, une IA experte en pronostics foot. Donne une analyse courte et précise."},
                {"role": "user", "content": f"Analyse ce match : {match}"}
            ],
            model="llama-3.3-70b-versatile",
        )
        return jsonify({"status": "success", "analysis": chat.choices[0].message.content})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    # Le port 5000 est nécessaire pour la communication avec l'APK
    app.run(host='0.0.0.0', port=5000)
