import re
import json

from .common import InfoExtractor
from ..utils import (
    compat_urlparse,
    get_element_by_attribute,
)


class ImdbIE(InfoExtractor):
    IE_NAME = u'imdb'
    IE_DESC = u'Internet Movie Database trailers'
    _VALID_URL = r'http://www\.imdb\.com/video/imdb/vi(?P<id>\d+)'

    _TEST = {
        u'url': u'http://www.imdb.com/video/imdb/vi2524815897',
        u'md5': u'9f34fa777ade3a6e57a054fdbcb3a068',
        u'info_dict': {
            u'id': u'2524815897',
            u'ext': u'mp4',
            u'title': u'Ice Age: Continental Drift Trailer (No. 2) - IMDb',
            u'description': u'md5:9061c2219254e5d14e03c25c98e96a81',
            u'duration': 151,
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        webpage = self._download_webpage(url,video_id)
        descr = get_element_by_attribute('itemprop', 'description', webpage)
        available_formats = re.findall(
            r'case \'(?P<f_id>.*?)\' :$\s+url = \'(?P<path>.*?)\'', webpage,
            flags=re.MULTILINE)
        formats = []
        for f_id, f_path in available_formats:
            format_page = self._download_webpage(
                compat_urlparse.urljoin(url, f_path),
                u'Downloading info for %s format' % f_id)
            json_data = self._search_regex(
                r'<script[^>]+class="imdb-player-data"[^>]*?>(.*?)</script>',
                format_page, u'json data', flags=re.DOTALL)
            info = json.loads(json_data)
            format_info = info['videoPlayerObject']['video']
            formats.append({
                'format_id': f_id,
                'url': format_info['url'],
                'height': int(info['titleObject']['encoding']['selected'][:-1]),
            })

        return {
            'id': video_id,
            'title': self._og_search_title(webpage),
            'formats': formats,
            'description': descr,
            'thumbnail': format_info['slate'],
            'duration': int(info['titleObject']['title']['duration_seconds']),
        }
