import pandas as pd
import streamlit as st


def main():
    pd.options.mode.copy_on_write = True
    st.set_page_config("IBKR Steuerrechner", layout="wide")

    start_pages = [
        st.Page("page/start/introduction.py", title="Einführung"),
        st.Page("page/start/create_statement.py", title="Kontoauszüge erstellen"),
        st.Page("page/start/upload_data.py", title="Daten hochladen")
    ]
    result_pages = [
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
    pg = st.navigation(start_pages + result_pages, position="hidden")

    with st.sidebar:
        st.header("Start")
        for page in start_pages:
            st.page_link(page)

        report = st.session_state.get("report", None)
        if report is not None:
            years = report.get_years()
            st.divider()
            st.header("Ergebnis")
            st.selectbox("Jahr", years, key="selected_year")
            for page in result_pages:
                st.page_link(page)

    pg.run()


if __name__ == "__main__":
    main()
