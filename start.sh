#!/bin/sh

# Start the Python video server in the background (runs locally on port 5688)
python3 -u /app/video_server.py &

# Ensure n8n binds to the port assigned by Render ($PORT, which defaults to 10000 on Render)
export N8N_PORT=${PORT:-5678}

# Start n8n in the foreground
n8n start
