FROM node:20-alpine

# Install system dependencies (Python, Git, FFmpeg)
RUN apk add --no-cache python3 py3-pip python3-dev build-base git ffmpeg gcompat libc6-compat

# Install n8n globally (v1.121.0 with database schema compatibility)
RUN npm install -g n8n@1.121.0 --omit=dev --unsafe-perm






# Set up directory for python server
WORKDIR /app

# Create python virtual env
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install python dependencies
RUN pip3 install --no-cache-dir requests gradio_client

# Copy server files
COPY video_server.py /app/video_server.py
COPY start.sh /app/start.sh

RUN chmod +x /app/start.sh

# Render maps the main port to whatever port the application listens on.
# start.sh will run n8n in the foreground which respects the $PORT env var.
CMD ["/app/start.sh"]



