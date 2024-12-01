import pandas as pd
import streamlit as st

from ibkr_steuerrechner.i18n import format_date, format_currency, COLUMN_NAME


def ensure_report_is_available():
    report = st.session_state.get("report", None)
    if report is None:
        st.switch_page("page/start/upload_data.py")
    return report


def ensure_selected_year():
    selected_year = st.session_state.get("selected_year", None)
    if selected_year is None:
        st.switch_page("page/start/report.py")
    return selected_year


def display_dataframe(df: pd.DataFrame, date_columns: list[str], number_columns: list[str]):
    background_color = ["background-color: White", "background-color: GhostWhite"]

    def alternate_background(row):
        return [background_color[row["sequence"] % 2]] * len(row)

    formats = ({date_column: lambda x: format_date(x) for date_column in date_columns} |
               {number_column: lambda x: format_currency(x) for number_column in number_columns})
    column_config = ({date_column: st.column_config.DateColumn(COLUMN_NAME[date_column])
                      for date_column in date_columns} |
                     {number_column: st.column_config.NumberColumn(COLUMN_NAME[number_column])
                      for number_column in number_columns} |
                     {col: COLUMN_NAME[col]
                      for col in df.columns
                      if col in COLUMN_NAME and col not in date_columns and col not in number_columns} |
                     {"sequence": None})
    st.dataframe(df.style.apply(alternate_background, axis=1).format(formats),
                 hide_index=True,
                 column_config=column_config,
                 use_container_width=True)
