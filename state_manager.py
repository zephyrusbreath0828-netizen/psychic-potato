import streamlit as st

def init_state():
    if "state" not in st.session_state:
        st.session_state.state = {
            "characters": [],
            "summary": "開始",
            "history": [],
            "relations": [],
            "endings": [],
            "logs": []
        }

    if "usage" not in st.session_state:
        st.session_state.usage = {
            "count": 0,
            "limit": 20
        }

    return st.session_state.state, st.session_state.usage
