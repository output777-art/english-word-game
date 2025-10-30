# Changelog

## [Unreleased]

## [2025-10-14] - Initial Release
- Added initial script to generate word list JSON from images

## [2025-10-14] - Update
- Added new images to the folder
- Modified the JSON generation script to include example sentences and translation placeholders

Script Update Log:

- Added display of duplicate word count even when zero, to always show consistency in run summary.

- Updated duplicate detection logic to identify duplicates within the current upload batch and report them as "deduplicated" words.

- Removed redundant listing of words that already exist in the vocabulary, showing only newly added words and batch duplicates.

## [2025-10-27] - Feature Expansion

- Added background music support 🎵  
- Introduced input_quiz: a fill-in-the-blank quiz feature  
- Added debug panel for easier app troubleshooting  
- Created Input Quiz Summary page to show quiz results  
- Enabled review of missed words after quizzes  
- Fixed Streamlit key duplication caused by repeated wrong words  
- Fixed incorrect return paths for multiple navigation buttons  

## Updates on [2025-10-28]

- Fixed: Prevented `st.balloons()` from triggering multiple times across navigation paths.
- UI Adjustment: Moved the background music player from the main page to the sidebar to reduce visual clutter.
- Fixed: Duplicate words in the "Review Missed Words" list are now deduplicated while preserving their original quiz order.
- Feature Added: Introduced a calendar-based check-in system with graphical visualization using Plotly. Users can now sign in daily and return to the learning mode via a dedicated button.

## Updates on [2025-10-30]
- Fixed: Correct answer count and accuracy rate in the quiz summary are now calculated directly from unique quiz words, ignoring repeated attempts and ensuring consistency.
- Added: Retry quiz with missed words directly from review mode for more efficient practice.
- Improved: Review mode now shows "Back to Quiz" when accessed from quiz, preserving user flow and avoiding accidental exit to learning mode.