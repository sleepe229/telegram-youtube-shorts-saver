#!/usr/bin/env python3
# coding: utf-8

import contextlib
import logging
import os
import re
import tempfile
import threading
import time
import traceback
from io import BytesIO

import psutil
import pyrogram
import yt_dlp
from pyrogram import Client, enums, filters, idle, types
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from youtubesearchpython import VideosSearch

from config import APP_HASH, APP_ID, OWNER, TOKEN
from downloader import ytdl_download

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s %(filename)s:%(lineno)d %(levelname).1s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

app = Client(
    'ytdl_bot',
    api_id=APP_ID,
    api_hash=APP_HASH,
    bot_token=TOKEN,
)

botStartTime = time.time()

# Helper functions
def sizeof_fmt(num: int, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return '%3.1f%s%s' % (num, unit, suffix)
        num /= 1024.0
    return '%.1f%s%s' % (num, 'Yi', suffix)

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
        if ytdl.extract_info(url, download=False).get('live_status') == 'is_live':
            return 'Live stream links are not supported.'
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

# Command handlers
@app.on_message(filters.command(['start']))
def start_handler(client: Client, message: types.Message):
    text = (
        'Hello! I am a YouTube Download Bot.\n\n'
        'Send me a YouTube link, and I will download the video for you.'
    )
    client.send_message(message.chat.id, text, disable_web_page_preview=True)

@app.on_message(filters.command(['help']))
def help_handler(client: Client, message: types.Message):
    text = (
        'To use this bot, simply send a YouTube video link.\n'
        'I will download the video and send it back to you.\n\n'
        'Commands:\n'
        '/start - Start the bot\n'
        '/help - Show this help message\n'
        '/stats - Show bot statistics'
    )
    client.send_message(message.chat.id, text, disable_web_page_preview=True)

@app.on_message(filters.command(['stats']))
def stats_handler(client: Client, message: types.Message):
    chat_id = message.chat.id
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    bot_uptime = timeof_fmt(time.time() - botStartTime)
    text = (
        f'**Bot Statistics:**\n'
        f'CPU Usage: {cpu_usage}%\n'
        f'Memory Usage: {memory.percent}%\n'
        f'Bot Uptime: {bot_uptime}'
    )
    client.send_message(chat_id, text)

# Main download handler
@app.on_message(filters.private & filters.text)
def download_handler(client: Client, message: types.Message):
    chat_id = message.chat.id
    url = message.text.strip()

    if not re.match(r'^https?://', url.lower()):
        text = search_ytb(url)
        message.reply_text(text, quote=True, disable_web_page_preview=True)
        return

    if text := link_checker(url):
        message.reply_text(text, quote=True)
        return

    bot_msg = message.reply_text('Processing your request...', quote=True)
    ytdl_download_entrance(client, bot_msg, url)


def ytdl_download_entrance(client: Client, bot_msg: types.Message, url: str):
    try:
        ytdl_normal_download(client, bot_msg, url)
    except Exception as e:
        logging.error('Failed to download %s, error: %s', url, e)
        error_msg = traceback.format_exc()
        bot_msg.edit_text(f'Download failed!❌\n\n`{error_msg}`', disable_web_page_preview=True)

def ytdl_normal_download(client: Client, bot_msg: types.Message, url: str):
    chat_id = bot_msg.chat.id
    with tempfile.TemporaryDirectory(prefix='ytdl-') as temp_dir:
        video_paths = ytdl_download(url, temp_dir, bot_msg)
        logging.info('Download complete.')
        client.send_chat_action(chat_id, enums.ChatAction.UPLOAD_VIDEO)
        bot_msg.edit_text('Download complete. Sending now...')
        for video_path in video_paths:
            client.send_video(
                chat_id,
                video=video_path,
                caption='Here is your video.',
                supports_streaming=True,
            )
        bot_msg.edit_text('Download success!✅')

if __name__ == '__main__':
    app.run()
