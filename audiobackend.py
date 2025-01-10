import os
import json
import sounddevice as sd
import numpy as np
import testaudio_only
from dotenv import load_dotenv
from openai import OpenAI
import tempfile
import soundfile as sf
import time

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load Whisper model
whisper_model = testaudio_only.load_model('base')

def record_audio(duration=5, samplerate=16000):
    """Record audio for a given duration and return the audio data."""
    print("Recording...")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()  # Wait until recording is finished
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
        response = openai.Completion.create(
            engine="text-davinci-003",  # or any other engine you prefer
            prompt=(
                "Ndinu wothandiza wokhoza kulankhula zilankhulo zambiri ndipo mumayembekezera mafunso mu chilankhulo chilichonse ndipo mumayankha mu mawonekedwe a JSON. "
                "JSON ikuyenera kukhala ndi maina atatu: 'chingelezi', yankho mu Chingelezi, 'translation' mu chichewa, ndipo 'speaker_language' chilembedwe cha chilankhulo chomwe funsolo lanenedwa. "
                "Mukalandira mafunso mu Chichewa, Chingelezi, French kapena m'Chilankhulo china chilichonse, muyenera kuyankha mu Chichewa 'chingelezi', kutanthauzira mu 'translation', ndi kulemba dzina la chilankhulo mu 'speaker_language'.\n\n"
                "User: Moni, muli bwanji?\n"
                "Assistant: {\"chingelezi\": \"Moni! Ndili bwino, inu muli bwanji?\", \"translation\": \"Hello! I'm fine, how are you?\", \"speaker_language\": \"Chichewa\"}\n\n"
                "User: What is your name?\n"
                "Assistant: {\"chingelezi\": \"Dzina langa ndi Assistant.\", \"translation\": \"My name is Assistant.\", \"speaker_language\": \"English\"}\n\n"
                "User: Salut, comment ça va?\n"
                "Assistant: {\"chingelezi\": \"Ndikuyenda bwino\", \"translation\": \"I am doing well.\", \"speaker_language\": \"French\"}\n\n"
                f"User: {prompt}\n"
                "Assistant:"
            ),
            max_tokens=150,
            n=1,
            stop=["User:"],
            temperature=0.7
        )
        message = response.choices[0].text.strip()
        
        try:
            parsed_message = json.loads(message)
            if 'chingelezi' not in parsed_message or 'translation' not in parsed_message:
                raise ValueError("Missing required fields in JSON response")
            return parsed_message
        except json.JSONDecodeError:
            return {
                "chingelezi": f"Pepani, sindinapeze yankho m'mawonekedwe a JSON. Ili ndi lomwe lalembedwa: {message}",
                "translation": f"Sorry, couldn't get a response in JSON format. This was received: {message}"
            }
    except Exception as e:
        return {
            "chingelezi": f"Panachitika vuto: {str(e)}",
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