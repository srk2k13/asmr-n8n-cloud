#!/bin/sh

# Start the Python video server in the background (runs on port 5688 internally)
python3 -u /etc/n8n/video_server.py &

# Start n8n using the official entrypoint wrapper (handles database, migrations, and binds to Render's $PORT automatically)
tini -- /docker-entrypoint.sh
