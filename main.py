import os
import eyed3
import requests
from pydub import AudioSegment
import random
import json

ELEVEN_LABS_API_KEY = "sk_1cab85281e6108cc0c3d914e52234318cdd4290516d0769c"
ELEVEN_LABS_VOICE_ID_1 = "Uq9DKccXXKZ6lc53ATJV"
ELEVEN_LABS_VOICE_ID_2 = "FmJ4FDkdrYIKzBTruTkV"

chatter_dir = "chatter"
if not os.path.exists(chatter_dir):
    os.makedirs(chatter_dir)

with open("voice_phrases.json", "r") as f:
    voice_phrases = json.load(f)

def elevenlabs_tts(text, output_file, voice_id):
    url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVEN_LABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.2,
            "similarity_boost": 0.85
        }
    }
    response = requests.post(url.format(voice_id=voice_id), headers=headers, json=data)
    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"Saved TTS to {output_file}")
    else:
        print(f"Failed to generate TTS: {response.text}")

def create_intro_audio():
    intro_text = (
        "Hey there, and welcome to DJ3000 radio - all day, every day, 24/7. I'm Bob."
        " And I'm Ryan, and this is DJ3000!"
    )
    intro_file = os.path.join(chatter_dir, "intro_radio.mp3")
    elevenlabs_tts(intro_text, intro_file, ELEVEN_LABS_VOICE_ID_1)
    return AudioSegment.from_mp3(intro_file)

def generate_inane_chatter():
    conversation = random.choice(voice_phrases["inane_chatter"])["conversation"]
    chatter_file = os.path.join(chatter_dir, "inane_chatter.mp3")
    elevenlabs_tts(conversation, chatter_file, ELEVEN_LABS_VOICE_ID_1)
    return AudioSegment.from_mp3(chatter_file)

def get_song_titles(directory):
    song_titles = []
    song_paths = []
    for file_name in os.listdir(directory):
        if file_name.endswith(".mp3"):
            file_path = os.path.join(directory, file_name)
            try:
                audio = eyed3.load(file_path)
                if audio.tag and audio.tag.title:
                    song_titles.append(audio.tag.title)
                else:
                    song_titles.append("Unknown")
                song_paths.append(file_path)
            except Exception as e:
                print(f"Error processing {file_name}: {e}")
    return song_titles, song_paths

def create_first_song_intro(song_title):
    first_song_intro = f"And now, to kick off our session, here's {song_title}! Enjoy the music!"
    first_intro_file = os.path.join(chatter_dir, "first_song_intro.mp3")
    elevenlabs_tts(first_song_intro, first_intro_file, ELEVEN_LABS_VOICE_ID_1)
    return AudioSegment.from_mp3(first_intro_file)

def create_radio_show(directory):
    song_titles, song_paths = get_song_titles(directory)
    combined_audio = create_intro_audio()
    if song_titles:
        first_song_title = song_titles[0]
        first_song_intro_audio = create_first_song_intro(first_song_title)
        first_song_audio = AudioSegment.from_mp3(song_paths[0])
        combined_audio = combined_audio + first_song_intro_audio + first_song_audio
        print(f"Added first song intro and song for {first_song_title}")

    for index in range(1, len(song_titles)):
        song_title = song_titles[index]
        next_song_title = song_titles[index + 1] if index + 1 < len(song_titles) else None

        if next_song_title:
            transition_phrase = random.choice(voice_phrases["song_transitions"]).format(song_title=song_title, next_song_title=next_song_title)
            transition_file = os.path.join(chatter_dir, f"transition_{index}.mp3")
            elevenlabs_tts(transition_phrase, transition_file, ELEVEN_LABS_VOICE_ID_2)

            if os.path.exists(transition_file) and os.path.exists(song_paths[index]):
                transition_audio = AudioSegment.from_mp3(transition_file)
                song_audio = AudioSegment.from_mp3(song_paths[index])
                combined_audio = combined_audio + transition_audio + song_audio
                print(f"Added transition and song for {song_title}")

        if random.randint(1, 3) == 1:
            inane_chatter_audio = generate_inane_chatter()
            combined_audio = combined_audio + inane_chatter_audio

    output_wav = "radio_show_output.wav"
    combined_audio.export(output_wav, format="wav")
    print(f"Generated full radio show: {output_wav}")

directory = ".//Music"
create_radio_show(directory)
