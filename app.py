import streamlit as st
import json
from gtts import gTTS
from io import BytesIO
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
    # gTTS does not support voice gender directly, so we ignore voice_type for now
    slow = False
    # Map speed slider to slow parameter roughly: slower speed if rate < 120
    if st.session_state.rate < 120:
        slow = True
    
    tts = gTTS(text=current["word"], lang='en', slow=slow)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    st.audio(mp3_fp.read(), format="audio/mp3")

# ===== 👉 Next button =====
if st.button("➡️ Next"):
    st.session_state.index = (st.session_state.index + 1) % len(word_list)
    st.rerun()  # 👈 Refresh page

    





