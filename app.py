import streamlit as st
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")

model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat()

st.title("チャットアプリ")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("入力してください")

if user_input:
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role":"user","content":user_input})

    with st.spinner("考え中..."):
        response = chat.send_message(user_input)
        answer = response.text

    st.chat_message("assistant").write(answer)
    st.session_state.messages.append({"role":"assistant","content":answer})
