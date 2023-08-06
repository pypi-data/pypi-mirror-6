# coding: utf-8

# This has to happen in the very beginning
import gevent
from gevent import monkey; monkey.patch_socket()

import re
import urlparse

import re
import socket

import requests
from BeautifulSoup import BeautifulSoup as Soup

from delegate import BaseDelegate
from delegate import DelegateMixin
import fs
from multitask import multi_task


__all__ = [
    "Thief",
    "DouBanThief"
]


class Thief(object):

    def __init__(self, album_id):
        self.album_id = album_id

    def iter_pages(self):
        """
        Returns a generator that yields
        URLs to paginated images found
        in the album_url.

        :return:    A generator
        :rtype:     Iterable
        """
        raise NotImplemented

    def iter_images(self, page_url):
        """
        Returns a generator that yields
        URLs of images found in the page.

        :param page: The URL to the page.
        :type page:  BaseString

        :return:    A generator.
        :rtype:     Iterable    
        """ 
        raise NotImplemented

    def get(self, url, **params):
        return requests.get(url)

    def re_search(self, pattern, content):
        """
        Search for a match in content.

        :param pattern: Pattern to match for
        :type pattern:  re.compile(...)

        :param content: Content to look for
        :type  content: BaseString

        :return:    Matching group
        :rtype:     ListType
        """
        # TODO exception handling
        return re.search(pattern, content).group()

class ThiefDelegate(BaseDelegate):

    def album_analysed(self, info):
        raise NotImplemented

    def one_image_downloaded(self, info):
        raise NotImplemented

class DouBanThief(Thief, DelegateMixin):

    delegation_type = ThiefDelegate

    PTN_IMG_COUNT = re.compile(r'\d+')
    # e.g., http://www.douban.com/photos/album/123394605/?start=18
    PAGE_SIZE = 18
    ALBUM_URL_ROOT = 'http://www.douban.com/photos/album/'

    def __init__(self, album_id, delegate=None, downloader=None):
        """
        :param delegate:    The delegator that reacts to the notification.
        :type delegate:     albumthief.delegate.ThiefDelegate
        """
        super(DouBanThief, self).__init__(album_id)
        self.make_album_url()
        self.delegate = delegate
        self.downloader = downloader

    def make_album_url(self):
        self.album_url = '%s/%s' % (self.ALBUM_URL_ROOT, self.album_id)

    def make_url_with_page_offset(self, offset):
        """
        With a page offset, make a link like this:
        http://www.douban.com/photos/album/123394605/?start=18

        :param offset:  The page offset
        :type  offset:  IntegerType

        :return:    The link to the paginated album page
        :rtype:     BaseString
        """
        return '%s?start=%s' % (self.album_url, offset * self.PAGE_SIZE)

    def find_all_img_link_in_a_page(self, url_page):
        page = self.get(url_page)
        soup = Soup(page.text)
        photos = soup.findAll(attrs={'class': 'photolst_photo'})
        imgs = [
            self.transform_img_thumb_url_into_original_url(
                p.first().attrMap['src'])
            for p in photos]
        return imgs

    def analyze_album(self):
        """
        Analyize the album to get the metadata
        about this album.
        """
        response = self.get(self.album_url)
        soup = Soup(response.text)

        def count_images():
            node_count = soup.find(attrs={'class': 'count'})
            text_count = node_count.text
            count = self.re_search(self.PTN_IMG_COUNT, text_count)
            return int(count)
        self.num_images = count_images()

        def get_name():
            album_name = soup.find('h1')
            # TODO Attension! Unicode 出没!
            return album_name.text
        self.album_name = get_name()
        self.delegating('album_analysed',
            {'album_name': self.album_name,
             'num_images': self.num_images})

    def iter_pages(self):
        """
        This implementation only hits request.get
        once and builds the crawl order out of the
        page size and number of images.
        """
        if self.num_images == 0:
            raise StopIteration("No images in this album")

        pages, reminder = divmod(self.num_images, self.PAGE_SIZE)
        if reminder > 0:
            pages = pages + 1
            for i in range(0, pages):
                url = self.make_url_with_page_offset(i)
                yield url

    def iter_images(self):
        """
        Find images in every page.
        This process is done concurrently using gevent.

        :return:    A generator over all images in this album
        :rtype:     GeneratorType
        """
        pages = self.iter_pages()
        results = multi_task(self.find_all_img_link_in_a_page, pages)
        return (
            img
            for result in results
            for img in result
        )

    def transform_img_thumb_url_into_original_url(self, url_img_thumb):
        """
        Transform a link like this:
            http://img5.douban.com/view/photo/thumb/public/p2173847816.jpg
        into:
            http://img3.douban.com/view/photo/photo/public/p2173847816.jpg
        """
        return url_img_thumb.replace('thumb', 'photo')

    def download(self, url):
        """
        Download an image at location specified by url.

        :param url:     The image url.
        :type: url:     BaseString
        """
        self.downloader.download(url)
        self.delegating('one_image_downloaded', {
            'downloaded_image_count': self.downloader.count,
            'image_url': url
        })

    def steal(self, concurency=50, path=None):
        """
        Start scraping and downloading.
        """
        self.analyze_album()
        self.downloader = fs.Downloader(self.album_name, path=path)
        multi_task(self.download, self.iter_images(), concurency)