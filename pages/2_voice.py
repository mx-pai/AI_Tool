import os
import wave
import pyaudio
import streamlit as st
from vosk import Model, KaldiRecognizer
import soundfile as sf
import io
import librosa

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
    recognition_results = []

    # Initialize session state for button click tracking
    if 'stop_button_clicked' not in st.session_state:
        st.session_state.stop_button_clicked = False

    while not st.session_state.stop_button_clicked:
        try:
            data = stream.read(4000, exception_on_overflow=False)
        except Exception as e:
            st.write(f"Error reading audio stream: {e}")
            break

        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            recognition_results.append(result)
        else:
            partial_result = recognizer.PartialResult()
            recognition_results.append(partial_result)

        # Display recognition results
        st.text_area("识别结果", value="\n".join(recognition_results), height=300)

        # Check if stop button was clicked
        if st.button("停止识别", key="stop_button_real_time"):
            st.session_state.stop_button_clicked = True

    stream.stop_stream()
    stream.close()
    p.terminate()

# 文件上传识别函数
def file_upload_recognition(audio_file):
    try:
        audio_bytes = audio_file.read()

        # 读取音频文件信息
        with io.BytesIO(audio_bytes) as f:
            data, samplerate = sf.read(f)

        # 检查采样率
        if samplerate != 48000:
            st.error("音频文件采样率不是48000 Hz，可能会导致识别问题。")
            return

        # 使用librosa进行重采样
        data_16k = librosa.resample(data, orig_sr=samplerate, target_sr=16000)

        print(f"音频长度: {len(data_16k)}")
        print(f"采样率: {samplerate}")

        # 将音频数据转换为Wave格式
        with io.BytesIO() as buffer:
            sf.write(buffer, data_16k, 16000, format='WAV')
            buffer.seek(0)
            wf = wave.open(buffer, "rb")

            recognizer = KaldiRecognizer(model, 16000)
            recognition_results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    st.write(f"识别结果: {result}")  # 添加此行以输出识别结果
                    #recognition_results.append(result)
                else:
                    partial_result = recognizer.PartialResult()
                    st.write(f"部分识别结果: {partial_result}")  # 添加此行以输出部分识别结果
                    #recognition_results.append(partial_result)
                    recognition_results.append(recognizer.FinalResult())

            st.text_area("识别结果", value="\n".join(recognition_results), height=300)

    except Exception as e:
        st.error(f"识别过程中出现错误: {e}")

# Streamlit 应用界面
st.title("语音识别工具")
st.write("请选择一个模式开始语音识别：")

# 选择实时识别或文件上传识别
mode = st.radio("选择识别模式：", ("实时识别", "文件上传"))

if mode == "实时识别":
    if st.button("开始实时识别", key="start_recognition_real_time"):
        st.session_state.stop_button_clicked = False
        real_time_recognition()

elif mode == "文件上传":
    uploaded_file = st.file_uploader("上传音频文件", type=["wav", "mp3"])
    if uploaded_file is not None:
        file_upload_recognition(uploaded_file)
