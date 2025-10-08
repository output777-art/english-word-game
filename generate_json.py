import os
import json

# Image folder path
image_folder = "images"

# Get all image file names
image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

# Construct word data
word_list = []

for image_file in image_files:
    # Remove the extension and use it as a word
    word = os.path.splitext(image_file)[0]
    word_list.append({
        "word": word.capitalize(),
        "image": os.path.join(image_folder, image_file).replace("\\", "/")  # Windows compatible
    })

# Writing a JSON file
with open("words.json", "w", encoding="utf-8") as f:
    json.dump(word_list, f, indent=4)

print(f"✅ {len(word_list)} words have been generated into words.json")
