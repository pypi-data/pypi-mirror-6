import re
import requests
import json

try:
    import urlparse
except ImportError:
    # support for py3
    import urllib.parse as urlparse

from django.template.loader import render_to_string
from django.utils.functional import cached_property

from .utils import import_by_path
from .settings import EMBED_VIDEO_BACKENDS, EMBED_VIDEO_TIMEOUT


class EmbedVideoException(Exception):
    """ Parental class for all embed_video exceptions """
    pass


class VideoDoesntExistException(EmbedVideoException):
    """ Exception thrown if video doesn't exist """
    pass


class UnknownBackendException(EmbedVideoException):
    """ Exception thrown if video backend is not recognized. """
    pass


class UnknownIdException(EmbedVideoException):
    """
    Exception thrown if backend is detected, but video ID cannot be parsed.
    """
    pass


def detect_backend(url):
    """
    Detect the right backend for given URL.

    Goes over backends in ``settings.EMBED_VIDEO_BACKENDS``,
    calls :py:func:`~VideoBackend.is_valid` and returns backend instance.
    """

    for backend_name in EMBED_VIDEO_BACKENDS:
        backend = import_by_path(backend_name)
        if backend.is_valid(url):
            return backend(url)

    raise UnknownBackendException


class VideoBackend(object):
    """
    Base class used as parental class for backends.

    .. code-block:: python

        class MyBackend(VideoBackend):
            ...

    """

    re_code = None
    """
    Compiled regex (:py:func:`re.compile`) to search code in URL.

    Example: ``re.compile(r'myvideo\.com/\?code=(?P<code>\w+)')``
    """

    re_detect = None
    """
    Compilede regec (:py:func:`re.compile`) to detect, if input URL is valid
    for current backend.

    Example: ``re.compile(r'^http://myvideo\.com/.*')``
    """

    pattern_url = None
    """
    Pattern in which the code is inserted.

    Example: ``http://myvideo.com?code=%s``
    """

    pattern_thumbnail_url = None
    """
    Pattern in which the code is inserted to get thumbnail url.

    Example: ``http://static.myvideo.com/thumbs/%s``
    """

    allow_https = True
    """
    Sets if HTTPS version allowed for specific backend.
    """

    template_name = 'embed_video/embed_code.html'
    """
    Name of embed code template used by :py:meth:`get_embed_code`.

    Passed template variables: ``{{ backend }}`` (instance of VideoBackend),
    ``{{ width }}``, ``{{ height }}``
    """

    def __init__(self, url, is_secure=False):
        """
        First it tries to load data from cache and if it don't succeed, run
        :py:meth:`init` and then save it to cache.
        """
        self.is_secure = is_secure
        self.backend = self.__class__.__name__
        self._url = url

    @cached_property
    def code(self):
        return self.get_code()

    @cached_property
    def url(self):
        return self.get_url()

    @cached_property
    def protocol(self):
        return 'https' if self.allow_https and self.is_secure else 'http'

    @cached_property
    def thumbnail(self):
        return self.get_thumbnail_url()

    @cached_property
    def info(self):
        return self.get_info()

    @classmethod
    def is_valid(cls, url):
        """
        Class method to control if passed url is valid for current backend. By
        default it is done by :py:data:`re_detect` regex.
        """
        return True if cls.re_detect.match(url) else False

    def get_code(self):
        """
        Returns video code matched from given url by :py:data:`re_code`.
        """
        match = self.re_code.search(self._url)
        if match:
            return match.group('code')

    def get_url(self):
        """
        Returns URL folded from :py:data:`pattern_url` and parsed code.
        """
        return self.pattern_url.format(code=self.code, protocol=self.protocol)

    def get_thumbnail_url(self):
        """
        Returns thumbnail URL folded from :py:data:`pattern_thumbnail_url` and
        parsed code.
        """
        return self.pattern_thumbnail_url.format(code=self.code,
                                                 protocol=self.protocol)

    def get_embed_code(self, width, height):
        """
        Returns embed code rendered from template :py:data:`template_name`.
        """
        return render_to_string(self.template_name, {
            'backend': self,
            'width': width,
            'height': height,
        })

    def get_info(self):
        raise NotImplementedError


class YoutubeBackend(VideoBackend):
    """
    Backend for YouTube URLs.
    """
    re_detect = re.compile(
        r'^(http(s)?://)?(www\.)?youtu(\.?)be(\.com)?/.*', re.I
    )

    re_code = re.compile(
        r'''youtu(\.?)be(\.com)?/  # match youtube's domains
            (embed/)?  # match the embed url syntax
            (v/)?
            (watch\?v=)?  # match the youtube page url
            (ytscreeningroom\?v=)?
            (feeds/api/videos/)?
            (user\S*[^\w\-\s])?
            (?P<code>[\w\-]{11})[a-z0-9;:@?&%=+/\$_.-]*  # match and extract
        ''',
        re.I | re.X
    )

    pattern_url = '{protocol}://www.youtube.com/embed/{code}?wmode=opaque'
    pattern_thumbnail_url = '{protocol}://img.youtube.com/vi/{code}/hqdefault.jpg'

    def get_code(self):
        code = super(YoutubeBackend, self).get_code()

        if not code:
            parse_data = urlparse.urlparse(self._url)

            try:
                code = urlparse.parse_qs(parse_data.query)['v'][0]
            except KeyError:
                raise UnknownIdException

        return code


class VimeoBackend(VideoBackend):
    """
    Backend for Vimeo URLs.
    """
    re_detect = re.compile(
        r'^((http(s)?:)?//)?(www\.)?(player\.)?vimeo\.com/.*', re.I
    )
    re_code = re.compile(r'''vimeo\.com/(video/)?(?P<code>[0-9]+)''', re.I)
    pattern_url = '{protocol}://player.vimeo.com/video/{code}'
    pattern_info = '{protocol}://vimeo.com/api/v2/video/{code}.json'

    def get_info(self):
        try:
            response = requests.get(
                self.pattern_info.format(code=self.code, protocol=self.protocol),
                timeout=EMBED_VIDEO_TIMEOUT
            )
            return json.loads(response.text)[0]
        except ValueError:
            raise VideoDoesntExistException()

    def get_thumbnail_url(self):
        return self.info.get('thumbnail_large')


class SoundCloudBackend(VideoBackend):
    """
    Backend for SoundCloud URLs.
    """
    base_url = 'http://soundcloud.com/oembed'

    re_detect = re.compile(r'^(http(s)?://(www\.)?)?soundcloud\.com/.*', re.I)
    re_code = re.compile(r'src=".*%2F(?P<code>\d+)&show_artwork.*"', re.I)
    re_url = re.compile(r'src="(?P<url>.*?)"', re.I)

    @cached_property
    def width(self):
        return self.info.get('width')

    @cached_property
    def height(self):
        return self.info.get('height')

    def get_info(self):
        params = {
            'format': 'json',
            'url': self._url,
        }
        r = requests.get(self.base_url, data=params,
                         timeout=EMBED_VIDEO_TIMEOUT)

        if r.status_code != 200:
            raise VideoDoesntExistException(
                'SoundCloud returned status code `{0}`.'.format(r.status_code)
            )

        return json.loads(r.text)

    def get_thumbnail_url(self):
        return self.info.get('thumbnail_url')

    def get_url(self):
        match = self.re_url.search(self.info.get('html'))
        return match.group('url')

    def get_code(self):
        match = self.re_code.search(self.info.get('html'))
        return match.group('code')

    def get_embed_code(self, width, height):
        return super(SoundCloudBackend, self). \
            get_embed_code(width=width, height=self.height)
