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
# 状態管理（state）
# =========================
if "state" not in st.session_state:
    st.session_state.state = {
        "characters": [],
        "relations": [],
        "summary": "開始",
        "history": [],
        "endings": [],
        "internal": []
    }

state = st.session_state.state

# =========================
# プロンプト構築（超重要）
# =========================
def build_prompt(user_input):

    character_text = "\n".join([
        f"""{c['name']}：
・{c['personality']}
・{c.get('traits','')}
・{c.get('relation','')}"""
        for c in state["characters"]
    ])

    internal_text = "\n".join([
        f"{c['name']}：親密度{c['intimacy']}/10 信頼{c['trust']}/10 感情:{c['emotion']}"
        for c in state["internal"]
    ])

    return f"""
【役割】
あなたは対話型物語エンジン。

【キャラクターDB】
{character_text}

【要約】
{state['summary']}

【内部状態】
{internal_text}

【ルール】
・自然な会話
・1〜2キャラのみ登場
・キャラ同士会話OK
・説明禁止

【イベント】
必要なら発生可：
・対立
・環境変化
・乱入
・感情変化

【分岐】
関係・行動に応じて変化

【エンディング】
到達した場合：
【エンディング】(内容)

【出力】
① 会話
② 必要なら【新キャラ候補】
③ 必ず：
【要約更新】
【関係変化】

【ユーザー入力】
{user_input}
"""

# =========================
# 状態更新（パーサ）
# =========================
def update_state_from_output(text):

    # 要約更新
    summary_match = re.search(r"【要約更新】(.+)", text)
    if summary_match:
        state["summary"] = summary_match.group(1)

    # 関係変化（簡易）
    rels = re.findall(r"(.+?)→(.+?)：(.+)", text)
    for r in rels:
        state["relations"].append({
            "from": r[0],
            "to": r[1],
            "type": r[2]
        })

    # エンディング
    if "【エンディング】" in text:
        state["endings"].append(text)

# =========================
# UI（タブ）
# =========================
tab1, tab2, tab3 = st.tabs(["💬 チャット", "🧑 キャラ", "⚙ 設定"])

# =========================
# ✅ チャット
# =========================
with tab1:

    st.title("対話型ストーリー")

    for h in state["history"]:
        with st.chat_message("user"):
            st.write(h["user"])
        with st.chat_message("assistant"):
            st.write(h["ai"])

    user_input = st.chat_input("行動やセリフを入力")

    if user_input:

        prompt = build_prompt(user_input)

        with st.chat_message("user"):
            st.write(user_input)

        try:
            with st.chat_message("assistant"):

                placeholder = st.empty()
                output = ""

                response = model.generate_content(prompt)
                text = response.text

                # ストリーミング風表示
                for char in text:
                    output += char
                    placeholder.write(output)

            # 履歴保存
            state["history"].append({
                "user": user_input,
                "ai": output
            })

            # 状態更新
            update_state_from_output(output)

        except Exception as e:
            st.error(f"エラー: {e}")

# =========================
# ✅ キャラ管理
# =========================
with tab2:

    st.title("キャラクター")

    mode = st.radio("モード", ["簡単", "詳細"])

    if mode == "簡単":
        simple = st.text_area("ざっくり設定")

        if st.button("生成"):
            prompt = f"""
            以下からキャラクター生成：

            {simple}

            出力：
            名前：
            性格：
            特徴：
            """
            res = model.generate_content(prompt)
            st.session_state.gen_char = res.text

    else:
        name = st.text_input("名前")
        personality = st.text_input("性格")

        if st.button("生成（詳細）"):
            st.session_state.gen_char = f"""
名前：{name}
性格：{personality}
"""

    if "gen_char" in st.session_state:
        st.text_area("生成結果", st.session_state.gen_char)

        if st.button("採用"):
            state["characters"].append({
                "name": "キャラ",
                "personality": st.session_state.gen_char,
                "traits": "",
                "relation": ""
            })
            st.success("追加しました")

    st.divider()

    st.subheader("一覧")

    for i, c in enumerate(state["characters"]):
