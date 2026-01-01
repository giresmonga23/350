from flask import Flask, request, jsonify
from groq import Groq
import os

app = Flask(__name__)

# Clé API via variable d'environnement
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    match = data.get('match')
    try:
        chat = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Tu es VisiFoot, une IA experte en pronostics foot. Donne une analyse courte et précise."},
                {"role": "user", "content": f"Analyse ce match : {match}"}
            ],
            model="llama-3.3-13b",  # modèle plus léger si ressources limitées
        )
        return jsonify({"status": "success", "analysis": chat.choices[0].message.content})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
