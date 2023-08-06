#!/usr/bin/env python

from urllib2 import urlopen

def application(environ, start_response):
    status = "200 OK"
    response_headers = [("Content-type", "text/plain")]
    start_response(status, response_headers)
    def response():
        yield "Hello "
        yield "World!"
    return response()

def test(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == "Hello World!"
