from .. import logger
from . import proxy
from .base_response import BaseResponse


class YoutubeResponse(BaseResponse):
    pass


class YoutubeBackend(object):
    response_class = YoutubeResponse
    api_url = "https://gdata.youtube.com/feeds/api/videos/%s?v=%s"
    api_version = 2

    @proxy
    def call(self, url):
        code = "Zce-QT7MGSE"
        url = self.api_url % (code, self.api_version)
        logger.debug("YouTube call to '%s'" % url)
        response = self.client.oembed(url)
        return self.wrap_response_data(response, fresh=True)

    @proxy
    def wrap_response_data(self, data, **kwargs):
        return self.response_class(data, **kwargs)
