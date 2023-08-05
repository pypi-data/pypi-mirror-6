# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses.

import io
import string
import hashlib

from random import getrandbits, choice

from os import urandom
from base64 import standard_b64encode

import flask
from werkzeug import Response

try:
    from PIL import ImageFile
except ImportError:
    ImageFile = None


def urlscheme(request):
    """return the current scheme (HTTP or HTTPS)"""

    if request.url.startswith('https://'):
        return 'https'
    return request.headers.get('X-Forwarded-Proto', 'http')


def md5(data):
    """returns md5 of data has hexdigest"""
    return hashlib.md5(data).hexdigest()


def A1(username, passwd, realm='Application'):
    """A1 HTTP Digest Authentication"""
    return md5(username + ':' + realm + ':' + passwd)


def prove_auth(app, req):
    """calculates digest response (MD5 and qop)"""
    auth = req.authorization

    account = app.db.accounts.find_one({'email': auth.username})
    _A1 = account['passwd'] if account else standard_b64encode(urandom(16))

    if str(auth.get('qop', '')) == 'auth':
        A2 = ':'.join([auth.nonce, auth.nc, auth.cnonce, 'auth',
                       md5(req.method + ':' + auth.uri)])
        return md5(_A1 + ':' + A2)
    else:
        # compatibility with RFC 2069: https://tools.ietf.org/html/rfc2069
        A2 = ':'.join([auth.nonce, md5(req.method + ':' + auth.uri)])
        return md5(_A1 + ':' + A2)


def login(f):
    """login decorator using HTTP Digest Authentication.  Pattern based on
    http://flask.pocoo.org/docs/patterns/viewdecorators/

    -- http://developer.getcloudapp.com/usage/#authentication"""

    app = flask.current_app

    def dec(*args, **kwargs):
        """This decorater function will send an authenticate header, if none
        is present and denies access, if HTTP Digest Auth failed."""

        request = flask.request
        usehtml = request.accept_mimetypes.accept_html

        if not request.authorization:
            response = Response(
                'Unauthorized', 401,
                content_type='text/html; charset=utf-8' if usehtml else 'application/json'
            )
            response.www_authenticate.set_digest(
                'Application', algorithm='MD5',
                nonce=standard_b64encode(urandom(32)),
                qop=('auth', ), opaque='%x' % getrandbits(128))
            return response
        else:
            account = app.db.accounts.find_one({'email': request.authorization.username})
            if account and account['activated_at'] == None:
                return Response('[ "Your account hasn\'t been activated. Please ' \
                                + 'check your email and activate your account." ]', 409)
            elif prove_auth(app, request) != request.authorization.response:
                return Response('Forbidden', 403)
        return f(*args, **kwargs)
    return dec


class private:
    """Check for private items in the web interface and ask for credentials if necessary.
    """
    def __init__(self, condition):
        self.condition = condition

    def __call__(self, f):
        def check(*args, **kwargs):
            item = flask.current_app.db.items.find_one({'short_id': kwargs['short_id']})
            if (item and not item['private']) or not self.condition(flask.request):
                return f(*args, **kwargs)
            return login(f)(*args, **kwargs)
        return check


def slug(length=8, charset=string.ascii_lowercase+string.digits):
    """generates a pseudorandom string of a-z0-9 of given length"""
    return ''.join([choice(charset) for x in xrange(length)])


def clear(account):
    for key in '_id', 'items', 'passwd':
        account.pop(key, None)
    return account


class conf:
    """stores conf.yaml, regenwolken has these config values:
        - HOSTNAME
        - BIND_ADDRESS
        - PORT
        - MONGODB_HOST
        - MONGODB_NAME
        - MONGODB_PORT
        - MONGODB_SESSION_SIZE: size used for the capped collection

        - ALLOWED_CHARS: characters allowed in username
        - MAX_CONTENT_LENGTH: maximum content length before raising 413
        - ALLOW_PRIVATE_BOOKMARKS: True | False
        - PUBLIC_REGISTRATION: instant registration, True | False

        - CACHE_BACKEND: SimpleCache
        - CACHE_TIMEOUT: 15*60

        - THUMBNAILS: True
        - SYNTAX_HIGHLIGHTING: True
        - MARKDOWN_FORMATTING: True
        """

    HOSTNAME = "localhost"
    BIND_ADDRESS = "127.0.0.1"
    PORT = 3000
    LOGFILE = 'rw.log'

    MONGODB_HOST = "127.0.0.1"
    MONGODB_PORT = 27017
    MONGODB_NAME = 'cloudapp'
    MONGODB_SESSION_SIZE = 100*1024

    ALLOWED_CHARS = string.digits + string.ascii_letters + '.- @'
    MAX_CONTENT_LENGTH = 64*1024*1024
    ALLOW_PRIVATE_BOOKMARKS = False
    PUBLIC_REGISTRATION = False
    SHORT_ID_MIN_LENGTH = 3

    CACHE_BACKEND = 'SimpleCache'
    CACHE_TIMEOUT = 15*60

    THUMBNAILS = True
    SYNTAX_HIGHLIGHTING = True
    MARKDOWN_FORMATTING = True


def thumbnail(fp, size=128, bs=2048):
    """generate png thumbnails"""

    p = ImageFile.Parser()

    try:
        while True:
            s = fp.read(bs)
            if not s:
                break
            p.feed(s)

        img = p.close()
        img.thumbnail((size, size))
        op = io.BytesIO()
        img.save(op, 'PNG')
        op.seek(0)
        return op.read().encode('base64')
    except IOError:
        raise


class Struct:
    """dict -> class, http://stackoverflow.com/questions/1305532/convert-python-dict-to-object"""
    def __init__(self, **entries):
        self.__dict__.update(entries)


def ppsize(num):
    '''pretty-print filesize.
    http://blogmag.net/blog/read/38/Print_human_readable_file_size'''
    for x in ['bytes','KiB','MiB','GiB','TB']:
        if num < 1024.0:
            return "%3.2f %s" % (num, x)
        num /= 1024.0
