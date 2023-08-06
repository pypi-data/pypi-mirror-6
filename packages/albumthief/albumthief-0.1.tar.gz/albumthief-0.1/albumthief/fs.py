# coding: utf-8
import os

import requests


__all__ = [
    'Downloader'
]


class Downloader(object):

    PATH = '%s/Pictures' % os.environ['HOME']

    def __init__(self, album_name, path=None):
        """
        A parrallel downloader that download items
        specified in targets.
        """
        self.album_name = album_name
        self.path = path or self.PATH
        self.make_album_dir(album_name, self.path)
        self.count = 0

    def make_album_dir(self, album_name, path):
        if not os.path.exists(path):
            raise IOError("No such path `%s`" % path)
        self.full_path = os.path.join(path, album_name)
        if not os.path.exists(self.full_path):
            os.mkdir(self.full_path)

    def download(self, url):
        name = os.path.basename(url)
        dest_path = os.path.join(self.full_path, name)
        if not os.path.exists(name):
            content = requests.get(url).content
            self.save(dest_path, content)
            self.count = (self.count + 1)

    def save(self, path, content):
        f = open(path, 'wb')
        f.write(content)
        f.close()
