from model import *
from main import *
import random
import time
import os
import uuid
from pydub import AudioSegment
import boto3

# Global Vars

SESSION_ID = uuid.uuid4()
LAST_SESSION_TIME = time.time()
DIRECTORY = ".//mymusic"
LAST_COMPLETED_SONG_INDEX = 0
CURRENT_SEGMENT = 0
LOOPING_ENABLED = False
FINISHED = False
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

# SETUP BOTO
s3 = boto3.client(
    service_name ="s3",
    endpoint_url = os.environ.get("S3_BUCKET"),
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name="auto", # Must be one of: wnam, enam, weur, eeur, apac, auto
)
# DELETE LAST SESSION

Segments.delete().where(Segments.session_id != SESSION_ID).execute()

# INTRO

segment_audio = create_intro_audio() + AudioSegment.silent(duration=2000)

# Define first_song_transition function
def first_song_transition(first_song, first_announcement, second_song, fade_duration=600):
    first_song_duration = len(first_song)
    first_announcement_half = first_announcement[:len(first_announcement) // 2]
    first_song_with_announcement = first_song.fade_out(fade_duration).overlay(first_announcement_half, position=(first_song_duration - len(first_announcement_half)))

    ms2_second_song = second_song[:200] - 12
    ms3_second_song = second_song[200:].fade_in(fade_duration)

    full_second_song = ms2_second_song + ms3_second_song

    first_announcement_second_half = first_announcement[len(first_announcement) // 2:]
    second_song_with_announcement = full_second_song.overlay(first_announcement_second_half)

    return first_song_with_announcement + second_song_with_announcement

# FIRST SONG
def generate_weather_report(prompt, location="Irvine, California"):
    api_key = os.getenv("WEATHER_API_KEY")  
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=imperial"
    
    try:
        response = requests.get(weather_url)
        weather_data = response.json()
        if response.status_code == 200 and "main" in weather_data:
            temperature = weather_data["main"]["temp"]
            high_temp = weather_data["main"]["temp_max"]
            low_temp = weather_data["main"]["temp_min"]
            description = f"Today the weather in {location} is {temperature}°F with highs of {high_temp}°F and lows of {low_temp}°F."
            
            weather_report = [[description, "Only report about the weather. DO NOT add anything else to the list!"]]
            
            news_audio = news(prompt, json.dumps(weather_report))
            return news_audio
        else:
            print(f"Failed to fetch weather data for {location}: {response.status_code}")
    except Exception as e:
        print(f"Error while generating weather report: {e}")
    
    return None


song_titles_unshuffled, song_paths_unshuffled = get_song_titles(DIRECTORY)
song_titles, song_paths = shuffle_corresponding_arrays(song_titles_unshuffled, song_paths_unshuffled)


if len(song_titles) > 1:
    first_song_title = song_titles[0]
    second_song_title = song_titles[1]
    first_song_intro_audio = create_first_song_intro(first_song_title)
    first_song_audio = AudioSegment.from_mp3(song_paths[0])
    second_song_audio = AudioSegment.from_mp3(song_paths[1])

    transition_phrase = random.choice(voice_phrases["song_transitions"]).format(song_title=first_song_title, next_song_title=second_song_title)
    transition_file = os.path.join(chatter_dir, "first_transition.mp3")
    voice_id = ELEVEN_LABS_VOICE_ID_1

    fallback_text = f"That was {first_song_title}, and up next is {second_song_title}."
    success = elevenlabs_tts(transition_phrase, transition_file, voice_id, fallback_text=fallback_text)

    if success and os.path.exists(transition_file):
        transition_audio = AudioSegment.from_mp3(transition_file)
        segment_audio = segment_audio + first_song_transition(first_song_audio, transition_audio, second_song_audio)
        print(f"Added transition between first and second song")

    for index in range(1, len(song_titles) - 1):
        if segment_audio.duration_seconds > 1800:
            break

        song_title = song_titles[index]
        next_song_title = song_titles[index + 1]

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
        if random.randint(1, 4) == 1:
            print("Generating News")
            resp = requests.get("https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml")
            xml_parse = ET.fromstring(resp.text)
            items = xml_parse.findall("channel/item")
            headlines = []
            for item in items:
                headlines.append([item.find("title").text, item.find("description").text])
            try:
                news_audio = news(prompt, str(random.choice(headlines)))
            except:
                print("Failed to generate news")
                    
        if random.randint(1, 4) == 1:
            insane_chatter_audio = generate_inane_chatter()
            segment_audio = segment_audio + insane_chatter_audio

        LAST_COMPLETED_SONG_INDEX = index + 1

# SET LOOPING 
if LOOPING_ENABLED:
    if LAST_COMPLETED_SONG_INDEX == len(song_titles)-1:
        LAST_COMPLETED_SONG_INDEX = 0
else:
    if LAST_COMPLETED_SONG_INDEX == len(song_titles)-1:
        FINISHED = True

CURRENT_SEGMENT += 1
segment_audio.export(f"segment_{CURRENT_SEGMENT}_{str(SESSION_ID)}.wav", format="wav")
fle = open(f"segment_{CURRENT_SEGMENT}_{str(SESSION_ID)}.wav", "rb")
s3.upload_fileobj(fle, "dj3000", f"segment_{CURRENT_SEGMENT}_{str(SESSION_ID)}.wav")
Segments.create(segment_name=f"segment_{CURRENT_SEGMENT}_{str(SESSION_ID)}", session_id=SESSION_ID, time_start=LAST_SESSION_TIME, time_end=LAST_SESSION_TIME + segment_audio.duration_seconds, last_song_index=LAST_COMPLETED_SONG_INDEX)
LAST_SESSION_TIME += segment_audio.duration_seconds

print(f"Segment {CURRENT_SEGMENT} created and uploaded to S3")

print("FINISHED:" + str(FINISHED))
print("LAST_COMPLETED_SONG_INDEX:" + str(LAST_COMPLETED_SONG_INDEX))
print("TOTAL SONGS:" + str(len(song_titles)))

# MID SEGMENTS

while True:
    if FINISHED:
        break
    if LAST_SESSION_TIME - time.time() < 300:
        segment_audio = AudioSegment.silent(duration=1000) + create_mid_show_intro(time=time.strftime("%I:%M %p", time.localtime(time.time() + 300))) + AudioSegment.silent(duration=2000)
        while True:
            for index in range(LAST_COMPLETED_SONG_INDEX, len(song_titles) - 1):
                if segment_audio.duration_seconds > 1800:
                    break
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

                    segment_audio = segment_audio + transition_with_fade(song_audio, transition_audio, next_song_audio)
                    print(f"Added transition and song for {song_title}")
                    
                if random.randint(1, 4) == 1:
                    print("Generating News")
                    resp = requests.get("https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml")
                    xml_parse = ET.fromstring(resp.text)
                    items = xml_parse.findall("channel/item")
                    headlines = []
                    for item in items:
                        headlines.append([item.find("title").text, item.find("description").text])
                    try:
                        news_audio = news(prompt, str(random.choice(headlines)))
                    except:
                        print("Failed to generate news")
                    
                if random.randint(1, 4) == 1:
                    insane_chatter_audio = generate_inane_chatter()
                    segment_audio = segment_audio + insane_chatter_audio
                LAST_COMPLETED_SONG_INDEX = index + 1
            if segment_audio.duration_seconds > 1800:
                break
            else:
                if LOOPING_ENABLED:
                    if LAST_COMPLETED_SONG_INDEX == len(song_titles)-1:
                        song_titles_unshuffled, song_paths_unshuffled = get_song_titles(DIRECTORY)
                        song_titles, song_paths = shuffle_corresponding_arrays(song_titles_unshuffled, song_paths_unshuffled)
                        LAST_COMPLETED_SONG_INDEX = 0
                else:
                    FINISHED = True
                    break
        CURRENT_SEGMENT += 1
        segment_audio.export(f"segment_{CURRENT_SEGMENT}_{str(SESSION_ID)}.wav", format="wav")
        fle = open(f"segment_{CURRENT_SEGMENT}_{str(SESSION_ID)}.wav", "rb")
        s3.upload_fileobj(fle, "dj3000", f"segment_{CURRENT_SEGMENT}_{str(SESSION_ID)}.wav")
        Segments.create(segment_name=f"segment_{CURRENT_SEGMENT}_{str(SESSION_ID)}", session_id=SESSION_ID, time_start=LAST_SESSION_TIME, time_end=LAST_SESSION_TIME + segment_audio.duration_seconds, last_song_index=LAST_COMPLETED_SONG_INDEX)
        LAST_SESSION_TIME += segment_audio.duration_seconds
        print("FINISHED:" + str(FINISHED))
        print("LAST_COMPLETED_SONG_INDEX:" + str(LAST_COMPLETED_SONG_INDEX))
        print("TOTAL SONGS:" + str(len(song_titles)))
    print("Generating Next Segment in: " + str(int(LAST_SESSION_TIME - time.time() - 300)) + " seconds", end="\r")
