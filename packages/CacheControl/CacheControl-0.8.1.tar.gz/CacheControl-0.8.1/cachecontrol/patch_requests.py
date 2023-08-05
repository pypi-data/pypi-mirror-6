from requests import models
from requests.packages.urllib3.response import HTTPResponse


__attrs__ = [
    '_content',
    'status_code',
    'headers',
    'url',
    'history',
    'encoding',
    'reason',
    'cookies',
    'elapsed',
]


def response_getstate(self):
    # consume everything
    if not self._content_consumed:
        self.content

    state = dict(
        (attr, getattr(self, attr, None))
        for attr in __attrs__
    )

    # deal with our raw content b/c we need it for our cookie jar
    state['raw_original_response'] = self.raw._original_response
    return state


def response_setstate(self, state):
    for name, value in state.items():
        if name != 'raw_original_response':
            setattr(self, name, value)

    setattr(self, 'raw', HTTPResponse())
    self.raw._original_response = state['raw_original_response']


models.Response.__getstate__ = response_getstate
models.Response.__setstate__ = response_setstate
