import streamlit as st
import pandas as pd
import datetime
import random
import requests
import os

# API配置（完全保留你原来参数不动）
API_KEY = st.secrets.get("API_KEY", os.getenv("API_KEY", ""))
MODEL_ID = "doubao-seed-2-0-lite-260428"
API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

# 页面基础配置
st.set_page_config(page_title="吹风机宣传语实验", layout="wide")

# 会话状态初始化
if "page_flag" not in st.session_state:
    st.session_state.page_flag = 0  # 0=知情同意页，1=实验聊天页
if "user_id" not in st.session_state:
    st.session_state.user_id = f"USER_{random.randint(100000, 999999)}"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0

# AI请求函数（原逻辑不变）
def call_api(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    post_data = {
        "model": MODEL_ID,
        "messages": messages,
        "temperature": 0.8
    }
    try:
        resp = requests.post(API_URL, headers=headers, json=post_data, timeout=30)
        resp.raise_for_status()
        res_json = resp.json()
        return res_json["choices"][0]["message"]["content"]
    except Exception as e:
        return f"调用异常：{str(e)}"

# 对话函数（原逻辑不变）
def chat(message):
    st.session_state.chat_history.append({"role": "user", "content": message})
    st.session_state.turn_count += 1
    messages = [
        {
            "role": "system",
            "content": "你是广告文案助手，为高速速干吹风机创作宣传语，提供创意文案与修改建议。"
        }
    ]
    messages.extend(st.session_state.chat_history)
    ai_response = call_api(messages)
    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
    return ai_response

# 保存CSV函数（原逻辑不变）
def save_data():
    dialog_content = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history])
    save_dict = {
        "user_id": st.session_state.user_id,
        "turns": st.session_state.turn_count,
        "dialog": dialog_content,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    df = pd.DataFrame([save_dict])
    csv_name = f"hairdryer_{st.session_state.user_id}.csv"
    df.to_csv(csv_name, index=False, encoding="utf-8-sig")
    return f"✅ 数据保存成功！用户ID: {st.session_state.user_id}，对话轮次: {st.session_state.turn_count}"

# ==========第一页：知情同意页面（对标截图版式，任务说明前置）==========
if st.session_state.page_flag == 0:
    st.markdown("# 欢迎参与本次实验！")
    st.markdown("""
尊敬的女士/先生：您好！非常感谢您参与本实验，
本实验旨在了解用户在**吹风机产品宣传文案创作**任务情境中与AI助手的交互行为，仅用于课程学术研究。

### 📌 任务说明
你扮演公司市场部员工，为高速吹风机创作宣传语。
- 产品核心卖点：快速吹干
- 请与AI进行至少3轮对话
- 完成对话后点击保存数据按钮

本次实验包含以下内容：
- 您将以市场部员工身份，完成高速吹风机宣传标语创作任务；
- 任务过程中，您可以与AI助手对话，辅助您完成相关文案创作；
- 任务完成后，请根据页面提示保存数据，并填写一份简短的后续问卷；
- 问卷中需要填写用户ID，请提前记录下您的用户ID，以便填写。
""")
    st.markdown("### 实验流程：")
    st.markdown("""
1. 阅读任务说明进入任务界面 → 分配用户ID
2. 完成角色对应的核心任务（与AI对话协作）
3. 完成任务后，点击页面中的"保存数据"按钮
4. 填写后测问卷
""")
    st.markdown("### ⚠️重要说明：")
    st.markdown("""
- 本实验无对错之分，请按您的真实想法完成任务
- 您可以随时退出实验，无需任何理由，数据不会被记录
- 所有数据仅用于学术研究，不会泄露任何个人信息
""")
    st.markdown("点击下方按钮，即表示您已阅读并同意以上说明，自愿参与本次实验。")
    # 进入实验按钮
    if st.button("我已阅读并同意，进入实验"):
        st.session_state.page_flag = 1
        st.rerun()

# ==========第二页：原聊天实验页面==========
else:
    st.markdown("# 💬 与AI助手对话，创作宣传语")
    st.markdown(f"**你的用户ID：{st.session_state.user_id}**")
    st.markdown("💡 提示：请至少进行3轮对话再保存数据")

    # 聊天框
    chat_box = st.container(border=True, height=420)
    with chat_box:
        for item in st.session_state.chat_history:
            if item["role"] == "user":
                st.chat_message("user").write(item["content"])
            else:
                st.chat_message("assistant").write(item["content"])

    # 输入框表单
    with st.form("input_form", clear_on_submit=True):
        user_input = st.text_input("输入消息", placeholder="请输入你的想法或指令……")
        submit_btn = st.form_submit_button("发送")

    if submit_btn and user_input.strip() != "":
        chat(user_input.strip())
        st.rerun()

    st.info(f"当前轮次：{st.session_state.turn_count} / 至少需要3轮")

    col1, col2 = st.columns(2)
    save_res_text = ""
    with col1:
        save_btn = st.button("📥 保存实验数据", type="primary", disabled=(st.session_state.turn_count < 3))
    with col2:
        clear_btn = st.button("清空对话")

    if save_btn:
        save_res_text = save_data()
    st.text_input("保存结果", value=save_res_text, disabled=True)

    if clear_btn:
        st.session_state.chat_history = []
        st.session_state.turn_count = 0
        st.rerun()
