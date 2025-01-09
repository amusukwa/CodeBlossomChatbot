import os
from dotenv import load_dotenv
import openai
import json

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def chatbot(prompt):
    """
    Amayankha mafunso pogwiritsa ntchito GPT-3 ya OpenAI.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", 
                 "content": "Ndinu wothandiza wokhoza kulankhula zilankhulo zambiri ndipo mumayembekezera mafunso mu chilankhulo chilichonse ndipo mumayankha mu mawonekedwe a JSON. JSON ikuyenera kukhala ndi maina atatu: 'chingelezi', yankho mu Chingelezi, 'translation' mu chichewa, ndipo 'speaker_language' chilembedwe cha chilankhulo chomwe funsolo lanenedwa. Mukalandira mafunso mu Chichewa, Chingelezi, French kapena m'Chilankhulo china chilichonse, muyenera kuyankha mu Chichewa 'chingelezi', kutanthauzira mu 'translation', ndi kulemba dzina la chilankhulo mu 'speaker_language'."},
                {"role": "user", "content": "Moni, muli bwanji?"}, # 1 shot prompting
                {"role": "assistant", "content": '{"chingelezi": "Moni! Ndili bwino, inu muli bwanji?", "translation": "Hello! I\'m fine, how are you?", "speaker_language": "Chichewa"}'},
                {"role": "user", "content": "What is your name"}, # 2 shot prompting
                {"role": "assistant","content" : '{"chingelezi": "Dzina langa ndi Assistant.", "translation": "My name is Assistant.", "speaker_language": "English"}'},
                {"role": "user", "content": "Salut, comment ça va?"}, # 3 shot prompting
                {"role": "assistant","content" : '{"chingelezi": "Ndikuyenda bwino", "translation": "I am doing well.", "speaker_language": "French"}'},
                {"role": "user", "content": prompt},
            ]
        )
        message = response.choices[0].message.content
        
        # Try to parse the message as JSON
        try:
            parsed_message = json.loads(message)
            # Ensure the required fields are present
            if 'chingelezi' not in parsed_message or 'translation' not in parsed_message:
                raise ValueError("Missing required fields in JSON response")
            return parsed_message
        except json.JSONDecodeError:
            # If parsing fails, create a JSON object with an error message
            return {
                "chingelezi": f"Pepani, sindinapeze yankho m'mawonekedwe a JSON. Ili ndi lomwe lalembedwa: {message}",
                "translation": f"Sorry, couldn't get a response in JSON format. This was received: {message}"
            }
    except Exception as e:
        # Return a JSON object with an error message
        return {
            "chingelezi": f"Panachitika vuto: {str(e)}",
            "translation": f"An error occurred: {str(e)}"
        }

def main():
    print("Robot: Lembani funso lanu pansipa. Lembani 'Pitani', 'Tulukani', kapena 'Chotsani' kuti mutseke nkhaniyi.\n[Translation] Type your question below. Type 'Bye', 'Quit', or 'Exit' to end the chat.")
    while True:
        user_input = input("Inu: ")
        if user_input.lower() in ['bye', 'quit', 'exit', 'pitani', 'tulukani', 'chotsani']:
            print("Robot: Pitani bwino!\n[Translation] Goodbye!")
            break
        response = chatbot(user_input)
        print(f"Response: {response}")


if __name__ == "__main__":
    main()