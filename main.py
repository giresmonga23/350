from fastapi import FastAPI
import math

app = FastAPI(title="FootBrain API")

def poisson(lmbda, k):
    return (lmbda ** k) * math.exp(-lmbda) / math.factorial(k)

def match_probabilities(xg_home, xg_away, max_goals=6):
    home = draw = away = 0
    for i in range(max_goals):
        for j in range(max_goals):
            p = poisson(xg_home, i) * poisson(xg_away, j)
            if i > j:
                home += p
            elif i == j:
                draw += p
            else:
                away += p
    return {
        "home_%": round(home * 100, 2),
        "draw_%": round(draw * 100, 2),
        "away_%": round(away * 100, 2)
    }

@app.get("/")
def root():
    return {"status": "FootBrain API online"}

@app.get("/predict")
def predict(home_xg: float, away_xg: float):
    return {
        "model": "Poisson MVP",
        "probabilities": match_probabilities(home_xg, away_xg),
        "note": "Analyse probabiliste, pas certitude"
  }
