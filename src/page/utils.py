import pandas as pd
import streamlit as st

from i18n import format_date, format_currency, COLUMN_NAME, format_number
from report import Report


def render_footer(page_left: str | None, page_right: str | None):
    st.write("")
    st.write("")
    left, right = st.columns([2, 1])
    if page_left:
        left.page_link(page_left, label="Zurück", icon=":material/arrow_back:")
    if page_right:
        right.page_link(page_right, label="Weiter", icon=":material/arrow_forward:")


def ensure_report_is_available() -> Report:
    report = st.session_state.get("report", None)
    if report is None:
        st.switch_page("page/start/upload_data.py")
    return report


def ensure_selected_year() -> int:
    selected_year = st.session_state.get("selected_year", None)
    if selected_year is None:
        st.switch_page("page/start/upload_data.py")
    return int(selected_year)


def display_dataframe(df: pd.DataFrame,
                      date_columns: list[str],
                      currency_columns: dict[str, str],
                      number_columns: list[str] = None):
    background_color = ["background-color: GhostWhite", "background-color: White"]
    if number_columns is None:
        number_columns = []

    def alternate_background(row):
        return [background_color[row["sequence"] % 2]] * len(row)

    formats = ({date_column: lambda x: format_date(x) for date_column in date_columns} |
               {currency_column: lambda x, c=currency: format_currency(x, c) for currency_column, currency in currency_columns.items()} |
               {number_column: lambda x: format_number(x) for number_column in number_columns})
    column_config = ({date_column: st.column_config.DateColumn(COLUMN_NAME[date_column])
                      for date_column in date_columns} |
                     {currency_column: st.column_config.NumberColumn(COLUMN_NAME.get(currency_column, currency_column))
                      for currency_column in currency_columns.keys()} |
                     {number_column: st.column_config.NumberColumn(COLUMN_NAME.get(number_column, number_column))
                      for number_column in number_columns} |
                     {col: COLUMN_NAME[col]
                      for col in df.columns
                      if col in COLUMN_NAME and col not in date_columns+list(currency_columns.keys())+number_columns} |
                     {"sequence": None})
    st.dataframe(df.style.apply(alternate_background, axis=1).format(formats),
                 hide_index=True,
                 column_config=column_config,
                 use_container_width=True)
