import streamlit as st
from navigation import hide_default_sidebar_nav, h2_sidebar

st.set_page_config(page_title="EnerTec Wasserstoff – Multimeter", layout="wide")

hide_default_sidebar_nav()
h2_sidebar()

st.logo('Solar/Logo_EnerTec_ohne_Hintergrund.png')

col1, col2, col3 = st.columns(3)
with col1:
    st.image('Solar/Logo_Stiftung_ohne_Hintergrund.png', width=250)
with col2:
    st.image('Solar/Logo_EnerTec_ohne_Hintergrund.png', width=250)
with col3:
    st.image('Solar/Logo_AES_ohne_Hintergrund.png', width=250)

st.title('Einstellung Multimeter – Wasserstoff')

st.write(
    'Bei den Wasserstoffexperimenten messt ihr die elektrische Spannung und die '
    'Stromstärke am Elektrolyseur beziehungsweise an der Brennstoffzelle. '
    'Da die Einstellung der Multimeter immer wieder zu Problemen führen kann, '
    'findet ihr hier die Einstellmöglichkeiten für die beiden Gerätetypen '
    '„Schwarz“ und „Rot“. Die Bilder sind dieselben wie im Solar-Workshop.'
)

st.subheader('Worauf müsst ihr achten?')
st.markdown('''
1. **Richtiges Multimeter wählen:** Verwendet die Anleitung für euer schwarzes oder rotes Gerät.
2. **Messbuchsen prüfen:** Das schwarze Kabel gehört in **COM**. Das rote Kabel kommt in die passende Buchse für Spannung beziehungsweise Stromstärke.
3. **Richtige Polung beachten:** Achtet beim Anschließen auf Plus und Minus. Ist die Polung vertauscht, kann ein negatives Vorzeichen angezeigt werden.
4. **Messart und Messbereich einstellen:** Für die Wasserstoffversuche benötigt ihr **Gleichspannung (DC V)** und **Gleichstrom (DC A)**. Wählt einen geeigneten Messbereich und überschreitet die zulässigen Werte des Geräts nicht.
''')

st.warning(
    '**Wichtig:** Spannung wird **parallel** zum zu untersuchenden Bauteil gemessen, '
    'Stromstärke **in Reihe**. Schließt ein auf Strommessung eingestelltes Multimeter '
    'niemals direkt parallel an eine Spannungsquelle an – dadurch kann ein Kurzschluss entstehen. '
    'Steckt Kabel nur bei ausgeschaltetem beziehungsweise stromlosem Aufbau um und fragt bei Unsicherheit die Betreuer.'
)

st.divider()
st.subheader('Welche Einstellungen benötigt ihr im Wasserstoff-Workshop?')
st.write(
    '**Versuch 1 – I-U-Kennlinie:** Ihr messt die Spannung am Elektrolyseur und die '
    'Stromstärke im Stromkreis. Die Stromwerte reichen laut Versuchsanleitung von '
    '0 bis 500 mA. Achtet darauf, dass der eingestellte Messbereich diesen Wert abdeckt.'
)
st.write(
    '**Versuch 2 – Proportionalitätskonstante:** Die Stromstärke wird auf 300, '
    '400 beziehungsweise 500 mA eingestellt. Prüft die Anzeige und die Einheit am Multimeter.'
)
st.write(
    '**Versuch 3 – Zugeführte Energie:** Die Stromstärke beträgt 400 mA. '
    'Für die Energieberechnung messt ihr zusätzlich die Spannung in Volt.'
)
st.write(
    '**Versuch 4 – Abgegebene Energie:** An der Brennstoffzelle betrachtet ihr '
    'Spannung und Stromstärke; die Musterwerte in der Anleitung sind in Volt und Ampere angegeben.'
)
st.write(
    '**Versuch 5 – Wirkungsgrade:** Ihr verwendet die zuvor ermittelten '
    'Energiewerte. Achtet besonders auf die Umrechnung von mA in A und mV in V.'
)

with st.expander('Einheiten kurz erklärt'):
    st.markdown('''
    - **1000 mA = 1 A** → zum Beispiel **400 mA = 0,400 A**.
    - **1000 mV = 1 V** → zum Beispiel **1600 mV = 1,6 V**.
    - Für die Formel **E = U · I · t** setzt ihr **U in V**, **I in A** und **t in s** ein. Das Ergebnis ist die Energie **E in Joule (J)**.
    ''')

st.info(
    'Die passenden Buchsen und Drehreglerstellungen unterscheiden sich je nach '
    'Multimeter. Orientiert euch an den folgenden Bildern und lasst die Einstellung '
    'im Zweifel von einem Betreuer kontrollieren.'
)

st.divider()
st.subheader('Multimeter Schwarz')

for titel, bild, hinweis in [
    ('Schwarz 2000mV', 'Solar/schwarz_2000mV.png', 'Gleichspannung im Millivoltbereich. Nur verwenden, wenn der erwartete Messwert innerhalb dieses Bereichs liegt.'),
    ('Schwarz 20V', 'Solar/schwarz_20V.png', 'Gleichspannung in Volt. Für Spannungen oberhalb von 2000 mV ist dieser Bereich häufig geeigneter.'),
    ('Schwarz 2000mA', 'Solar/schwarz_2000mA.png', 'Gleichstrom im Milliamperebereich. Bei 300–500 mA muss die entsprechende Buchse laut Gerätebeschriftung geeignet sein.'),
    ('Schwarz 10A', 'Solar/schwarz_10A.png', 'Gleichstrom im Amperebereich. Beachtet dafür die passende 10-A-Buchse und die Gerätegrenzen.'),
]:
    st.markdown(f'#### {titel}')
    st.image(bild, width=500)
    st.caption(hinweis)
    st.divider()

st.subheader('Multimeter Rot')

for titel, bild, hinweis in [
    ('Rot mV', 'Solar/rot_mV.png', 'Gleichspannung im Millivoltbereich; prüft, ob der Messwert im zulässigen Bereich liegt.'),
    ('Rot V', 'Solar/rot_V.png', 'Gleichspannung in Volt; für die Spannung des Elektrolyseurs beziehungsweise der Brennstoffzelle.'),
    ('Rot mA', 'Solar/rot_mA.png', 'Gleichstrom im Milliamperebereich. Wichtig: Dieser Eingang kann je nach Gerät geringer abgesichert sein als 500 mA. Vor dem Messen Gerätebeschriftung prüfen!'),
    ('Rot A', 'Solar/rot_A.png', 'Gleichstrom im Amperebereich; verwendet die dazugehörige Strombuchse und achtet auf die maximal zulässige Stromstärke.'),
]:
    st.markdown(f'#### {titel}')
    st.image(bild, width=500)
    st.caption(hinweis)
    st.divider()

st.subheader('Häufige Fehler')
st.markdown('''
- **Anzeige bleibt bei 0:** Prüft zunächst den Stromkreis, die Verbindungskabel und die eingestellte Messart.
- **Anzeige zeigt „OL“ oder „1“:** Der Messbereich könnte überschritten sein. Messung unterbrechen und einen geeigneten Bereich wählen.
- **Negatives Vorzeichen:** Prüft, ob Plus und Minus vertauscht sind.
- **Unplausible Stromwerte:** Prüft, ob die richtige Strombuchse und der passende Messbereich eingestellt sind. Eine durchgebrannte Gerätesicherung kann ebenfalls die Ursache sein.
''')

st.warning('Falls etwas nicht funktioniert: Nicht durch Ausprobieren beliebig umstecken. Fragt die Betreuer vor Ort.')
