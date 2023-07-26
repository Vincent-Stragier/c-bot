"""Text to speech module."""
import io
import os
import tempfile

import pyttsx4

# Import text to speech engine
engine_tts = pyttsx4.init()


def generate_sound_file(text: str, voice: int, rate: float = 200, volume: float = 1.0) -> io.BytesIO:
    """Generate a sound file from text.

    Args:
        text (str): the text to convert to speech
        voice (int): the voice to use
        rate (float): the rate of the speech (default is 200 words per minute)
        volume (float): the volume of the speech (default is 1.0)

    Returns:
        BytesIO: the sound file
    """
    temp_file = io.BytesIO()
    with tempfile.TemporaryDirectory() as temp_dir:

        # Set the voice
        voice = engine_tts.getProperty('voices')[voice]
        engine_tts.setProperty('voice', voice.id)
        # Default is 200 words per minute
        engine_tts.setProperty('rate', rate)
        engine_tts.setProperty('volume', volume)

        # Save the file
        file_name = os.path.join(temp_dir, 'sound.mp3')
        engine_tts.save_to_file(text, file_name)
        engine_tts.runAndWait()

        while not os.listdir(temp_dir):
            # Wait for the file to be created
            pass

        # Read the file
        with open(file_name, 'rb') as audio_file:
            temp_file = io.BytesIO(audio_file.read())

    return temp_file
