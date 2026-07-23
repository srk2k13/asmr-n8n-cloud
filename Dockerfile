FROM node:20-alpine

# Install system dependencies (Python, Git, FFmpeg, native libs for n8n)
RUN apk add --no-cache python3 py3-pip python3-dev build-base git ffmpeg gcompat libc6-compat vips-dev

# Install n8n globally (latest version)
ARG BUILD_DATE=2026-07-23-v3
RUN npm install -g n8n@latest --unsafe-perm



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
