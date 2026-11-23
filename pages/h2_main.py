import streamlit as st
from pathlib import Path
from navigation import hide_default_sidebar_nav, h2_sidebar

st.set_page_config(page_title="EnerTec – Wasserstoff", layout="wide")

hide_default_sidebar_nav()
h2_sidebar()

# Logo-Pfade aus dem bestehenden Projekt.
LOGO_STIFTUNG = "Solar/Logo_Stiftung_ohne_Hintergrund.png"
LOGO_ENERTEC = "Solar/Logo_EnerTec_ohne_Hintergrund.png"
LOGO_AES = "Solar/Logo_AES_ohne_Hintergrund.png"

if Path(LOGO_ENERTEC).is_file():
    st.logo(LOGO_ENERTEC)

col1, col2, col3 = st.columns(3)
for spalte, bild, beschreibung in [
    (col1, LOGO_STIFTUNG, "Stiftung"),
    (col2, LOGO_ENERTEC, "EnerTec"),
    (col3, LOGO_AES, "Lehrstuhl AES"),
]:
    with spalte:
        if Path(bild).is_file():
            st.image(bild, width=250)
        else:
            st.caption(f"Logo {beschreibung} nicht gefunden: {bild}")

st.title("Übersicht – Wasserstoffexperimente")

st.subheader("Bitte lesen!")
st.write("Herzlich willkommen beim EnerTec Workshop!")
st.write(
    "Ihr befindet euch auf der Startseite des Wasserstoff-Workshops. "
    "Hier lernt ihr, wie mithilfe von elektrischem Strom Wasserstoff erzeugt wird, "
    "wie eine Brennstoffzelle daraus wieder elektrische Energie gewinnt und "
    "welche Energieverluste dabei entstehen."
)
st.write(
    "Diese Website ist interaktiv aufgebaut. Über die Seitenleiste links könnt ihr "
    "zwischen den Versuchen und den Zusatzinformationen wechseln. "
    "Weiter unten findet ihr eine kurze Beschreibung aller fünf Versuche. "
    "Mit den Schaltflächen gelangt ihr direkt zu den jeweiligen Experimenten."
)
st.write(
    "Auf der Seite **Aufbau Versuchskoffer** findet ihr zusätzliche Hilfe zum Versuchsaufbau. "
    "Auch auf den einzelnen Versuchsseiten sind Aufbauhinweise vorhanden. "
    "Bei Fragen helfen euch die Betreuer vor Ort gerne weiter. Viel Spaß beim Experimentieren!"
)

st.info(
    "**Wichtig:** Arbeitet mit den elektrischen Geräten und dem Wasserstoff-Versuchskoffer "
    "nur nach Einweisung durch eure Betreuer. Beachtet die Hinweise zum Versuchsaufbau."
)

st.divider()
st.subheader("Übersicht der Versuche")
st.write("Die Versuche bauen inhaltlich aufeinander auf. Ihr könnt sie über die Buttons direkt öffnen.")

VERSUCHE = [
    (
        "Versuch 1: Zersetzungsspannung und I-U-Kennlinie",
        "Ihr messt die Spannung am Elektrolyseur bei Stromstärken von 0 bis 500 mA. "
        "Aus euren Messwerten erstellt ihr eine I-U-Kennlinie und bestimmt näherungsweise "
        "die Zersetzungsspannung.",
        "pages/h2_Versuch_1.py",
    ),
    (
        "Versuch 2: Proportionalitätskonstante",
        "Ihr untersucht, wie viel Wasserstoff bei verschiedenen Stromstärken in jeweils "
        "drei Minuten entsteht. Aus der Volumenänderung berechnet ihr eine "
        "Proportionalitätskonstante.",
        "pages/h2_Versuch_2.py",
    ),
    (
        "Versuch 3: Zugeführte Energie des Elektrolyseurs",
        "Ihr erzeugt bei einer konstanten Stromstärke von 400 mA insgesamt 10 ml Wasserstoff. "
        "Dazu messt ihr die benötigte Zeit und Spannung und berechnet die zugeführte "
        "elektrische Energie.",
        "pages/h2_Versuch_3.py",
    ),
    (
        "Versuch 4: Abgegebene Energie der Brennstoffzelle",
        "Anhand vorgegebener Spannungs- und Stromwerte berechnet ihr, wie viel "
        "elektrische Energie die Brennstoffzelle abgibt. Danach könnt ihr eure "
        "Ergebnisse mit einer Musterlösung vergleichen.",
        "pages/h2_Versuch_4.py",
    ),
    (
        "Versuch 5: Wirkungsgrade",
        "Ihr vergleicht die elektrische Energie aus den Versuchen 3 und 4 mit dem "
        "Energieinhalt des Wasserstoffs. So bestimmt ihr die Wirkungsgrade von "
        "Elektrolyseur, Brennstoffzelle und Gesamtsystem.",
        "pages/h2_Versuch_5.py",
    ),
]

for nummer, (titel, beschreibung, seite) in enumerate(VERSUCHE, start=1):
    st.markdown(f"### {titel}")
    st.write(beschreibung)
    if st.button(f"Zu Versuch {nummer}", key=f"h2_uebersicht_versuch_{nummer}"):
        st.switch_page(seite)
    st.divider()

st.subheader("Zusatzinformationen")
st.write(
    "Weitere Erklärungen, Aufbauhilfen und Videos findet ihr über die Seitenleiste links. "
    "Wenn ihr bei der Durchführung nicht weiterkommt, fragt eure Betreuer."
)

if st.button("← Zurück zur Startseite", key="h2_uebersicht_startseite"):
    st.switch_page("Startseite.py")






