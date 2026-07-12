#!/bin/sh

# Start the Python video server in the background (runs on port 5688 internally)
python3 -u /app/video_server.py &

# Start n8n in the foreground (runs on the port Render sets in the $PORT environment variable)
n8n start
