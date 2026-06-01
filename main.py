import requests
import pandas as pd
from dotenv import load_dotenv
import os
import time

# Wczytaj token z .env
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

BASE_URL = "https://api.football-data.org/v4"
headers = {"X-Auth-Token": API_TOKEN}


def get_teams():
    """Pobiera wszystkie kluby z Premier League"""
    url = f"{BASE_URL}/competitions/PL/teams"
    response = requests.get(url, headers=headers)
    data = response.json()
    teams = data["teams"]
    print(f"Pobrano {len(teams)} klubów z Premier League")
    return teams


def get_top_scorer_per_club(teams):
    """Dla każdego klubu pobiera zawodników i znajduje króla strzelców"""
    results = []

    # Pobierz RAZ listę wszystkich strzelców z sezonu (oszczędza requesty!)
    print("Pobieram listę strzelców Premier League...")
    scorers_url = f"{BASE_URL}/competitions/PL/scorers?season=2024&limit=100"
    scorers_response = requests.get(scorers_url, headers=headers)
    all_scorers = scorers_response.json().get("scorers", [])
    print(f"Pobrano {len(all_scorers)} strzelców\n")

    time.sleep(7)

    for team in teams:
        team_id = team["id"]
        team_name = team["name"]
        print(f"Pobieram skład: {team_name}...")

        # Pobierz skład drużyny żeby mieć pozycje zawodników
        url = f"{BASE_URL}/teams/{team_id}"
        response = requests.get(url, headers=headers)
        data = response.json()
        squad = data.get("squad", [])

        # Zbuduj słownik: id zawodnika -> pozycja
        position_map = {
            player["id"]: player.get("position", "N/A")
            for player in squad
        }

        # Filtruj strzelców tylko z tego klubu
        club_scorers = [
            s for s in all_scorers
            if s["team"]["id"] == team_id
        ]

        if not club_scorers:
            results.append({
                "Klub": team_name,
                "Król strzelców": "Brak danych",
                "Gole": 0,
                "Pozycja": "-"
            })
            time.sleep(7)
            continue

        # Znajdź zawodnika z największą liczbą goli
        top = max(club_scorers, key=lambda x: x["goals"])
        player_id = top["player"]["id"]

        results.append({
            "Klub": team_name,
            "Król strzelców": top["player"]["name"],
            "Gole": top["goals"],
            "Pozycja": position_map.get(player_id, "N/A")
        })

        time.sleep(7)

    return results


def save_to_csv(results):
    """Zapisuje wyniki do pliku CSV"""
    df = pd.DataFrame(results)
    df = df.sort_values("Gole", ascending=False)
    df.to_csv("data/krolowie_strzelcow.csv", index=False, encoding="utf-8-sig")
    print("\nZapisano do data/krolowie_strzelcow.csv")
    return df


def save_to_excel(df):
    """Zapisuje wyniki do pliku Excel z formatowaniem"""
    os.makedirs("data", exist_ok=True)
    path = "data/krolowie_strzelcow.xlsx"

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Królowie strzelców", index=False)

        worksheet = writer.sheets["Królowie strzelców"]

        # Szerokość kolumn
        worksheet.column_dimensions["A"].width = 30
        worksheet.column_dimensions["B"].width = 25
        worksheet.column_dimensions["C"].width = 10
        worksheet.column_dimensions["D"].width = 20

    print(f"Zapisano do {path}")


def main():
    print("=== Football ETL Pipeline ===\n")

    # 1. Pobierz kluby
    teams = get_teams()

    # 2. Znajdź króla strzelców każdego klubu
    results = get_top_scorer_per_club(teams)

    # 3. Zapisz wyniki
    os.makedirs("data", exist_ok=True)
    df = save_to_csv(results)
    save_to_excel(df)

    # 4. Pokaż wyniki w konsoli
    print("\n=== KRÓLOWIE STRZELCÓW PREMIER LEAGUE ===\n")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()