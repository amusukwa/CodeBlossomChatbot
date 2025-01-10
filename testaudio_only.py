import numpy as np
import whisper
import sounddevice as sd

# Load the Whisper model
model = whisper.load_model("base")

# Function to record and transcribe audio
def test_whisper_integration(duration=5, samplerate=16000):
    try:
        # Record audio
        print("Recording audio...")
        audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
        sd.wait()
        print("Recording complete.")

        # Convert audio data to 1D array as Whisper expects mono audio
        audio_data = audio_data.flatten()

        # Transcribe audio
        print("Transcribing audio...")
        result = model.transcribe(audio_data, fp16=False)  # Use fp16=False for CPU compatibility
        print("Transcription complete.")

        return result['text'].strip()
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return None

# Test transcribing
transcription = test_whisper_integration()
if transcription:
    print("Transcribed Text:", transcription)
else:
    print("Failed to transcribe audio.")
