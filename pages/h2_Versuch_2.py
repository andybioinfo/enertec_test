from pathlib import Path

import pandas as pd
import streamlit as st

from navigation import hide_default_sidebar_nav, h2_sidebar


st.set_page_config(page_title="Wasserstoff – Versuch 2", layout="wide")
hide_default_sidebar_nav()
h2_sidebar()

st.title("Versuch 2: Proportionalitätskonstante")
st.write(
    "In diesem Versuch untersucht ihr, wie viel Wasserstoff ein Elektrolyseur "
    "bei verschiedenen Stromstärken innerhalb von drei Minuten erzeugt. "
    "Aus euren Messwerten berechnet ihr die Proportionalitätskonstante."
)
st.divider()

st.subheader("Information")
st.write(
    "Elektrolyseure werden zur gezielten Herstellung von Wasserstoff verwendet. "
    "Dabei wird der erzeugte Wasserstoff in der Regel nicht direkt verbraucht, "
    "sondern zunächst gespeichert. Nichtsdestotrotz ist eine gesteuerte "
    "Erzeugung eines bestimmten Volumens gewünscht. Dazu ist es notwendig, "
    "die erzeugte Menge an Gas für eine eingespeiste Menge an Energie zu kennen."
)
st.write(
    "Im ersten Schritt betrachten wir dazu vereinfacht die Stromstärke über "
    "der Zeit, um ein Maß für die erzeugte Menge an Wasserstoff zu gewinnen. "
    "Dieses Maß nennen wir **Proportionalitätskonstante**. Sie gibt an, "
    "wie viele Milliliter Wasserstoff pro Minute und pro Ampere "
    "vom Elektrolyseur erzeugt werden. Damit kann die erzeugte Menge "
    "Wasserstoff für verschiedene Zeiten und Stromstärken abgeschätzt werden."
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
    st.info(
        "Verwendet den Versuchsaufbau aus Versuch 1. "
        "Die Abbildung kann unter 'img/h2_versuch1_aufbau.png' ergänzt werden."
    )
st.write("**Digitalmultimeter Strom:** DC A")
st.divider()

st.subheader("Aufgabe")
st.write(
    "Bestimmt für verschiedene Stromstärken die **Volumenänderung des "
    "Wasserstoffs während einer Messdauer von jeweils drei Minuten**. "
    "Notiert das Wasserstoffvolumen zu Beginn und am Ende jeder Messperiode "
    "und berechnet daraus die Volumenänderung (Delta)."
)
st.write(
    "Das Volumen zu Beginn der ersten Messung entspricht dem Volumen "
    "am Ende von Versuch 1, sofern ihr direkt mit diesem Aufbau weitermesst. "
    "Stellt danach nacheinander die vorgegebenen Stromstärken "
    "von **300 mA**, **400 mA** und **500 mA** ein."
)
st.write(
    "Berechnet aus der Volumenänderung zuerst die Menge Wasserstoff "
    "in **ml pro Minute** und daraus die Proportionalitätskonstante "
    "in **ml/(min·A)**."
)
st.info(
    "**Hinweis:** Jede Messung dauert **3 Minuten**. "
    "Lest das Anfangs- und Endvolumen jeweils an derselben Skala ab. "
    "Tragt die gemessenen Volumina in **ml** ein."
)
st.divider()

st.subheader("Digitale Messwerttabelle")
st.caption(
    "Gebt für jede Stromstärke das Start- und Endvolumen ein. "
    "Die weiteren Spalten werden automatisch berechnet. "
    "Nicht gemessene Werte bleiben leer."
)

STROMSTAERKEN_MA = (300, 400, 500)
MESSDAUER_MIN = 3.0

def formatiere_wert(wert, stellen=2):
    if pd.isna(wert):
        return "–"
    return f"{wert:.{stellen}f}".replace(".", ",")

messungen = []
for strom_ma in STROMSTAERKEN_MA:
    st.markdown(f"**Messung bei {strom_ma} mA – Messdauer: 3 Minuten**")
    col_start, col_ende = st.columns(2)
    with col_start:
        start = st.number_input(
            f"Volumen H₂ Start (ml) bei {strom_ma} mA",
            min_value=0.0,
            value=None,
            step=0.1,
            format="%.1f",
            placeholder="Startvolumen eingeben",
            key=f"h2_v2_start_{strom_ma}",
        )
    with col_ende:
        ende = st.number_input(
            f"Volumen H₂ Ende (ml) bei {strom_ma} mA",
            min_value=0.0,
            value=None,
            step=0.1,
            format="%.1f",
            placeholder="Endvolumen eingeben",
            key=f"h2_v2_ende_{strom_ma}",
        )

    if start is not None and ende is not None and ende >= start:
        delta_drei_min = ende - start
        delta_pro_min = delta_drei_min / MESSDAUER_MIN
        konstante = delta_pro_min / (strom_ma / 1000.0)
    else:
        delta_drei_min = None
        delta_pro_min = None
        konstante = None
        if start is not None and ende is not None:
            st.warning(
                f"Bei {strom_ma} mA ist das Endvolumen kleiner als "
                "das Startvolumen. Bitte überprüft eure Eingaben."
            )

    messungen.append(
        {
            "Strom I (mA)": strom_ma,
            "Volumen H₂ Start (ml)": start,
            "Volumen H₂ Ende (ml)": ende,
            "Delta H₂ (ml / 3 min)": delta_drei_min,
            "Delta H₂ (ml / min)": delta_pro_min,
            "Proportionalitätskonstante (ml / (min·A))": konstante,
        }
    )

messwerte = pd.DataFrame(messungen)
konstanten = [
    m["Proportionalitätskonstante (ml / (min·A))"]
    for m in messungen
    if m["Proportionalitätskonstante (ml / (min·A))"] is not None
]
mittelwert = sum(konstanten) / len(konstanten) if konstanten else None

anzeige = pd.DataFrame(
    [
        {
            "Strom I (mA)": str(m["Strom I (mA)"]),
            "Volumen H₂ Start (ml)": formatiere_wert(m["Volumen H₂ Start (ml)"], 1),
            "Volumen H₂ Ende (ml)": formatiere_wert(m["Volumen H₂ Ende (ml)"], 1),
            "Delta H₂ (ml / 3 min)": formatiere_wert(m["Delta H₂ (ml / 3 min)"], 2),
            "Delta H₂ (ml / min)": formatiere_wert(m["Delta H₂ (ml / min)"], 2),
            "Proportionalitätskonstante (ml / (min·A))": formatiere_wert(
                m["Proportionalitätskonstante (ml / (min·A))"], 2
            ),
        }
        for m in messungen
    ]
    + [
        {
            "Strom I (mA)": "Mittelwert",
            "Volumen H₂ Start (ml)": "–",
            "Volumen H₂ Ende (ml)": "–",
            "Delta H₂ (ml / 3 min)": "–",
            "Delta H₂ (ml / min)": "–",
            "Proportionalitätskonstante (ml / (min·A))": formatiere_wert(mittelwert, 2),
        }
    ]
)
st.dataframe(anzeige, hide_index=True, use_container_width=True)

st.divider()
st.subheader("Auswertung")
st.markdown("**1. Volumenänderung über drei Minuten:**")
st.latex(r"\Delta V = V_{\mathrm{Ende}} - V_{\mathrm{Start}}")
st.markdown("**2. Wasserstoffvolumen pro Minute:**")
st.latex(r"\dot V = \frac{\Delta V}{3\,\mathrm{min}}")
st.markdown("**3. Proportionalitätskonstante:**")
st.latex(r"k = \frac{\dot V}{I\ (\mathrm{in\ A})}")
st.caption("Wichtig: 300 mA = 0,3 A; 400 mA = 0,4 A; 500 mA = 0,5 A.")

if mittelwert is not None:
    st.metric(
        "Mittelwert der Proportionalitätskonstante",
        f"{formatiere_wert(mittelwert)} ml/(min·A)",
    )
    if len(konstanten) < len(STROMSTAERKEN_MA):
        st.caption(
            f"Vorläufiger Mittelwert aus {len(konstanten)} von "
            f"{len(STROMSTAERKEN_MA)} Messungen."
        )
else:
    st.info("Tragt Messwerte ein, um die Proportionalitätskonstante zu berechnen.")

if st.button("Ergebnisse anzeigen", type="primary", use_container_width=True):
    st.session_state["h2_v2_ergebnisse"] = True

if st.session_state.get("h2_v2_ergebnisse", False):
    st.subheader("Vergleich eurer Messungen")
    gueltige_messungen = messwerte.dropna(
        subset=["Proportionalitätskonstante (ml / (min·A))"]
    )
    if gueltige_messungen.empty:
        st.info("Für einen Vergleich benötigt ihr mindestens eine vollständige Messung.")
    else:
        diagrammdaten = gueltige_messungen.set_index("Strom I (mA)")[
            ["Proportionalitätskonstante (ml / (min·A))"]
        ]
        st.bar_chart(diagrammdaten, x_label="Stromstärke I (mA)", y_label="k (ml/(min·A))")
        st.write(
            "Vergleicht die berechneten Werte: Eine näherungsweise konstante "
            "Proportionalitätskonstante bedeutet, dass das erzeugte "
            "Wasserstoffvolumen pro Zeit näherungsweise proportional "
            "zur Stromstärke ist."
        )

st.divider()
st.subheader("Fragen zur Auswertung")
st.write("1. Sind die berechneten Proportionalitätskonstanten für alle drei Stromstärken ähnlich groß?")
st.text_area("Eure Antwort zu Frage 1", key="h2_v2_antwort_1")
st.write("2. Welche Gründe könnten Unterschiede zwischen euren Messwerten erklären?")
st.text_area("Eure Antwort zu Frage 2", key="h2_v2_antwort_2")
st.write("3. Wie viel Wasserstoff würde euer Elektrolyseur bei 400 mA in 10 Minuten ungefähr erzeugen?")
st.text_area("Eure Antwort zu Frage 3", key="h2_v2_antwort_3")
st.caption(
    "Die drei Fragen sind als zusätzliche digitale Auswertung ergänzt; "
    "die Vorlage endet bei der Berechnung des Mittelwerts."
)
