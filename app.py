import streamlit as st
from gen import chat,transcription  # Import the chat function from your gen.py
import base64
import time
from pydub import AudioSegment
import io
def autoplay_audio(audio_bytes):
    # Convert byte content to audio segment
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
    # Calculate the length of the audio in seconds
    audio_length = len(audio) / 1000.0
    
    b64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
    <audio autoplay="true">
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    sound = st.empty()
    sound.markdown(audio_html, unsafe_allow_html=True)
    
    # Wait for the audio to finish playing
    time.sleep(audio_length)
    
    sound.empty() 
def main():
    st.title("Conversational AI")
    
    user_input = st.text_input("You: ", key="user_input", placeholder="Type your message here...")
    
    if st.button('Send'):
        response, audio_data = chat(user_input)
        st.write("Chat: ", response)
        if audio_data:
            gen_audio_bytes_io, content_type = audio_data
            autoplay_audio(gen_audio_bytes_io.getvalue())

if __name__ == "__main__":
    main()



# if st.button('Send'):
#     response, audio_data = chat(user_input)
#     st.write("Chat: ", response)
#     if audio_data:
#         gen_audio_bytes_io, _ = audio_data
#         autoplay_audio(gen_audio_bytes_io.getvalue())