import pandas as pd
import streamlit as st


def main():
    pd.options.mode.copy_on_write = True

    pg = st.navigation(
        {
            "Start": [
                st.Page("page/start/introduction.py", title="Einführung"),
                st.Page("page/start/create_statement.py", title="Kontoauszüge erstellen"),
                st.Page("page/start/upload_data.py", title="Daten hochladen"),
                st.Page("page/start/tax_report_dates.py", title="Abgabezeitpunkte"),
                st.Page("page/start/report.py", title="Auswertung")
            ],
            "Ergebnis": [
                st.Page("page/result/deposits.py", title="Ein- und Auszahlungen"),
                st.Page("page/result/interests.py", title="Zinsen"),
                st.Page("page/result/dividends.py", title="Dividenden"),
                st.Page("page/result/stocks.py", title="Aktiengeschäfte"),
                st.Page("page/result/bonds.py", title="Anleihen"),
                st.Page("page/result/short_options.py", title="Stillhaltergeschäfte"),
                st.Page("page/result/long_options.py", title="Termingeschäfte"),
                st.Page("page/result/foreign_currencies.py", title="Fremdwährungsgewinne"),
                st.Page("page/result/forexes.py", title="Forex-Trades"),
                st.Page("page/result/other_fees.py", title="Sonstige Gebühren"),
                st.Page("page/result/unknown_lines.py", title="Sonstiges")
            ]
        }
    )
    pg.run()
    return


if __name__ == "__main__":
    main()
