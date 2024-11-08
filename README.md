# YouTube Video Download Bot

This bot is designed for downloading YouTube videos, with enhanced error handling and silent retry capabilities in case of network limitations or rate limits. Built with Pyrogram, it leverages `yt-dlp` for downloading and `youtubesearchpython` for search functionality. Additionally, the bot is containerized using Docker for easy deployment and scalability.

## Features
- **Download Videos:** Download videos directly from YouTube by sending a YouTube link.
- **Automatic Retries:** Automatically retries failed downloads silently, ensuring uninterrupted service.
- **System Statistics:** Provides bot usage statistics, including CPU and memory usage.
- **Dockerized Deployment:** Easily deploy the bot using Docker and Docker Compose.

## Requirements
- **Python 3.11**
- **Docker & Docker Compose** (for containerized deployment)
- **Telegram API Credentials:**
  - API ID
  - API Hash
  - Bot Token

## Installation

1. Clone the repository:
    ```bash
    https://github.com/sleepe229/telegram-youtube-shorts-saver.git
    cd telegram-youtube-shorts-saver
    ```

2. Setup Environment Variables
Create a .env file in the root directory of the project and add your Telegram API credentials
    ```bash
    APP_ID=your_app_id
    APP_HASH=your_app_hash
    TOKEN=your_bot_token
    OWNER=your_owner_id
    ```

**Important**: Ensure that the .env file is added to .gitignore to prevent sensitive information from being pushed to version control.

3. Using Docker (Recommended)

#### a. Build and Run the Docker Container
    docker-compose up -d --build
#### b. Verify the Container is Running
    docker-compose ps
#### c. View Logs
    docker-compose logs -f cringe_bot_container

4. Local Setup (Without Docker)
#### a. Create a Virtual Environment
    python3 -m venv venv
    source venv/bin/activate # On Linux
    venv\Scripts\activate # On Windows 
#### b. Verify the Container is Running
    pip install --upgrade pip
    pip install -r requirements.txt
#### c. Run the bot
    python main.py

## Commands
- `/start` - Start the bot and receive a welcome message.
- `/help` - Display help instructions.
- `/stats` - Show bot statistics, including CPU and memory usage.

## Usage
- Send a YouTube link to download the video.
