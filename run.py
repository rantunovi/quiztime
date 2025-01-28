import os
from app import create_app, socketio
from eventlet import wsgi
import eventlet

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    wsgi.server(eventlet.listen(('0.0.0.0', port)), app)

