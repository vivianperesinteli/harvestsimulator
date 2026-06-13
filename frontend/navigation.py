"""Shared navigation helper for all pages."""

import streamlit as st


def go(page: str) -> None:
    st.session_state.page = page
    if page == "simulation_input":
        st.session_state.processing_done = False
        st.session_state.sim_results = None
    st.rerun()
