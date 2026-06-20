def build_prompt(user_input):

    character_text = "\n".join([
        f"""{c['name']}：
・{c['personality']}
・{c['traits']}
・{c['relation']}"""
        for c in state["characters"]
    ])

    internal_text = "\n".join([
        f"{c['name']}：親密度{c['intimacy']}/10 信頼{c['trust']}/10 感情:{c['emotion']}"
        for c in state["internal"]
    ])

    return f"""
【システム役割】
あなたは対話型物語エンジン。
キャラクターの一貫性と関係性を維持しながら自然な会話を行う。

---

【キャラクターDB】
{character_text}

---

【要約】
{state['summary']}

---

【内部状態】
{internal_text}

---

【ルール】

・1ターン1〜2キャラ
・自然な会話
・説明禁止
・キャラ同士の会話OK
・必要ならイベント発生OK

---

【イベント】

必要に応じて以下を発生：
・乱入
・対立
・環境変化
・感情変化

---

【分岐】

状態・関係・行動に応じて自然に分岐する

---

【エンディング】

条件を満たしたら以下を出力：
【エンディング】(名前)

---

【出力】

① 会話

② 必要なら
【新キャラ候補】

③ 必ず
【要約更新】
【関係変化】

---

【ユーザー入力】
{user_input}
"""

user_input = st.chat_input("入力")

if user_input:

    prompt = build_prompt(user_input)

    response = model.generate_content(prompt)
    output = response.text

def update_state_from_output(text):

    if "【要約更新】" in text:
        # 簡易更新
        state["summary"] = "更新された"

state["history"].append({
    "user": user_input,
    "ai": output
})
