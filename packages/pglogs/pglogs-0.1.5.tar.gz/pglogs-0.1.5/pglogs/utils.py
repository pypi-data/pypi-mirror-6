# -*- coding: utf-8 -*-
from datetime import datetime
import json

from werkzeug.local import LocalProxy
from flask import Response as FlaskResponse
from requests import Response as RequestsResponse


def _json_dumps_with_dt(some_dict):
    some_dict['dt'] = datetime.utcnow().strftime("%b %d %Y %H:%M:%S")
    return json.dumps(some_dict)


def pack_request_log(request):
    """
    The "request" arg must be a werkzeug LocalProxy instance
    """
    if not isinstance(request, LocalProxy):
        raise TypeError(
            "The request arg must be a werkzeug LocalProxy instance."
        )
    packed = dict()
    packed['url'] = request.url
    packed['method'] = request.method
    packed['headers'] = []
    for h in request.headers:
        packed['headers'].append({h[0]: h[1]})
    packed['data'] = request.data
    return _json_dumps_with_dt(packed)


def pack_response_log(response):
    """
    The "response" arg must be 'flask.wrappers.Response' instance
    or 'requests.models.Response' instance.
    """
    packed = dict()
    packed['headers'] = []

    if isinstance(response, FlaskResponse):
        packed['data'] = response.data
        packed['mimetype'] = response.mimetype
        for h in response.headers:
            packed['headers'].append({h[0]: h[1]})

    elif isinstance(response, RequestsResponse):
        packed['data'] = response.text
        packed['headers'] = dict(response.headers)

    else:
        raise TypeError("The response arg must be flask.wrappers.Response \
or requests.models.Response instance.")

    packed['status_code'] = response.status_code

    return _json_dumps_with_dt(packed)


def pack_request_from_dict(request):
    """
    The 'request' must be a dict instance and contains the following keys:
    'url', 'method', 'headers', 'data'
    """
    if not isinstance(request, dict):
        raise TypeError("The request arg must be a dict")
    packed = dict()
    packed['url'] = request.get('url')
    packed['method'] = request.get('method')
    packed['headers'] = request.get('headers')
    packed['data'] = request.get('data')
    return _json_dumps_with_dt(packed)
