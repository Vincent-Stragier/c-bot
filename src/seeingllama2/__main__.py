"""Main entry point for the application when run with the -m switch."""
from seeingllama2 import app, socketio

if __name__ == "__main__":
    socketio.init_app(app, async_mode="eventlet")

    host = app.config["config"]["flask"].get("host", "localhost")
    port = app.config["config"]["flask"].get("port", 5000)
    socketio.run(app, host=host, port=port, debug=app.debug)

else:
    raise RuntimeError("Only for use with the -m switch, not as a Python API")
