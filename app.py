import streamlit as st
import json
import google.generativeai as genai

# =========================
# 設定
# =========================
genai.configure(api_key="YOUR_API_KEY")

model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# セッション状態初期化
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
# UI：タイトル
# =========================
st.title("対話型ストーリーアプリ")

# =========================
# チャット入力
# =========================
user_input = st.text_area("あなたの行動・発言")

if st.button("送信"):

    character_text = "\n".join([
        f"{c['name']}：{c['personality']} / {c['traits']} / {c['relation']}"
        for c in state["characters"]
    ])

    internal_text = "\n".join([
        f"{c['name']} 親密度{c['intimacy']} 信頼{c['trust']} 感情{c['emotion']}"
        for c in state["internal"]
    ])

    prompt = f"""
【キャラクターDB】
{character_text}

【関係】
{state['relations']}

【要約】
{state['summary']}

【内部状態】
{internal_text}

【ユーザー入力】
{user_input}
"""

    try:
        response = model.generate_content(prompt)
        output = response.text

        st.write("### AI")
        st.write(output)

        state["history"].append({
            "user": user_input,
            "ai": output
        })

        # 簡易要約更新
        state["summary"] = "ストーリー進行中"

    except Exception as e:
        st.error(f"エラー: {e}")


# =========================
# キャラ生成
# =========================
st.subheader("キャラクター生成")

mode = st.radio("モード選択", ["簡単入力", "詳細設定"])

if mode == "簡単入力":
    simple = st.text_area("曖昧な設定")

    if st.button("キャラ生成（簡単）"):
        prompt = f"""
曖昧な情報からキャラクターを生成してください：

{simple}

出力：
名前：
性格：
特徴：
関係：
"""
        res = model.generate_content(prompt)
        st.session_state.generated_char = res.text

else:
    personality = st.text_input("性格")
    traits = st.text_input("特徴")
    relation = st.text_input("関係")

    if st.button("キャラ生成（詳細）"):
        prompt = f"""
以下からキャラ生成：

性格：{personality}
特徴：{traits}
関係：{relation}

不足補完してください
"""
        res = model.generate_content(prompt)
        st.session_state.generated_char = res.text


# =========================
# 生成結果表示
# =========================
if "generated_char" in st.session_state:
    st.text_area("生成結果", st.session_state.generated_char)

    if st.button("採用"):
        # 簡易パース（本格は後で強化可）
        state["characters"].append({
            "name": "新キャラ",
            "personality": st.session_state.generated_char,
            "traits": "",
            "relation": ""
        })
        st.success("追加しました")

# =========================
# キャラ一覧
# =========================
st.subheader("キャラクター一覧")

for i, c in enumerate(state["characters"]):
    st.write(f"**{c['name']}**")
    if st.button(f"削除 {i}"):
        del state["characters"][i]
        st.rerun()


# =========================
# セーブ / ロード
# =========================
st.subheader("セーブ / ロード")

save_data = json.dumps(state)

st.download_button(
    "セーブ（JSON）",
    save_data,
    file_name="save.json"
)

upload = st.file_uploader("ロード")

if upload:
    state.clear()
    state.update(json.load(upload))
    st.success("ロード完了")

# =========================
# デバッグ
# =========================
if st.checkbox("デバッグ表示"):
    st.json(state)
