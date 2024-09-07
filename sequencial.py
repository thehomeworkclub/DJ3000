from model import *
from main import *
import random
import time
import os
import uuid
from pydub import AudioSegment

# Start Sequential

# Global Vars

SESSION_ID = uuid.uuid4()
LAST_SESSION_TIME = time.time()
DIRECTORY = ".//Music"
LAST_COMPLETED_SONG_INDEX = 0
CURRENT_SEGMENT = 0

# DELETE LAST SESSION

Segments.delete().where(Segments.session_id != SESSION_ID).execute()

# INTRO

segment_audio = create_intro_audio() + AudioSegment.silent(duration=2000)

# FIRST SONG

song_titles, song_paths = get_song_titles(DIRECTORY)

if song_titles:
        # TODO: Shuffle Songs
        first_song_title = song_titles[0]
        first_song_intro_audio = create_first_song_intro(first_song_title)
        first_song_audio = AudioSegment.from_mp3(song_paths[0])

        segment_audio = segment_audio + (first_song_intro_audio.append(first_song_audio, crossfade=2000))
        
        print(f"Added first song intro and song for {first_song_title}")

        for index in range(0, len(song_titles) - 1):
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
            
            if random.randint(1, 3) == 1:
                insane_chatter_audio = generate_inane_chatter()
                segment_audio = segment_audio + insane_chatter_audio
                
            LAST_COMPLETED_SONG_INDEX = index + 1

# SET LOOPING 

if LAST_COMPLETED_SONG_INDEX == len(song_titles):
    LAST_COMPLETED_SONG_INDEX = 0

Segments.create(segment_name="segment_" + str(CURRENT_SEGMENT), session_id=SESSION_ID, time_start=LAST_SESSION_TIME, time_end=LAST_SESSION_TIME + segment_audio.duration_seconds, last_song_index=LAST_COMPLETED_SONG_INDEX)
CURRENT_SEGMENT += 1
LAST_SESSION_TIME += segment_audio.duration_seconds
segment_audio.export(f"segment_{CURRENT_SEGMENT}.wav", format="wav")
print(f"Segment {CURRENT_SEGMENT} created")

# MID SEGMENTS

while True:
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
                
                if random.randint(1, 3) == 1:
                    insane_chatter_audio = generate_inane_chatter()
                    segment_audio = segment_audio + insane_chatter_audio
                    
                LAST_COMPLETED_SONG_INDEX = index + 1
            if segment_audio.duration_seconds > 1800:
                break
            else:
                print("Radio is Looping")
                LAST_COMPLETED_SONG_INDEX = 0
        
        Segments.create(segment_name="segment_" + str(CURRENT_SEGMENT), session_id=SESSION_ID, time_start=LAST_SESSION_TIME, time_end=LAST_SESSION_TIME + segment_audio.duration_seconds, last_song_index=LAST_COMPLETED_SONG_INDEX)
        CURRENT_SEGMENT += 1
        LAST_SESSION_TIME += segment_audio.duration_seconds
        segment_audio.export(f"segment_{CURRENT_SEGMENT}.wav", format="wav")


