FROM node:18-alpine

# Install system dependencies (must be run as root)
RUN apk add --no-cache python3 py3-pip python3-dev build-base git ffmpeg

# Create a non-root user required by Hugging Face Spaces (UID 1000)
RUN adduser -D -u 1000 user

# Set up working directory and change ownership
WORKDIR /home/user/app
RUN chown -R user:user /home/user

# Switch to the non-root user
USER user
ENV HOME=/home/user
ENV PATH="/home/user/venv/bin:/home/user/.npm-global/bin:$PATH"

# Configure npm to install globally in user directory to avoid permission issues
RUN mkdir /home/user/.npm-global && npm config set prefix '/home/user/.npm-global'

# Install n8n
RUN npm install -g n8n

# Set up Python virtual environment
RUN python3 -m venv /home/user/venv
RUN pip3 install --no-cache-dir requests gradio_client

# Copy application files with correct ownership
COPY --chown=user:user video_server.py /home/user/app/video_server.py
COPY --chown=user:user start.sh /home/user/app/start.sh

RUN chmod +x /home/user/app/start.sh

# Expose Hugging Face Space port
EXPOSE 7860

CMD ["/home/user/app/start.sh"]
