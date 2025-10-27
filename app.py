import streamlit as st
import json
from gtts import gTTS
from io import BytesIO
import base64
import random
import time
from datetime import date
import os
from typing import List, Dict

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

# ---------------- Background Music ----------------
bg_music_on = st.sidebar.checkbox("Background Music🎵", value=True)

if bg_music_on:
    st.audio("sounds/bg_music.mp3", format="audio/mp3", start_time=0)


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

    st.markdown(
        f"### 🎯 Daily Goal: {st.session_state.daily_learned}/{DAILY_GOAL} words learned today"
    )
    st.progress(min(st.session_state.daily_learned / DAILY_GOAL, 1.0))

    if (
        st.session_state.daily_learned >= DAILY_GOAL
        and not st.session_state.daily_goal_celebrated
    ):
        st.success("🎉 Daily goal completed! Great job!")
        st.balloons()
        st.session_state.daily_goal_celebrated = True


# ---------------- Achievements ----------------
def check_achievements():
    achieved = []
    if (
        st.session_state.streak >= 3
        and "Streak Master" not in st.session_state.achievements
    ):
        st.session_state.achievements.append("Streak Master")
        achieved.append("Streak Master")
    if (
        st.session_state.total_learned >= TOTAL_WORDS
        and "Word Collector" not in st.session_state.achievements
    ):
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
        st.warning(
            "⚠️ Speech recognition is unavailable. This feature only works locally with a microphone."
        )
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

    for i, word in enumerate(st.session_state.review_list):
        item = next(it for it in word_list if it["word"] == word)
        with st.expander(f"{item['word'].capitalize()}"):
            st.image(item["image"], width=150)

            if "example" in item:
                st.markdown(f"📖 *{item['example']}*")
                if st.button(
                    f"🔊 Read example: {item['word']}",
                    key=f"rev_example_{item['word']}_{i}",
                ):
                    play_tts(item["example"])

            if item.get("translation"):
                if st.checkbox(
                    f"Show translation",
                    key=f"trans_rev_{item['word']}_{i}",
                ):
                    st.markdown(f"📘 Translation: {item['translation']}")

            if st.button(
                f"🔊 Read word: {item['word']}",
                key=f"rev_read_{item['word']}_{i}",
            ):
                play_tts(item["word"])

    if st.button("Back to Learn"):
        st.session_state.mode = "learn"
        st.rerun()

    if st.button("Back to Quiz"):
        st.session_state.mode = "input_quiz"
        st.session_state.input_quiz_state = "idle"
        st.session_state.reset_input_quiz = True
        st.rerun()

    if st.session_state.get("review_return_to") == "input_quiz_summary":
        if st.button("🏁 Back to Quiz Summary"):
            st.session_state.mode = "input_quiz_summary"
            del st.session_state[
                "review_return_to"
            ]  # ✅ Clear the mark to avoid residue
            st.rerun()


# ---------------- Goal Completed ----------------
if st.session_state.mode == "goal_completed":

    st.success("🎉 You've completed your daily goal of learning 10 words!")
    st.markdown(
        "You can now start today's input quiz to review the 10 words you have just learned."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🧩 Start Daily Input Quiz"):
            DAILY_GOAL = 10

            # Get exactly today's 10 learned words
            learned_today = st.session_state.get("learned_words", [])[-DAILY_GOAL:]

            # Remove duplicates and ensure exactly 10 by re-sampling if needed
            unique_today = list(set(learned_today))
            while len(unique_today) < DAILY_GOAL:
                unique_today.append(random.choice(unique_today))
            random.shuffle(unique_today)
            quiz_words = unique_today[:DAILY_GOAL]

            # Initialize quiz states
            st.session_state.input_quiz_list = quiz_words
            st.session_state.input_quiz_idx = 0
            st.session_state.input_quiz_answer = ""
            st.session_state.input_quiz_state = "idle"
            st.session_state.input_quiz_show_hint = False
            st.session_state.input_quiz_score = 0
            st.session_state.input_quiz_results = []  # store (word, correct/incorrect)
            st.session_state.mode = "input_quiz"

            time.sleep(0.8)
            st.rerun()

    with col2:
        if st.button("🔁 Review Learned Words"):
            st.session_state.mode = "review"
            time.sleep(0.6)
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

    st.session_state.show_translation = st.checkbox(
        "Show translation", value=st.session_state.show_translation
    )
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

            # ✅ New: Record the complete word object learned today
            if "today_learned_words" not in st.session_state:
                st.session_state.today_learned_words = []
            if current not in st.session_state.today_learned_words:
                st.session_state.today_learned_words.append(current)

            st.session_state.index += 1

            if (
                st.session_state.daily_learned >= DAILY_GOAL
                and not st.session_state.daily_goal_completed
            ):
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

    correct_item = next(
        w for w in word_list if w["word"] == st.session_state.quiz_correct_word
    )
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
                        st.session_state.high_score = max(
                            st.session_state.high_score, st.session_state.score
                        )
                        check_achievements()
                    else:
                        st.session_state.quiz_result = "wrong"
                        st.session_state.streak = 0
                        if (
                            st.session_state.quiz_correct_word
                            not in st.session_state.review_list
                        ):
                            st.session_state.review_list.append(
                                st.session_state.quiz_correct_word
                            )
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
            st.error(
                f"❌ Wrong. Correct answer: **{st.session_state.quiz_correct_word.capitalize()}**"
            )
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

# ---------------- Input_Quiz (New) ----------------
elif st.session_state.mode == "input_quiz":

    # ✅ Initialize all quiz state variables (executed only once)
    if "input_quiz_initialized" not in st.session_state:
        st.session_state.input_quiz_idx = 0
        st.session_state.input_quiz_results = []
        st.session_state.input_quiz_score = 0
        st.session_state.input_quiz_state = "idle"
        st.session_state.input_quiz_show_hint = False
        st.session_state.input_quiz_answers = {}

        learned_words: List[Dict] = st.session_state.get("today_learned_words", [])
        sampled_items = random.sample(learned_words, k=min(10, len(learned_words)))
        st.session_state.input_quiz_list = [w["word"] for w in sampled_items]

        st.session_state.input_quiz_initialized = True  # ✅ Flag initialized

    quiz_list = st.session_state.input_quiz_list
    idx = st.session_state.input_quiz_idx

    # ------------------- Debug Panel -------------------
    with st.expander("🛠 Debug Info"):
        st.write(f"Index: {idx}")
        st.write(f"State: {st.session_state.input_quiz_state}")
        st.write(f"Answer: {st.session_state.input_quiz_answers.get(idx, '')}")
        st.write(f"Score: {st.session_state.input_quiz_score}")
        st.write(f"Results: {st.session_state.input_quiz_results}")
        st.write(f"Quiz List: {quiz_list}")
        st.write(
            "Today Learned Words:", st.session_state.get("today_learned_words", [])
        )

    # ------------------- All questions done -------------------
    if idx >= len(quiz_list):
        st.session_state.mode = "input_quiz_summary"
        st.rerun()

    current_word = quiz_list[idx]
    item = next((w for w in word_list if w["word"] == current_word), None)
    if not item:
        st.warning("Word data missing, skipping.")
        st.session_state.input_quiz_results.append((current_word, False))
        st.session_state.input_quiz_idx += 1
        st.rerun()

    st.title(f"⌨️ Daily Input Quiz {idx + 1}/{len(quiz_list)}")
    st.image(item["image"], width=280)
    st.markdown("👉 Type the correct English word for this image:")

    # ------------------- Text Input -------------------
    input_key = f"input_quiz_text_{idx}"

    # ✅ If the flag is True, clear the input box binding value
    if st.session_state.get("reset_input_quiz"):
        if input_key in st.session_state:
            st.session_state[input_key] = ""  # Now it is safe to empty
        st.session_state["reset_input_quiz"] = False  # Reset Flag

    st.session_state.input_quiz_answers.setdefault(idx, "")
    user_input = st.text_input(
        "Your Answer:", value=st.session_state.input_quiz_answers[idx], key=input_key
    )
    st.session_state.input_quiz_answers[idx] = user_input

    # ------------------- Submit -------------------
    if st.button("✅ Submit") and st.session_state.input_quiz_state == "idle":
        if user_input.strip().lower() == current_word.lower():
            st.session_state.input_quiz_results.append((current_word, True))
            st.session_state.input_quiz_score += 1
            st.session_state.input_quiz_state = "correct"
            play_tts("Correct!")
        else:
            st.session_state.input_quiz_results.append((current_word, False))
            st.session_state.input_quiz_state = "wrong"
            st.session_state.input_quiz_show_hint = False
            play_tts("Wrong answer!")

    # ------------------- Correct State -------------------
if (
    st.session_state.mode == "input_quiz"
    and st.session_state.get("input_quiz_state") == "correct"
):
    st.success(f"🎉 Correct! The answer is **{quiz_list[idx].capitalize()}**")
    if st.button("➡️ Continue"):
        st.session_state.input_quiz_idx += 1
        st.session_state.input_quiz_state = "idle"
        st.rerun()

# ------------------- Wrong State -------------------
if (
    st.session_state.mode == "input_quiz"
    and st.session_state.get("input_quiz_state") == "wrong"
):
    st.error("❌ Incorrect!")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("💡 Show Hint"):
            st.session_state.input_quiz_show_hint = True

    with col2:
        if st.button("🔁 Review This Word"):
            st.session_state.review_word = quiz_list[idx]
            st.session_state.mode = "review"
            st.session_state.input_quiz_state = "idle"
            st.session_state.reset_input_quiz = True
            st.rerun()

    with col3:
        if st.button("➡️ Skip to Next"):
            st.session_state.input_quiz_idx += 1
            st.session_state.input_quiz_state = "idle"
            st.session_state.input_quiz_show_hint = False
            st.rerun()

    with col4:
        if st.button("🔄 Try Again"):
            st.session_state.input_quiz_answers[idx] = ""
            st.session_state.input_quiz_state = "idle"
            st.session_state.input_quiz_show_hint = False
            st.session_state.reset_input_quiz = True
            st.rerun()

    if st.session_state.input_quiz_show_hint:
        st.info(f"Hint: The correct answer is **{quiz_list[idx].capitalize()}**")


# ---------------- Input Quiz Summary ----------------
elif st.session_state.mode == "input_quiz_summary":
    st.title("📊 Daily Input Quiz Summary")

    score = st.session_state.get("input_quiz_score", 0)
    total = len(st.session_state.get("input_quiz_list", []))
    correct_rate = round((score / total) * 100, 1) if total else 0

    st.markdown(f"### ✅ Correct: {score}/{total} ({correct_rate}%)")

    # Show missed words
    wrong_words = [w for w, ok in st.session_state.input_quiz_results if not ok]
    if wrong_words:
        st.markdown("### ❌ Words to Review:")
        for w in wrong_words:
            st.markdown(f"- **{w.capitalize()}**")

    st.progress(score / total if total else 0)
    st.balloons()

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔁 Review Missed Words"):
            if wrong_words:
                st.session_state.review_list = wrong_words
                st.session_state.review_return_to = (
                    "input_quiz_summary"  # ✅ Set return target
                )
                st.session_state.mode = "review"
                time.sleep(0.8)
                st.rerun()
            else:
                st.success("All correct! Nothing to review.")
    with col2:
        if st.button("📚 Continue Learning"):
            st.session_state.mode = "learn"
            time.sleep(0.8)
            st.rerun()
    with col3:
        if st.button("🏁 End Session"):
            st.markdown("See you next time! 👋")
            st.stop()
