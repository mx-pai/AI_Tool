import streamlit as st
from utils.studio_style import apply_studio_style
from openai import OpenAI

# st.set_page_config(
#     #page_title="AI-Write",
#     page_icon="😎",
# )

client = OpenAI(
    api_key=st.secrets['api-keys']['kimiai-api-key'],  # 使用密钥
    base_url="https://api.moonshot.cn/v1",
)

st.set_page_config(
    page_title="小工具",
)

def get_suggestions(text, intent="general", num_suggestions=5):
    # 根据用户选择的风格生成相应的提示词
    if intent == "公文":
        prompt = (
            f"请将以下句子改写为符合中国公文格式的正式语气。"
            f"要求用词准确，语气正式，遵循公文写作规范。"
            f"请使用正式的术语、规范的表达方式，确保格式和内容符合正式文书的标准。"
            f"例如，可以使用常见的公文结构，如引言、主体和结尾。"
            f"\n\n原句：{text}"
        )
    elif intent == "搞怪语言":
        prompt = (
            f"请将以下句子改写为有趣、搞怪的风格。"
            f"可以采用以下几种搞怪风格之一：鲁迅体（带有讽刺和幽默）、黛玉体（带有古典文学的风格）等。"
            f"请加入夸张的修饰词、幽默的比喻，或者具有戏剧性的表达，使句子充满趣味和个性。"
            f"\n\n原句：{text}"
        )
    elif intent == "人情世故":
        prompt = (
            f"请将以下句子改写为符合人情世故的表达方式。"
            f"请在改写中加入对人际关系、礼貌和社会习俗的考量。"
            f"确保语言中包含适当的礼貌用语、友好的态度，以及对社会互动的尊重。"
            f"例如，可以使用关怀和礼貌的措辞，以体现对对方的尊重和体贴。"
            f"\n\n原句：{text}"
        )
    elif intent == "长篇":
        prompt = (
            f"请将以下句子扩展为一段详细的长篇描述。"
            f"增加背景信息、具体细节和额外的解释，使内容更加丰富和完整。"
            f"确保逻辑清晰，描述全面，以便读者能获得充分的信息。"
            f"\n\n原句：{text}"
        )
    elif intent == "简洁":
        prompt = (
            f"请将以下句子简化为简洁明了的表达方式。"
            f"去掉冗余信息，保持信息的核心内容，同时确保语言流畅和易于理解。"
            f"请使用简洁的句子结构和直接的表达方式。"
            f"\n\n原句：{text}"
        )
    else:
        prompt = (
            f"请将以下句子改写为通用风格，适用于各种场合。"
            f"确保语气中性，表达清晰，适合在各种文体中使用。"
            f"避免使用特定风格或术语，使句子适合一般的交流需求。"
            f"\n\n原句：{text}"
        )

    try:
        rewrite_resp = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            n=num_suggestions,  # 生成多个回复
        )

        if rewrite_resp.choices:
            rewritten_texts = [choice.message.content.strip() for choice in rewrite_resp.choices]
            st.session_state["rewrite_rewritten_texts"] = rewritten_texts
        else:
            st.error("API 响应中缺少有效的 'choices' 数据。")
            st.session_state["rewrite_rewritten_texts"] = ["无法获取改写建议，请稍后重试。"]

    except Exception as e:
        st.error(f"API 调用失败: {e}")
        st.session_state["rewrite_rewritten_texts"] = ["无法获取改写建议，请稍后重试。"]

def show_next(cycle_length):
    curr_index = st.session_state["rewrite_curr_index"]
    next_index = (curr_index + 1) % cycle_length
    st.session_state["rewrite_curr_index"] = next_index

def show_prev(cycle_length):
    curr_index = st.session_state["rewrite_curr_index"]
    prev_index = (curr_index - 1) % cycle_length
    st.session_state["rewrite_curr_index"] = prev_index

if __name__ == '__main__':
    apply_studio_style()

    st.title("语言修饰工具")
    st.write("轻松改写！使用人工智能写作伴侣，解决你的改写、扩写、缩写、优化语言等需求，让你能够轻松表达。")
    text = st.text_area(
        label="将你要改的话写在下面吧",
        max_chars=500,
        placeholder="请输入内容",
    ).strip()

    intent = st.radio(
        "选择你的改写风格 👉",
        key="intent",
        options=["通用", "公文", "搞怪语言", "长篇", "简洁","人情世故"],
        horizontal=True
    )

    st.button(label="改写 ✍️", on_click=lambda: get_suggestions(text, intent=intent))
    if "rewrite_rewritten_texts" in st.session_state:
        suggestions = st.session_state["rewrite_rewritten_texts"]
        ph = st.empty()
        if "rewrite_curr_index" not in st.session_state:
            st.session_state["rewrite_curr_index"] = 0
        curr_index = st.session_state["rewrite_curr_index"]
        ph.text_area(label="改写建议", value=suggestions[curr_index], height=200)
        col1, col2, col3, *_ = st.columns([1, 1, 1, 10])
        with col1:
            st.button("<", on_click=show_prev, args=(len(suggestions),))
        with col2:
            st.markdown(f"{curr_index + 1}/{len(suggestions)}")
        with col3:
            st.button("\>", on_click=show_next, args=(len(suggestions),))
