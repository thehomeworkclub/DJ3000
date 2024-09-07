import os
import eyed3
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

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

def text_to_speech(text, output_file):
    tts = gTTS(text)
    tts.save(output_file)

def create_audio_intro(song_title, song_path):
    intro_text = f"Now playing {song_title}. Enjoy the music!"
    intro_file = "intro.mp3"
    text_to_speech(intro_text, intro_file)
    intro_audio = AudioSegment.from_mp3(intro_file)
    song_audio = AudioSegment.from_mp3(song_path)
    combined_audio = intro_audio + song_audio
    end_text = f"The song {song_title} has just ended."
    end_file = "end.mp3"
    text_to_speech(end_text, end_file)
    end_audio = AudioSegment.from_mp3(end_file)
    final_audio = combined_audio + end_audio
    output_wav = f"{song_title}_output.wav"
    final_audio.export(output_wav, format="wav")
    
    print(f"Generated {output_wav}")
directory = ".//Music"
song_titles, song_paths = get_song_titles(directory)
print("Processing songs...")

for song_title, song_path in zip(song_titles, song_paths):
    create_audio_intro(song_title, song_path)
