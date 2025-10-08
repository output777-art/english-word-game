🧠 English Word Game - Vocabulary Learning App

A beginner-friendly vocabulary learning web app using images and English words.
Built with Python and Streamlit.

📸 Project Overview

This project is a simple vocabulary learning game designed for English learners.
Users can match images with English words to reinforce their memory.

It supports bulk image addition and automatic generation of the word list JSON file.
Perfect for Python beginners, educational games, or learning how to build web apps without frontend knowledge.

🔧 Tech Stack

Python 3.x

Streamlit
 — Frontend web framework

JSON — For storing word and image data

VS Code — Recommended development environment

🚀 How to Run Locally

Make sure you have Python and pip installed. (Using a virtual environment is recommended.)

1️⃣ Install dependencies
pip install streamlit pyttsx3

2️⃣ Start the App
streamlit run app.py


Your browser will open automatically at:
http://localhost:8501
 — and you're ready to play! 🎉

🗂️ Project Structure
📁 english-word-game/
├── app.py              # Main app script (Streamlit)
├── images/             # PNG images used in the game
├── generate_json.py    # Script to generate words.json
├── words.json          # JSON file with word-image mapping
├── requirements.txt    # Dependency list for deployment
└── README.md           # Project documentation

✨ Features

Use local PNG images as vocabulary flashcards

Automatically generate a word list from filenames

Easily expandable by adding new images

Zero frontend knowledge needed — built entirely in Python

Ready for deployment online (Streamlit Cloud / Hugging Face Spaces)

📌 How to Add New Words

Add .png files into the images/ folder

File name should match the word (e.g., apple.png, cat.png)

Run the generator script:

python generate_json.py


Relaunch the app — new words will be automatically loaded.

📚 Target Audience

Python beginners

Anyone interested in Streamlit

Educational game developers

Students building their first AI/web portfolio project

✅ What's Next?

Add multiple choice (4-option) quiz mode

Add voice narration using TTS (like gTTS)

Support multi-language vocab sets

Deploy to web (Streamlit Cloud or Hugging Face Spaces)

🧑‍💻 Author

Created by a Python learner exploring the path of AI tool development.