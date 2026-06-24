import streamlit as st
import google.generativeai as genai

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")

st.title("動作確認")

user_input = st.text_input("入力")

if user_input:
    response = model.generate_content(user_input)
    st.write(response.text)
