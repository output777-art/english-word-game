import os
import json

# Path to the image folder
image_folder = "images"
json_file = "words.json"

# Load existing words if the file exists
if os.path.exists(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        existing_words = json.load(f)
else:
    existing_words = []

# Build a dictionary for existing words (key: lowercase word)
existing_dict = {entry["word"].lower(): entry for entry in existing_words}

# Get all image file names (png/jpg/jpeg)
image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# Track duplicates within this upload
current_run_words = set()
duplicate_in_upload = []

new_words_count = 0

for image_file in image_files:
    word = os.path.splitext(image_file)[0].strip().lower()

    # Detect duplicates within the current upload batch
    if word in current_run_words:
        duplicate_in_upload.append(word)
        continue
    current_run_words.add(word)

    # Skip if the word already exists in the dictionary
    if word in existing_dict:
        continue

    # Add new word entry
    existing_dict[word] = {
        "word": word.capitalize(),
        "image": os.path.join(image_folder, image_file).replace("\\", "/"),
        "example": "",
        "translation": ""
    }
    new_words_count += 1

# Write the updated word list back to the JSON file
updated_word_list = list(existing_dict.values())
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(updated_word_list, f, indent=4, ensure_ascii=False)

# Final output summary
print(f"✅ Vocabulary list successfully generated. Total words: {len(updated_word_list)}.")
print(f"🆕 New words added in this run: {new_words_count}.")

# Always show duplicate count, even if zero
deduped = sorted(set(duplicate_in_upload))
print(f"♻️  Duplicate image names detected and de-duplicated: {len(deduped)}" + (f" ({', '.join(deduped)})" if deduped else ""))

