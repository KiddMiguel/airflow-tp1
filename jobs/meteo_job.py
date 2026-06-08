import json
import os
from urllib.parse import urlencode
from urllib.request import urlopen


DATA_DIR = "/opt/airflow/data/meteo"
RAW_FILE = f"{DATA_DIR}/meteo_brute.json"
CLEAN_FILE = f"{DATA_DIR}/meteo_propre.json"
REPORT_FILE = f"{DATA_DIR}/rapport_meteo.txt"

VILLES = [
    {"ville": "Paris", "country_code": "FR"},
    {"ville": "Lyon", "country_code": "FR"},
    {"ville": "Marseille", "country_code": "FR"},
    {"ville": "Brazzaville", "country_code": "CG"},
    {"ville": "Pointe-Noire", "country_code": "CG"},
]

GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_API_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODE_LABELS = {
    0: "ciel degage",
    1: "principalement degage",
    2: "partiellement nuageux",
    3: "couvert",
    45: "brouillard",
    48: "brouillard givrant",
    51: "bruine legere",
    53: "bruine moderee",
    55: "bruine dense",
    56: "bruine verglacante legere",
    57: "bruine verglacante dense",
    61: "pluie legere",
    63: "pluie moderee",
    65: "forte pluie",
    66: "pluie verglacante legere",
    67: "pluie verglacante forte",
    71: "faible neige",
    73: "neige moderee",
    75: "forte neige",
    77: "grains de neige",
    80: "averses legeres",
    81: "averses moderees",
    82: "averses violentes",
    85: "averses de neige legeres",
    86: "averses de neige fortes",
    95: "orage",
    96: "orage avec faible grele",
    99: "orage avec forte grele",
}


def _get_json(url, params):
    query = urlencode(params)
    with urlopen(f"{url}?{query}", timeout=30) as response:
        return json.load(response)


def _get_coordinates(ville, country_code):
    payload = _get_json(
        GEOCODING_API_URL,
        {
            "name": ville,
            "count": 1,
            "language": "fr",
            "format": "json",
            "countryCode": country_code,
        },
    )
    results = payload.get("results") or []
    if not results:
        raise ValueError(f"Aucune coordonnee trouvee pour {ville} ({country_code}).")

    premier_resultat = results[0]
    return premier_resultat["latitude"], premier_resultat["longitude"]


def _get_current_weather(latitude, longitude):
    payload = _get_json(
        FORECAST_API_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,weather_code",
            "timezone": "auto",
            "forecast_days": 1,
        },
    )
    current = payload.get("current")
    if not current:
        raise ValueError("La reponse de l'API meteo ne contient pas de bloc current.")

    return current


def extraire_meteo():
    os.makedirs(DATA_DIR, exist_ok=True)

    donnees = []
    for entree in VILLES:
        ville = entree["ville"]
        country_code = entree["country_code"]
        latitude, longitude = _get_coordinates(ville, country_code)
        current = _get_current_weather(latitude, longitude)

        donnees.append(
            {
                "ville": ville,
                "country_code": country_code,
                "latitude": latitude,
                "longitude": longitude,
                "temperature": current["temperature_2m"],
                "humidite": current["relative_humidity_2m"],
                "weather_code": current["weather_code"],
                "condition": WEATHER_CODE_LABELS.get(current["weather_code"], "inconnu"),
                "date_observation": current["time"],
            }
        )

    with open(RAW_FILE, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, ensure_ascii=False, indent=4)

    print(f"Extraction terminee : {len(donnees)} villes meteo recuperees.")


def valider_meteo():
    with open(RAW_FILE, "r", encoding="utf-8") as fichier:
        donnees = json.load(fichier)

    if not donnees:
        raise ValueError("Aucune donnee meteo trouvee.")

    colonnes_obligatoires = [
        "ville",
        "country_code",
        "latitude",
        "longitude",
        "temperature",
        "humidite",
        "weather_code",
        "condition",
        "date_observation",
    ]

    for ligne in donnees:
        for colonne in colonnes_obligatoires:
            if colonne not in ligne:
                raise ValueError(f"Colonne manquante : {colonne}")

    print("Validation reussie : les donnees meteo sont completes.")


def transformer_meteo():
    with open(RAW_FILE, "r", encoding="utf-8") as fichier:
        donnees = json.load(fichier)

    donnees_transformees = []
    for ligne in donnees:
        donnees_transformees.append(
            {
                "ville": ligne["ville"].strip().upper(),
                "country_code": ligne["country_code"],
                "latitude": float(ligne["latitude"]),
                "longitude": float(ligne["longitude"]),
                "temperature_celsius": float(ligne["temperature"]),
                "humidite_pourcentage": int(ligne["humidite"]),
                "weather_code": int(ligne["weather_code"]),
                "condition": str(ligne["condition"]).strip().lower(),
                "date_observation": ligne["date_observation"],
            }
        )

    with open(CLEAN_FILE, "w", encoding="utf-8") as fichier:
        json.dump(donnees_transformees, fichier, ensure_ascii=False, indent=4)

    print("Transformation terminee : donnees nettoyees et typees.")


def generer_rapport():
    with open(CLEAN_FILE, "r", encoding="utf-8") as fichier:
        donnees = json.load(fichier)

    temperature_moyenne = sum(v["temperature_celsius"] for v in donnees) / len(donnees)
    ville_plus_chaude = max(donnees, key=lambda v: v["temperature_celsius"])

    lignes = [
        "RAPPORT METEO",
        "=============",
        f"Nombre de villes analysees : {len(donnees)}",
        f"Temperature moyenne : {temperature_moyenne:.2f} degC",
        (
            "Ville la plus chaude : "
            f"{ville_plus_chaude['ville']} ({ville_plus_chaude['temperature_celsius']} degC)"
        ),
        "",
        "Detail par ville :",
    ]

    for ville in donnees:
        lignes.append(
            f"- {ville['ville']} ({ville['country_code']}) : "
            f"{ville['temperature_celsius']} degC, "
            f"{ville['humidite_pourcentage']} %, "
            f"{ville['condition']}, "
            f"observe le {ville['date_observation']}"
        )

    rapport = "\n".join(lignes)

    with open(REPORT_FILE, "w", encoding="utf-8") as fichier:
        fichier.write(rapport)

    print(rapport)
