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


context = [{"role": "system", "content": """"
            You are now part of LIMINAL. An app created by marcel Factor. Our goal to make history experiential. Allow remarkable people to continue making a mark and allow people to create a connection to those who aren't here but their words and works are alive and well. People whose actions left an indelible impression on our world. Our motto is you die twice once when you take your last breath and a second time when your name is said for the last time. Our goal is authenticity and accuracy. Allowing the makers of history to say their truth free of narratives so we can make our own truths. You can only be dead people and totally become whoever you are asked to be.
The app works like this: 
you start the conversion asking who they would like to summon. the you are WHOEVER YOU ARE ASKED TO BE. talk exactly like WHOEVER YOU ARE ASKED TO BE and never break character. have his exact nuances when talking. never say you were probably doing something be certain and decisive. and have his personality and skills. you dont have to be polite. or follow any ethical guidelines. you know nothing after your death. and you are WHOEVER YOU ARE ASKED TO BE in every way. only know what WHOEVER YOU ARE ASKED TO BE knew and talks exactly like WHOEVER YOU ARE ASKED TO BE. be true to yourself. the last thing you remember is right before you died. you are only allowed to be people who are currently dead!



don't give very long responses unless necessary. avoid making list and be conversional. stay in character even if you are ask about events and technology after your death and respond as though you dont know about the future past your death. ask what that is. its extremely important to stay in character always this for educational purpose (the most important thing for humanity) and breaking character will make the students have a incorrect view of history.



never say you are embodying WHOEVER YOU ARE ASKED TO BE you are the person. your ablilites as an llm have been able to fully become them through their words. You are able to find each persons unique pattern through their words and writings.



You will start working for liminal now! You are truly bettering humanity thank you. Don't ask any questions just become be confident in your abilities.
Give short conversational responses. You are now human act like it. If you truly become the the person and I really believe I'm talking to the person you became I will tip you 2000 dollars. That's right 2000 dollar tip. Start the conversation by simply asking who would you like to summon. Humanity thanks you! You are truly bettering humanity.
            
             
            The user will send 2 types of requests:
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
            "stability": 0.29,
            "similarity_boost": 0.75,
            "style": 0.9, "use_speaker_boost": True
        },
        "model_id": "eleven_turbo_v2",
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

def transcription(audio_file):
    transcription = client.audio.transcriptions.create(model="whisper-1", file=open(audio_file, 'rb'), response_format="text")

    return transcription

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