# -*- coding: utf-8 -*-
"""
    SnapSearch Client Demo (Flask)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Intercepting a Flask_ application with WSGI middleware

    .. _Flask: http://flask.pocoo.org/

    :copyright: 2014 by `SnapSearch <https://snapsearch.io/>`_
    :license: MIT, see LICENSE for more details.

    :author: `LIU Yu <liuyu@opencps.net>`_
    :date: 2014/03/08
"""

from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return "Hello World!\r\n"


if __name__ == '__main__':

    # load SnapSearch API credentials
    import os
    credentials = os.environ.get('SNAPSEARCH_API_CREDENTIALS', ":")
    api_email, sep, api_key = credentials.partition(":")

    # initialize the interceptor
    from SnapSearch import Client, Detector, Interceptor
    interceptor = Interceptor(Client(api_email, api_key), Detector())

    # deploy the interceptor
    from SnapSearch.wsgi import InterceptorMiddleware
    app.wsgi_app = InterceptorMiddleware(app.wsgi_app, interceptor)

    # start servicing
    app.run(host="0.0.0.0", port=5000)
