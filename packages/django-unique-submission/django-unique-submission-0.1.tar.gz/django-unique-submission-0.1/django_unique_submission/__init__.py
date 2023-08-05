"""
All rights reservered Lvye.cn
Meng Zhuo <mengzhuo@lvye.cn>
"""

import os
import datetime

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

_LACK_TOKEN_RESPONESE = HttpResponse(_('Lack of Unique Token'), status=412)
_CONFLICT_RESPONESE = HttpResponse(_('Request Conflicted'), status=409)

# 5 hours*3600 = 18000 seconds
_UNIQUE_TIMEOUT = getattr(settings, 'UNIQUE_TOKEN_TIMEOUT', 18000)
_UNIQUE_TOKEN_ID = getattr(settings, 'UNIQUE_TOKEN_ID', 'unique_tokens')
_UNIQUE_TOKEN_KEY = getattr(settings, 'UNIQUE_TOKEN_KEY', 'unique_token')


def unique(issue_method="GET", validate_method='POST'):

    def _controller(view_func):
        def wrapper(request, *args, **kwargs):
            if not _UNIQUE_TOKEN_ID in request.session:
                request.session.setdefault(_UNIQUE_TOKEN_ID, {})
            if request.method == validate_method:
                # check timeouted token
                now = datetime.datetime.now()
                request.session[_UNIQUE_TOKEN_ID] = dict(((tok, exp_time)
                                                          for tok, exp_time in request.session[_UNIQUE_TOKEN_ID].iteritems()
                                                          if exp_time > now))

                # start checking
                token = request.POST.get(
                    _UNIQUE_TOKEN_KEY) or request.GET.get(_UNIQUE_TOKEN_KEY)

                available_tokens = request.session[_UNIQUE_TOKEN_ID]
                if not token:
                    return _LACK_TOKEN_RESPONESE
                elif token in available_tokens:
                    del available_tokens[token]
                else:
                    return _CONFLICT_RESPONESE

                request.session.unique_token = ''

            elif request.method == issue_method:

                available_tokens = request.session[_UNIQUE_TOKEN_ID]
                utok = os.urandom(24).encode('hex').strip()
                available_tokens[
                    utok] = datetime.datetime.now() + datetime.timedelta(seconds=_UNIQUE_TIMEOUT)
                request.session.unique_token = utok
                request.session.save()

            return view_func(request, *args, **kwargs)
        return wrapper
    return _controller
