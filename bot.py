
import os
import telebot
import random
import math

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def poisson_prob(lmbda, k):
    return (lmbda ** k) * math.exp(-lmbda) / math.factorial(k)

def calculate_probabilities(xg_home, xg_away):
    home = draw = away = 0
    for i in range(6):
        for j in range(6):
            p = poisson_prob(xg_home, i) * poisson_prob(xg_away, j)
            if i > j:
                home += p
            elif i == j:
                draw += p
            else:
                away += p
    return int(home*100), int(draw*100), int(away*100)

@bot.message_handler(func=lambda m: True)
def handle(m):
    if "vs" in m.text.lower():
        xh = round(random.uniform(1.2, 2.4), 2)
        xa = round(random.uniform(0.8, 2.0), 2)
        p1, px, p2 = calculate_probabilities(xh, xa)

        msg = (
            f"📊 ANALYSE VISIFOOT\n\n"
            f"Match : {m.text}\n"
            f"1: {p1}% | N: {px}% | 2: {p2}%\n"
            f"xG : {xh} - {xa}"
        )
        bot.reply_to(m, msg)
    else:
        bot.reply_to(m, "Envoie un match (ex: Real vs Barca)")
