# Base image
FROM python:3.12

# Install curl, unzip, and other necessary dependencies
RUN apt-get update && apt-get install -y curl unzip

# Download and install the latest ChromeDriver
RUN LATEST_DRIVER=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    curl -O https://chromedriver.storage.googleapis.com/$LATEST_DRIVER/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm chromedriver_linux64.zip

# Set environment variables
ENV PYTHONPATH="/app/src"

# Set the working directory
WORKDIR /project

# Copy your application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run your Python script
ENTRYPOINT ["echo"]
CMD ["Data Pipeline Ready!"]
