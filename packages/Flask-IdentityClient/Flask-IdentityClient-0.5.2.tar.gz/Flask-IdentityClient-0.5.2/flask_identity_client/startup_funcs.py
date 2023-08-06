# coding: UTF-8
from __future__ import absolute_import, division, print_function, unicode_literals

import urllib
from functools import wraps, partial
from collections import namedtuple
from time import time
from email.utils import parsedate_tz, mktime_tz
from httplib2 import HttpLib2Error
from werkzeug.exceptions import Unauthorized, HTTPException, default_exceptions
from flask import current_app as app, redirect, request, session, url_for, g
from .views import PWRemoteApp

__all__ = ['user_required', 'resources_from_middle']


#-----------------------------------------------------------------------
# user_required

def user_required():
    login_url = url_for('identity_client.index', next=request.url)

    user_data = g.user_data = session.get('user_data')
    if not user_data:
        return redirect(login_url)


#-----------------------------------------------------------------------
# resources_from_middle

def single_argument_memoize(f):
    memo = {}

    @wraps(f)
    def wrapper(arg):
        resp = memo.get(arg)
        if resp is None:
            resp = memo[arg] = f(arg)
        return resp

    return wrapper


@single_argument_memoize
def resources_from_middle(settings_key):
    return partial(_resources_from_middle, settings_key=settings_key)


def _resources_from_middle(settings_key):
    settings = app.config[settings_key]
    token = ':'.join((settings['TOKEN'], settings['SECRET'])).encode('base64').strip()
    auth = ' '.join(('Basic', token))
    url = join_path(settings['HOST'], settings['PATH'])

    _, oauth_secret = session['access_token']
    url = '{url}?oauth_token_secret={secret}&oauth_scope={scope}' \
          .format(
              url = url,
              secret = escape(oauth_secret),
              scope = escape(url),
          )

    headers = {
        'Authorization': auth,
        'Accept': 'application/json',
    }

    current = session.get('resources')
    if current:
        current = current if isinstance(current, Resources) else Resources(*current)

        if current.expires and current.expires > time():
            # not expired yet, grant it’s a resource instance
            session['resources'] = current
            return

        if current.etag:
            headers['If-None-Match'] = current.etag

    try:
        session['resources'] = make_request(url, headers, current)

    except HttpLib2Error as exc:
        logger = app.logger.getChild(resources_from_middle.__name__).getChild(settings_key)
        logger.error('(%s) %s', type(exc).__name__, exc)
        session['resources'] = None

    except HTTPException as exc:
        logger = app.logger.getChild(resources_from_middle.__name__).getChild(settings_key)
        logger.error('(%s) code:%s - %s', type(exc).__name__, exc.code, exc)
        session['resources'] = None


def make_request(url, headers, current):
    response = PWRemoteApp.get_instance().get(url, headers=headers)

    expires = parsedate_tz(response.headers.get('Expires'))
    expires = min(mktime_tz(expires), time() + 600) if expires else None

    if response.status == 200:
        return Resources(
            data = response.data,
            etag = response.headers.get('ETag'),
            expires = expires,
        )

    elif response.status == 401:
        # unauthorized means the OAuth must be remade
        # delegate responsability to application
        return Unauthorized

    elif response.status == 304 or current:
        # no changes
        return Resources(
            data = current.data,
            etag = current.etag,
            expires = expires,
        )

    else:
        exc_class = default_exceptions.get(response.status)
        if not exc_class:
            exc_class = type(b'Code{}'.format(response.status), (HTTPException,), { 'code': response.status })
        raise exc_class(response.data)


#-----------------------------------------------------------------------
# Auxiliar

def join_path(host, path):
    host = host[:-1] if host.endswith('/') else host
    path = path[1:] if path.startswith('/') else path
    return '/'.join((host, path))


escape = lambda s: urllib.quote(s.encode('utf-8'), safe='~ ').replace(' ', '+')

Resources = namedtuple('Resources', 'data etag expires')
