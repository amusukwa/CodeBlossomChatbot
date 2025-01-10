import streamlit as st
from audiobackend import record_audio, transcribe_audio, chatbot

def main():
    st.title("Chichewa and English Multimodal Chatbot")
    st.write("Record your question or type it below.")

    # Option to select input method
    input_method = st.radio("Select input method:", ('Record Audio', 'Type Text'))

    # Audio recording method
    if input_method == 'Record Audio':
        if st.button("Start Recording"):
            duration = 5  # Record for 5 seconds
            audio_data = record_audio(duration)
            transcribed_text = transcribe_audio(audio_data)
            st.write(f"Transcribed Text: {transcribed_text}")
            response = chatbot(transcribed_text)
            st.json(response)

    # Text input method
    elif input_method == 'Type Text':
        user_input = st.text_input("Type your question here:")
        if user_input:
            response = chatbot(user_input)
            st.json(response)

if __name__ == "__main__":
    main()