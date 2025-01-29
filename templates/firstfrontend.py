import streamlit as st
from firstchatbotBkend import chatbot

def main():
    st.title("Chichewa and English Chatbot")
    st.write("Enter your questions below in any language, and the chatbot will respond.")

    user_input = st.text_input("Type your question here:")
    
    if st.button("Submit"):
        if user_input.strip() != "":
            response = chatbot(user_input)
            st.json(response)
        else:
            st.write("Please enter a question.")

if __name__ == "__main__":
    main()