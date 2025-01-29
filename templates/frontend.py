import streamlit as st
import sounddevice as sd
import numpy as np
from io import BytesIO
from backend import transcribe_audio, chatbot

st.title("Chichewa and English Multimodal Chatbot")
st.write("Record your question or type it below.")

# Option to select input method
input_method = st.radio("Select input method:", ('Record Audio', 'Type Text'))

# Audio recording method
if input_method == 'Record Audio':
    if st.button("Start Recording"):
        with st.spinner("Recording..."):
            # Record for a fixed duration
            duration = 5  # seconds
            samplerate = 16000
            audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
            sd.wait()
            st.success("Recording complete!")
            audio_buffer = BytesIO()
            np.save(audio_buffer, audio_data)
            audio_buffer.seek(0)
            
            # Transcribe audio
            st.text("Transcribing...")
            transcribed_text = transcribe_audio(audio_buffer.getvalue())

    if 'transcribed_text' in locals():
        st.write(f"Transcribed Text: {transcribed_text}")
        response = chatbot(transcribed_text)
        st.json(response)

# Text input method
elif input_method == 'Type Text':
    user_input = st.text_input("Type your question here:")
    if user_input:
        response = chatbot(user_input)
        st.json(response)