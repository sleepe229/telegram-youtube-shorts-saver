#!/usr/bin/env python3
# coding: utf-8

import contextlib
import logging
import os
import re
import tempfile
import time
import traceback
import asyncio
from io import BytesIO

import psutil
import yt_dlp
from pyrogram import Client, enums, filters, types
from pyrogram.errors import FloodWait
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
    for unit in ['', 'Ки', 'Ми', 'Ги', 'Ти', 'Пи', 'Эи', 'Зи']:
        if abs(num) < 1024.0:
            return '%3.1f%s%s' % (num, unit, suffix)
        num /= 1024.0
    return '%.1f%s%s' % (num, 'Йи', suffix)

def timeof_fmt(seconds: int):
    periods = [('д', 86400), ('ч', 3600), ('м', 60), ('с', 1)]
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
            return 'Ссылки на прямые трансляции не поддерживаются.'
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
async def start_handler(client: Client, message: types.Message):
    text = (
        'Привет! Я бот для загрузки видео с YouTube.\n\n'
        'Отправьте мне ссылку на видео YouTube, и я скачаю его для вас.'
    )
    await client.send_message(message.chat.id, text, disable_web_page_preview=True)

@app.on_message(filters.command(['help']))
async def help_handler(client: Client, message: types.Message):
    text = (
        'Чтобы использовать этого бота, просто отправьте ссылку на видео YouTube.\n'
        'Я скачаю видео и отправлю его вам.\n\n'
        'Команды:\n'
        '/start - Запустить бота\n'
        '/help - Показать это сообщение помощи\n'
        '/stats - Показать статистику бота'
    )
    await client.send_message(message.chat.id, text, disable_web_page_preview=True)

@app.on_message(filters.command(['stats']))
async def stats_handler(client: Client, message: types.Message):
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    bot_uptime = timeof_fmt(time.time() - botStartTime)
    text = (
        f'**Статистика бота:**\n'
        f'Использование CPU: {cpu_usage}%\n'
        f'Использование памяти: {memory.percent}%\n'
        f'Время работы бота: {bot_uptime}'
    )
    await client.send_message(message.chat.id, text)

# YouTube link handler with regex
YOUTUBE_REGEX = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/[^\s]+'

@app.on_message(filters.regex(YOUTUBE_REGEX))
async def youtube_link_handler(client: Client, message: types.Message):
    url = re.search(YOUTUBE_REGEX, message.text).group(0).strip()

    if text := link_checker(url):
        await message.reply_text(text, quote=True)
        return

    bot_msg = await message.reply_text('Обрабатываю ваш запрос...', quote=True)
    await ytdl_download_entrance(client, bot_msg, url)

# Text handler to download video for personal messages
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

    bot_msg = await message.reply_text('Обрабатываю ваш запрос...', quote=True)
    await ytdl_download_entrance(client, bot_msg, url)

# Main download function with error handling
async def ytdl_download_entrance(client: Client, bot_msg: types.Message, url: str):
    try:
        await ytdl_normal_download(client, bot_msg, url)
    except FloodWait as e:
        await asyncio.sleep(e.value)  # Wait the required time silently
        await ytdl_normal_download(client, bot_msg, url)  # Retry download
    except Exception as e:
        logging.error('Не удалось скачать %s, ошибка: %s', url, e)
        error_msg = traceback.format_exc()
        await bot_msg.edit_text(f'Ошибка при загрузке!❌\n\n`{error_msg}`', disable_web_page_preview=True)

# Download video and send to chat
async def ytdl_normal_download(client: Client, bot_msg: types.Message, url: str):
    chat_id = bot_msg.chat.id
    with tempfile.TemporaryDirectory(prefix='ytdl-') as temp_dir:
        video_paths = ytdl_download(url, temp_dir, bot_msg)
        logging.info('Загрузка завершена.')
        await client.send_chat_action(chat_id, enums.ChatAction.UPLOAD_VIDEO)
        await bot_msg.edit_text('Загрузка завершена. Отправляю видео...')
        
        for video_path in video_paths:
            sent = False
            while not sent:
                try:
                    await client.send_video(
                        chat_id,
                        video=video_path,
                        caption='Вот ваше видео.',
                        supports_streaming=True,
                    )
                    sent = True  # Break loop if successful
                except FloodWait as e:
                    await asyncio.sleep(e.value)  # Wait silently
                except Exception as e:
                    logging.error('Не удалось отправить видео, ошибка: %s', e)
                    sent = True  # Stop retrying on non-FloodWait errors
        await bot_msg.edit_text('Видео успешно отправлено!✅')

if __name__ == '__main__':
    app.run()
