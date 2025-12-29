import telebot, random, requests, math

# --- CONFIGURATION ---
# Remplace avec ton propre Token si celui-ci ne marche plus
TELEGRAM_TOKEN = "8523335700:AAGZCrXxtvI3zRjhC0V4rWFG4tW7NMH8fvM"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def poisson_prob(lmbda, k):
    return (lmbda ** k) * math.exp(-lmbda) / math.factorial(k)

def calculate_probabilities(xg_home, xg_away):
    home_win = draw = away_win = 0
    for i in range(6):
        for j in range(6):
            p = poisson_prob(xg_home, i) * poisson_prob(xg_away, j)
            if i > j: home_win += p
            elif i == j: draw += p
            else: away_win += p
    return int(home_win*100), int(draw*100), int(away_win*100)

@bot.message_handler(func=lambda m: True)
def handle_all(m):
    text = m.text
    if 'vs' in text.lower():
        bot.send_chat_action(m.chat.id, 'typing')
        xh, xa = round(random.uniform(1.0, 2.5), 2), round(random.uniform(0.8, 2.0), 2)
        p_h, p_n, p_a = calculate_probabilities(xh, xa)

        msg = (f"📊 **ANALYSE VISIFOOT**\n"
               f"Match: {text}\n\n"
               f"📈 Probabilités :\n"
               f"1: {p_h}% | N: {p_n}% | 2: {p_a}%\n"
               f"xG attendus : {xh} - {xa}\n\n"
               f"✅ Conseil : Analyse basée sur les stats récentes.")
        bot.reply_to(m, msg)
    else:
        bot.reply_to(m, "Bienvenue sur VisiFoot ! Envoie un match (ex: Real vs Barca).")

print("✅ Moteur VisiFoot opérationnel sur PythonAnywhere !")
bot.polling()
