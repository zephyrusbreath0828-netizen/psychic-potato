import streamlit as st
import google.generativeai as genai
import re

# =========================
# 初期設定
# =========================
st.set_page_config(page_title="AI Story App", layout="wide")

genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# state（記憶）
# =========================
if "state" not in st.session_state:
    st.session_state.state = {
        "characters": [],
        "summary": "開始",
        "history": [],
        "relations": [],
        "endings": []
    }

state = st.session_state.state

# =========================
# プロンプト生成
# =========================
def build_prompt(user_input):

    char_text = "\n".join([
        f"{c['name']}：{c['personality']}"
        for c in state["characters"]
    ])

    return f"""
あなたは対話型ストーリーAIです。

【キャラクター】
{char_text}

【これまで】
{state["summary"]}

【ルール】
・自然な会話
・1〜2人のみ登場
・説明しない
・必要ならイベント

【エンディング】
条件満たしたら：
【エンディング】と出力

【出力】
①会話
②【要約更新】
③【関係変化】

【ユーザー入力】
{user_input}
"""

# =========================
# AI出力の解析（パーサ）
# =========================
def update_state(output_text):

    # 要約更新
    match = re.search(r"【要約更新】(.+)", output_text)
    if match:
        state["summary"] = match.group(1)

    # エンディング検出
    if "【エンディング】" in output_text:
        state["endings"].append(output_text)

# =========================
# UI
# =========================

tab1, tab2, tab3 = st.tabs(["💬 チャット", "🧑 キャラ", "⚙ 設定"])

# =========================
# チャット
# =========================
with tab1:

    st.title("対話型ストーリー")

    # 履歴表示
    for h in state["history"]:
        with st.chat_message("user"):
            st.write(h["user"])
        with st.chat_message("assistant"):
            st.write(h["ai"])

    # 入力欄
    user_input = st.chat_input("メッセージを入力")

    if user_input:

        prompt = build_prompt(user_input)

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            output = ""

            try:
                response = model.generate_content(prompt)
                text = response.text

                # ストリーミング風
                for ch in text:
                    output += ch
                    placeholder.write(output)

            except Exception as e:
                st.error(e)
                output = "エラーが発生しました"

        # 保存
        state["history"].append({
            "user": user_input,
            "ai": output
        })

        # state更新
        update_state(output)

# =========================
# キャラ管理
# =========================
with tab2:

    st.title("キャラクター")

    name = st.text_input("名前")
    personality = st.text_input("性格")

    if st.button("追加"):
        if name and personality:
            state["characters"].append({
                "name": name,
                "personality": personality
            })
            st.success("追加しました")
        else:
            st.warning("入力してください")

    st.divider()

    st.subheader("一覧")

    if len(state["characters"]) == 0:
        st.write("まだキャラがいません")

    for i, c in enumerate(state["characters"]):

        col1, col2 = st.columns([4,1])

        with col1:
            st.write(f"**{c['name']}** - {c['personality']}")

        with col2:
            if st.button("削除", key=f"del{i}"):
                state["characters"].pop(i)
                st.rerun()

# =========================
# 設定
# =========================
with tab3:

    st.title("設定")

    if st.checkbox("デバッグ表示"):
        st.json(state)

    if st.button("履歴クリア"):
        state["history"] = []
        st.success("クリアしました")
