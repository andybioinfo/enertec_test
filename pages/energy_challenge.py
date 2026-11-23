"""EnerTec – Energie-Landkarte / Energy Map Challenge.

A clickable, fully self-contained map-building game for Streamlit.
Uses only the existing EnerTec language.py and navigation.py modules.
Save as pages/h19_Energie_Landkarte.py.
"""

from __future__ import annotations

import math
import random

import pandas as pd
import streamlit as st

from language import lang
from navigation import hide_default_sidebar_nav

st.set_page_config(page_title="EnerTec – Energie-Landkarte", page_icon="⚡", layout="wide")
hide_default_sidebar_nav()

# -------- Game rules: illustrative values, not real-world project data --------
BUDGET = 150
DAY_LENGTH = 24
TERRAIN = [
    ["hill", "hill", "hill", "plain", "plain", "hill", "hill", "hill"],
    ["hill", "forest", "plain", "plain", "river", "plain", "hill", "hill"],
    ["forest", "plain", "city", "city", "river", "plain", "plain", "hill"],
    ["forest", "plain", "city", "city", "river", "plain", "plain", "plain"],
    ["plain", "plain", "plain", "plain", "river", "plain", "plain", "plain"],
    ["plain", "plain", "plain", "plain", "river", "plain", "plain", "plain"],
]
TERRAIN_ICONS = {"hill": "⛰️", "plain": "🌾", "forest": "🌲", "river": "🌊", "city": "🏙️"}
TERRAIN_NAMES = {
    "hill": ("Hügel", "Hill"), "plain": ("Freifläche", "Open land"),
    "forest": ("Wald (geschützt)", "Forest (protected)"),
    "river": ("Fluss", "River"), "city": ("Stadt", "City"),
}
# Cost = game coins. Power = maximum illustrative MW; storage capacity in MWh.
TECH = {
    "solar": {"icon": "☀️", "title": ("Solarpark", "Solar farm"), "cost": 12, "power": 2.2, "terrain": {"plain"}},
    "wind": {"icon": "🌬️", "title": ("Windrad", "Wind turbine"), "cost": 20, "power": 2.8, "terrain": {"hill", "plain"}},
    "hydro": {"icon": "💦", "title": ("Wasserkraft", "Hydropower"), "cost": 26, "power": 1.65, "terrain": {"river"}},
    "battery": {"icon": "🔋", "title": ("Batteriespeicher", "Battery storage"), "cost": 18, "capacity": 3.5, "terrain": {"plain"}},
    "hydrogen": {"icon": "🧪", "title": ("H₂-Speicher", "H₂ storage"), "cost": 24, "capacity": 8.0, "terrain": {"plain"}},
}
WEATHER = {
    "balanced": ("🌤️ Wechselhaft", "🌤️ Mixed weather"),
    "sunny": ("☀️ Sonnenschein", "☀️ Sunny"),
    "windy": ("🌪️ Stürmischer Tag", "🌪️ Windy"),
    "cloudy": ("🌧️ Regenwetter", "🌧️ Rainy"),
}
STATE = "enertec_map_challenge_v2"


def new_game():
    return {"buildings": {}, "chosen": "solar", "weather": "balanced", "results": None,
            "notice": "", "runs": [], "show_rules": False}


if STATE not in st.session_state:
    st.session_state[STATE] = new_game()
game = st.session_state[STATE]


def counts():
    return {tech: list(game["buildings"].values()).count(tech) for tech in TECH}


def price():
    return sum(TECH[tech]["cost"] for tech in game["buildings"].values())


def place(row, col):
    position = (row, col)
    selected = game["chosen"]
    terrain = TERRAIN[row][col]
    if selected == "erase":
        if position in game["buildings"]:
            game["buildings"].pop(position)
            game["notice"] = lang("Anlage entfernt. Münzen zurückerhalten!", "Building removed. Coins refunded!")
        else:
            game["notice"] = lang("Hier steht keine Anlage.", "No building on this tile.")
    elif position in game["buildings"]:
        game["notice"] = lang("Feld belegt! Wähle zuerst 'Entfernen'.", "Tile occupied! Select 'Remove' first.")
    elif terrain not in TECH[selected]["terrain"]:
        game["notice"] = lang("Hier darfst du diese Anlage nicht bauen. Schau auf die Landschaft!",
                              "You cannot build that here. Look at the terrain!")
    elif price() + TECH[selected]["cost"] > BUDGET:
        game["notice"] = lang("Zu wenig Münzen. Entferne eine andere Anlage.",
                              "Not enough coins. Remove another building.")
    else:
        game["buildings"][position] = selected
        game["notice"] = lang("Anlage errichtet! 🎉", "Building placed! 🎉")
    game["results"] = None


def generation_profile(weather):
    """24 hourly model records, units of MW / MW per plant. Deterministic."""
    factors = {"balanced": (0.9, 1.0, 1.0), "sunny": (1.2, 0.7, 0.85),
               "windy": (0.65, 1.4, 1.05), "cloudy": (0.4, 0.9, 1.15)}
    sol_factor, wind_factor, river_factor = factors[weather]
    rng = random.Random({"balanced": 13, "sunny": 24, "windy": 35, "cloudy": 46}[weather])
    records = []
    for hour in range(DAY_LENGTH):
        daylight = max(0.0, math.sin((hour - 6) / 12 * math.pi))
        cloud = 0.76 + rng.uniform(-0.13, 0.16)
        solar_factor = min(1.0, sol_factor * daylight * cloud)
        wind = max(0.12, min(0.95, 0.42 * wind_factor + 0.17 * math.sin(0.66 * hour + 1)
                                 + rng.uniform(-0.13, 0.13)))
        demand = (3.7 + 0.7 * math.exp(-((hour - 8) / 2.6) ** 2)
                  + 1.65 * math.exp(-((hour - 19) / 3.2) ** 2))
        if hour in (18, 19, 20):
            demand += 0.45  # City event
        records.append({"hour": hour, "solar_unit": TECH["solar"]["power"] * solar_factor,
                        "wind_unit": TECH["wind"]["power"] * wind,
                        "hydro_unit": TECH["hydro"]["power"] * river_factor,
                        "demand": demand})
    return records


def run_simulation(buildings, weather):
    """Hour-by-hour balance. Storage initial state: 25% full, not free renewable energy.

    To avoid gifting free energy, batteries and H2 start EMPTY; charge from daytime surplus.
    Battery 90% charge * 90% discharge, H2 38% electricity->electricity overall.
    Storage state is *deliverable electric energy* for H2, and internal energy for battery.
    Back-up generation balances any shortfall (no physical blackouts).
    """
    n = {code: list(buildings.values()).count(code) for code in TECH}
    bat_cap = TECH["battery"]["capacity"] * n["battery"]
    h_cap = TECH["hydrogen"]["capacity"] * n["hydrogen"]
    bat_energy = 0.0
    h_energy = 0.0
    rows = []
    for hour in generation_profile(weather):
        solar = n["solar"] * hour["solar_unit"]
        wind = n["wind"] * hour["wind_unit"]
        hydro = n["hydro"] * hour["hydro_unit"]
        demand = hour["demand"]
        renewable = solar + wind + hydro
        net = renewable - demand
        battery_out = hydrogen_out = emergency = surplus_lost = 0.0
        if net >= 0:
            # Charging rate in MW, charge eff. = 0.90
            bat_in = min(net, n["battery"] * 1.9, max(0.0, (bat_cap - bat_energy) / 0.90))
            bat_energy += bat_in * 0.90
            net -= bat_in
            # Hydrogen: round-trip efficiency 0.38 (already included on charge)
            h_in = min(net, n["hydrogen"] * 1.6, max(0.0, (h_cap - h_energy) / 0.38))
            h_energy += h_in * 0.38
            surplus_lost = max(0.0, net - h_in)
        else:
            need = -net
            battery_out = min(need, n["battery"] * 1.9, bat_energy * 0.90)
            bat_energy -= battery_out / 0.90
            need -= battery_out
            hydrogen_out = min(need, n["hydrogen"] * 1.5, h_energy)
            h_energy -= hydrogen_out
            need -= hydrogen_out
            emergency = max(0.0, need)
        rows.append({"hour": hour["hour"], "demand": demand, "solar": solar,
                     "wind": wind, "hydro": hydro, "battery": battery_out,
                     "hydrogen": hydrogen_out, "backup": emergency,
                     "spill": surplus_lost, "battery_level": bat_energy, "hydrogen_level": h_energy})
    total_demand = sum(x["demand"] for x in rows)
    backup = sum(x["backup"] for x in rows)
    spill = sum(x["spill"] for x in rows)
    fraction = max(0.0, 1.0 - backup / max(total_demand, 0.00001))
    # Transparent game score; 1000 max. No claim of real economic optimality.
    score = round(850 * fraction + 100 * (1 - min(spill / max(total_demand, 1), 1))
                  + 50 * (1 - sum(TECH[k]["cost"] for k in buildings.values()) / BUDGET))
    return {"rows": rows, "score": score, "coverage": fraction * 100,
            "demand": total_demand, "backup": backup, "spill": spill,
            "co2": backup * 0.7, "green": total_demand - backup}


def number(n, digits=1):
    value = f"{n:.{digits}f}"
    return value.replace(".", ",") if lang("DE", "EN") == "DE" else value


# -------- Page visuals --------------------------------------------------------
st.markdown("""
<style>
.block-container {max-width:1360px;padding-top:1.1rem;padding-bottom:2rem;}
.map-hero {padding:1.15rem 1.5rem;border-radius:20px;background:linear-gradient(115deg,#143c68,#187864);
 color:white;margin-bottom:1rem;box-shadow:0 10px 26px rgba(6,70,90,.12)}
.map-hero h1,.map-hero p{color:white!important;margin:.35rem 0;}
.map-hero p{opacity:.95}
.map-eyebrow{letter-spacing:.14em;font-size:.75rem;font-weight:800;color:#c9fcdb;}
.tile-title{font-weight:700;color:#258c77;font-size:.82rem}
div[data-testid="stButton"] > button {border-radius:10px;font-weight:700;}
/* Terrain coloring: map cells are native buttons and remain keyboard accessible. */
""" + "\n".join(
    f'.st-key-map_tile_{r}_{c} button {{'
    f'background:{ {"plain":"#e8f5c5","hill":"#dbc9b7","forest":"#aad6b7","river":"#bde8fa","city":"#d4dce6"}[terrain] };'
    'color:#173950!important;border:1px solid rgba(40,85,70,.3)!important;'
    'min-height:57px;width:100%;font-size:1.27rem;'
    '}'
    for r, row in enumerate(TERRAIN) for c, terrain in enumerate(row)
) + "\n</style>", unsafe_allow_html=True)

st.markdown(
    '<div class="map-hero"><div class="map-eyebrow">ENERTEC · ENERGY MAP CHALLENGE</div>'
    f'<h1>🗺️ {lang("Baue deine eigene Energielandschaft!", "Build your energy landscape!")}</h1>'
    f'<p>{lang("Setze Kraftwerke auf die Karte, bleib im Budget und versorge die Stadt mit möglichst viel erneuerbarer Energie.", "Place power plants on the map, stay on budget and power your city with renewable energy.")}</p></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("🗺️ " + lang("Energie-Landkarte", "Energy map"))
    if st.button(lang("← Zur Startseite", "← Back to homepage"), use_container_width=True):
        st.switch_page("Startseite.py")
    if st.button(lang("🔄 Karte zurücksetzen", "🔄 Reset map"), use_container_width=True):
        st.session_state[STATE] = new_game()
        st.rerun()
    st.caption(lang("Die Sprache bleibt beim Wechsel erhalten.", "Language selection is preserved."))

side, main = st.columns([1, 2.25], gap="large")
with side:
    st.subheader(lang("🏗️ Wähle deine Anlage", "🏗️ Pick a building"))
    options = list(TECH) + ["erase"]
    choice = st.radio(
        lang("Bauwerkzeug", "Building tool"), options=options,
        format_func=lambda k: (f'{TECH[k]["icon"]} {lang(*TECH[k]["title"])} · {TECH[k]["cost"]} 🪙'
                               if k in TECH else lang("🧹 Anlage entfernen", "🧹 Remove building")),
        key="map_challenge_selected", label_visibility="collapsed",
    )
    game["chosen"] = choice
    cost = price()
    remaining = BUDGET - cost
    c1,c2 = st.columns(2)
    c1.metric(lang("Budget übrig", "Budget left"), f"{remaining} 🪙")
    c2.metric(lang("Gebaut", "Built"), len(game["buildings"]))
    st.progress(cost / BUDGET)
    st.caption(lang("Bauwerke können jederzeit kostenlos entfernt werden.",
                    "You can remove buildings and get the full cost refunded."))
    st.divider()
    st.markdown("**" + lang("Bau-Regeln", "Build rules") + "**")
    st.write(lang("☀️ Solar: auf Freiflächen", "☀️ Solar: open land"))
    st.write(lang("🌬️ Wind: auf Hügeln und Freiflächen", "🌬️ Wind: hills and open land"))
    st.write(lang("💦 Wasser: direkt am Fluss", "💦 Hydro: river tiles"))
    st.write(lang("🔋 Batterie / 🧪 H₂: auf Freiflächen", "🔋 Battery / 🧪 H₂: open land"))
    st.caption(lang("🌲 Wälder und 🏙️ Stadt bleiben unbebaut.",
                    "🌲 Forests and 🏙️ city areas cannot be built on."))

with main:
    st.subheader(lang("🌍 Deine Landkarte", "🌍 Your map"))
    st.caption(lang("1. Anlage links auswählen   2. Feld auf der Karte anklicken   3. Simulation starten",
                    "1. Select a building   2. Click a map tile   3. Run the simulation"))
    with st.container(border=True):
        for r, line in enumerate(TERRAIN):
            columns = st.columns(len(line), gap="small")
            for c, terrain in enumerate(line):
                building = game["buildings"].get((r,c))
                symbol = TECH[building]["icon"] if building else TERRAIN_ICONS[terrain]
                tip = (lang(*TECH[building]["title"]) + " · " if building else "") + lang(*TERRAIN_NAMES[terrain])
                with columns[c]:
                    if st.button(symbol, key=f"map_tile_{r}_{c}", help=tip,
                                 use_container_width=True):
                        place(r,c)
                        st.rerun()
    if game["notice"]:
        st.caption(game["notice"])
    st.caption(lang("🌾 Freifläche    ⛰️ Hügel    🌲 Wald    🌊 Fluss    🏙️ Stadt",
                    "🌾 Open land    ⛰️ Hills    🌲 Forest    🌊 River    🏙️ City"))

st.divider()
st.subheader(lang("⚙️ Deine Energieversorgung testen", "⚙️ Test your power supply"))
st.write(lang(
    "Deine Stadt benötigt **24 Stunden lang Strom**. Solar, Wind und Wasserkraft liefern je nach Wetter. "
    "Batterien und Wasserstoff speichern Überschüsse. Wenn die Energie nicht reicht, hilft ein "
    "fossiles Notkraftwerk aus – aber das kostet Punkte.",
    "Your city needs **electricity for 24 hours**. Solar, wind and hydropower respond to the weather. "
    "Batteries and hydrogen can store surplus energy. If power is still short, "
    "a fossil-fuel backup plant helps out – but costs points.",
))

weather = st.selectbox(
    lang("Wetterlage auswählen", "Choose a weather scenario"), list(WEATHER),
    format_func=lambda code: lang(*WEATHER[code]), key="map_challenge_weather",
)
game["weather"] = weather
if not game["buildings"]:
    st.info(lang("Baue zuerst mindestens ein Kraftwerk auf der Karte.",
                 "Build at least one power plant on the map first."))

if st.button(lang("🚀 24 STUNDEN SIMULIEREN", "🚀 SIMULATE 24 HOURS"),
             type="primary", use_container_width=True,
             disabled=not any(x in {"solar","wind","hydro"} for x in game["buildings"].values())):
    game["results"] = run_simulation(game["buildings"],weather)
    game["runs"].append({"points":game["results"]["score"],
                         "coverage":round(game["results"]["coverage"],1),
                         "spent":price(),"weather":lang(*WEATHER[weather])})
    st.rerun()

if game["results"]:
    result = game["results"]
    st.divider()
    points = result["score"]
    if result["coverage"] >= 98:
        trophy, rank = "🏆", lang("Energie-Legende", "Energy Legend")
    elif result["coverage"] >= 85:
        trophy, rank = "🥇", lang("Energie-Profi", "Energy Pro")
    elif result["coverage"] >= 65:
        trophy, rank = "🥈", lang("Stadtretter", "City Saver")
    else:
        trophy, rank = "🔧", lang("Nächster Versuch!", "Try Again!")
    st.subheader(f"{trophy} {rank} · {points} / 1000 {lang('Punkte','points')}")
    result_cols = st.columns(4)
    result_cols[0].metric(lang("Erneuerbare Deckung", "Renewable coverage"),f"{number(result['coverage'])} %")
    result_cols[1].metric(lang("Notstrom", "Backup power"),f"{number(result['backup'])} MWh")
    result_cols[2].metric(lang("Ungenutzte Energie", "Unused energy"),f"{number(result['spill'])} MWh")
    result_cols[3].metric(lang("CO₂ durch Notstrom", "Backup CO₂"),f"{number(result['co2'])} t")

    chart_data = pd.DataFrame(result["rows"])
    chart_cols = {
        "demand":lang("Bedarf", "Demand"), "solar":lang("Solarstrom", "Solar"),
        "wind":lang("Windstrom", "Wind"), "hydro":lang("Wasserkraft", "Hydropower"),
        "battery":lang("Batterieabgabe", "Battery output"),
        "hydrogen":lang("H₂-Abgabe", "H₂ output"),
        "backup":lang("Notstrom", "Backup")}
    st.subheader("📈 " + lang("So lief dein Tag", "How your day went"))
    st.line_chart(chart_data.set_index("hour")[list(chart_cols)].rename(columns=chart_cols),
                  x_label=lang("Stunde", "Hour"), y_label="MW")
    st.caption(lang(
        "Eine Stunde bei 1 MW entspricht 1 MWh. Die Simulation verwendet fiktive Anlagengrößen "
        "und Wetterdaten. Der angenommene CO₂-Faktor für Notstrom beträgt 0,7 t/MWh.",
        "One hour at 1 MW corresponds to 1 MWh. The simulation uses fictional plant "
        "capacities and weather profiles. Backup emission factor: assumed 0.7 t/MWh.",
    ))
    if result["coverage"] >= 98:
        st.balloons()
        st.success(lang("Fast ohne fossilen Notstrom! Versuch jetzt, das Budget noch effizienter zu nutzen.",
                        "Almost no fossil backup! Now try using your budget even more efficiently."))
    else:
        st.info(lang(
            "💡 Tipp: Nachts liefert Solarstrom nichts. Versuch es mit Wind, Wasserkraft oder "
            "Speichern. Wasserstoff hat dabei deutlich höhere Umwandlungsverluste als eine Batterie.",
            "💡 Tip: Solar panels produce nothing at night. Try wind, hydropower or storage. "
            "Hydrogen storage has higher conversion losses than batteries.",
        ))

    with st.expander(lang("🏅 Deine Ergebnisse in dieser Sitzung", "🏅 Your results in this session")):
        table = pd.DataFrame(sorted(game["runs"], key=lambda x:x["points"],reverse=True))
        st.dataframe(table, use_container_width=True, hide_index=True)

with st.expander(lang("🧠 Wie funktionieren Kraftwerke und Speicher im Spiel?",
                      "🧠 How do plants and storage work in the game?")):
    st.write(lang(
        "**Solar:** Liefert nur tagsüber, wetterabhängig. **Wind:** Kann auch nachts erzeugen, "
        "schwankt aber. **Wasserkraft:** Liefert im Modell relativ gleichmäßig Strom. "
        "**Batterie:** Speichert Überschüsse, mit jeweils 90 % Lade- und Entladewirkungsgrad. "
        "**Wasserstoff:** Aus überschüssigem Strom wird Wasserstoff erzeugt und später wieder "
        "Strom gewonnen. Im Modell liegt der vereinfachte Strom-zu-Strom-Wirkungsgrad bei 38 %. "
        "Beide Speicher starten leer. Die Stadt verbraucht je nach Stunde rund 3,7–6 MW. "
        "Alle Anlagenkosten, Leistungen und Umweltwerte sind **Spielwerte**, keine reale Standortplanung.",
        "**Solar:** Produces electricity only during daylight and depends on weather. **Wind:** "
        "Also works at night but fluctuates. **Hydro:** Produces relatively steady power in this model. "
        "**Battery:** Stores surplus with 90% charging and 90% discharge efficiency. "
        "**Hydrogen:** Surplus electricity is turned into hydrogen and later back into power; "
        "the model uses a simplified 38% electricity-to-electricity efficiency. "
        "Both storage types start empty. City demand varies around 3.7–6 MW. "
        "All prices, outputs and environmental figures are **game values**, not real site planning.",
    ))
