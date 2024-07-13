# Audio WPM Analyzer

## Description
SpeakingSpeed is a desktop app that measures speaking speed in audio files, and calculates words per minute (WPM).

## Features

- Load and analyze audio files (supports .wav, .mp3, and .m4a formats)
- Display audio waveform visualization
- Calculate Words Per Minute (WPM)
- Show total word count and audio duration
## Requirements

- Python 3.7+
- PySide6
- speech_recognition
- pydub
- numpy
- matplotlib

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yousifj129/SpeakingSpeed.git
   ```

2. Navigate to the project directory:
   ```
   cd SpeakingSpeed
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. Click on "Select Audio File" to choose an audio file for analysis.

3. Once a file is selected, the waveform will be displayed.

4. Click "Analyze" to process the audio and calculate the WPM.

5. The results will be displayed, showing the Words Per Minute, total word count, and audio duration.

## How it works

1. The application uses `pydub` to handle various audio formats and convert them to WAV if necessary.
2. The audio waveform is visualized using `matplotlib`.
3. Speech recognition is performed using the `speech_recognition` library with Google's Speech Recognition API.
4. The word count is calculated from the transcribed text, and WPM is computed based on the audio duration.

## Note

This application requires an internet connection for the speech recognition feature, as it uses Google's Speech Recognition API.