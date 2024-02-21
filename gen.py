from openai import OpenAI
from dotenv import load_dotenv
import os
from elevenlabs import clone, set_api_key, voices
import requests
from pydub import AudioSegment
from pydub.playback import play
import io
import json
import tempfile
from playsound import playsound

load_dotenv()


set_api_key(os.getenv("11LABS_API_KEY"))    
client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))


context = [{"role": "system", "content": """"You are a helpful AI chatbot. The user will send 2 types of requests:
             1) A normal conversation with you
             2) Ask to talk to a different person
             
             Your Job is to return a response in a json object in the following format:
             {
             'response' : Answer the question
             'person' : whoever the last requested person to talk to was asked by the user
             }
             The 'person' object will start with the value 'Default' and will only change if the user asks for it
             """
             }]


def normalize_text(text):
    return text.lower()

def audio(message, person):
    voicess = voices()
    search_terms_normalized = [normalize_text(word) for word in person.split()]
    default_voice_id = None 
    for voice in voicess:
        if normalize_text(voice.name) == "rachel": 
            default_voice_id = voice.voice_id
            break

    for voice in voicess:
        voice_name_normalized = [normalize_text(word) for word in voice.name.split()]
        try:
            if any(term in voice_name_normalized for term in search_terms_normalized) or any(name in search_terms_normalized for name in voice_name_normalized):
                return generate_audio(voice.voice_id, message)  
        except Exception as e:
            print(e)

    if default_voice_id is not None:
        return generate_audio(default_voice_id, message)
    else:
        print("Default voice 'Rachel' not found.")
        return None, None

def generate_audio(voice_id, message):
    """Function to generate audio from the given voice ID and message."""
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
    headers = {
        'accept': 'audio/mpeg',
        'xi-api-key': os.getenv("11LABS_API_KEY"),  
        'Content-Type': 'application/json',
    }
    data = {
        "text": message,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0, "use_speaker_boost": True
        },
        "model_id": "eleven_multilingual_v2",
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return io.BytesIO(response.content), "audio/mp3"
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None, None

def play_audio(audio_bytes):
    audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        audio_segment.export(tmpfile.name, format="mp3")
        playsound(tmpfile.name)
        os.remove(tmpfile.name)


def chat(prompt):
  context.append({"role" : "user", "content" : prompt})
  completion = client.chat.completions.create(
      model="gpt-4-0125-preview",
      messages=context,
      max_tokens=4096,
      response_format={ "type": "json_object" }
  )
  result = completion.choices[0].message.content
  context.append({"role" : "assistant", "content" : result})
  data = json.loads(result)
  response = data["response"]
  person = data["person"]  
  gen_audio = audio(response, person)
  return response, gen_audio

    
def transcription(audio):
    audio_file = open(audio, "rb")
    transcript = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file, 
    response_format="text"
)
    return transcript

if __name__ == "__main__":
  while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit","exit","bye"]:
      break
    response, audio_data = chat(user_input)
    print("Chat: ", response)
    if audio_data:
        gen_audio_bytes_io, content_type = audio_data
        play_audio(gen_audio_bytes_io.getvalue()) 