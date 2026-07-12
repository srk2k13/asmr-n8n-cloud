#!/bin/sh

# Start the Python video server in the background (runs locally inside the container on port 5688)
python3 -u /home/user/app/video_server.py &

# Start n8n in the foreground (runs on port 7860 as expected by Hugging Face)
n8n start
