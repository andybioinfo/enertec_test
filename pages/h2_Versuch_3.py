from pathlib import Path

import pandas as pd
import streamlit as st

from navigation import hide_default_sidebar_nav, h2_sidebar


st.set_page_config(page_title="Wasserstoff – Versuch 3", layout="wide")
hide_default_sidebar_nav()
h2_sidebar()

st.title("Versuch 3: Zugeführte Energie Elektrolyseur")
st.write(
    "In diesem Versuch messt ihr, wie viel elektrische Energie benötigt wird, "
    "um **10 ml Wasserstoff** mit dem Elektrolyseur zu erzeugen."
)
st.divider()

st.subheader("Information")
st.write(
    "In den folgenden Experimenten beschäftigen wir uns mit dem **Wirkungsgrad**. "
    "Der Wirkungsgrad ist der Quotient aus abgegebener Leistung oder Energie "
    "und aufgenommener Leistung oder Energie. In diesem Versuch ermittelt ihr "
    "die Grundlage für die Berechnung des Wirkungsgrades des Elektrolyseurs, "
    "der in **Versuch 5** abschließend bestimmt wird."
)
st.divider()

st.subheader("Aufbau")
aufbau_bild = Path("img/h2_versuch1_aufbau.png")
if aufbau_bild.exists():
    st.image(
        str(aufbau_bild),
        caption="Versuchsaufbau (wie bei Versuch 1)",
        width=650,
    )
else:
    st.info("Verwendet den Versuchsaufbau aus Versuch 1.")
st.write("**Digitalmultimeter Spannung:** DC V")
st.write("**Digitalmultimeter Strom:** DC A")
st.divider()

st.subheader("Aufgabe")
st.write(
    "Betreibt den Stromregler mit einer **konstanten Stromstärke von 400 mA**. "
    "Messt die Zeit, die benötigt wird, um **10 ml H₂** zu erzeugen. "
    "Notiert die gemessene Zeit und die Spannung während des Experiments."
)
st.write(
    "Da die Spannung während des Versuchs ungefähr konstant sein sollte, "
    "empfiehlt es sich, sie mehrmals abzulesen: beispielsweise immer dann, "
    "wenn weitere **2 ml Wasserstoff** erzeugt wurden. "
    "Bildet anschließend den Mittelwert aus euren Spannungsmessungen."
)
st.write(
    "Tragt die Messwerte in die digitale Tabelle ein. "
    "Die elektrische Energie zur Erzeugung von 10 ml Wasserstoff "
    "wird automatisch berechnet."
)
st.info(
    "**Formel:** E = I · U · t  \n\n"
    "Für die Berechnung gilt: Stromstärke I in **A**, "
    "Spannung U in **V**, Zeit t in **s**; Ergebnis E in **J**."
)
st.divider()

st.subheader("Digitale Messwerttabelle")
st.caption(
    "Messt die Spannung bei den angegebenen Wasserstoffvolumina. "
    "Noch nicht gemessene Werte können leer bleiben."
)

VOLUMINA_ML = (0, 2, 4, 6, 8, 10)
STROM_A = 0.4

spannungen = []
spalten = st.columns(3)
for index, volumen in enumerate(VOLUMINA_ML):
    with spalten[index % 3]:
        spannung = st.number_input(
            f"Spannung bei {volumen} ml H₂ (V)",
            min_value=0.0,
            value=None,
            step=0.01,
            format="%.2f",
            placeholder="Messwert eingeben",
            key=f"h2_v3_spannung_{volumen}",
        )
        spannungen.append(spannung)

vorhandene_spannungen = [u for u in spannungen if u is not None]
mittelwert = (
    sum(vorhandene_spannungen) / len(vorhandene_spannungen)
    if vorhandene_spannungen else None
)

tabelle = pd.DataFrame(
    {
        "Volumen H₂ (ml)": [*VOLUMINA_ML, "Mittelwert"],
        "Spannung U (V)": [*spannungen, mittelwert],
    }
)
st.dataframe(tabelle, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Berechnung der zugeführten elektrischen Energie")

zeit_s = st.number_input(
    "Benötigte Zeit für 10 ml H₂ (in Sekunden)",
    min_value=0.0,
    value=None,
    step=1.0,
    format="%.1f",
    placeholder="Gemessene Zeit eingeben",
    key="h2_v3_zeit_s",
)

energie_j = (
    STROM_A * mittelwert * zeit_s
    if mittelwert is not None and zeit_s is not None and zeit_s > 0
    else None
)

col_i, col_u, col_t, col_e = st.columns(4)
col_i.metric("Strom I", "0,4 A")
col_u.metric(
    "Mittlere Spannung U",
    f"{mittelwert:.2f} V".replace(".", ",") if mittelwert is not None else "–",
)
col_t.metric(
    "Zeit t",
    f"{zeit_s:.1f} s".replace(".", ",") if zeit_s is not None else "–",
)
col_e.metric(
    "Energie E",
    f"{energie_j:.2f} J".replace(".", ",") if energie_j is not None else "–",
)

if mittelwert is not None and zeit_s is not None and zeit_s > 0:
    st.success(
        f"E = 0,4 A · {mittelwert:.2f} V · {zeit_s:.1f} s "
        f"= **{energie_j:.2f} J**".replace(".", ",")
    )
    if len(vorhandene_spannungen) < len(VOLUMINA_ML):
        st.warning(
            "Es fehlen noch Spannungsmesswerte. Der angezeigte Mittelwert "
            "und die Energie basieren nur auf den bisher eingegebenen Spannungen."
        )
else:
    st.info(
        "Tragt mindestens einen Spannungswert und die gemessene Zeit ein, "
        "damit die Energie berechnet werden kann. Für das vollständige "
        "Versuchsergebnis sollten alle sechs Spannungswerte vorliegen."
    )

st.markdown("**Ergebnistabelle**")
ergebnis = pd.DataFrame(
    [
        {
            "Stromstärke I (A)": STROM_A,
            "Mittlere Spannung U (V)": mittelwert,
            "Zeit t (s)": zeit_s,
            "Energie E (J)": energie_j,
        }
    ]
)
st.dataframe(ergebnis, hide_index=True, use_container_width=True)

st.divider()
st.subheader("Auswertung")
st.write(
    "Vergleicht die sechs Spannungsmessungen: Ist die Spannung während der "
    "Wasserstofferzeugung tatsächlich annähernd konstant? "
    "Welche Bedeutung hat die mittlere Spannung für die Energieberechnung?"
)
antwort = st.text_area(
    "Eure Beobachtungen (optional)",
    placeholder="Notiert hier eure Beobachtungen ...",
    key="h2_v3_beobachtung",
)
