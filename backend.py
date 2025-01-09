
import os
import sounddevice as sd
import numpy as np
import whisper
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# OpenAI API Key

# Load Whisper model
model = whisper.load_model('base') 

def record_audio(duration=5, samplerate=16000):
    print("Kulemba mawu...")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()  # Dikirani mpaka kulembedwa kumaliza
    print("Kulembedwa kwatha.")
    return np.squeeze(audio_data)

def transcribe_audio(audio_data, samplerate=16000):
    print("Kutembenuza mawu kukhala malemba...")
    # Whisper model expects np.ndarray as input with shape (samples,)
    result = model.transcribe(audio_data, language='en')
    text = result['text']
    print("Kutembenuza kwatha.")
    return text.strip()

def chatbot(prompt):
    # Construct the full conversation prompt with a three-shot example
    full_prompt = (
        "You are a chatbot that understands Chichewa and English. Answer in JSON format "
        "with 'chichewa' for the response in Chichewa and 'translation' for the English translation.\n\n"
        "User: Muli bwanji?\n"
        "Assistant: {\"chichewa\": \"Ndili bwino kaya, inu muli bwanji?\", \"translation\": \"I am doing great, how are you doing?\"}\n\n"
        "User: Dzina lanu ndindani?\n"
        "Assistant: {\"chichewa\": \"Dzina langa ndi Assistant.\", \"translation\": \"My name is Assistant.\"}\n\n"
        "User: Kodi mutha kulankhula zinenero ziti?\n"
        "Assistant: {\"chichewa\": \"Ndingathe kulankhula Chichewa ndi Chingerezi.\", \"translation\": \"I can speak Chichewa and English.\"}\n\n"
        f"User: {prompt}\n"
        "Assistant:"
    )

    response = client.completions.create(engine="text-davinci-003",
    prompt=full_prompt,
    max_tokens=150,
    n=1,
    stop=["User:"],
    temperature=0.7)

    # Try parsing the response to JSON
    try:
        message = response.choices[0].text.strip()
        parsed_message = json.loads(message)
        # Ensure required keys are present
        if 'chichewa' not in parsed_message or 'translation' not in parsed_message:
            raise ValueError("Keys zofunikira zasowa mu JSON response")
        return parsed_message
    except (json.JSONDecodeError, ValueError) as e:
        # Handle errors in JSON parsing
        return {
            "chichewa": f"Cholakwika chachitika: {str(e)}",
            "translation": f"An error occurred: {str(e)}"
        }

def main():
    while True:
        print("Lembani 'record' ngati mukufuna kugwiritsa ntchito mawu kapena 'type' kuti mulembere funso lanu. Lembani 'exit' kuti mutuluke.")
        method = input("Sankhani njira: ").lower()

        if method == 'exit':
            print("Tsalani bwino!")
            break
        elif method == 'record':
            # Lembani ndikukweza mawu kukhala malemba
            audio = record_audio()
            transcribed_text = transcribe_audio(audio)
        elif method == 'type':
            transcribed_text = input("Lembani funso lanu: ")

        # Pitilizani kuzungulira lotsatira ngati palibe malemba ovomerezeka
        if not transcribed_text:
            continue

        # Sindikizani mawu ofotokozedwa ngati alemba
        print(f"Munati: {transcribed_text}")

        # Pezani yankho kuchokera ku chatbot
        response = chatbot(transcribed_text)
        print(f"Yankho: {response}\n")

if __name__ == "__main__":
    main()
