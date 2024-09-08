# DJ3000 Radio Project

---

## Overview
The DJ3000 project was inspired when a team member was watching the Simpsons and was inspired by a futuristic robot introduced as a joke - the DJ3000. Built to replace the jobs of radio station hosts, the DJ3000 "plays CD's automatically" and even replaces the entertainment values of radio hosts with "three distinct varieties of inane chatter. 'Hey hey! What about that weather out there?' 'Woah... that was the caller from Hell' 'Well hot dog! We have a wiener!' ... 'Wow, looks like those clowns in Congress did it again!'" - The Simpsons, Bart Gets an Elephant. We have not only brought the futuristic machine to life, but have improved its humanness and made it small enough to fit in your pocket.
This system uses **Python**, **Pydub**, **ElevenLabs API**, and a Raspberry Pi to create seamless, AI-driven radio shows that can be transmitted live over FM frequencies.

---

## Features
- **Playlist Management**: DJ3000 shuffles a playlist of user-supplied music files.
- **AI DJ Chatter**: AI-generated back-and-forth chatter between DJ personalities, providing a humorous, lifelike experience.
- **Song Transitions**: Smooth crossfades between songs with DJ commentary.
- **FM Broadcast**: Generated `.wav` files are transmitted over FM frequencies using a Raspberry Pi.
  
---

## How it Works
1. **Playlist Generation**: The user adds songs to a playlist. DJ3000 shuffles the songs and ensures no repeats occur.
2. **AI Voices**: The ElevenLabs API is used to generate DJ-style voice commentary, which is added between songs.
3. **Song Transitions**: The system handles crossfading between songs and the insertion of AI-generated chatter.
4. **WAV File Generation**: DJ3000 exports the entire radio show as a `.wav` file.
5. **FM Broadcast**: Using `fm_transmitter`, the `.wav` file is broadcast via FM on a Raspberry Pi.

---

## Installation

### Requirements
- **Python 3.x**
- **Pydub**: For audio manipulation.
- **ElevenLabs API**: For AI voice generation.
- **Raspberry Pi**: For FM broadcasting (Pi 4 reccomended).
- **fm_transmitter**: A tool to broadcast `.wav` files over FM using a Raspberry Pi.

### Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/dj3000-radio.git
   cd dj3000-radio
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up ElevenLabs API**:
   - Obtain an API key from [ElevenLabs](https://elevenlabs.io).
   - Create a `.env` file in the project root and add your API key:
     ```bash
     ELEVEN_LABS_API_KEY=your_api_key_here
     ```

4. **Install fm_transmitter on Raspberry Pi**:
   Follow the installation steps in the [fm_transmitter repository](https://github.com/markondej/fm_transmitter).

---

## Usage

1. **Add Songs**:
   Place your `.mp3` files into the `Music` folder.

2. **Run the DJ3000 Script**:
   ```bash
   python sequential.py
   ```

   This will generate a `.wav` file that contains the radio show.

3. **Broadcast via FM**:
   ```bash
   sudo ./fm_transmitter -f 100.1 segment_1.wav
   ```
   Replace `100.1` with your desired FM frequency.

---

## File Structure

```bash
├── Music/                   # Place your .mp3 files here
├── chatter/                 # AI-generated DJ chatter files
├── sequential.py            # Main Python script
├── main.py                  # Handles AI voice generation and transitions
├── model.py                 # Handles database and segments
├── requirements.txt         # Python dependencies
├── .env                     # API keys and environment variables
└── README.md                # Project documentation
```

---

## Example Query

Here’s an example of how the system generates a playlist and transitions between songs:

```python
{
  getPlaylist {
    id
    title
    artist
    duration
    filePath
  }
}
```

---

## Planned Features
- **Enhanced Song Metadata**: Use AI to announce the song title and artist in real-time.
- **Real-time Playlist Updates**: Modify the playlist while the broadcast is live.
- **Improved FM Broadcasting**: Enhance the signal range of the Raspberry Pi FM transmission.

---

## Built With
- **Python**: For managing audio and running the core logic.
- **Pydub**: For slicing and mixing audio files.
- **ElevenLabs API**: For generating AI voice commentary.
- **fm_transmitter**: For broadcasting `.wav` files over FM via Raspberry Pi.

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

