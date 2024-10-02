# Base image using Debian slim
FROM python:3.10

# Set USER to ROOT
USER root

# Install necessary dependencies
RUN apt-get update && apt-get install -y wget unzip && \
	wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
	apt install -y ./google-chrome-stable_current_amd64.deb && \
	rm google-chrome-stable_current_amd64.deb && \
	apt-get clean

# Set environment variables
ENV PYTHONPATH="/project/src"

# Set the working directory
WORKDIR /project

# Copy your application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the default command to run your Python script
CMD ["python", "scripts/run_incremental_pipeline.py"]
