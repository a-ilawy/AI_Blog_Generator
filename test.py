import assemblyai as aai

# Set your AssemblyAI API key
aai.settings.api_key = ""

# Create a transcriber instance
transcriber = aai.Transcriber()

# Path to your audio file (can be a local path or a URL)
audio_file = "E:/test2.mp3"  # Replace with your file path

# Transcribe the file
transcript = transcriber.transcribe(audio_file)

# Print the transcribed text
print(transcript.text)
