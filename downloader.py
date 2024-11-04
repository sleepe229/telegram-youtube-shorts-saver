#!/usr/bin/env python3
# coding: utf-8

from io import StringIO
import pathlib

import yt_dlp as ytdl
from pyrogram import types
from tqdm import tqdm

# Helper functions
def sizeof_fmt(num: int, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return '%3.1f%s%s' % (num, unit, suffix)
        num /= 1024.0
    return '%.1f%s%s' % (num, 'Yi', suffix)

def edit_text(bot_msg: types.Message, text: str):
    bot_msg.edit_text(text)

def tqdm_progress(desc, total, finished):
    from io import StringIO
    from tqdm import tqdm

    f = StringIO()
    with tqdm(
        total=total,
        initial=finished,
        file=f,
        ascii=False,
        ncols=30,
        bar_format='{l_bar}{bar} |{n_fmt}/{total_fmt} \r {percentage:.0f}%',
        unit_scale=False,
    ) as t:
        pass

    raw_output = f.getvalue()
    tqdm_output = raw_output.split('|')
    progress = f'`[{tqdm_output[1]}]`'
    detail = tqdm_output[2].strip()
    text = f'''
{desc}

{progress}
{detail}
    '''
    f.close()
    return text

def ytdl_download(url: str, tempdir: str, bot_msg):
    output = pathlib.Path(tempdir, '%(title).70s.%(ext)s').as_posix()
    ydl_opts = {
        'outtmpl': output,
        'format': 'best',
        'quiet': True,
    }

    try:
        with ytdl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        video_paths = list(pathlib.Path(tempdir).glob('*'))
    except Exception as e:
        raise e

    return video_paths
