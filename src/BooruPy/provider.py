# Copyright (C) 2012 Christopher Kaster
# This file is part of BooruPy
#
# You should have received a copy of the GNU General Public License
# along with BooruPy. If not, see <http://www.gnu.org/licenses/>
import json
import urllib
from urlparse import urljoin
from image import Image
from xml.etree import ElementTree

class BaseProvider:
    def _get_URLopener(self):
        return urllib.FancyURLopener({}) # todo: add proxy support

    def _get_json(self, request_url):
        opener = self._get_URLopener()
        raw_json = opener.open(request_url)
        return json.load(raw_json)

    def _get_xml(self, request_url):
        opener = self._get_URLopener()
        raw_xml = opener.open(request_url).read()
        return ElementTree.XML(raw_xml)

class DanbooruProvider(BaseProvider):
    def __init__(self, base_url, name, shortname):
        self._base_url = base_url
        self.name = name
        self.shortname = shortname
        self._img_url = urljoin(self._base_url,
            "/post/index.json?tags=%s&limit=%s&page=%s")
        self._tag_url = urljoin(self._base_url,
                "/tags/index.json?limit=%s&page=%s")

    def _request_tag(self):
        limit = 100
        page = 0
        ende = False
        while not ende:
            page += 1
            page_link = self._tag_url % (limit, page)
            tags = self._get_json(page_link)
            if len(tags) < limit:
                ende = True
            yield tags

    def get_tags(self):
        for tags in self._request_tag():
            for tag in tags:
                yield tag.count, tag.name

    def _request_images(self, tags):
        limit = 100
        page = 0
        ende = False
        while not ende:
            page += 1
            page_link = self._img_url % ('+'.join(tags), limit, page)
            images = self._get_json(page_link)
            if len(images) < limit:
                ende = True
            yield images

    def get_images(self, tags):
        for images in self._request_images(tags):
            for i in images:
                yield Image.from_dict(i)
    
class GelbooruProvider(BaseProvider):
    def __init__(self, base_url, name, shortname):
        self._base_url = base_url
        self._img_url = urljoin(self._base_url,
            "/index.php?page=dapi&s=post&q=index&tags=%s&limit=%s&pid=%s")
        self.name = name
        self.shortname = shortname
        self._tag_url = urljoin(self._base_url,
                "/index.php?page=dapi&s=tag&q=index&limit=%s&pid=%s")

    def _request_tag(self):
        limit = 100
        page = 0
        ende = False
        while not ende:
            page += 1
            page_link = self._tag_url % (limit, page)
            tags = self._get_xml(page_link)
            if len(tags) < limit:
                ende = True
            yield tags

    def get_tags(self):
        for tags in self._request_tag():
            for tag in tags:
                yield tag.count, tag.name

    def _request_images(self, tags):
        limit = 100
        page = 0
        ende = False
        while not ende:
            page += 1
            page_link = self._img_url % ( '+'.join(tags), limit, page )            
            images = self._get_xml(page_link)
            if len(images) < limit:
                ende = True
            yield images

    def get_images(self, tags):
        for images in self._request_images(tags):
            for i in images:
                yield Image.from_etree(i)
