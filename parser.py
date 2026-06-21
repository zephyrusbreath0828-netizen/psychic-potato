import re

def update_state_from_output(state, output):

    # 要約更新
    match = re.search(r"【要約更新】(.+)", output)
    if match:
        state["summary"] = match.group(1)

    # エンディング
    if "【エンディング】" in output:
        state["endings"].append(output)
