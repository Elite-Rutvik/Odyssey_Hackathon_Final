import elevenlabs
from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv

load_dotenv('.env.local')
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

input_text = "Hello world! This is a test message."

def text_to_speech_using_elevenlabs(input_text, output_file_path):
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY) 
    audio = client.generate( 
        text= input_text, 
        voice= "Aria", 
        output_format= "mp3_22050_32", 
        model= "eleven_turbo_v2" 
    )
    elevenlabs.save(audio,output_file_path)

text_to_speech_using_elevenlabs(input_text, output_file_path="output.mp3")
