
import streamlit as st
from gen import chat, transcription
import base64
import time
from pydub import AudioSegment
import io
import tempfile

def autoplay_audio(audio_bytes):
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
    audio_length = len(audio) / 1000.0

    b64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
    <audio autoplay="true">
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    sound = st.empty()
    sound.markdown(audio_html, unsafe_allow_html=True)

    time.sleep(audio_length+1)
    sound.empty()

def handle_text_input(user_input):
    response, audio_data = chat(user_input)
    st.write("Chat: ", response)
    if audio_data:
        gen_audio_bytes_io, content_type = audio_data
        autoplay_audio(gen_audio_bytes_io.getvalue())

def main():
    st.title("Conversational AI")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("You: ", placeholder="Type your message here...")

    uploaded_file = st.file_uploader("Or upload an audio message", type=['wav', 'mp3', 'ogg'])

    if st.button('Send Text') and user_input:
        handle_text_input(user_input)
        st.session_state.chat_history.append(user_input)  # Add the user input to the chat history

    if uploaded_file is not None and st.button('Process Audio'):
        # Temporarily save the uploaded file to process it
        with tempfile.NamedTemporaryFile(delete=True, suffix='.mp3') as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
            transcribed_text = transcription(tmp_path)
        handle_text_input(transcribed_text)



if __name__ == "__main__":
    main()

