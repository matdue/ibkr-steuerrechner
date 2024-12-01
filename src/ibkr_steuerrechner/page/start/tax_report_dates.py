import datetime
import tomllib

import streamlit as st

from ibkr_steuerrechner.page.utils import ensure_report_is_available


report = ensure_report_is_available()

st.set_page_config("IBKR Steuerrechner", layout="wide")
st.title("Abgabezeitpunkte der Steuererklärung")

# Do not use the whole width to display the introduction, use a smaller part to make it better readable
intro, _ = st.columns([2, 1])
intro.write("### Abgabezeitpunkte angeben")
# Prämien aus Stillhaltergeschäften können mit den Kosten, die durch Glattstellungsgeschäfte entstehen, verrechnet werden.
# Das geht auch dann, wenn die Glattstellung im nachfolgenden Jahr stattfindet. Auf diese Weise können die Einkünfte
# im ersten Jahr reduziert werden, was eine geringere Steuer zur Folge hat.
# Stillhaltergeschäfte, die über den Jahreswechsel gehalten und erst im Folgejahr glattgestellt werden,
# können so abgerechnet werden, dass die Kosten für die Glattstellung mit den erzielten Prämien im gleichen Jahr verrechnet werden.
#
intro.write("""Prämien aus Stillhaltergeschäften können mit den Kosten, die durch Glattstellungsgeschäfte entstehen, 
    verrechnet werden. Das geht auch dann, wenn die Glattstellung erst im nachfolgenden Jahr erfolgt. Auf diese Weise 
    können die Einkünfte im ersten Jahr reduziert werden, was eine geringere Steuer zur Folge hat
    (vgl. [BFH-Urteil vom 02. August 2022, VIII R 27/21)](https://www.bundesfinanzhof.de/de/entscheidung/entscheidungen-online/detail/STRE202210176/)).""")
intro.write("""Damit die Verrechnung korrekt erfolgt, wählen Sie unten für jedes Kalenderjahr den Stichtag aus, bis zu 
    dem Glattstellungen in das Vorjahr übertragen werden. In den meisten Fällen dürfte das das Datum der Abgabe Ihrer 
    Steuererklärung sein.""")
intro.write("""Alle übrigen, d.h. späteren, Glattstellungen werden in dem Kalenderjahr berücksichtigt, in dem sie 
    angefallen sind.""")

options = ["Im Jahr der Prämienerzielung", "Im Jahr der Glattstellung"]
taxation_of_glattstellung = intro.radio(
    "Versteuerung von Glattstellungsgeschäften",
    options,
    captions=[
        "Glattstellungen sollen im Jahr der Prämienerzielung versteuert werden",
        "Glattstellungen sollen im Jahr der Entstehung versteuert werden"
    ]
)
if taxation_of_glattstellung == options[0]:
    years = report.get_years()
    cut_off_dates = st.session_state.get("cut_off_dates", None)
    if cut_off_dates is None:
        cut_off_dates = {year: datetime.date(int(year) + 1, 5, 1) for year in years}
    intro.write("Haben Sie die Daten früher schon einmal erfasst und gespeichert? Dann können Sie sie hier wieder "
                "hochladen, nachdem Sie den nachfolgenden Block aufgeklappt haben.")
    with intro.expander("Daten hochladen"):
        uploaded_config = st.file_uploader("Abgabezeitpunkte hochladen", "toml")
        if uploaded_config is not None:
            config = tomllib.loads(uploaded_config.getvalue().decode("utf-8"))
            loaded_cut_off_dates = config.get("cut-off-dates", {"year": {}}).get("year", None)
            cut_off_dates = cut_off_dates | loaded_cut_off_dates
    for year in years:
        cut_off_dates[year] = intro.date_input(
            year,
            cut_off_dates[year],
            min_value = datetime.date(int(year) + 1, 1, 1),
            format = "DD.MM.YYYY"
        )
    st.session_state["cut_off_dates"] = cut_off_dates

    intro.write("Die hier eingetragenen Daten können Sie für zukünftige Auswertungen speichern.")
    download_data = ("[cut-off-dates]\n" +
                     "".join([f"year.{year} = {date}\n" for year, date in cut_off_dates.items()]))
    intro.download_button("Abgabezeitpunkte herunterladen",
                          download_data,
                          "ibkr-steuerrechner.toml",
                          "application/octet-stream")

left, right = st.columns([2, 1])
left.page_link("page/start/upload_data.py", label="Zurück", icon=":material/arrow_back:")
if st.session_state.get("report", None) is not None:
    right.page_link("page/start/report.py", label="Weiter", icon=":material/arrow_forward:")
