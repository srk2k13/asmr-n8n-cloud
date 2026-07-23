FROM n8nio/n8n:1.121.3

USER root

# Install system dependencies (Python3, FFmpeg)
RUN apk add --no-cache python3 py3-pip ffmpeg

WORKDIR /app

# Create python virtual env
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install python dependencies
RUN /app/venv/bin/pip install --no-cache-dir requests gradio_client

# Copy server files
COPY video_server.py /app/video_server.py
COPY start.sh /app/start.sh

RUN chmod +x /app/start.sh

# Render maps the main port to whatever port the application listens on.
CMD ["/app/start.sh"]
