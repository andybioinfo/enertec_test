from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from navigation import hide_default_sidebar_nav, h2_sidebar

st.set_page_config(page_title="Wasserstoff – Versuch 1", layout="wide")
hide_default_sidebar_nav()
h2_sidebar()

# Die Abbildung liegt im Ordner img/ des Projekts.
AUFBAU_BILD = Path("img/h2_versuch1_aufbau.png")

st.title("Versuch 1: Zersetzungsspannung und I-U-Kennlinie")
st.write(
    "In diesem Versuch untersucht ihr, wie sich die Spannung am Elektrolyseur "
    "bei unterschiedlichen Stromstärken verändert. Aus euren Messwerten "
    "erstellt ihr die I-U-Kennlinie und bestimmt näherungsweise die Zersetzungsspannung."
)
st.divider()

st.subheader("Aufbau (gilt für alle Wasserstoff-Experimente)")
if AUFBAU_BILD.exists():
    st.image(str(AUFBAU_BILD), caption="Versuchsaufbau mit Elektrolyseur, Messgeräten und Timer", width=650)
else:
    st.info(f"Aufbaubild ergänzen: {AUFBAU_BILD}")

st.markdown("**Einstellung der Digitalmultimeter:**")
st.write("Spannungsmessung: **DC V**")
st.write("Strommessung: **DC A**")
st.divider()

st.subheader("Information")
st.write(
    "Ein Elektrolyseur verwendet elektrischen Strom, um eine chemische Reaktion "
    "herbeizuführen. Bei der Elektrolyse von Wasser wird Wasser in Wasserstoff "
    "und Sauerstoff zerlegt. Dabei entstehen die Gase im Volumenverhältnis 2:1."
)
st.latex(r"2\,H_2O \rightarrow 2\,H_2 + O_2")
st.write(
    "Damit die Reaktion ablaufen kann, muss mindestens eine bestimmte elektrische "
    "Spannung anliegen. Diese wird als **Zersetzungsspannung** bezeichnet. "
    "In diesem Experiment bestimmt ihr sie näherungsweise mithilfe der I-U-Kennlinie "
    "des Elektrolyseurs."
)
st.divider()

st.subheader("Aufgabe")
st.write(
    "Beginnt mit **0 mA** und erhöht den Strom in Schritten von **50 mA** bis "
    "**500 mA**. Messt für jede Stromstärke die zugehörige Spannung und tragt "
    "sie unten in die digitale Tabelle ein. Anschließend könnt ihr eure Messwerte "
    "als I-U-Diagramm zeichnen lassen."
)
st.info(
    "**Hinweis zum ersten Messpunkt (0 mA):** Lest die Spannung erst ab, "
    "wenn sie sich stabilisiert hat und nicht mehr stark ansteigt.\n\n"
    "**Hinweis zu den weiteren Messpunkten:** Messt die Spannung nach jedem "
    "Umstellen möglichst nach der gleichen Zeit, zum Beispiel nach 10 Sekunden. "
    "Die Spannung kann sich mit der Zeit verändern."
)
st.divider()

st.subheader("Digitale Messwerttabelle")
st.caption("Tragt die gemessene Spannung U in mV ein. Leere Felder werden nicht gezeichnet.")

stromwerte = list(range(0, 501, 50))
spannungen = []
spalten = st.columns(4)
for index, strom in enumerate(stromwerte):
    with spalten[index % 4]:
        spannung = st.number_input(
            f"U bei I = {strom} mA (mV)",
            min_value=0.0,
            value=None,
            step=1.0,
            format="%.1f",
            key=f"h1_spannung_{strom}",
            placeholder="Messwert eingeben",
        )
        spannungen.append(spannung)

tabelle = pd.DataFrame({
    "Strom I (mA)": stromwerte,
    "Spannung U (mV)": spannungen,
})
st.dataframe(tabelle.T, use_container_width=True)

if st.button("I-U-Kennlinie zeichnen", type="primary", use_container_width=True):
    st.session_state["h1_diagramm_anzeigen"] = True

if st.session_state.get("h1_diagramm_anzeigen", False):
    messpunkte = [