#!/usr/bin/env python3
# coding: utf-8

import pathlib
import yt_dlp
import logging

def ytdl_download(url: str, save_dir: str, bot_msg):
    """
    downloads a youtube video and saves it in the specified directory.

    :param url: youtube video url
    :param save_dir: path to the directory for saving the video
    :param bot_msg: bot message for updating status (if necessary)
    :return: list of paths to the downloaded video files
    """
    output_template = pathlib.Path(save_dir) / '%(title).70s.%(ext)s'
    ydl_opts = {
        'outtmpl': str(output_template),
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        # add progress hook if necessary
        # 'progress_hooks': [my_hook],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        video_paths = list(pathlib.Path(save_dir).glob('*'))
        return video_paths
    except Exception as e:
        logging.error(f"error downloading video: {e}")
        raise e
