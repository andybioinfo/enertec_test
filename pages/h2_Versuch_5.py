"""EnerTec Wasserstoff – Versuch 5: Wirkungsgrade.

Ablage: pages/h2_Versuch_5.py
Navigation: st.switch_page("pages/h2_Versuch_5.py")
"""

import streamlit as st
from navigation import hide_default_sidebar_nav, h2_sidebar

st.set_page_config(page_title="Wasserstoff – Versuch 5", layout="wide")
hide_default_sidebar_nav()
h2_sidebar()

BRENNWERT = 11.71  # J/ml Wasserstoff; Vorgabe aus dem Arbeitsblatt
VOLUMEN = 10.0    # ml Wasserstoff


def format_de(wert, stellen=2):
    """Formatiert Zahlen mit deutschem Dezimalkomma."""
    return f"{wert:.{stellen}f}".replace(".", ",")


def ergebnis_pruefen(bezeichnung, eingabe, richtig, toleranz):
    if eingabe is None:
        st.info(f"{bezeichnung}: Noch keine eigene Lösung eingetragen.")
    elif abs(eingabe - richtig) <= toleranz:
        st.success(f"{bezeichnung}: Richtig!")
    else:
        st.warning(f"{bezeichnung}: Überprüft eure Rechnung noch einmal.")


st.title("Versuch 5: Wirkungsgrade")
st.write(
    "In diesem Versuch berechnet ihr die Wirkungsgrade des Elektrolyseurs, "
    "der Brennstoffzelle und des gesamten Systems. "
    "Tragt zunächst eure Ergebnisse selbst ein. Danach könnt ihr "
    "die berechneten Lösungen zum Vergleichen anzeigen lassen."
)
st.divider()

st.subheader("Information")
st.write(
    "Neben der bisher verwendeten elektrischen Energie gibt es weitere Energieformen. "
    "Dazu zählt die thermische Energie, die über den Elektrolyseur und die Brennstoffzelle "
    "während der elektrochemischen Reaktion abgegeben wird, sowie die chemische Energie, "
    "die durch das Entweichen des Wasserstoffs frei wird. Diese anderen Energieformen "
    "sind der Grund für die realen Wirkungsgrade, die wir im Folgenden für die "
    "einzelnen Teilkomponenten des Systems und das Gesamtsystem bestimmen möchten."
)
st.divider()

st.subheader("Aufgabe")
st.write(
    "Berechnet die **Teilwirkungsgrade des Elektrolyseurs und der Brennstoffzelle**, "
    "indem ihr die chemische Energie des Wasserstoffs mit der bereits berechneten "
    "elektrischen Energie aus Versuch 3 beziehungsweise Versuch 4 vergleicht. "
    "Berechnet zuerst den Brennwert für **10 ml Wasserstoff**. "
    "Tragt eure Ergebnisse in die Tabellen ein."
)
st.info(
    "**Vorgegebener Brennwert für Wasserstoff:** "
    "B = **11,71 J/ml**.\n\n"
    "**Wirkungsgrad:** η = nutzbare abgegebene Energie / zugeführte Energie. "
    "Für die Prozentangabe: η · 100 %."
)

st.divider()
st.subheader("1. Chemische Energie von 10 ml H₂")
st.write("Berechnet zuerst die chemische Energie des Wasserstoffs.")

kopf = st.columns(3)
kopf[0].markdown("**Brennwert B (J/ml)**")
kopf[1].markdown("**Volumen H₂ (ml)**")
kopf[2].markdown("**Brennwert von 10 ml H₂ (J)**")
zeile = st.columns(3)
zeile[0].write(format_de(BRENNWERT))
zeile[1].write(format_de(VOLUMEN, 0))
with zeile[2]:
    energie_chem_eigene = st.number_input(
        "Berechnete chemische Energie (J)",
        min_value=0.0, value=None, step=0.1, format="%.2f",
        key="h2_v5_chem_eigene", placeholder="Selbst berechnen",
        label_visibility="collapsed",
    )

st.divider()
st.subheader("2. Wirkungsgrad des Elektrolyseurs")
st.write(
    "Übertragt die **zugeführte elektrische Energie** für 10 ml H₂ aus "
    "**Versuch 3**. Berechnet daraus den Wirkungsgrad des Elektrolyseurs."
)
energie_zu = st.number_input(
    "Zugeführte elektrische Energie aus Versuch 3 (J)",
    min_value=0.0, value=None, step=1.0, format="%.2f",
    key="h2_v5_ein", placeholder="Energie aus Versuch 3 eingeben",
)
cols = st.columns(2)
with cols[0]:
    eta_el_abs = st.number_input(
        "Wirkungsgrad Elektrolyseur (absolut, z. B. 0,75)",
        min_value=0.0, value=None, step=0.01, format="%.4f",
        key="h2_v5_eta_el_abs",
    )
with cols[1]:
    eta_el_pro = st.number_input(
        "Wirkungsgrad Elektrolyseur (in %)",
        min_value=0.0, value=None, step=0.1, format="%.2f",
        key="h2_v5_eta_el_pro",
    )

st.divider()
st.subheader("3. Wirkungsgrad der Brennstoffzelle")
st.write(
    "Übertragt die **abgegebene elektrische Energie** für 10 ml H₂ aus "
    "**Versuch 4**. Berechnet daraus den Wirkungsgrad der Brennstoffzelle."
)
energie_ab = st.number_input(
    "Abgegebene elektrische Energie aus Versuch 4 (J)",
    min_value=0.0, value=None, step=1.0, format="%.2f",
    key="h2_v5_aus", placeholder="Energie aus Versuch 4 eingeben",
)
cols = st.columns(2)
with cols[0]:
    eta_bz_abs = st.number_input(
        "Wirkungsgrad Brennstoffzelle (absolut, z. B. 0,35)",
        min_value=0.0, value=None, step=0.01, format="%.4f",
        key="h2_v5_eta_bz_abs",
    )
with cols[1]:
    eta_bz_pro = st.number_input(
        "Wirkungsgrad Brennstoffzelle (in %)",
        min_value=0.0, value=None, step=0.1, format="%.2f",
        key="h2_v5_eta_bz_pro",
    )

st.divider()
st.subheader("4. Fragen")
st.write("**Welcher Wirkungsgrad ist höher: der des Elektrolyseurs oder der Brennstoffzelle?**")
st.text_area("Eure Antwort", key="h2_v5_frage_1", placeholder="Schreibt eure Überlegung auf ...")
st.write("**Wie könntet ihr den Gesamtwirkungsgrad des Systems bestimmen?**")
st.text_area("Eure Überlegung", key="h2_v5_frage_2", placeholder="Schreibt eure Überlegung auf ...")

st.divider()
st.subheader("5. Ergebnisse mit der Lösung vergleichen")
st.write(
    "Wenn ihr eure Tabellen ausgefüllt habt, könnt ihr die Musterrechnung anzeigen. "
    "Für Versuch 3 wird **euer eigener Messwert** verwendet. "
    "Für Versuch 4 könnt ihr den Wert aus der Vorlage (**41,0 J**) eingeben."
)

if "h2_v5_loesung_sichtbar" not in st.session_state:
    st.session_state["h2_v5_loesung_sichtbar"] = False

if st.button(
    "Musterlösung ausblenden" if st.session_state["h2_v5_loesung_sichtbar"]
    else "Musterlösung anzeigen und vergleichen",
    type="primary", use_container_width=True,
):
    st.session_state["h2_v5_loesung_sichtbar"] = not st.session_state["h2_v5_loesung_sichtbar"]

if st.session_state["h2_v5_loesung_sichtbar"]:
    energie_chem = BRENNWERT * VOLUMEN
    st.markdown("#### Tabelle 1: Chemische Energie")
    st.write(
        f"**B = {format_de(BRENNWERT)} J/ml**, "
        f"**V = {format_de(VOLUMEN, 0)} ml** → "
        f"**E₍chem₎ = B · V = {format_de(energie_chem)} J**"
    )
    ergebnis_pruefen("Chemische Energie", energie_chem_eigene, energie_chem, 0.11)

    st.markdown("#### Tabelle 2: Elektrolyseur")
    if energie_zu is None or energie_zu <= 0:
        st.info("Tragt eine zugeführte Energie größer als 0 J aus Versuch 3 ein, um den Wirkungsgrad zu vergleichen.")
    else:
        eta_el = energie_chem / energie_zu
        st.latex(r"\eta_{\mathrm{Elektrolyseur}}=\frac{E_{\mathrm{chemisch}}}{E_{\mathrm{zugefuehrt}}}")
        st.write(
            f"η = {format_de(energie_chem)} J / {format_de(energie_zu)} J "
            f"= **{format_de(eta_el, 4)}** = **{format_de(eta_el * 100)} %**"
        )
        ergebnis_pruefen("Elektrolyseur (absolut)", eta_el_abs, eta_el, 0.005)
        ergebnis_pruefen("Elektrolyseur (prozentual)", eta_el_pro, eta_el * 100, 0.11)
        if eta_el > 1:
            st.warning("Der berechnete Wirkungsgrad liegt über 100 %. Prüft die Messwerte und Einheiten aus Versuch 3.")

    st.markdown("#### Tabelle 3: Brennstoffzelle")
    if energie_ab is None:
        st.info("Tragt die abgegebene Energie aus Versuch 4 ein, um den Wirkungsgrad zu vergleichen.")
    else:
        eta_bz = energie_ab / energie_chem
        st.latex(r"\eta_{\mathrm{Brennstoffzelle}}=\frac{E_{\mathrm{abgegeben}}}{E_{\mathrm{chemisch}}}")
        st.write(
            f"η = {format_de(energie_ab)} J / {format_de(energie_chem)} J "
            f"= **{format_de(eta_bz, 4)}** = **{format_de(eta_bz * 100)} %**"
        )
        ergebnis_pruefen("Brennstoffzelle (absolut)", eta_bz_abs, eta_bz, 0.005)
        ergebnis_pruefen("Brennstoffzelle (prozentual)", eta_bz_pro, eta_bz * 100, 0.11)
        if eta_bz > 1:
            st.warning("Der berechnete Wirkungsgrad liegt über 100 %. Prüft die Energie aus Versuch 4.")

    st.markdown("#### Fragen und Gesamtwirkungsgrad")
    st.write(
        "Der höhere Teilwirkungsgrad hängt von euren Messwerten ab. "
        "Den Gesamtwirkungsgrad ermittelt ihr durch Multiplikation "
        "der beiden Teilwirkungsgrade oder direkt aus dem Verhältnis "
        "von abgegebener zu zugeführter elektrischer Energie."
    )
    st.latex(
        r"\eta_{\mathrm{gesamt}}=\eta_{\mathrm{Elektrolyseur}}\cdot"
        r"\eta_{\mathrm{Brennstoffzelle}}="
        r"\frac{E_{\mathrm{abgegeben}}}{E_{\mathrm{zugefuehrt}}}"
    )
    if energie_zu is not None and energie_zu > 0 and energie_ab is not None:
        eta_gesamt = energie_ab / energie_zu
        st.success(f"Gesamtwirkungsgrad: **{format_de(eta_gesamt * 100)} %**")

st.divider()
st.caption("EnerTec Workshop · Wasserstoff · Versuch 5")
