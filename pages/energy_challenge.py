"""EnerTec Energie-Challenge – bilingual, self-contained Streamlit mini-game.

Put this file at pages/energie_challenge.py. Requires the existing language.py
and navigation.py from the EnerTec project; no extra graphics or data files.
"""

import math
import random
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from language import lang

st.set_page_config(page_title="EnerTec | Energy City Challenge", layout="wide", page_icon="⚡")

# This is a cross-topic game: hide the default page list, but leave a prominent home button.
from navigation import hide_default_sidebar_nav
hide_default_sidebar_nav()

KEY = "enertec_energy_challenge_v1"
PRICES = {"solar": 8, "wind": 12, "battery": 9, "hydrogen": 11}
START_BUDGET = 120
ROUND_HOURS = 4
HOURS = 24
SCENARIOS = {
    "sun": {"seed": 131, "solar": 1.20, "wind": 0.70, "cloud": 0.92},
    "wind": {"seed": 275, "solar": 0.82, "wind": 1.22, "cloud": 0.83},
    "chaos": {"seed": 431, "solar": 0.95, "wind": 0.99, "cloud": 0.72},
}


def fresh_state():
    return {"phase": "planning", "plan": {}, "scenario": "chaos", "rows": [],
            "round": 0, "battery_charge": 0.0, "hydrogen_charge": 0.0,
            "saves_left": 2, "saves_used": 0, "score": 0, "history": [],
            "last_action": "none", "events": [], "reveal": False}


if KEY not in st.session_state:
    st.session_state[KEY] = fresh_state()
game = st.session_state[KEY]


@st.cache_data
def create_day(scenario):
    """Deterministic educational 24h generation & demand profiles (MW)."""
    p = SCENARIOS[scenario]
    rng = random.Random(p["seed"])
    day = []
    for h in range(HOURS):
        sunlight = max(0.0, math.sin(math.pi * (h - 6) / 12))
        cloud = max(0.25, min(1.1, p["cloud"] + rng.uniform(-0.2, 0.18)))
        solar_mw_per_unit = 0.95 * p["solar"] * sunlight * cloud
        wind_factor = max(0.11, min(0.92, 0.48 * p["wind"] + 0.22 * math.sin(h * 0.62 + p["seed"]) + rng.uniform(-0.15, 0.15)))
        wind_mw_per_unit = 1.35 * wind_factor
        demand = 2.45 + 0.75 * math.exp(-((h - 8) / 2.6) ** 2) + 1.6 * math.exp(-((h - 19) / 3.2) ** 2)
        demand += rng.uniform(-0.15, 0.15)
        event = ""
        if scenario == "chaos" and h in (10, 11):
            solar_mw_per_unit *= 0.25
            event = "cloud"
        if scenario == "chaos" and h in (17, 18):
            demand += 0.95
            event = "concert"
        if scenario == "wind" and h in (4, 5):
            wind_mw_per_unit *= 0.35
            event = "calm"
        day.append({"hour": h, "solar_unit": solar_mw_per_unit,
                    "wind_unit": wind_mw_per_unit, "demand": demand, "event": event})
    return day


def simulate_hours(plan, scenario, initial_battery, initial_hydrogen, start, action):
    """One hour steps, power in MW and energy in MWh; diesel is the balancing backup.

    Battery has 90% charging and discharging efficiency.
    Hydrogen tank is represented in *deliverable electrical* MWh, with a
    simplified 38% electricity-to-electricity efficiency applied on charging.
    """
    data = create_day(scenario)
    b_capacity = plan["battery"] * 2.4
    h_capacity = plan["hydrogen"] * 4.5
    battery = min(initial_battery, b_capacity)
    hydrogen = min(initial_hydrogen, h_capacity)
    rows = []
    for hour in range(start, min(start + ROUND_HOURS, HOURS)):
        d = data[hour]
        solar = d["solar_unit"] * plan["solar"]
        wind = d["wind_unit"] * plan["wind"]
        demand = d["demand"] * (0.82 if action == "save" else 1.0)
        renewable = solar + wind
        difference = renewable - demand
        battery_out = hydrogen_out = backup = wasted = 0.0
        if difference >= 0:
            # Charge electrical battery first, then convert surplus into H2.
            battery_input = min(difference, plan["battery"] * 1.1,
                                max(0, (b_capacity - battery) / 0.9))
            battery += battery_input * 0.9
            difference -= battery_input
            hydrogen_input = min(difference, plan["hydrogen"] * 1.4,
                                 max(0, (h_capacity - hydrogen) / 0.38))
            hydrogen += hydrogen_input * 0.38
            wasted = max(0, difference - hydrogen_input)
        else:
            missing = -difference
            battery_out = min(missing, plan["battery"] * 1.1, battery * 0.9)
            battery -= battery_out / 0.9
            missing -= battery_out
            hydrogen_out = min(missing, plan["hydrogen"] * 0.85, hydrogen)
            hydrogen -= hydrogen_out
            missing -= hydrogen_out
            backup = max(0, missing)
        rows.append({"hour": hour, "demand": demand, "solar": solar, "wind": wind,
                     "battery_used": battery_out, "hydrogen_used": hydrogen_out,
                     "backup": backup, "spill": wasted, "battery_level": battery,
                     "hydrogen_level": hydrogen, "event": d["event"], "action": action})
    return rows, battery, hydrogen


def tally(rows, plan):
    if not rows:
        return {"coverage": 0, "green": 0, "backup": 0, "demand": 0, "spill": 0, "co2": 0, "points": 0}
    demand = sum(x["demand"] for x in rows)
    backup = sum(x["backup"] for x in rows)
    spill = sum(x["spill"] for x in rows)
    green = max(0, demand - backup)
    coverage = 100 * green / max(demand, 0.0001)
    # The game's objective intentionally rewards serving demand, renewable share,
    # low curtailment, and sensible budget use. This is a game score, not a model KPI.
    budget_spent = sum(plan[k] * PRICES[k] for k in PRICES)
    points = round(max(0, 750 * green / max(demand, .0001)
                       + 170 * (1 - min(spill / max(demand, .0001), 1))
                       + 80 * (1 - budget_spent / START_BUDGET)))
    return {"coverage": coverage, "green": green, "backup": backup, "demand": demand,
            "spill": spill, "co2": backup * 0.7, "points": points}


def number(v, decimals=1):
    s = f"{v:.{decimals}f}"
    return s.replace(".", ",") if lang("DE", "EN") == "DE" else s


st.markdown("""
<style>
.block-container {max-width: 1250px; padding-top: 1rem; padding-bottom: 3rem;}
.challenge-hero {background: linear-gradient(115deg,#123d63,#08746d 65%,#0c9ca2);
    border-radius: 23px; padding: 1.4rem 1.8rem; color: white; margin-bottom: 1.2rem;
    box-shadow:0 12px 30px rgba(0,80,110,.14);}
.challenge-hero h1 {color:white !important; font-size:2.15rem; margin:.25rem 0 .5rem;}
.challenge-hero p {color:#eefcff !important; font-size:1.02rem; margin-bottom:.35rem;}
.challenge-label {text-transform:uppercase; letter-spacing:.12em; font-size:.75rem;
    font-weight:800; color:#b8f2e5;}
.event-tag {background:rgba(24,130,140,.09);border-left:4px solid #15938b;
    border-radius:9px;padding:.75rem 1rem;margin:.35rem 0 1rem;}
div[data-testid="stButton"] > button {border-radius:12px; font-weight:700; min-height:45px;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚡ " + lang("Energie-Challenge", "Energy Challenge"))
    if st.button(lang("← Zur Startseite", "← Back to home"), use_container_width=True):
        st.switch_page("Startseite.py")
    if st.button(lang("🔄 Challenge zurücksetzen", "🔄 Reset challenge"), use_container_width=True):
        st.session_state[KEY] = fresh_state()
        st.rerun()
    st.caption(lang("Deine Sprachauswahl bleibt erhalten.", "Your language selection is preserved."))

st.markdown(
    "<div class='challenge-hero'><div class='challenge-label'>ENERTEC · CITY BUILDER</div>"
    f"<h1>⚡ {lang('Rette die Energiestadt!', 'Power the City!')}</h1>"
    f"<p>{lang('24 Stunden. Ein begrenztes Budget. Strom für alle. Deine Entscheidungen zählen!', '24 hours. A limited budget. Power for everyone. Your decisions matter!')}</p>"
    "</div>", unsafe_allow_html=True)

if game["phase"] == "planning":
    st.subheader("🏗️ " + lang("Mission 1: Baue dein Energiesystem", "Mission 1: Build your energy system"))
    st.write(lang(
        "Die Stadt braucht Tag und Nacht Strom. Baue Solaranlagen und Windräder, "
        "speichere Überschüsse in Batterien oder Wasserstoff und überstehe Wetterüberraschungen. "
        "Bei Strommangel springt ein Diesel-Notkraftwerk ein – das kostet Klimapunkte!",
        "The city needs electricity all day and night. Build solar panels and wind turbines, "
        "store surplus energy in batteries or hydrogen, and survive weather surprises. "
        "A diesel backup generator covers shortages – but costs climate points!"))
    st.caption(lang("Alle Werte sind vereinfachte Spielannahmen, keine realen Anlagenpreise oder Prognosen.",
                    "All values are simplified game assumptions, not real equipment prices or forecasts."))

    scenario = st.selectbox(lang("🌤️ Wähle das Wetter", "🌤️ Choose the weather"),
        options=["sun", "wind", "chaos"],
        format_func=lambda s: {"sun":lang("☀️ Sonnentag", "☀️ Sunny day"),
                                "wind":lang("🌬️ Windtag", "🌬️ Windy day"),
                                "chaos":lang("🌦️ Überraschungsmix (empfohlen)", "🌦️ Surprise mix (recommended)")}[s],
        key="challenge_scenario_select")
    st.markdown("#### " + lang("Dein Baubudget: 120 Münzen 🪙", "Your construction budget: 120 coins 🪙"))
    items = [
        ("solar", "☀️", lang("Solaranlagen", "Solar arrays"), lang("Viel Strom bei Tageslicht", "Strong in daylight")),
        ("wind", "🌬️", lang("Windräder", "Wind turbines"), lang("Auch nachts produktiv", "Generate even at night")),
        ("battery", "🔋", lang("Batteriespeicher", "Battery storage"), lang("Effizient, aber begrenzter Speicher", "Efficient but limited storage")),
        ("hydrogen", "💧", lang("Wasserstoffspeicher", "Hydrogen storage"), lang("Speichert Energie länger, mit Verlusten", "Longer storage, with losses")),
    ]
    col_a, col_b = st.columns(2, gap="large")
    settings = {}
    for i, (key, emoji, title, detail) in enumerate(items):
        with (col_a if i % 2 == 0 else col_b):
            st.markdown(f"**{emoji} {title}** · {PRICES[key]} 🪙")
            st.caption(detail)
            settings[key] = st.slider(title, 0, 10, value={"solar":4,"wind":4,"battery":2,"hydrogen":2}[key],
                                      key=f"challenge_plan_{key}", label_visibility="collapsed")
    cost = sum(PRICES[k] * settings[k] for k in PRICES)
    remaining = START_BUDGET - cost
    c1, c2, c3 = st.columns(3)
    c1.metric(lang("Verplant", "Spent"), f"{cost} 🪙")
    c2.metric(lang("Übrig", "Remaining"), f"{remaining} 🪙")
    c3.metric(lang("Anlagen & Speicher", "Units & storage"), sum(settings.values()))
    st.progress(min(1.0, cost / START_BUDGET))
    if remaining < 0:
        st.error(lang("Budget überschritten! Entferne ein paar Anlagen.", "Over budget! Remove a few units."))
    if settings["solar"] + settings["wind"] == 0:
        st.warning(lang("Du brauchst mindestens eine Solar- oder Windanlage.", "You need at least one solar or wind unit."))
    st.info(lang(
        "💡 **Tipp:** Die Sonne scheint nicht nachts! Eine Mischung aus Solar, Wind und Speicher ist oft cleverer als alles auf eine Karte zu setzen.",
        "💡 **Tip:** The sun does not shine at night! A mix of solar, wind and storage can be smarter than betting on one technology."))
    if st.button(lang("🚀 STADT STARTEN", "🚀 LAUNCH CITY"), type="primary", use_container_width=True,
                 disabled=remaining < 0 or settings["solar"] + settings["wind"] == 0):
        game.update({"phase":"running", "plan": settings.copy(), "scenario":scenario,
                     "rows":[], "round":0, "battery_charge": settings["battery"]*2.4*0.35,
                     "hydrogen_charge": settings["hydrogen"]*4.5*0.25,
                     "saves_left":2, "saves_used":0, "score":0, "last_action":"none"})
        st.rerun()

elif game["phase"] == "running":
    r = game["round"]
    start = r * ROUND_HOURS
    end = start + ROUND_HOURS
    st.subheader(f"🎮 {lang('Mission 2: Halte die Lichter an!', 'Mission 2: Keep the lights on!')}")
    st.progress(r / 6)
    st.caption(lang(f"Runde {r+1} von 6 · {start:02d}:00–{end:02d}:00 Uhr",
                    f"Round {r+1} of 6 · {start:02d}:00–{end:02d}:00"))
    total = tally(game["rows"],game["plan"])
    top = st.columns(4)
    top[0].metric(lang("Grüner Strom", "Green energy share"), f"{number(total['coverage'],0)} %" if game["rows"] else "—")
    top[1].metric("🔋 " + lang("Batterie", "Battery"), f"{number(game['battery_charge'])} MWh")
    top[2].metric("💧 H₂", f"{number(game['hydrogen_charge'])} MWh")
    top[3].metric("🛟 " + lang("Spar-Joker", "Save boosts"), str(game["saves_left"]))

    day = create_day(game["scenario"])
    event_codes = sorted({day[h]["event"] for h in range(start,end)}-{''})
    event_text = {"cloud":lang("☁️ Wolkenfront! Die Solaranlagen liefern zeitweise deutlich weniger.",
                               "☁️ Cloud front! Solar generation drops for a while."),
                  "concert":lang("🎤 Stadtfest! Am Abend steigt der Stromverbrauch.",
                                 "🎤 City festival! Evening electricity demand spikes."),
                  "calm":lang("🍃 Flaute! Der Wind schläft für einige Stunden ein.",
                              "🍃 Wind lull! Wind generation drops for a few hours.")}
    if event_codes:
        for event in event_codes:
            st.warning(event_text[event])
    else:
        st.info(lang("🌈 Wetterbericht: Keine besonderen Ereignisse in dieser Runde.",
                     "🌈 Weather report: No special events this round."))

    st.write(lang("Was ist dein Zug? Entscheide vor dem Start der nächsten vier Stunden:",
                  "What's your move? Decide before the next four hours begin:"))
    choices = ["none"] + (["save"] if game["saves_left"] else [])
    action = st.radio(lang("Deine Aktion", "Your action"), options=choices,
        format_func=lambda x: lang("⚡ Normalbetrieb", "⚡ Normal operation") if x=="none" else
                lang("🛟 Spar-Joker einsetzen: 18 % weniger Bedarf (1 von 2)",
                     "🛟 Use an energy-saving boost: 18% less demand (1 of 2)"),
        key=f"challenge_action_{r}")
    st.caption(lang("Der Spar-Joker steht insgesamt zweimal zur Verfügung. Er reduziert den Bedarf nur in dieser Runde.",
                    "You can use the energy-saving boost twice in total. It reduces demand only for this round."))
    if st.button(lang("▶️ Nächste 4 Stunden simulieren", "▶️ Simulate next 4 hours"),
                 type="primary", use_container_width=True):
        newrows, batt, h2 = simulate_hours(game["plan"],game["scenario"],
            game["battery_charge"],game["hydrogen_charge"], start, action)
        game["rows"].extend(newrows)
        game["battery_charge"] = batt
        game["hydrogen_charge"] = h2
        game["round"] += 1
        game["last_action"] = action
        if action == "save":
            game["saves_left"] -= 1
            game["saves_used"] += 1
        if game["round"] == 6:
            game["phase"] = "results"
        st.rerun()

    if game["rows"]:
        st.divider()
        st.subheader("📊 " + lang("Deine Stadt bisher", "Your city so far"))
        df = pd.DataFrame(game["rows"])
        chart = df.set_index("hour")[["demand", "solar", "wind", "battery_used", "hydrogen_used", "backup"]]
        chart.columns = [lang("Verbrauch", "Demand"), lang("Solar", "Solar"),
                         lang("Wind", "Wind"), lang("Batterie", "Battery"),
                         lang("Wasserstoff", "Hydrogen"), lang("Notstrom", "Backup")]
        st.line_chart(chart)
        st.caption(lang("Leistung in MW · Jede Stunde entspricht einer Stunde Simulation.",
                        "Power in MW · Each timestep represents one hour."))
        if game["last_action"] == "save":
            st.success(lang("💪 Gute Teamarbeit! Eure Sparaktion hat den Bedarf in der letzten Runde gesenkt.",
                            "💪 Nice teamwork! Your saving boost reduced demand in the last round."))

else:
    result = tally(game["rows"],game["plan"])
    score = result["points"]
    if score >= 880:
        medal, rank_de, rank_en = "🏆", "ENERGIE-LEGENDE", "ENERGY LEGEND"
    elif score >= 720:
        medal, rank_de, rank_en = "🥇", "STADTRETTER", "CITY SAVER"
    elif score >= 560:
        medal, rank_de, rank_en = "🥈", "ENERGIE-PROFI", "ENERGY PRO"
    else:
        medal, rank_de, rank_en = "🔧", "NÄCHSTER VERSUCH!", "TRY AGAIN!"
    st.header(f"{medal} {lang('Mission geschafft!', 'Mission completed!')}")
    st.subheader(lang(rank_de,rank_en))
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("⭐ " + lang("Punkte", "Points"),score)
    c2.metric("🌱 " + lang("Grüner Strom", "Green share"),f"{number(result['coverage'])} %")
    c3.metric("🛢️ " + lang("Notstrom", "Backup"),f"{number(result['backup'])} MWh")
    c4.metric("🌍 " + lang("CO₂ aus Notstrom", "Backup CO₂"),f"{number(result['co2'])} t")
    st.progress(min(1.0, score/1000))
    if result["backup"] <= 0.01:
        st.success(lang("🌟 Kein Notstrom nötig – die Stadt wurde komplett durch erneuerbare Energie und Speicher versorgt!",
                        "🌟 No backup needed – the city was powered entirely by renewables and storage!"))
    else:
        st.info(lang("💡 Stromausfälle wurden durch das Diesel-Notkraftwerk verhindert. Probiere andere Anlagenkombinationen, um weniger Notstrom zu brauchen.",
                     "💡 The diesel backup prevented power cuts. Try another mix to reduce reliance on it."))
    st.caption(lang("Spiel-CO₂-Wert: vereinfachter Faktor 0,7 t CO₂ pro MWh Diesel-Notstrom; kein vollständiger Lebenszyklusvergleich.",
                    "Game CO₂ value: simplified 0.7 t CO₂ per MWh of diesel backup; not a full life-cycle comparison."))
    df = pd.DataFrame(game["rows"])
    plot = df.set_index("hour")[["demand","solar","wind","backup"]]
    plot.columns = [lang("Bedarf", "Demand"),"Solar","Wind",lang("Notstrom", "Backup")]
    st.subheader("📉 " + lang("24-Stunden-Analyse", "24-hour analysis"))
    st.line_chart(plot)
    st.markdown("#### " + lang("Deine Auszeichnungen", "Your achievements"))
    if result["coverage"] >= 95:
        st.write(lang("🏅 **Fast fossilfrei:** Mindestens 95 % des Verbrauchs grün gedeckt.",
                      "🏅 **Almost fossil-free:** At least 95% of demand covered by green electricity."))
    if game["saves_used"] > 0:
        st.write(lang("🛟 **Energiespar-Held:** Du hast bewusst Energie gespart.",
                      "🛟 **Energy-saving hero:** You took action to reduce demand."))
    if game["plan"]["solar"] and game["plan"]["wind"] and game["plan"]["battery"] and game["plan"]["hydrogen"]:
        st.write(lang("🧩 **Teamwork:** Alle vier Technologien eingesetzt.",
                      "🧩 **Teamwork:** Used all four technologies."))
    st.write(lang("🔬 **Lernpunkt:** Wasserstoff ist ein Energiespeicher, keine Energiequelle. Beim Umwandeln geht Energie verloren.",
                  "🔬 **Learning point:** Hydrogen stores energy; it is not an energy source. Conversion causes energy losses."))
    if not game.get("recorded", False):
        game["history"].append({"score":score, "coverage":result["coverage"],
                                "scenario":game["scenario"], "time":datetime.now().strftime("%H:%M")})
        game["recorded"] = True
    with st.expander(lang("🏁 Deine bisherigen Versuche (nur in dieser Sitzung)",
                          "🏁 Your previous attempts (this session only)")):
        rankdf = pd.DataFrame(sorted(game["history"],key=lambda x:x["score"], reverse=True))
        st.dataframe(rankdf,hide_index=True,use_container_width=True)
    st.divider()
    st.subheader(lang("Noch eine Runde?", "Play again?"))
    if st.button(lang("🎲 Neues Spiel starten", "🎲 Start a new game"),type="primary",use_container_width=True):
        history = game["history"][:]
        st.session_state[KEY] = fresh_state()
        st.session_state[KEY]["history"] = history
        st.rerun()

with st.expander("🧠 " + lang("Wie funktioniert das Modell?", "How does the model work?")):
    st.write(lang(
        "**Simulation statt echte Netzdaten:** 24 Stunden mit je 1 Stunde Zeitschritt. "
        "Solarstrom hängt von Tageszeit und Wolken ab, Windstrom vom simulierten Wind. "
        "Zuerst wird die aktuelle erneuerbare Erzeugung genutzt. Überschüsse laden zunächst "
        "den Batteriespeicher (90 % Lade- und 90 % Entladewirkungsgrad) und dann den "
        "Wasserstoffspeicher (38 % vereinfachter Strom-zu-Strom-Wirkungsgrad). "
        "Bei Strommangel werden zuerst Batterie und dann Wasserstoff entladen. "
        "Reicht das nicht, erzeugt das Diesel-Notkraftwerk den fehlenden Strom. "
        "Die dargestellten Kapazitäten, Kosten und Punkte sind Spielannahmen.",
        "**Simulation, not real grid data:** 24 hourly time steps. Solar output depends on time "
        "and cloud cover, wind output on simulated weather. Current renewable generation "
        "is used first. Surplus charges the battery (90% charging and 90% discharge efficiency), "
        "then the hydrogen store (simplified 38% electricity-to-electricity efficiency). "
        "If electricity is short, the battery and then hydrogen discharge. Remaining shortages "
        "are met by diesel backup. Capacities, prices and points are game assumptions."))
