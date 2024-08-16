import streamlit as st

if __name__ == '__main__':

    st.set_page_config(
    page_title="Hello",
    page_icon="👋",
    )

    st.write("# Welcome to Streamlit! 👋")
    st.markdown("#### 尝试使用Streamlit构建应用，省的自己再敲前端代码了")
    st.markdown("##### 计划：")
    st.checkbox(" AI改写")
    st.checkbox("语音转文字")
    st.checkbox("AI提示词")
    st.checkbox("思考者")

    st.sidebar.success("Select a demo above.")
    st.sidebar.title("欢迎使用AI工具")
