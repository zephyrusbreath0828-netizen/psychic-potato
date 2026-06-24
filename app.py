import streamlit as st
import google.generativeai as genai

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")

st.title("テスト")

user_input = st.chat_input("入力してください")

if user_input:
    with st.spinner("考え中..."):
        response = model.generate_content(user_input)
        st.write(response.text)
