# -*- coding: utf-8 -*-

"""borrowed from an old copy of Reddit's source code"""

import logging
import urllib
import StringIO
import math

from PIL import Image, ImageFile
from urllib2 import Request, HTTPError, URLError, build_opener
from httplib import InvalidURL

from settings import USERAGENT

log = logging.getLogger(__name__)

chunk_size = 1024
thumbnail_size = 90, 90

def image_to_str(image):
    s = StringIO.StringIO()
    image.save(s, image.format)
    s.seek(0)
    return s.read()

def str_to_image(s):
    s = StringIO.StringIO(s)
    s.seek(0)
    image = Image.open(s)
    return image

def prepare_image(image):
    image = square_image(image)
    image.thumbnail(thumbnail_size, Image.ANTIALIAS) # this one is inplace
    return image

def image_entropy(img):
    """calculate the entropy of an image"""

    hist = img.histogram()
    hist_size = sum(hist)
    hist = [float(h) / hist_size for h in hist]
    return -sum([p * math.log(p, 2) for p in hist if p != 0])

def square_image(img):
    """if the image is taller than it is wide, square it off. determine
    which pieces to cut off based on the entropy pieces."""

    x,y = img.size
    while y > x:
        # slice 10px at a time until square
        slice_height = min(y - x, 10)

        bottom = img.crop((0, y - slice_height, x, y))
        top = img.crop((0, 0, x, slice_height))

        # remove the slice with the least entropy
        if image_entropy(bottom) < image_entropy(top):
            img = img.crop((0, 0, x, y - slice_height))
        else:
            img = img.crop((0, slice_height, x, y))

        x,y = img.size

    return img

def clean_url(url):
    """url quotes unicode data out of urls"""

    url = url.encode('utf8')
    url = ''.join([urllib.quote(c) if ord(c) >= 127 else c for c in url])
    return url

def fetch_url(url, referer=None, retries=1, dimension=False):
    """"""

    cur_try = 0
    nothing = None if dimension else (None, None)
    url = clean_url(url)

    if not url.startswith(('http://', 'https://')):
        return nothing

    while True:
        try:
            req = Request(url)
            req.add_header('User-Agent', USERAGENT)
            if referer:
                req.add_header('Referer', referer)

            opener = build_opener()
            open_req = opener.open(req, timeout=5)

            # if we only need the dimension of the image, we may not
            # need to download the entire thing
            if dimension:
                content = open_req.read(chunk_size)
            else:
                content = open_req.read()

            content_type = open_req.headers.get('content-type')

            if not content_type:
                return nothing

            if 'image' in content_type:
                p = ImageFile.Parser()
                new_data = content
                while not p.image and new_data:
                    try:
                        p.feed(new_data)
                    except IOError, e: # jpg error on some computers
                        log.critical('***jpeg misconfiguration! check pillow or pil'
                                'installation this machine: %s' % str(e))
                        p = None
                        break
                    new_data = open_req.read(chunk_size)
                    content += new_data

                if p is None:
                    return nothing
                # return the size, or return the data
                if dimension and p.image:
                    return p.image.size
                elif dimension:
                    return nothing
            elif dimension:
                # expected an image, but didn't get one
                return nothing

            return content_type, content

        except (URLError, HTTPError, InvalidURL), e:
            cur_try += 1
            if cur_try >= retries:
                # log.debug('error while fetching: %s referer: %s' % (url, referer))
                return nothing
        finally:
            if 'open_req' in locals():
                open_req.close()

def fetch_size(url, referer=None, retries=1):
    return fetch_url(url, referer, retries, dimension=True)

class Scraper:
    def __init__(self, url, imgs, top_img):
        self.url = url
        self.imgs = imgs
        self.top_img = top_img

    def largest_image_url(self):
        if not self.imgs and not self.top_img:
            return None

        # either og:img tag or link rel-src
        if self.top_img:
            return self.top_img

        max_area = 0
        max_url = None

        for img_url in self.imgs:
            size = fetch_size(img_url, referer=self.url)
            if not size:
                continue

            area = size[0] * size[1]

            # ignore little images
            if area < 5000:
                # logger.debug('ignore little %s' % img_url)
                continue

            # PIL won't scale up, so we set a min width and
            # maintain the aspect ratio
            if size[0] < thumbnail_size[0]:
                continue

            # ignore excessively long/wide images
            if max(size) / min(size) > 1.5:
                # logger.debug('ignore dims %s' % img_url)
                continue

            # penalize images with "sprite" in their name
            if 'sprite' in img_url.lower():
                # logger.debug('penalizing sprite %s' % img_url)
                area /= 10

            if area > max_area:
                max_area = area
                max_url = img_url

        # log.debug('using max img ' + max_url)
        return max_url

    def thumbnail(self):
        """Identifies top image, trims out a thumbnail and also has a url"""

        image_url = self.largest_image_url()
        if image_url:
            content_type, image_str = fetch_url(image_url, referer=self.url)
            if image_str:
                image = str_to_image(image_str)
                try:
                    image = prepare_image(image)
                except IOError, e:
                    # print 'can\'t read interlaced PNGs, ignore'
                    if 'interlaced' in e.message:
                        return None
                    #raise
                return image, image_url

        return None, None


if __name__ == '__main__':
    import urlparse
    import lxml.html
    import requests

    url = 'http://www.cnn.com/'
    html = requests.get(url).text
    lxml_root = lxml.html.fromstring(html)

    imgs = [ urlparse.urljoin(url, u)
             for u in lxml_root.xpath('//img/@src') ]
    print imgs

    s = Scraper(url, imgs=imgs, top_img=None)
    img, url = s.thumbnail()

    print 'top img', url
    # img.save('cnn.png')

