import os
import whisper
import openai
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load Whisper model
model = whisper.load_model('base')

def transcribe_audio(audio_data, samplerate=16000):
    """Transcribe audio data using the Whisper model."""
    result = model.transcribe(audio_data, language="en")
    text = result['text']
    return text.strip()

def chatbot(prompt):
    """Generate a response from the OpenAI model based on the user's input."""
    # Set up the three-shot example for better responses
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

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=full_prompt,
        max_tokens=150,
        n=1,
        stop=["User:"],
        temperature=0.7
    )
    
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