import os
import streamlit as st
import requests
import json
import time
import hashlib
import random

# 定义每个大模型的服务器URL和端口
model_servers = {
    "Yi-6B-lora": "http://localhost:6009",
    "GLM4-9B-lora": "http://localhost:6008",
    "Qwen2-7B-lora": "http://localhost:6007",
    "LLaMA3-8B-lora": "http://localhost:6006",
}

# RAGFlow的基本URL和API密钥
ragflow_base_url = os.getenv("RAGFLOW_BASE_URL", "https://demo.ragflow.io/v1/api")
ragflow_api_key = os.getenv("RAGFLOW_API_KEY", "")

def query_model(server_url, messages_json):
    response = requests.post(server_url, json=messages_json)
    return response.json()

def query_ragflow(conversation_id, message):
    if not ragflow_api_key:
        return {"data": None, "retcode": 401, "retmsg": "RAGFLOW_API_KEY is not configured"}
    headers = {
        "Authorization": f"Bearer {ragflow_api_key}"
    }
    payload = {
        "conversation_id": conversation_id,
        "messages": [message]
    }
    response = requests.post(f"{ragflow_base_url}/completion", headers=headers, json=payload, stream=True, proxies={"http": None, "https": None})
    
    valid_response = []
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8').lstrip("data:").strip()
            try:
                json_line = json.loads(decoded_line)
                if "data" in json_line and isinstance(json_line["data"], dict):
                    valid_response.append(json_line)
            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {e.msg}")

    if valid_response:
        return valid_response[-1]
    else:
        return {"data": None, "retcode": 100, "retmsg": "No valid response received"}

def create_new_conversation(user_id):
    if not ragflow_api_key:
        return {"data": None, "retcode": 401, "retmsg": "RAGFLOW_API_KEY is not configured"}
    headers = {
        "Authorization": f"Bearer {ragflow_api_key}"
    }
    response = requests.get(f"{ragflow_base_url}/new_conversation", headers=headers, params={"user_id": user_id}, proxies={"http": None, "https": None})
    return response.json()

# 初始化session_state
if 'messages' not in st.session_state:
    st.session_state['messages'] = [{"role": "system", "content": "你是一个宠物犬智能诊疗小助手，你需要根据用户的问题和知识库内容进行回答。当所有知识库内容与问题无关时，答案需要考虑聊天历史。以下是知识库内容：{knowledge} 以上是知识库内容。"}]
if 'selected_model' not in st.session_state:
    st.session_state['selected_model'] = "Qwen2-7B-lora"
if 'login' not in st.session_state:
    st.session_state['login'] = False
if 'request_times' not in st.session_state:
    st.session_state['request_times'] = []
if 'users' not in st.session_state:
    st.session_state['users'] = {}
if 'registration_attempts' not in st.session_state:
    st.session_state['registration_attempts'] = {}
if 'invites' not in st.session_state:
    st.session_state['invites'] = ["hzau2021"]
if 'show_login' not in st.session_state:
    st.session_state['show_login'] = False
if 'show_register' not in st.session_state:
    st.session_state['show_register'] = False
if 'conversation_id' not in st.session_state:
    st.session_state['conversation_id'] = None

def generate_invite():
    invite = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
    st.session_state['invites'].append(invite)
    return invite

def register_user(username, password, invite):
    if username in st.session_state['users']:
        return False, "用户名已存在"
    if invite not in st.session_state['invites']:
        return False, "邀请码无效"
    st.session_state['users'][username] = {
        'password': hashlib.sha256(password.encode()).hexdigest(),
        'request_times': []
    }
    # st.session_state['invites'].remove(invite)
    return True, "注册成功"

def is_limited():
    current_time = time.time()
    st.session_state['request_times'] = [
        t for t in st.session_state['request_times'] if current_time - t < 600
    ]
    return len(st.session_state['request_times']) >= 5

# Streamlit应用程序
if os.path.exists("./assets/HZAU.jpg"):
    st.sidebar.image("./assets/HZAU.jpg", use_container_width=True)
st.title("宠物犬小助手 🐶")
st.sidebar.markdown("### 用于模型微调的数据来自：")
st.sidebar.markdown("- 《狗狗疾病一本足够》")
st.sidebar.markdown("- 《宠物疾病大全》")
st.sidebar.markdown("- 《犬猫常见疾病防治》")
st.sidebar.markdown("感谢以上书籍提供知识来源")

if not st.session_state['login']:
    if st.sidebar.button("用户登录", key="login_button"):
        st.session_state['show_login'] = True
    if st.sidebar.button("新用户注册", key="register_button"):
        st.session_state['show_register'] = True

if st.session_state.get('show_login'):
    with st.sidebar.expander("登录"):
        st.subheader("用户登录")
        username = st.text_input("用户名", key="login_username")
        password = st.text_input("密码", type="password", key="login_password")
        if st.button("登录确认", key="login_confirm_button"):
            if username in st.session_state['users'] and \
                st.session_state['users'][username]['password'] == hashlib.sha256(password.encode()).hexdigest():
                st.session_state['login'] = username
                st.session_state['show_login'] = False
                st.success("登录成功")
            else:
                st.error("用户名或密码错误")
        if st.button("取消", key="login_cancel_button"):
            st.session_state['show_login'] = False

if st.session_state.get('show_register'):
    with st.sidebar.expander("注册"):
        st.subheader("新用户注册")
        new_username = st.text_input("新用户名", key="register_username")
        new_password = st.text_input("新密码", type="password", key="register_password")
        invite_code = st.text_input("邀请码", key="invite_code")
        if st.button("注册确认", key="register_confirm_button"):
            success, message = register_user(new_username, new_password, invite_code)
            st.info(message)
            if success:
                st.session_state['show_register'] = False
        if st.button("取消", key="register_cancel_button"):
            st.session_state['show_register'] = False

if st.session_state['login']:
    st.sidebar.success(f"已登录: {st.session_state['login']}")
    if st.sidebar.button("退出", key="logout_button"):
        st.session_state.update({'login': False})
else:
    st.sidebar.error("未登录")

if st.session_state['login']:
    st.sidebar.subheader("生成邀请码")
    if st.sidebar.button("生成邀请码", key="generate_invite_button"):
        invite = generate_invite()
        st.sidebar.write(f"新邀请码: {invite}")

selected_model = st.selectbox("选择大模型", list(model_servers.keys()), index=list(model_servers.keys()).index(st.session_state['selected_model']))
st.write(f"当前选择的模型: {selected_model}")

if st.button("切换模型", key="switch_model_button"):
    st.session_state['selected_model'] = selected_model
    st.session_state['messages'] = [{"role": "system", "content": "你是一个宠物犬智能诊疗小助手，你需要根据用户的问题和知识库内容进行回答。当所有知识库内容与问题无关时，答案需要考虑聊天历史。以下是知识库内容：{knowledge} 以上是知识库内容。"}]

use_rag = st.checkbox("是否加入RAG知识库", key="use_rag")

if prompt := st.chat_input():
    if st.session_state['login'] or (not st.session_state['login'] and not is_limited()):
        # 记录用户的提问
        st.session_state.messages.append({"role": "user", "content": f"{prompt}"})
        st.chat_message("user").write(prompt)

        # 处理知识库内容
        knowledge_content = ""
        if use_rag:
            if st.session_state['conversation_id'] is None:
                response = create_new_conversation(st.session_state['login'] or "guest_user")
                if response['retcode'] == 0:
                    st.session_state['conversation_id'] = response['data']['id']
                else:
                    st.error(f"创建会话失败: {response['retmsg']}")
                    st.stop()

            rag_response = query_ragflow(st.session_state['conversation_id'], st.session_state.messages[-1])
            print(rag_response)
            if rag_response['retcode'] == 0 and rag_response['data'] and 'reference' in rag_response['data']:
                rag_chunks = rag_response['data']['reference']['chunks']
                for chunk in rag_chunks:
                    knowledge_content += chunk['content_with_weight'] + "\n"
            else:
                st.error(f"RAGFlow 查询失败: {rag_response['retmsg']}")

        # 合并用户的问题和知识库内容
        combined_content = f"用户的问题：{prompt}\n以下是知识库内容：{knowledge_content}"

        # 将合并后的内容作为单独的消息发送给模型
        query_messages = st.session_state['messages'][:-1] + [{"role": "user", "content": combined_content}]
        
        server_url = model_servers[st.session_state['selected_model']]
        response = query_model(server_url, json.dumps(query_messages))
        
        # 将模型的回答添加到历史对话中
        answer = response['response']
        st.session_state['messages'].append({"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)
        
        if use_rag and knowledge_content:
            with st.expander("点击查看参考的知识库内容"):
                st.write(knowledge_content)
        
        if not st.session_state['login']:
            st.session_state['request_times'].append(time.time())
    else:
        st.warning("10分钟内最多只能使用5次，请稍后再试")

st.write("对话历史:")
for chat in st.session_state['messages'][1:]:
    with st.chat_message(chat['role']):
        st.write(chat['content'])

st.markdown("<div style='text-align: center; padding: 20px;'>网站作者：华中农业大学2021大数据系暑期实训小组</div>", unsafe_allow_html=True)
