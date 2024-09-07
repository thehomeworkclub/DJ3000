import os
import eyed3

def getnames(directory):
    song_names = []
    for file_name in os.listdir(directory):
        if file_name.endswith(".mp3"):
            file_path = os.path.join(directory, file_name)
            try:
                audio = eyed3.load(file_path)
                if audio.tag and audio.tag.title:
                    song_names.append(audio.tag.title)
                else:
                    song_names.append("Unknown")
            except Exception as e:
                print(f"Error processing {file_name}: {e}")
    return song_names

directory = ".//Music"
song_names = getnames(directory)
print("Song names:")
for song_name in song_names:
    print(song_name)
