import streamlit as st

from page.utils import ensure_report_is_available, ensure_selected_year


report = ensure_report_is_available()
selected_year = ensure_selected_year()

st.title(f"Zusammenfassung ({selected_year})")
