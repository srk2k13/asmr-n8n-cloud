FROM n8nio/n8n:latest

# Install Python and build dependencies (n8n image is Debian-based, so we use apt-get)
USER root
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create and activate Python virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install Python requirements
RUN pip3 install --no-cache-dir requests gradio_client

# Copy video server files
COPY video_server.py /etc/n8n/video_server.py
COPY start.sh /etc/n8n/start.sh

RUN chmod +x /etc/n8n/start.sh

# Execute startup script
CMD ["/etc/n8n/start.sh"]
