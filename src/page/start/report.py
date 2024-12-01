import streamlit as st

from page.utils import ensure_report_is_available


report = ensure_report_is_available()

st.set_page_config("IBKR Steuerrechner", layout="wide")
st.title("Auswertung")

# Do not use the whole width to display the introduction, use a smaller part to make it better readable
intro, _ = st.columns([2, 1])
intro.write("### Auswertung starten")
intro.write("""Wählen Sie nun das Kalenderjahr aus, für das die Kontoauszüge ausgewertet werden sollen. Sie können
    beliebig oft zwischen den Kalenderjahren wechseln, ohne die Kontoauszügen neu hochladen zu müssen.""")

years = report.get_years()
years_options = ["Bitte wählen"] + years

previous_selected_year = st.session_state.get("selected_year", years_options[0])
try:
    previous_selected_index = years_options.index(str(previous_selected_year))
except ValueError:
    previous_selected_index = 0
selected_year = intro.selectbox("Für welches Kalenderjahr soll die Auswertung erfolgen?", years_options,
                                index=previous_selected_index)
if selected_year != years_options[0]:
    intro.write("""Die Auswertung steht bereit. Sie können mit Weiter zur ersten Seite der Auswertung fortfahren,
    oder wählen links im Menü die gewünschte Auswertung. Sie können jederzeit auf diese Seite zurückkehren und das
    Kalenderjahr wechseln.""")
    st.session_state["selected_year"] = int(selected_year)
else:
    if "selected_year" in st.session_state:
        del st.session_state["selected_year"]

left, right = st.columns([2, 1])
left.page_link("page/start/tax_report_dates.py", label="Zurück", icon=":material/arrow_back:")
if selected_year != years_options[0]:
    right.page_link("page/result/deposits.py", label="Weiter", icon=":material/arrow_forward:")
