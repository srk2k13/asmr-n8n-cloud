FROM n8nio/n8n:latest

USER root

# Install Python 3 & FFmpeg
RUN apk add --no-cache python3 py3-pip ffmpeg

WORKDIR /app

# Create python virtual env
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# Install python dependencies
RUN /app/venv/bin/pip install --no-cache-dir requests gradio_client

# Copy server files
COPY video_server.py /app/video_server.py
COPY start.sh /app/start.sh

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]


