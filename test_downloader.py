# test_downloader.py

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
        # Тестирование корректного форматирования размера файлов
        self.assertEqual(sizeof_fmt(0), '0.0B')
        self.assertEqual(sizeof_fmt(1023), '1023.0B')
        self.assertEqual(sizeof_fmt(1024), '1.0KiB')
        self.assertEqual(sizeof_fmt(1024 * 1024), '1.0MiB')
        self.assertEqual(sizeof_fmt(1024 * 1024 * 1024), '1.0GiB')
        self.assertEqual(sizeof_fmt(1024 ** 4), '1.0TiB')

    def test_edit_text(self):
        # Мокаем объект сообщения
        bot_msg = MagicMock(spec=types.Message)
        text = "Тестовое сообщение"
        edit_text(bot_msg, text)
        bot_msg.edit_text.assert_called_once_with(text)

    def test_tqdm_progress(self):
        # Тестирование генерации текста прогресса
        desc = "Скачивание"
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
        # Проверяем, что файлы существуют
        for video_path in video_paths:
            self.assertTrue(os.path.exists(video_path))
        # Выводим путь к видеофайлу
        print(f"Видео сохранено в: {video_paths[0]}")
        # Теперь временная директория не будет удалена автоматически
        # Вы можете удалить ее вручную после просмотра содержимого
        # Если хотите, можете раскомментировать следующую строку для удаления
        # shutil.rmtree(tempdir)

if __name__ == '__main__':
    unittest.main()
