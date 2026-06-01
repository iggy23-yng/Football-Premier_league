
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

def load_data():
    """Wczytuje dane z CSV"""
    df = pd.read_csv("data/krolowie_strzelcow.csv", encoding="utf-8-sig")
    # Usuń wiersze bez danych
    df = df[df["Król strzelców"] != "Brak danych"]
    df = df.sort_values("Gole", ascending=True)  # ascending=True bo wykres poziomy
    return df


def plot_top_scorers_per_club(df):
    """Rysuje poziomy bar chart - król strzelców każdego klubu"""

    fig, ax = plt.subplots(figsize=(12, 10))

    # Kolory słupków - gradient od niebieskiego do czerwonego
    colors = plt.cm.RdYlGn([x / max(df["Gole"]) for x in df["Gole"]])

    bars = ax.barh(
        y=df["Klub"],
        width=df["Gole"],
        color=colors,
        edgecolor="white",
        linewidth=0.5,
        height=0.6
    )

    # Dodaj imię zawodnika i liczbę goli na słupku
    for bar, (_, row) in zip(bars, df.iterrows()):
        width = bar.get_width()
        ax.text(
            width + 0.1,
            bar.get_y() + bar.get_height() / 2,
            f"{row['Król strzelców']} ({int(row['Gole'])} goli)",
            va="center",
            ha="left",
            fontsize=9,
            color="#333333"
        )

    # Styl wykresu
    ax.set_xlabel("Liczba goli", fontsize=12, labelpad=10)
    ax.set_title(
        "⚽ Królowie strzelców Premier League 2024/25\nNajlepszy strzelec każdego klubu",
        fontsize=14,
        fontweight="bold",
        pad=20
    )

    ax.set_xlim(0, max(df["Gole"]) + 8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="y", labelsize=10)
    ax.grid(axis="x", alpha=0.3, linestyle="--")

    plt.tight_layout()

    # Zapisz wykres
    os.makedirs("data", exist_ok=True)
    path = "data/krolowie_strzelcow_chart.png"
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"Wykres zapisany: {path}")
    plt.show()


def main():
    print("=== Generowanie wykresów ===\n")
    df = load_data()
    plot_top_scorers_per_club(df)


if __name__ == "__main__":
    main()



