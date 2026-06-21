import google.generativeai as genai
from parser import update_state_from_output

def build_prompt(state, user_input):

    char_text = "\n".join([
        f"{c['name']}：{c['personality']}"
        for c in state["characters"]
    ])

    return f"""
あなたは対話型ストーリーAIです。

【キャラクター】
{char_text}

【要約】
{state["summary"]}

【ユーザー入力】
{user_input}
"""

def send_message(model, state, usage, user_input):

    if usage["count"] >= usage["limit"]:
        return "上限に達しました"

    prompt = build_prompt(state, user_input)

    response = model.generate_content(prompt)
    output = response.text

    usage["count"] += 1

    state["history"].append({
        "user": user_input,
        "ai": output
    })

    update_state_from_output(state, output)

    return output
