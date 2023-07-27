#!/bin/env python
from seeingllama2 import app, socketio

if __name__ == "__main__":
    app.debug = True
    socketio.init_app(app, async_mode="eventlet")
    socketio.run(app)

else:
    raise RuntimeError("Only for use with the -m switch, not as a Python API")
