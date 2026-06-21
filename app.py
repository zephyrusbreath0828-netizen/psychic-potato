import streamlit as st
import google.generativeai as genai

from state_manager import init_state
from logic import send_message

# API設定
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# state取得
state, usage = init_state()

st.title("ストーリー")

# 履歴
for h in state["history"]:
    with st.chat_message("user"):
        st.write(h["user"])
    with st.chat_message("assistant"):
        st.write(h["ai"])

user_input = st.chat_input("入力")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        output = send_message(model, state, usage, user_input)
        st.write(output)
