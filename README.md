# YouTube Video Download Bot

This bot is designed for downloading YouTube videos, with enhanced error handling and silent retry capabilities in case of network limitations or rate limits. Built with Pyrogram, it leverages `yt_dlp` for downloading and `youtubesearchpython` for search functionality.

## Features
- Download videos directly from YouTube.
- Search YouTube videos with a text query.
- Automatically retries failed downloads silently, ensuring uninterrupted service.
- Provides bot usage statistics, including CPU and memory usage.

## Requirements
- Python 3.8+
- Telegram API credentials (API ID, API Hash, Bot Token)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/YouTubeVideoDownloadBot.git
    cd YouTubeVideoDownloadBot
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Configure your environment variables in `config.py`:
    ```python
    APP_ID = 'your_app_id'
    APP_HASH = 'your_app_hash'
    TOKEN = 'your_bot_token'
    ```

4. Run the bot:
    ```bash
    python main.py
    ```

## Commands
- `/start` - Start the bot and receive a welcome message.
- `/help` - Display help instructions.
- `/stats` - Show bot statistics, including CPU and memory usage.

## Usage
- Send a YouTube link to download the video.
- Send a text query to search for top 5 YouTube videos and receive the links.
- The bot automatically handles links with live streaming status and sends appropriate feedback.

## Testing
Run the tests to ensure the download and utility functions work correctly:
```bash
python -m unittest discover
