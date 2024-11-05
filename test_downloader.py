#!/usr/bin/env python3
# coding: utf-8

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
import pathlib
from io import StringIO
from pyrogram import types
from downloader import sizeof_fmt, edit_text, tqdm_progress, ytdl_download

class TestDownloader(unittest.TestCase):

    def test_sizeof_fmt(self):
        # test correct formatting of file sizes
        self.assertEqual(sizeof_fmt(0), '0.0B')
        self.assertEqual(sizeof_fmt(1023), '1023.0B')
        self.assertEqual(sizeof_fmt(1024), '1.0KiB')
        self.assertEqual(sizeof_fmt(1024 * 1024), '1.0MiB')
        self.assertEqual(sizeof_fmt(1024 * 1024 * 1024), '1.0GiB')
        self.assertEqual(sizeof_fmt(1024 ** 4), '1.0TiB')

    def test_edit_text(self):
        # mock the message object
        bot_msg = MagicMock(spec=types.Message)
        text = "test message"
        edit_text(bot_msg, text)
        bot_msg.edit_text.assert_called_once_with(text)

    def test_tqdm_progress(self):
        # test progress text generation
        desc = "downloading"
        total = 100
        finished = 50
        result = tqdm_progress(desc, total, finished)
        self.assertIn(desc, result)
        self.assertIn('50/100', result)

    def test_ytdl_download(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        tempdir = tempfile.mkdtemp()
        bot_msg = MagicMock(spec=types.Message)
        video_paths = ytdl_download(url, tempdir, bot_msg)
        self.assertIsInstance(video_paths, list)
        self.assertTrue(len(video_paths) > 0)
        # check that files exist
        for video_path in video_paths:
            self.assertTrue(os.path.exists(video_path))
        # print the path to the video file
        print(f"video saved at: {video_paths[0]}")
        # the temporary directory will not be deleted automatically
        # you can delete it manually after inspecting the contents
        # if desired, uncomment the following line to delete
        # shutil.rmtree(tempdir)

if __name__ == '__main__':
    unittest.main()
