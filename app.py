import streamlit as st
from gen import chat,transcription  # Import the chat function from your gen.py
import base64
import time
import tempfile
def autoplay_audio(audio_bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
    <audio autoplay>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)    
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