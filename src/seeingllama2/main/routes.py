"""Application routes."""
from flask import current_app, render_template, request, send_file

from . import main
from .voice import generate_sound_file


@main.route("/", methods=["GET"])
def index() -> str:
    # Needs to implement a mechanism to restore the previous session
    # if the user is already connected
    return render_template("index.htm", **current_app.config["config"]["html_index"])


@main.route("/a", methods=["GET"])
def generate_audio():
    """Generate an audio file from text.

    Returns:
        Response: the audio file
    """
    text = request.args.get("text", "")
    voice = int(request.args.get("voice", "0"))
    rate = float(request.args.get("rate", "200"))
    volume = float(request.args.get("volume", "1"))

    return send_file(
        generate_sound_file(text=text, voice=voice, rate=rate, volume=volume),
        download_name="sound.mp3",
    )
