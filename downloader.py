#!/usr/bin/env python3
# coding: utf-8

import pathlib
import time
import yt_dlp
import logging

def ytdl_download(url: str, save_dir: str, bot_msg):
    """
    downloads a youtube video and saves it in the specified directory.
    handles network errors and retries the download in case of failure.
    """
    output_template = pathlib.Path(save_dir) / '%(title).70s.%(ext)s'
    ydl_opts = {
        'outtmpl': str(output_template),
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        # add progress hook if necessary
    }

    retries = 3  # retry 3 times on failure
    for attempt in range(retries):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            video_paths = list(pathlib.Path(save_dir).glob('*'))
            return video_paths
        except yt_dlp.utils.DownloadError as e:
            logging.error(f"Download error on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                time.sleep(5)  # wait before retrying
            else:
                raise  # after retries, raise the error
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise
