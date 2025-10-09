import streamlit as st
import json
from gtts import gTTS
from io import BytesIO
import base64
import random
import time
import os

# ----- Load word data -----
with open("words.json", "r") as f:
    word_list = json.load(f)

TOTAL_WORDS = len(word_list)
WORDS_PER_ROUND = 3
TOTAL_ROUNDS = max(1, TOTAL_WORDS // WORDS_PER_ROUND)

# ----- Initialize session state -----
if "index" not in st.session_state:
    st.session_state.index = 0
if "learned_words" not in st.session_state:
    st.session_state.learned_words = []
if "mode" not in st.session_state:
    st.session_state.mode = "learn"  # "learn" or "quiz"
if "round" not in st.session_state:
    st.session_state.round = 1
if "total_learned" not in st.session_state:
    st.session_state.total_learned = 0

# Quiz state
if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = None
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

# New: Save the correct answers and options of this round of quiz to avoid confusion caused by refreshing
if "quiz_correct_word" not in st.session_state:
    st.session_state.quiz_correct_word = None
if "quiz_options" not in st.session_state:
    st.session_state.quiz_options = []

# ----- Helper: play TTS -----
def play_tts(word, rate=150):
    slow = rate < 120
    tts = gTTS(text=word, lang='en', slow=slow)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    audio_bytes = mp3_fp.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    st.markdown(
        f"""
        <audio id="ttsAudio" autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        <script>
            var audio = document.getElementById("ttsAudio");
            if (audio) {{
                audio.play().catch(err => console.log("Autoplay prevented:", err));
            }}
        </script>
        """,
        unsafe_allow_html=True,
    )

# ----- Helper: play sound from local file -----
def play_sound(filepath):
    if not os.path.exists(filepath):
        st.warning(f"Sound file not found: {filepath}")
        return
    with open(filepath, "rb") as f:
        audio_bytes = f.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    st.markdown(
        f"""
        <audio id="soundEffect" autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        <script>
            var audio = document.getElementById("soundEffect");
            if (audio) {{
                audio.play().catch(err => console.log("Autoplay prevented:", err));
            }}
        </script>
        """,
        unsafe_allow_html=True,
    )

# ----- Helper: show progress and restart button -----
def show_progress():
    st.markdown(f"### 📊 Overall Progress: Round {st.session_state.round}/{TOTAL_ROUNDS}")
    completed = (st.session_state.round - 1) / TOTAL_ROUNDS
    st.progress(completed)
    st.caption(f"Total learned words: **{st.session_state.total_learned} / {TOTAL_WORDS}**")

    # Restart button
    if st.button("🔁 Restart Game", key=f"restart_{st.session_state.round}"):
        st.session_state.index = 0
        st.session_state.learned_words = []
        st.session_state.mode = "learn"
        st.session_state.round = 1
        st.session_state.total_learned = 0
        st.session_state.quiz_result = None
        st.session_state.selected_option = None
        st.session_state.quiz_submitted = False
        st.session_state.quiz_correct_word = None
        st.session_state.quiz_options = []
        st.rerun()

# ===========================================================
# 🧠 LEARNING MODE
# ===========================================================
if st.session_state.mode == "learn":
    show_progress()

    if st.session_state.index >= len(word_list):
        st.success("🎉 You have learned all words! Restart or enjoy the quiz.")
        if st.button("🔁 Restart Game", key="restart_end_learn"):
            st.session_state.index = 0
            st.session_state.learned_words = []
            st.session_state.mode = "learn"
            st.session_state.round = 1
            st.session_state.total_learned = 0
            st.session_state.quiz_result = None
            st.session_state.selected_option = None
            st.session_state.quiz_submitted = False
            st.session_state.quiz_correct_word = None
            st.session_state.quiz_options = []
            st.rerun()
        st.stop()

    current = word_list[st.session_state.index]
    st.title(f"📖 Learn New Words — Round {st.session_state.round}")
    progress = len(st.session_state.learned_words) + 1
    st.write(f"**Progress:** Word {progress}/{WORDS_PER_ROUND}")

    st.image(current["image"], width=300)
    st.markdown(f"## Word: **{current['word'].capitalize()}**")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔊 Read Aloud", key=f"read_{st.session_state.index}"):
            play_tts(current["word"])
    with col2:
        if st.button("➡️ Next", key=f"next_{st.session_state.index}"):
            if current["word"] not in st.session_state.learned_words:
                st.session_state.learned_words.append(current["word"])
                st.session_state.total_learned += 1

            st.session_state.index += 1

            # After 3 learned words → go to quiz
            if len(st.session_state.learned_words) >= WORDS_PER_ROUND:
                st.session_state.mode = "quiz"
                st.session_state.quiz_result = None
                st.session_state.selected_option = None
                st.session_state.quiz_submitted = False
                st.session_state.quiz_correct_word = None
                st.session_state.quiz_options = []

            st.rerun()

# ===========================================================
# 🎯 QUIZ MODE
# ===========================================================
elif st.session_state.mode == "quiz":
    show_progress()
    st.title(f"🎯 Quiz Time — Round {st.session_state.round}")

    # Preventing Exceeding Round Numbers
    if st.session_state.round > TOTAL_ROUNDS:
        st.success("🎉 You have completed all rounds! Congratulations!")
        if st.button("🔁 Restart Game", key="restart_finish_quiz"):
            st.session_state.index = 0
            st.session_state.learned_words = []
            st.session_state.mode = "learn"
            st.session_state.round = 1
            st.session_state.total_learned = 0
            st.session_state.quiz_result = None
            st.session_state.selected_option = None
            st.session_state.quiz_submitted = False
            st.session_state.quiz_correct_word = None
            st.session_state.quiz_options = []
            st.rerun()
        st.stop()

    # Initialize the correct answer and options for the current round (only initialize once)
    if st.session_state.quiz_correct_word is None or len(st.session_state.quiz_options) == 0:
        st.session_state.quiz_correct_word = random.choice(st.session_state.learned_words)
        all_words = [w["word"] for w in word_list if w["word"] != st.session_state.quiz_correct_word]
        distractors = random.sample(all_words, min(3, len(all_words)))
        options = [st.session_state.quiz_correct_word] + distractors
        random.shuffle(options)
        st.session_state.quiz_options = options
        st.session_state.quiz_result = None
        st.session_state.selected_option = None
        st.session_state.quiz_submitted = False

    correct_word = st.session_state.quiz_correct_word
    options = st.session_state.quiz_options
    correct_item = next(w for w in word_list if w["word"] == correct_word)

    st.image(correct_item["image"], width=300)
    st.write("👉 Choose the correct word for this image:")

    if not st.session_state.quiz_submitted:
        cols = st.columns(len(options))
        for i, opt in enumerate(options):
            with cols[i]:
                if st.button(opt.capitalize(), key=f"quiz_opt_{st.session_state.round}_{opt}"):
                    st.session_state.selected_option = opt
                    if opt == correct_word:
                        st.session_state.quiz_result = "correct"
                    else:
                        st.session_state.quiz_result = "wrong"
                    st.session_state.quiz_submitted = True
                    st.rerun()
    else:
        # Feedback display
        if st.session_state.quiz_result == "correct":
            st.success("✅ Correct! Moving to next round...")
            play_sound("sounds/correct.mp3")
            play_tts(correct_word)
            time.sleep(2)

            # Reset status to enter the next round
            st.session_state.learned_words = []
            st.session_state.round += 1
            st.session_state.mode = "learn"
            st.session_state.quiz_result = None
            st.session_state.selected_option = None
            st.session_state.quiz_submitted = False
            st.session_state.quiz_correct_word = None
            st.session_state.quiz_options = []
            st.rerun()

        elif st.session_state.quiz_result == "wrong":
            st.error(f"❌ Wrong! The correct answer was: **{correct_word.capitalize()}**")
            play_sound("sounds/wrong.mp3")

            if st.button("🔁 Review these words again", key=f"review_again_{st.session_state.round}"):
                first_word = st.session_state.learned_words[0]
                first_index = next(
                    i for i, w in enumerate(word_list) if w["word"] == first_word
                )
                st.session_state.index = first_index
                st.session_state.mode = "learn"
                st.session_state.quiz_result = None
                st.session_state.selected_option = None
                st.session_state.quiz_submitted = False
                st.session_state.quiz_correct_word = None
                st.session_state.quiz_options = []
                st.rerun()







