import pyttsx3

# Meeting text content
text = (
    "This is a test meeting. The first action item is to review the budget by Friday. "
    "The second action item is to prepare the project report by Monday."
)

# Initialize TTS engine
engine = pyttsx3.init()
engine.save_to_file(text, 'test_meeting.wav')
engine.runAndWait()

print("✅ Created 'test_meeting.wav' with spoken meeting content.")