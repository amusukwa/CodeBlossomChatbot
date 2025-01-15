import os
import json
import sounddevice as sd
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
import tempfile
import soundfile as sf
import time

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def detect_silence(audio_chunk, threshold=0.01):
    """Detect silence in audio chunk."""
    return np.mean(np.abs(audio_chunk)) < threshold

def record_audio(samplerate=16000):
    """Record audio until silence is detected and return the audio data."""
    print("Listening... (Speak now)")
    
    chunk_duration = 0.5  # 500ms chunks
    silence_duration = 1.5  # 1.5 seconds of silence to stop
    chunk_samples = int(samplerate * chunk_duration)
    silence_chunks = int(silence_duration / chunk_duration)
    
    audio_data = []
    silence_counter = 0
    speech_detected = False
    min_audio_length = 1 * samplerate  # Minimum 1 second of audio

    with sd.InputStream(samplerate=samplerate, channels=1, dtype='float32') as stream:
        while True:
            chunk, _ = stream.read(chunk_samples)
            audio_data.extend(chunk)

            if detect_silence(chunk):
                silence_counter += 1
                if silence_counter >= silence_chunks and speech_detected and len(audio_data) > min_audio_length:
                    break
            else:
                silence_counter = 0
                speech_detected = True

            # Safety check to prevent infinite recording
            if len(audio_data) > 30 * samplerate:  # Max 30 seconds
                break

    print("Recording complete.")
    return np.array(audio_data)

def transcribe_audio(audio_data, samplerate=16000):
    """Transcribe audio data using OpenAI's Whisper API."""
    print("Transcribing audio...")
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        sf.write(temp_audio.name, audio_data, samplerate, format='WAV')
    
    try:
        with open(temp_audio.name, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        text = transcription.text
        print("Transcription complete.")
        return text.strip()
    finally:
        os.unlink(temp_audio.name)

def chatbot(prompt):
    """Generate a response from the OpenAI model based on the user's input."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", 
                 "content": "Ndinu wothandiza wokhoza kulankhula zilankhulo zambiri ndipo mumayembekezera mafunso mu chilankhulo chilichonse ndipo mumayankha mu mawonekedwe a JSON. JSON ikuyenera kukhala ndi maina atatu: 'chingelezi', yankho mu Chingelezi, 'translation' mu chichewa, ndipo 'speaker_language' chilembedwe cha chilankhulo chomwe funsolo lanenedwa. Mukalandira mafunso mu Chichewa, Chingelezi, French kapena m'Chilankhulo china chilichonse, muyenera kuyankha mu Chichewa 'chingelezi', kutanthauzira mu 'translation', ndi kulemba dzina la chilankhulo mu 'speaker_language'."},
                {"role": "user", "content": "Moni, muli bwanji?"},
                {"role": "assistant", "content": '{"chingelezi": "Moni! Ndili bwino, inu muli bwanji?", "translation": "Hello! I\'m fine, how are you?", "speaker_language": "Chichewa"}'},
                {"role": "user", "content": "What is your name"},
                {"role": "assistant","content" : '{"chingelezi": "Dzina langa ndi Assistant.", "translation": "My name is Assistant.", "speaker_language": "English"}'},
                {"role": "user", "content": "Salut, comment ça va?"},
                {"role": "assistant","content" : '{"chingelezi": "Ndikuyenda bwino", "translation": "I am doing well.", "speaker_language": "French"}'},
                {"role": "user", "content": prompt},
            ]
        )
        message = response.choices[0].message.content
        
        try:
            parsed_message = json.loads(message)
            if 'chingelezi' not in parsed_message or 'translation' not in parsed_message:
                raise ValueError("Missing required fields in JSON response")
            return parsed_message
        except json.JSONDecodeError:
            return {
                "chichewa": f"Pepani, sindinapeze yankho m'mawonekedwe a JSON. Ili ndi lomwe lalembedwa: {message}",
                "translation": f"Sorry, couldn't get a response in JSON format. This was received: {message}"
            }
    except Exception as e:
        return {
            "chichewa": f"Panachitika vuto: {str(e)}",
            "translation": f"An error occurred: {str(e)}"
        }

def main():
    print("Welcome to the continuous voice assistant!")
    print("Speak after the 'Listening...' prompt. The assistant will respond after detecting silence.")
    print("Press Ctrl+C to exit the program.")

    try:
        while True:
            audio_data = record_audio()
            if len(audio_data) > 0:
                transcription = transcribe_audio(audio_data)
                print(f"You said: {transcription}")
                if transcription.strip():
                    response = chatbot(transcription)
                    print("Assistant's response:")
                    print(json.dumps(response, indent=2, ensure_ascii=False))
                else:
                    print("No speech detected. Please try again.")
            else:
                print("No audio recorded. Please try again.")
            print("\nReady for next input...")
            time.sleep(1)  # Short pause before next listening session
    except KeyboardInterrupt:
        print("\nExiting the program. Goodbye!")

if __name__ == "__main__":
    main()