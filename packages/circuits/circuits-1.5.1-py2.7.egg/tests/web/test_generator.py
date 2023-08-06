#!/usr/bin/env python

from urllib2 import urlopen

from circuits.web import Controller

class Root(Controller):

    def index(self):
        def response():
            yield "Hello "
            yield "World!"
        return response()

def test(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == "Hello World!"
