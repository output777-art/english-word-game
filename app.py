import streamlit as st
import json
import pyttsx3
import os

#  Reading a json file
with open("words.json", "r") as f:
    word_list = json.load(f)

# Init index
if "index" not in st.session_state:
    st.session_state.index = 0

# Init voice setting(default)
if "voice_type" not in st.session_state:
    st.session_state.voice_type = "Male"
if "rate" not in st.session_state:
    st.session_state.rate = 150  # default speech

# Get the current word
current = word_list[st.session_state.index]

# Content
st.title("🔤 Know the Words ")
st.image(current["image"], width=300)
st.markdown(f"## Word: **{current['word'].capitalize()}**")

# ===== 🎛️ Settings section: Speech rate + Voice type =====
with st.expander("🎛️ Voice Settings", expanded=True):
    st.session_state.rate = st.slider("Speed", min_value=80, max_value=250, value=st.session_state.rate, step=10)
    st.session_state.voice_type = st.radio("Voice", options=["Male", "Female"], index=0 if st.session_state.voice_type == "Male" else 1)

# ===== 🔊 Read aloud =====
if st.button("🔊 Read Aloud"):
    engine = pyttsx3.init()
    engine.setProperty("rate", st.session_state.rate)  # set speech rate

    # Get all available sounds
    voices = engine.getProperty("voices")
    
    # Set the sound according to choice
    selected_voice = None
    for voice in voices:
        if st.session_state.voice_type.lower() in voice.name.lower():
            selected_voice = voice
            break
    if selected_voice:
        engine.setProperty("voice", selected_voice.id)

    engine.say(current["word"])
    engine.runAndWait()

# ===== 👉 Next button =====
if st.button("➡️ Next"):
    st.session_state.index = (st.session_state.index + 1) % len(word_list)
    st.rerun()  # 👈 Refresh page





