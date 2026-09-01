#!/bin/sh
# Start the Python video server in the background
python3 -u /app/video_server.py > /var/log/video_server.log 2>&1 &
# Ensure n8n binds to the port assigned by Render
export N8N_PORT=$PORT
# Start n8n in the foreground
n8n start --port=$PORT
