import os
import eyed3
import requests
from pydub import AudioSegment
import random
import json
import nltk
import time
from dotenv import load_dotenv

nltk.download('punkt_tab')

load_dotenv()

ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
ELEVEN_LABS_VOICE_ID_1 = "Uq9DKccXXKZ6lc53ATJV"  
ELEVEN_LABS_VOICE_ID_2 = "rWV5HleMkWb5oluMwkA7"  


chatter_dir = "chatter"
if not os.path.exists(chatter_dir):
    os.makedirs(chatter_dir)

with open("voice_phrases.json", "r") as f:
    voice_phrases = json.load(f)

def elevenlabs_tts(text, output_file, voice_id, stability=0.2, similarity_boost=0.85, retries=3, fallback_text=""):
    url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVEN_LABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost
        }
    }
    
    for attempt in range(retries):
        response = requests.post(url.format(voice_id=voice_id), headers=headers, json=data)
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"Saved TTS to {output_file}")
            return True
        else:
            print(f"Failed to generate TTS (attempt {attempt + 1}/{retries}): {response.text}")
            time.sleep(1)  

    print(f"Failed to generate TTS after {retries} attempts.")
    

    if fallback_text:
        print(f"Using fallback text for transition: {fallback_text}")
        fallback_data = {
            "text": fallback_text,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost
            }
        }
        response = requests.post(url.format(voice_id=voice_id), headers=headers, json=fallback_data)
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"Saved fallback TTS to {output_file}")
            return True

    return False

def create_intro_audio():
    bob_intro = "Hey there, and welcome to DJ3000 radio - all day, every day, 24 7. I'm Bob."
    ryan_intro = "And I'm Ryan, and this is DJ3000!"

    bob_intro_file = os.path.join(chatter_dir, "bob_intro_radio.mp3")
    ryan_intro_file = os.path.join(chatter_dir, "ryan_intro_radio.mp3")

    elevenlabs_tts(bob_intro, bob_intro_file, ELEVEN_LABS_VOICE_ID_1)
    elevenlabs_tts(ryan_intro, ryan_intro_file, ELEVEN_LABS_VOICE_ID_2)

    bob_audio = AudioSegment.from_mp3(bob_intro_file)
    ryan_audio = AudioSegment.from_mp3(ryan_intro_file)

    return bob_audio + ryan_audio

def create_mid_show_intro(time):
    bob_intro = "Yo yo! The time is " + str(time) + " and you're listening to DJ3000 radio. I'm Bob."
    ryan_intro = "And I'm Ryan! Thanks for tuning in to DJ3000, lets keep going with that music!!"

    bob_intro_file = os.path.join(chatter_dir, "bob_mid_show_radio.mp3")
    ryan_intro_file = os.path.join(chatter_dir, "ryan_late_show_radio.mp3")

    elevenlabs_tts(bob_intro, bob_intro_file, ELEVEN_LABS_VOICE_ID_1)
    elevenlabs_tts(ryan_intro, ryan_intro_file, ELEVEN_LABS_VOICE_ID_2)

    bob_audio = AudioSegment.from_mp3(bob_intro_file)
    ryan_audio = AudioSegment.from_mp3(ryan_intro_file)

    return bob_audio + ryan_audio

def generate_inane_chatter():
    conversation = random.choice(voice_phrases["inane_chatter"])["conversation"]
    sentences = nltk.sent_tokenize(conversation)
    print(sentences)

    chatter_audio = AudioSegment.silent(duration=500)

    for i, sentence in enumerate(sentences):
        voice_id = ELEVEN_LABS_VOICE_ID_1 if i % 2 == 0 else ELEVEN_LABS_VOICE_ID_2
        chatter_file = os.path.join(chatter_dir, f"inane_chatter_{i}.mp3")
        elevenlabs_tts(sentence, chatter_file, voice_id, stability=0.2, similarity_boost=0.95)
        sentence_audio = AudioSegment.from_mp3(chatter_file)
        chatter_audio = chatter_audio + sentence_audio + AudioSegment.silent(duration=300)

    return chatter_audio

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
    first_song_intro_bob = f"And now, to kick off our session, here's {song_title}! Enjoy the music!"
    first_intro_file = os.path.join(chatter_dir, "first_song_intro.mp3")
    elevenlabs_tts(first_song_intro_bob, first_intro_file, ELEVEN_LABS_VOICE_ID_1, stability=0.4)
    return AudioSegment.from_mp3(first_intro_file)


def transition_with_fade(previous_song, announcement, next_song, fade_duration=2000):
    prev_song_duration = len(previous_song)

    faded_out_song = previous_song.fade_out(fade_duration)

    combined_audio = faded_out_song.overlay(announcement, position=(prev_song_duration - fade_duration))

    half_announcement_duration = len(announcement) // 2
    new_song_fade_in = next_song.fade_in(fade_duration + half_announcement_duration)

    combined_audio = combined_audio.overlay(new_song_fade_in, position=(prev_song_duration + half_announcement_duration))

    return combined_audio

def create_radio_show(directory):
    song_titles, song_paths = get_song_titles(directory)
    combined_audio = create_intro_audio()

    if song_titles:
        first_song_title = song_titles[0]
        first_song_intro_audio = create_first_song_intro(first_song_title)
        first_song_audio = AudioSegment.from_mp3(song_paths[0])

        combined_audio = combined_audio + first_song_intro_audio + first_song_audio
        print(f"Added first song intro and song for {first_song_title}")

    for index in range(1, len(song_titles) - 1):
        song_title = song_titles[index]
        next_song_title = song_titles[index + 1]

        transition_phrase = random.choice(voice_phrases["song_transitions"]).format(song_title=song_title, next_song_title=next_song_title)
        transition_file = os.path.join(chatter_dir, f"transition_{index}.mp3")
        voice_id = ELEVEN_LABS_VOICE_ID_1 if index % 2 == 0 else ELEVEN_LABS_VOICE_ID_2

        fallback_text = f"That was {song_title}, and up next is {next_song_title}."
        success = elevenlabs_tts(transition_phrase, transition_file, voice_id, fallback_text=fallback_text)

        if success and os.path.exists(transition_file) and os.path.exists(song_paths[index]):
            transition_audio = AudioSegment.from_mp3(transition_file)
            song_audio = AudioSegment.from_mp3(song_paths[index])
            next_song_audio = AudioSegment.from_mp3(song_paths[index + 1])

            combined_audio = combined_audio + transition_with_fade(song_audio, transition_audio, next_song_audio)
            print(f"Added transition and song for {song_title}")

        if random.randint(1, 3) == 1:
            insane_chatter_audio = generate_inane_chatter()
            combined_audio = combined_audio + insane_chatter_audio

    output_wav = "radio_show_output.wav"
    combined_audio.export(output_wav, format="wav")
    print(f"Generated full radio show: {output_wav}")
