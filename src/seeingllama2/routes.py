"""Application routes."""
from flask import render_template, request, send_file
from . import app as main
from .voice import generate_sound_file


@ main.route("/")
def index() -> str:
    # Needs to implement a mechanism to restore the previous session
    # if the user is already connected
    return render_template(
        "index.htm", **main.config['config']['html_index'])


@ main.route('/a')
def generate_audio():
    """Generate an audio file from text.

    Returns:
        Response: the audio file
    """
    text = request.args.get('text', '')
    voice = int(request.args.get('voice', '0'))
    rate = float(request.args.get('rate', '200'))
    volume = float(request.args.get('volume', '1'))

    return send_file(generate_sound_file(
        text=text, voice=voice, rate=rate, volume=volume),
        download_name='sound.mp3')
