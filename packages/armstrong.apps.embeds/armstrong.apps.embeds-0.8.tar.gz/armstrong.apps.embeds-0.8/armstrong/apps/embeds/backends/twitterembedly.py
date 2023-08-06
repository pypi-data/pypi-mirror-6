from ..models import EmbedType
from .base_response import BaseResponse
from .embedly import EmbedlyBackend


TWITTER_SCRIPT_TAG = '<blockquote class="twitter-tweet">' \
    '<a href="%s"></a></blockquote>' \
    '<script async src="https://platform.twitter.com/widgets.js" ' \
    'charset="utf-8"></script>'


class TwitterembedlyResponse(BaseResponse):
    def is_valid(self):
        return not (
            not self._data or
            self._data.get('error') or
            self._data.get('type', '') == 'error')

    @property
    def type(self):
        """Force this to be a `rich` type"""

        if not hasattr(self, '_type'):
            self._type = None
            self._type, _ = EmbedType.objects.get_or_create(name='rich')
        return self._type

    @property
    def render(self):
        url = self._data.get('url')
        return TWITTER_SCRIPT_TAG % url if url else ''


class TwitterembedlyBackend(EmbedlyBackend):
    """Use Embedly to grab Twitter metadata but use a different Response"""
    response_class = TwitterembedlyResponse
