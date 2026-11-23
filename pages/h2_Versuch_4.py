from pathlib import Path

import pandas as pd
import streamlit as st

from navigation import hide_default_sidebar_nav, h2_sidebar


st.set_page_config(page_title="Wasserstoff – Versuch 4", layout="wide")
hide_default_sidebar_nav()
h2_sidebar()

st.title("Versuch 4: Abgegebene Energie Brennstoffzelle")
st.write(
    "In diesem Versuch berechnet ihr die elektrische Energie, die eine "
    "Brennstoffzelle bei der Nutzung von Wasserstoff abgibt. "
    "Füllt zunächst die Tabellen selbst aus und vergleicht eure Antworten "
    "danach mit der Musterlösung."
)
st.divider()

st.subheader("Information")
st.write(
    "Eine Brennstoffzelle ist ein technisches Gerät, in dem chemische "
    "Reaktionsenergie in Form elektrischer Energie freigesetzt wird. "
    "Dabei wird ein Brennstoff durch ein Oxidationsmittel oxidiert. "
    "In unserem Fall ist Wasserstoff der Brennstoff und Sauerstoff das "
    "Oxidationsmittel. In diesem Experiment ermittelt ihr die Grundlage "
    "für die Berechnung des Wirkungsgrades der Brennstoffzelle, "
    "der in Versuch 6 bestimmt wird."
)
st.divider()

st.subheader("Aufgabe")
st.write(
    "Experiment 4 sorgt häufig für Probleme. Deshalb sind die Messwerte "
    "in der Versuchsvorlage bereits vorgegeben. Hier könnt ihr sie zuerst "
    "**selbst eintragen**, die Mittelwerte bestimmen und anschließend "
    "die abgegebene elektrische Energie berechnen. "
    "Die Musterlösung wird erst angezeigt, wenn ihr sie aufruft."
)
st.info(
    "**Formel:** E = I · U · t  \n\n"
    "Stromstärke **I** in A, Spannung **U** in V, Zeit **t** in s, "
    "Energie **E** in J.  \n\n"
    "Für **10 ml H₂** wird in dieser Aufgabe die berechnete Energie "
    "für **5 ml H₂** verdoppelt."
)
st.divider()

st.subheader("1. Messwerttabelle ausfüllen")
st.write(
    "Tragt zunächst die sechs Spannungs- und Stromwerte für die "
    "Wasserstoffvolumina von **0 bis 5 ml** ein. "
    "Berechnet anschließend die beiden Mittelwerte."
)

volumina = (0, 1, 2, 3, 4, 5)
loesung_spannung = (0.82, 0.83, 0.81, 0.82, 0.81, 0.83)
loesung_strom = (0.0621, 0.0623, 0.0616, 0.0630, 0.0627, 0.0625)

spaltenkopf = st.columns([1.1, 1.5, 1.6])
spaltenkopf[0].markdown("**Volumen H₂ (ml)**")
spaltenkopf[1].markdown("**Spannung U (V)**")
spaltenkopf[2].markdown("**Stromstärke I (A)**")

messungen_u = []
messungen_i = []
for volumen in volumina:
    spalten = st.columns([1.1, 1.5, 1.6], vertical_alignment="center")
    spalten[0].write(f"**{volumen}**")
    with spalten[1]:
        u = st.number_input(
            f"Spannung bei {volumen} ml (V)",
            min_value=0.0,
            value=None,
            step=0.01,
            format="%.2f",
            key=f"h2_v4_u_{volumen}",
            placeholder="U eingeben",
            label_visibility="collapsed",
        )
    with spalten[2]:
        i = st.number_input(
            f"Strom bei {volumen} ml (A)",
            min_value=0.0,
            value=None,
            step=0.0001,
            format="%.4f",
            key=f"h2_v4_i_{volumen}",
            placeholder="I eingeben",
            label_visibility="collapsed",
        )
    messungen_u.append(u)
    messungen_i.append(i)

st.markdown("**Eure berechneten Mittelwerte:**")
col_u, col_i = st.columns(2)
with col_u:
    mittel_u = st.number_input(
        "Mittlere Spannung U (V)",
        min_value=0.0,
        value=None,
        step=0.01,
        format="%.2f",
        placeholder="Mittelwert berechnen",
        key="h2_v4_mittel_u",
    )
with col_i:
    mittel_i = st.number_input(
        "Mittlere Stromstärke I (A)",
        min_value=0.0,
        value=None,
        step=0.0001,
        format="%.4f",
        placeholder="Mittelwert berechnen",
        key="h2_v4_mittel_i",
    )

st.divider()
st.subheader("2. Energie berechnen")
st.write(
    "Übernehmt eure Mittelwerte und verwendet die vorgegebene "
    "**Zeit von 400 s**, um die Energie für 5 ml H₂ zu berechnen. "
    "Berechnet danach die Energie für 10 ml H₂."
)

col1, col2, col3 = st.columns(3)
with col1:
    rechnung_i = st.number_input(
        "Stromstärke I (A)", min_value=0.0, value=None,
        step=0.0001, format="%.4f", key="h2_v4_rechnung_i",
        placeholder="Mittelwert eintragen",
    )
with col2:
    rechnung_u = st.number_input(
        "Spannung U (V)", min_value=0.0, value=None,
        step=0.01, format="%.2f", key="h2_v4_rechnung_u",
        placeholder="Mittelwert eintragen",
    )
with col3:
    st.metric("Zeit t", "400 s")

col4, col5 = st.columns(2)
with col4:
    energie_5 = st.number_input(
        "Energie E für 5 ml H₂ (J)", min_value=0.0,
        value=None, step=0.1, format="%.1f",
        key="h2_v4_energie_5", placeholder="Selbst ausrechnen",
    )
with col5:
    energie_10 = st.number_input(
        "Energie E für 10 ml H₂ (J)", min_value=0.0,
        value=None, step=0.1, format="%.1f",
        key="h2_v4_energie_10", placeholder="Selbst ausrechnen",
    )

st.divider()
st.subheader("3. Mit der Musterlösung vergleichen")
st.write(
    "Wenn ihr eure Tabellen ausgefüllt habt, könnt ihr die Musterlösung "
    "einblenden und eure Ergebnisse vergleichen."
)

if "h2_v4_loesung_sichtbar" not in st.session_state:
    st.session_state["h2_v4_loesung_sichtbar"] = False

if st.button(
    "Musterlösung ausblenden" if st.session_state["h2_v4_loesung_sichtbar"]
    else "Musterlösung anzeigen",
    type="primary",
    key="h2_v4_loesung_toggle",
):
    st.session_state["h2_v4_loesung_sichtbar"] = not st.session_state["h2_v4_loesung_sichtbar"]

if st.session_state["h2_v4_loesung_sichtbar"]:
    st.markdown("#### Musterlösung: Messwerttabelle")
    loesung_tabelle = pd.DataFrame({
        "Volumen H₂ (ml)": [*volumina, "Mittelwert"],
        "Spannung U (V)": [*[f"{u:.2f}".replace(".", ",") for u in loesung_spannung], "0,82"],
        "Stromstärke I (A)": [*[f"{i:.4f}".replace(".", ",") for i in loesung_strom], "0,0624"],
    })
    st.dataframe(loesung_tabelle, use_container_width=True, hide_index=True)

    st.markdown("#### Musterlösung: Energieberechnung")
    st.latex(r"E_{5\,\mathrm{ml}} = 0{,}0624\,\mathrm{A}\cdot 0{,}82\,\mathrm{V}\cdot 400\,\mathrm{s} \approx 20{,}5\,\mathrm{J}")
    st.latex(r"E_{10\,\mathrm{ml}} = 2 \cdot 20{,}5\,\mathrm{J} = 41{,}0\,\mathrm{J}")
    st.caption("Die Musterlösung verwendet gerundete Mittelwerte wie in der Versuchsvorlage.")

    st.markdown("#### Vergleich eurer Ergebnisse")
    vergleich = [
        ("Mittlere Spannung", mittel_u, 0.82, 0.005, "V"),
        ("Mittlere Stromstärke", mittel_i, 0.0624, 0.00005, "A"),
        ("Stromstärke in der Rechnung", rechnung_i, 0.0624, 0.00005, "A"),
        ("Spannung in der Rechnung", rechnung_u, 0.82, 0.005, "V"),
        ("Energie für 5 ml", energie_5, 20.5, 0.05, "J"),
        ("Energie für 10 ml", energie_10, 41.0, 0.05, "J"),
    ]
    for name, eingabe, soll, toleranz, einheit in vergleich:
        if eingabe is None:
            st.write(f"**{name}:** Noch nicht eingetragen.")
        elif abs(eingabe - soll) <= toleranz + 1e-10:
            st.success(f"{name}: Stimmt mit der Musterlösung überein ({soll:g} {einheit}).")
        else:
            st.warning(f"{name}: Noch einmal prüfen (Musterlösung: {soll:g} {einheit}).")

    st.write("**Denkt daran:** Kleine Rundungsabweichungen sind je nach Rechenweg möglich.")

st.divider()
st.subheader("Frage zur Auswertung")
st.write(
    "Warum ist die abgegebene elektrische Energie der Brennstoffzelle "
    "für die spätere Berechnung des Wirkungsgrades wichtig?"
)
st.text_area("Eure Überlegungen", key="h2_v4_antwort", placeholder="Schreibt hier eure Antwort ...")
