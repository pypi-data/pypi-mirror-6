import urllib
import json

from exceptions import *

DIFFBOT_API_URL = 'http://api.diffbot.com/v2/'

class DiffBot(object):
    """
    DiffBot(token, url[, ...])
    """
    API_NAME = None

    def __init__(self, *args, **kwargs):
        if len(args) != 2:
            raise TypeError
        else:        
            self.token = args[0]
            self.url = args[1]

        # optional arguments
        self.all = kwargs.get('all')
        self.callback = kwargs.get('callback')
        self.fields = kwargs.get('fields')
        self.format = kwargs.get('format')
        self.mode = kwargs.get('mode')
        self.timeout = kwargs.get('timeout')
        self.stats = kwargs.get('stats')


    def _get_api_url(self):
        return '%s%s' % (DIFFBOT_API_URL, self.API_NAME)

    def get_params(self):
        context = {}
        for attr in self.attrs:
            if getattr(self, attr) is not None:
                context[attr] = getattr(self, attr)
        params = urllib.urlencode(context)
        return params

    def get(self):
        params = self.get_params()
        request = urllib.urlopen('%s?%s' % (self._get_api_url(), params))
        return request.read()

    def get_JSON(self):
        """
        returns a dictionary object
        """
        response = self.get()
        return json.loads(response)



class DiffBotArticle(DiffBot):
    """
    DiffBotArticle(token, url[, fields][, timeout][, callback])
    """

    API_NAME = 'article'
    attrs = ['token', 'url', 'fields',
                'timeout', 'callback']

    def __init__(self, *args, **kwargs):
        super(DiffBotArticle, self).__init__(*args, **kwargs)


class DiffBotFrontpage(DiffBot):
    API_NAME = 'frontpage'
    attrs = ['token', 'url', 'timeout',
                'format', 'all']

    def __init__(self, *args, **kwargs):
        super(DiffBotFrontpage, self).__init__(*args, **kwargs)


class DiffBotImage(DiffBot):
    API_NAME = 'image'
    attrs = ['token', 'url', 'fields',
                'timeout', 'callback']

    def __init__(self, *args, **kwargs):
        super(DiffBotImage, self).__init__(*args, **kwargs)


class DiffBotAnalyze(DiffBot):
    API_NAME = 'analyze'
    attrs = ['token', 'url', 'mode',
                'fields', 'stats']

    def __init__(self, *args, **kwargs):
        super(DiffBotAnalyze, self).__init__(*args, **kwargs)


class DiffBotProduct(DiffBot):
    API_NAME = 'product'
    attrs = ['token', 'url', 'fields',
                'timeout', 'callback']

    def __init__(self, *args, **kwargs):
        super(DiffBotProduct, self).__init__(*args, **kwargs)


"""
class DiffBotCrawl(DiffBot):
    API_NAME = 'crawl'
"""

