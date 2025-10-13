import streamlit as st
import json
from gtts import gTTS
from io import BytesIO
import base64
import random
import time
from datetime import date
import os

# ---------------- Load word list ----------------
with open("words.json", "r", encoding="utf-8") as f:
    word_list = json.load(f)

for w in word_list:
    if "translation" not in w:
        w["translation"] = ""

TOTAL_WORDS = len(word_list)
WORDS_PER_ROUND = 3
TOTAL_ROUNDS = max(1, TOTAL_WORDS // WORDS_PER_ROUND)
DAILY_GOAL = 10

# ---------------- Session State Initialization ----------------
def init_state():
    defaults = {
        "index": 0,
        "learned_words": [],
        "mode": "learn",
        "round": 1,
        "total_learned": 0,
        "score": 0,
        "high_score": 0,
        "streak": 0,
        "achievements": [],
        "quiz_correct_word": None,
        "quiz_options": [],
        "quiz_result": None,
        "quiz_submitted": False,
        "selected_option": None,
        "daily_date": str(date.today()),
        "daily_learned": 0,
        "show_translation": False,
        "review_list": [],
        "daily_goal_celebrated": False,
        "daily_goal_completed": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

if st.session_state.daily_date != str(date.today()):
    st.session_state.daily_date = str(date.today())
    st.session_state.daily_learned = 0
    st.session_state.daily_goal_celebrated = False
    st.session_state.daily_goal_completed = False

# ---------------- TTS Playback ----------------
def play_tts(text, slow=False):
    tts = gTTS(text=text, lang="en", slow=slow)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    audio_base64 = base64.b64encode(mp3_fp.read()).decode()
    st.markdown(
        f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        """,
        unsafe_allow_html=True,
    )

# ---------------- Header ----------------
if st.session_state.mode in ["learn", "quiz"]:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"### 🔁 Round: {st.session_state.round}/{TOTAL_ROUNDS}")
    with col2:
        st.markdown(f"### 🧠 Score: `{st.session_state.score}`")
    with col3:
        st.markdown(f"### 🏆 High Score: `{st.session_state.high_score}`")

    st.markdown(f"### 🎯 Daily Goal: {st.session_state.daily_learned}/{DAILY_GOAL} words learned today")
    st.progress(min(st.session_state.daily_learned / DAILY_GOAL, 1.0))

    if st.session_state.daily_learned >= DAILY_GOAL and not st.session_state.daily_goal_celebrated:
        st.success("🎉 Daily goal completed! Great job!")
        st.balloons()
        st.session_state.daily_goal_celebrated = True

# ---------------- Achievements ----------------
def check_achievements():
    achieved = []
    if st.session_state.streak >= 3 and "Streak Master" not in st.session_state.achievements:
        st.session_state.achievements.append("Streak Master")
        achieved.append("Streak Master")
    if st.session_state.total_learned >= TOTAL_WORDS and "Word Collector" not in st.session_state.achievements:
        st.session_state.achievements.append("Word Collector")
        achieved.append("Word Collector")
    if achieved:
        st.balloons()
        for a in achieved:
            st.success(f"Achievement unlocked: {a}")

# ---------------- Pronunciation Practice ----------------
def pronunciation_practice(word):
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.6)
            st.info("🎤 Listening... Please speak now.")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
    except (ImportError, OSError, Exception):
        st.warning("⚠️ Speech recognition is unavailable. This feature only works locally with a microphone.")
        return

    try:
        user_speech = recognizer.recognize_google(audio)
        st.write(f"You said: `{user_speech}`")
        if user_speech.strip().lower() == word.strip().lower():
            st.success("✅ Good job — pronunciation matched!")
        else:
            st.error(f"❌ Detected: '{user_speech}'. Try again.")
    except sr.UnknownValueError:
        st.error("Sorry, could not understand the audio.")
    except sr.RequestError:
        st.error("Speech recognition service unavailable.")

# ---------------- Review Mode ----------------
def review_mode():
    st.title("🔁 Review Mode")
    if not st.session_state.review_list:
        st.warning("No learned words available for review.")
        if st.button("Back to Learn"):
            st.session_state.mode = "learn"
            st.rerun()
        st.stop()

    for word in st.session_state.review_list:
        item = next(it for it in word_list if it["word"] == word)
        with st.expander(f"{item['word'].capitalize()}"):
            st.image(item["image"], width=150)
            if "example" in item:
                st.markdown(f"📖 *{item['example']}*")
                if st.button(f"🔊 Read example: {item['word']}", key=f"rev_example_{item['word']}"):
                    play_tts(item["example"])
            if item.get("translation"):
                if st.checkbox(f"Show translation", key=f"trans_rev_{item['word']}"):
                    st.markdown(f"📘 Translation: {item['translation']}")
            if st.button(f"🔊 Read word: {item['word']}", key=f"rev_read_{item['word']}"):
                play_tts(item["word"])

    if st.button("Back to Learn"):
        st.session_state.mode = "learn"
        st.rerun()

# ---------------- Goal Completed ----------------
if st.session_state.mode == "goal_completed":
    st.success("🎉 You've completed your daily goal!")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📚 Continue Learning"):
            st.session_state.mode = "learn"
            st.rerun()
    with col2:
        if st.button("🔁 Review Learned Words"):
            st.session_state.mode = "review"
            st.rerun()
    with col3:
        if st.button("❌ End Session"):
            st.markdown("See you next time! 👋")
            st.stop()

# ---------------- Learn Mode ----------------
if st.session_state.mode == "learn":
    if st.session_state.index >= len(word_list):
        st.success("🎓 You have learned all available words!")
        st.markdown(f"🏁 Final Score: `{st.session_state.score}`")
        if st.button("Restart Game"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.stop()

    current = word_list[st.session_state.index]
    st.title("📘 Learn New Word")
    st.image(current["image"], width=300)
    st.markdown(f"## ✏️ Word: **{current['word'].capitalize()}**")

    if "example" in current:
        st.markdown(f"📖 *{current['example']}*")

    st.session_state.show_translation = st.checkbox("Show translation", value=st.session_state.show_translation)
    if st.session_state.show_translation and current.get("translation"):
        st.markdown(f"📘 Translation: {current['translation']}")

    colA, colB, colC, colD = st.columns(4)
    with colA:
        if st.button("🔊 Read word", key="tts_word"):
            play_tts(current["word"])
    with colB:
        if "example" in current and st.button("📖 Read example", key="tts_example"):
            play_tts(current["example"])
    with colC:
        if st.button("🎤 Practice pronunciation", key="pronounce"):
            pronunciation_practice(current["word"])
    with colD:
        if st.button("➡️ Next", key="next_word"):
            if current["word"] not in st.session_state.learned_words:
                st.session_state.learned_words.append(current["word"])
                st.session_state.total_learned += 1
                st.session_state.daily_learned += 1
                if current["word"] not in st.session_state.review_list:
                    st.session_state.review_list.append(current["word"])

            st.session_state.index += 1

            if st.session_state.daily_learned >= DAILY_GOAL and not st.session_state.daily_goal_completed:
                st.session_state.daily_goal_completed = True
                st.session_state.mode = "goal_completed"
                st.rerun()

            if len(st.session_state.learned_words) >= WORDS_PER_ROUND:
                st.session_state.mode = "quiz"
                st.session_state.quiz_correct_word = None
                st.session_state.quiz_options = []
                st.session_state.quiz_result = None
                st.session_state.quiz_submitted = False
                st.session_state.selected_option = None

            st.rerun()

    if st.session_state.review_list:
        if st.button("🔁 Go to Review Mode"):
            st.session_state.mode = "review"
            st.rerun()

# ---------------- Quiz Mode ----------------
elif st.session_state.mode == "quiz":
    st.title("🧠 Quiz Time")

    if st.session_state.round > TOTAL_ROUNDS:
        st.success("✅ You finished all rounds!")
        st.markdown(f"🏁 Final Score: `{st.session_state.score}`")
        if st.button("Restart Game"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.stop()

    if st.session_state.quiz_correct_word is None:
        correct = random.choice(st.session_state.learned_words)
        st.session_state.quiz_correct_word = correct
        all_words = [w["word"] for w in word_list if w["word"] != correct]
        distractors = random.sample(all_words, min(3, len(all_words)))
        options = [correct] + distractors
        random.shuffle(options)
        st.session_state.quiz_options = options

    correct_item = next(w for w in word_list if w["word"] == st.session_state.quiz_correct_word)
    st.image(correct_item["image"], width=300)
    st.markdown("👉 Choose the correct word for this image:")

    if not st.session_state.quiz_submitted:
        cols = st.columns(len(st.session_state.quiz_options))
        for i, opt in enumerate(st.session_state.quiz_options):
            with cols[i]:
                if st.button(opt.capitalize(), key=f"quiz_{i}_{opt}"):
                    st.session_state.selected_option = opt
                    if opt == st.session_state.quiz_correct_word:
                        st.session_state.quiz_result = "correct"
                        st.session_state.score += 10
                        st.session_state.streak += 1
                        st.session_state.high_score = max(st.session_state.high_score, st.session_state.score)
                        check_achievements()
                    else:
                        st.session_state.quiz_result = "wrong"
                        st.session_state.streak = 0
                        if st.session_state.quiz_correct_word not in st.session_state.review_list:
                            st.session_state.review_list.append(st.session_state.quiz_correct_word)
                    st.session_state.quiz_submitted = True
                    st.rerun()
    else:
        if st.session_state.quiz_result == "correct":
            st.success("✅ Correct!")
            play_tts(st.session_state.quiz_correct_word)
            time.sleep(1.2)
            st.session_state.learned_words = []
            st.session_state.round += 1
            st.session_state.mode = "learn"
            st.session_state.quiz_correct_word = None
            st.session_state.quiz_options = []
            st.session_state.quiz_result = None
            st.session_state.quiz_submitted = False
            st.session_state.selected_option = None
            st.rerun()
        elif st.session_state.quiz_result == "wrong":
            st.error(f"❌ Wrong. Correct answer: **{st.session_state.quiz_correct_word.capitalize()}**")
            play_tts(f"The correct word is {st.session_state.quiz_correct_word}")
            if st.button("🔁 Go to Review Mode"):
                st.session_state.mode = "review"
                st.rerun()
            if st.button("➡️ Continue to next"):
                st.session_state.learned_words = []
                st.session_state.round += 1
                st.session_state.mode = "learn"
                st.session_state.quiz_correct_word = None
                st.session_state.quiz_options = []
                st.session_state.quiz_result = None
                st.session_state.quiz_submitted = False
                st.session_state.selected_option = None
                st.rerun()

# ---------------- Review Fallback ----------------
elif st.session_state.mode == "review":
    review_mode()












