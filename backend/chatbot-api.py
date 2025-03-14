import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import json

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Allows all methods
    allow_headers=["Content-Type", "Authorization"],  # Allows all headers
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print(f"API key loaded: {'Yes' if api_key else 'No'}")


class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    chingelezi: str
    translation: str
    speaker_language: str = None

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
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
                {"role": "user", "content": request.prompt},
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
                "chingelezi": f"Pepani, sindinapeze yankho m'mawonekedwe a JSON. Ili ndi lomwe lalembedwa: {message}",
                "translation": f"Sorry, couldn't get a response in JSON format. This was received: {message}",
                "speaker_language": "error"
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "chingelezi": f"Panachitika vuto: {str(e)}",
                "translation": f"An error occurred: {str(e)}",
                "speaker_language": "error"
            }
        )

@app.get("/")
async def root():
    return {"message": "Welcome to the Multilingual Chatbot API"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=8080)