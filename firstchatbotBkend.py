import os
# Ikani phukusi la openai ngati silipo
try:
    from openai import OpenAI
except ImportError:
    print("Kuyika phukusi la openai...")
    os.system('pip install openai')
    from openai import OpenAI
# OpenAI API key mulowe apa
api_key = 'your-api-key-here'
client = OpenAI(api_key=api_key)
def chatbot(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7
        )
        message = response.choices[0].message.content.strip()
        return message
    except Exception as e:
        return f"Chinachake chachitika: {str(e)}"
def main():
    print("Yankhula ndi Chatbot! Lekani kulemba 'bye'.")
    while True:
        user_input = input("Inu: ")
        if user_input.lower() in ['bye', 'exit', 'quit']:
            print("Chatbot: Tionana!")
            break
        response = chatbot(user_input)
        print(f"Chatbot: {response}")
if __name__ == "__main__":
    main()