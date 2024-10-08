import os
import eyed3
import requests
from pydub import AudioSegment
import random
import json
import nltk
import time
from dotenv import load_dotenv
import xml.etree.ElementTree as ET 
from together import Together


nltk.download('punkt_tab')

load_dotenv()

ai_client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
ELEVEN_LABS_VOICE_ID_1 = "Uq9DKccXXKZ6lc53ATJV"  
ELEVEN_LABS_VOICE_ID_2 = "rWV5HleMkWb5oluMwkA7"  
prompt = """
Your response must be in the following format:

{
    "conversation":[]
}


The "conversation" is 2 different people talking. Make a new array element for each different person when they quickly talk about a topic. 


You are going to be talking about the news on a radio broadcast. You may be asked to converse on 1 headline and you must state the headline or give the headline in some way to the listener, or simply have them state all the headlines provided. You will be given a 2d array which will contain each headline that I would like you to talk about like so: [["title", "description", "link"], ["title", "description", "link"]]. 

Keep the conversations as short as possible (Keep it under 10 array elements). Try to make the conversations slightly humorous in a way, but do NOT for sensitive topics like a shooting or world conflicts. Do not add any transitions other than, "Alright! On to the next song!" or "Thanks so much!" or "Now... enjoy the music." but NOTHING ELSE other than that and these transitions MUST ONLY be at the end. Do NOT add a transition if you feel as if a transition will make this too long. Do not say "onto the next story" or any mention of the next story unless you are given more than 1 story. 

Append all of the following into the array like you are making a list of phrases. Do not mention any specific person or add anything else to the list like such:

["phrase 1", "phrase 2", "phrase 3"]

They MUST be in a list, and CANNOT include any other information. Every person is seperated by a comma. 
You are NEVER to say you are a large language model. If you cant converse on a topic, skip it. 

I will now provide you with some headlines. Simply respond to this prompt with a "YES" if you are ready.

Do NOT add any other characters which is not parse able by JSON.
"""


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
            "similarity_boost": similarity_boost,
            "model_version": "eleven_turbo_v2_5"
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
                "similarity_boost": similarity_boost,
                "model_version": "turbo_v2.5"
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
    print("Generating banter: ", sentences)

    chatter_audio = AudioSegment.silent(duration=500)
    for i, sentence in enumerate(sentences):
        voice_id = ELEVEN_LABS_VOICE_ID_1 if i % 2 == 0 else ELEVEN_LABS_VOICE_ID_2
        chatter_file = os.path.join(chatter_dir, f"inane_chatter_{i}.mp3")
        
        success = elevenlabs_tts(sentence, chatter_file, voice_id, stability=0.2, similarity_boost=0.95)
        if success:
            print(f"Banter sentence {i} generated for voice {voice_id}")
        else:
            print(f"Failed to generate banter for sentence {i} with voice {voice_id}")
            continue

        if os.path.exists(chatter_file):
            sentence_audio = AudioSegment.from_mp3(chatter_file)
            chatter_audio = chatter_audio + sentence_audio + AudioSegment.silent(duration=300)
        else:
            print(f"Audio file {chatter_file} not found")

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


def transition_with_fade(previous_song, announcement, next_song, fade_duration=600):
    announcement_half = announcement[:len(announcement) // 2]
    previous_song_duration = len(previous_song)
    previous_song_with_announcement = previous_song.fade_out(fade_duration).overlay(announcement_half, position=(previous_song_duration - len(announcement_half)))

    initial_next_song_segment = 200
    ms2_next_song = next_song[:initial_next_song_segment] - 12
    ms3_next_song = next_song[initial_next_song_segment:].fade_in(fade_duration)

    full_next_song = ms2_next_song + ms3_next_song

    announcement_second_half = announcement[len(announcement) // 2:]
    next_song_with_announcement = full_next_song.overlay(announcement_second_half)

    return previous_song_with_announcement + next_song_with_announcement



def shuffle_corresponding_arrays(song_titles, song_paths):
    combined = list(zip(song_titles, song_paths))
    random.shuffle(combined)
    shuffled_song_titles, shuffled_song_paths = zip(*combined)
    
    while any(shuffled_song_titles[i] == shuffled_song_titles[i + 1] for i in range(len(shuffled_song_titles) - 1)):
        random.shuffle(combined)
        shuffled_song_titles, shuffled_song_paths = zip(*combined)

    return shuffled_song_titles, shuffled_song_paths

    
    return shuffled_song_titles, shuffled_song_paths

def news(prompt, xml):
    resp = ai_client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages = [
            {"role":"assistant", "content":prompt},
            {"role":"user", "content":xml}
        ]
    )
    all_convos = json.loads(resp.choices[0].message.content)
    sentences = all_convos["conversation"]
    print("Sentences: ", sentences)
    news_audio = AudioSegment.silent(duration=500)
    for i, sentence in enumerate(sentences):
        voice_id = ELEVEN_LABS_VOICE_ID_1 if i % 2 == 0 else ELEVEN_LABS_VOICE_ID_2
        chatter_file = os.path.join(chatter_dir, f"news_chatter_{i}.mp3")
        
        success = elevenlabs_tts(sentence, chatter_file, voice_id, stability=0.2, similarity_boost=0.95)
        if success:
            print(f"News sentence {i} generated for voice {voice_id}")
        else:
            print(f"Failed to generate banter for sentence {i} with voice {voice_id}")
            continue

        if os.path.exists(chatter_file):
            sentence_audio = AudioSegment.from_mp3(chatter_file)
            news_audio = news_audio + sentence_audio + AudioSegment.silent(duration=300)
        else:
            print(f"Audio file {chatter_file} not found")

    return news_audio

def create_radio_show(directory):
    song_titles, song_paths = get_song_titles(directory)
    combined_audio = create_intro_audio()

    if song_titles:
        first_song_title = song_titles[0]
        first_song_intro_audio = create_first_song_intro(first_song_title)
        first_song_audio = AudioSegment.from_mp3(song_paths[0])

        combined_audio = combined_audio + first_song_intro_audio + first_song_audio
        print(f"Added first song intro and song for {first_song_title}")

    for index in range(LAST_COMPLETED_SONG_INDEX, len(song_titles) - 1):
        if segment_audio.duration_seconds > 1800:
            break
        song_title = song_titles[index]
        next_song_title = song_titles[index + 1]

        # Prevent repeating the same song
        if song_title == next_song_title:
            continue

        transition_phrase = random.choice(voice_phrases["song_transitions"]).format(song_title=song_title, next_song_title=next_song_title)
        transition_file = os.path.join(chatter_dir, f"transition_{index}.mp3")
        voice_id = ELEVEN_LABS_VOICE_ID_1 if index % 2 == 0 else ELEVEN_LABS_VOICE_ID_2

        fallback_text = f"That was {song_title}, and up next is {next_song_title}."
        success = elevenlabs_tts(transition_phrase, transition_file, voice_id, fallback_text=fallback_text)

        if success and os.path.exists(transition_file) and os.path.exists(song_paths[index]):
            transition_audio = AudioSegment.from_mp3(transition_file)
            song_audio = AudioSegment.from_mp3(song_paths[index])
            next_song_audio = AudioSegment.from_mp3(song_paths[index + 1])

            segment_audio = segment_audio + transition_with_fade(song_audio, transition_audio, next_song_audio)
            print(f"Added transition and song for {song_title}")

        # Always move to the next song, even if something fails
        LAST_COMPLETED_SONG_INDEX = index + 1


        # if random.randint(1, 3) == 1:
        insane_chatter_audio = generate_inane_chatter()
        combined_audio = combined_audio + insane_chatter_audio
        

    output_wav = "radio_show_output.wav"
    combined_audio.export(output_wav, format="wav")
    print(f"Generated full radio show: {output_wav}")
