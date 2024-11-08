#!/usr/bin/env python3
# coding: utf-8

import contextlib
import logging
import os
import re
import shutil
import tempfile
import time
import traceback
import threading  # adding the threading module
from io import BytesIO

import psutil
import yt_dlp
from pyrogram import Client, enums, filters, types
from pyrogram.errors import FloodWait, MessageNotModified
from youtubesearchpython import VideosSearch

from config import APP_HASH, APP_ID, OWNER, TOKEN
from downloader import ytdl_download

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s %(filename)s:%(lineno)d %(levelname).1s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

PROXY = {
    "scheme": "socks5",  # HTTP proxy scheme
    "hostname": "34.124.190.108",  # Proxy server address without "http://"
    "port": 8080,  # Proxy server port
    # "username": "proxy_username",  # Uncomment if authentication is required
    # "password": "proxy_password"   # Uncomment if authentication is required
}


app = Client(
    'ytdl_bot',
    api_id=APP_ID,
    api_hash=APP_HASH,
    bot_token=TOKEN,
    # proxy=PROXY
)

botStartTime = time.time()

# define the path to the temple_files directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLE_FILES_DIR = os.path.join(BASE_DIR, 'temple_files')
os.makedirs(TEMPLE_FILES_DIR, exist_ok=True)  # create the directory if it doesn't exist

# helper functions
def sizeof_fmt(num: int, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return f'{num:3.1f}{unit}{suffix}'
        num /= 1024.0
    return f'{num:.1f}Yi{suffix}'

def timeof_fmt(seconds: int):
    periods = [('d', 86400), ('h', 3600), ('m', 60), ('s', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)}{period_name}'
    return result

def link_checker(url: str) -> str:
    ytdl = yt_dlp.YoutubeDL()
    with contextlib.suppress(yt_dlp.utils.DownloadError):
        info = ytdl.extract_info(url, download=False)
        if info.get('live_status') == 'is_live':
            return 'Links to live streams are not supported.'
    return ''

def search_ytb(kw: str):
    videos_search = VideosSearch(kw, limit=5)
    text = ''
    results = videos_search.result()['result']
    for item in results:
        title = item.get('title')
        link = item.get('link')
        index = results.index(item) + 1
        text += f'{index}. {title}\n{link}\n\n'
    return text

# safe edit message function
async def safe_edit_message(bot_msg: types.Message, new_text: str, **kwargs):
    if bot_msg.text != new_text:
        try:
            await bot_msg.edit_text(new_text, **kwargs)
        except MessageNotModified:
            pass  # the message already contains this text
        except FloodWait as e:
            logging.warning(f"FloodWait: waiting for {e.value} seconds.")
            time.sleep(e.value + 1)  # wait the required time plus 1 second
            await safe_edit_message(bot_msg, new_text, **kwargs)  # try again
        except Exception as e:
            logging.error(f"Error editing message: {e}")

# monitoring function
def monitor(directory=TEMPLE_FILES_DIR, max_videos=15, check_interval=60):
    """
    monitors the directory for the number of video files.
    when the number of videos reaches or exceeds max_videos, clears the directory.

    :param directory: path to the directory to monitor.
    :param max_videos: maximum allowed number of video files.
    :param check_interval: check interval in seconds.
    """
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'}

    while True:
        try:
            if not os.path.exists(directory):
                logging.info(f"Directory {directory} does not exist. Creating it.")
                os.makedirs(directory)

            files = os.listdir(directory)
            video_files = [f for f in files if os.path.splitext(f)[1].lower() in video_extensions]
            video_count = len(video_files)

            logging.info(f"Current number of video files: {video_count}")

            if video_count >= max_videos:
                logging.info(f"Number of video files reached or exceeded ({video_count} >= {max_videos}). Clearing directory.")
                for f in video_files:
                    try:
                        os.remove(os.path.join(directory, f))
                        logging.info(f"Deleted file: {f}")
                    except Exception as e:
                        logging.error(f"Failed to delete file {f}: {e}")
        except Exception as e:
            logging.error(f"Error in monitoring function: {e}")

        time.sleep(check_interval)

# command handlers
@app.on_message(filters.command(['start']))
async def start_handler(client: Client, message: types.Message):
    text = (
        'Hello! I am a YouTube video downloader bot.\n\n'
        'Send me a YouTube video link, and I will download it for you.'
    )
    await client.send_message(message.chat.id, text, disable_web_page_preview=True)

@app.on_message(filters.command(['help']))
async def help_handler(client: Client, message: types.Message):
    text = (
        'To use this bot, simply send a YouTube video link.\n'
        'I will download the video and send it to you.\n\n'
        'Commands:\n'
        '/start - start the bot\n'
        '/help - show this help message\n'
        '/stats - show bot statistics'
    )
    await client.send_message(message.chat.id, text, disable_web_page_preview=True)

@app.on_message(filters.command(['stats']))
async def stats_handler(client: Client, message: types.Message):
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    bot_uptime = timeof_fmt(int(time.time() - botStartTime))
    text = (
        f'**Bot Statistics:**\n'
        f'CPU Usage: {cpu_usage}%\n'
        f'Memory Usage: {memory.percent}%\n'
        f'Bot Uptime: {bot_uptime}'
    )
    await client.send_message(message.chat.id, text)

# youtube link handler with regex
YOUTUBE_REGEX = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/[^\s]+'

@app.on_message(filters.regex(YOUTUBE_REGEX))
async def youtube_link_handler(client: Client, message: types.Message):
    url = re.search(YOUTUBE_REGEX, message.text).group(0).strip()

    if text := link_checker(url):
        await message.reply_text(text, quote=True)
        return

    bot_msg = await message.reply_text('fucking work again...', quote=True)
    await ytdl_download_entrance(client, bot_msg, url)

# text handler to download video for private messages
@app.on_message(filters.private & filters.text)
async def download_handler(client: Client, message: types.Message):
    url = message.text.strip()

    if not re.match(r'^https?://', url.lower()):
        text = search_ytb(url)
        await message.reply_text(text, quote=True, disable_web_page_preview=True)
        return

    if text := link_checker(url):
        await message.reply_text(text, quote=True)
        return

    bot_msg = await message.reply_text('', quote=True)
    await ytdl_download_entrance(client, bot_msg, url)

# main download function with error handling and isolated download directory
async def ytdl_download_entrance(client: Client, bot_msg: types.Message, url: str, retries=3):
    temp_dir = tempfile.mkdtemp(dir=TEMPLE_FILES_DIR)  # Создаем уникальную временную папку для каждого запроса
    try:
        await ytdl_normal_download(client, bot_msg, url, temp_dir)
    except FloodWait as e:
        if retries > 0:
            logging.warning(f"FloodWait: waiting for {e.value} seconds. Attempts left: {retries}")
            time.sleep(e.value + 1)
            await ytdl_download_entrance(client, bot_msg, url, retries - 1)
        else:
            await safe_edit_message(bot_msg, 'Too many requests. Please try again later.')
    except Exception as e:
        logging.error('Failed to download %s, error: %s', url, e)
        error_msg = traceback.format_exc()
        await safe_edit_message(bot_msg, f'Error during download!❌\n\n`{error_msg}`', disable_web_page_preview=True)
    finally:
        shutil.rmtree(temp_dir)  # Удаляем временную папку после завершения обработки

# download video and send to chat with isolated directory
async def ytdl_normal_download(client: Client, bot_msg: types.Message, url: str, temp_dir: str):
    chat_id = bot_msg.chat.id
    video_paths = ytdl_download(url, temp_dir, bot_msg)  
    logging.info('Download completed.')

    await client.send_chat_action(chat_id, enums.ChatAction.UPLOAD_VIDEO)

    for video_path in video_paths:
        sent = False
        while not sent:
            try:
                await client.send_video(
                    chat_id,
                    video=video_path,
                    caption="anyone who aint seen it is a loshped malenkii",
                    supports_streaming=True,
                )
                sent = True  # exit loop if successful
            except FloodWait as e:
                logging.warning(f"FloodWait: waiting for {e.value} seconds.")
                time.sleep(e.value + 1)
            except Exception as e:
                logging.error('Failed to send video, error: %s', e)
                sent = True

    # delete the message "Starting video download..."
    await bot_msg.delete()
    
    # send notification of successful video sending
    await client.send_message(chat_id, 'the sun is in the sky, the negri are plowing')

# function to start monitoring in a separate thread
def start_monitoring():
    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()
    logging.info("Monitoring function is active.")

if __name__ == '__main__':
    # start the monitoring function in a separate thread
    start_monitoring()
    
    # start the bot
    logging.info("Bot started.")
    app.run()  # run() method blocks the main thread and manages the bot