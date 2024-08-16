import os
import wave
import pyaudio
import streamlit as st
from vosk import Model, KaldiRecognizer

# 加载Vosk模型
model_path = r"D:\\1AI\\AI_Tool\\model\\vosk-model-small-cn-0.22"
if not os.path.exists(model_path):
    raise Exception(f"Model path {model_path} does not exist")

try:
    model = Model(model_path)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Failed to load model: {e}")
# 实时语音识别函数

def real_time_recognition():
    recognizer = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    st.write("开始说话...")
    try:
        while True:
            data = stream.read(4000)
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                st.write(result)
            else:
                partial_result = recognizer.PartialResult()
                st.write(partial_result)
            if st.button("停止识别"):  # 添加停止识别按钮
                break
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

# 文件上传识别函数
def file_upload_recognition(audio_file):
    recognizer = KaldiRecognizer(model, 16000)
    wf = wave.open(audio_file, "rb")

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            st.write(result)
    st.write(recognizer.FinalResult())

# Streamlit 应用界面
st.title("语音识别工具")
st.write("请选择一个模式开始语音识别：")

# 选择实时识别或文件上传识别
mode = st.radio("选择识别模式：", ("实时识别", "文件上传"))

if mode == "实时识别":
    if st.button("开始实时识别"):
        real_time_recognition()

elif mode == "文件上传":
    uploaded_file = st.file_uploader("上传音频文件", type=["wav"])
    if uploaded_file is not None:
        file_upload_recognition(uploaded_file)
