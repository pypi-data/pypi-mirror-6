# Module:   debugger
# Date:     5th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Debugger Tests"""

import sys

import pytest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO  # NOQA

from circuits import Debugger
from circuits.core import Event, Component


class test(Event):
    """test Event"""


class App(Component):

    raiseException = False

    def test(self, raiseException=False):
        if raiseException:
            raise Exception()


class Logger(object):

    msg = None

    def debug(self, msg):
        self.msg = msg

    error = debug


def test_main():
    app = App()
    stderr = StringIO()
    debugger = Debugger(file=stderr)
    debugger.register(app)
    while app:
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger.events

    e = Event()
    app.fire(e)
    app.flush()
    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    debugger.events = False
    assert not debugger.events

    e = Event()
    app.fire(e)

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""
    stderr.seek(0)
    stderr.truncate()


def test_file(tmpdir):
    logfile = str(tmpdir.ensure("debug.log"))
    stderr = open(logfile, "w+")

    app = App()
    debugger = Debugger(file=stderr)
    debugger.register(app)
    while app:
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger.events

    e = Event()
    app.fire(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    debugger.events = False
    assert not debugger.events

    e = Event()
    app.fire(e)

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""
    stderr.seek(0)
    stderr.truncate()


def test_filename(tmpdir):
    if "__pypy__" in sys.modules:
        pytest.skip("Broken on pypy")

    logfile = str(tmpdir.ensure("debug.log"))
    stderr = open(logfile, "r+")

    app = App()
    debugger = Debugger(file=logfile)
    debugger.register(app)
    while app:
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger.events

    e = Event()
    app.fire(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    debugger.events = False
    assert not debugger.events

    e = Event()
    app.fire(e)

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""
    stderr.seek(0)
    stderr.truncate()


def test_exceptions():
    app = App()
    stderr = StringIO()
    debugger = Debugger(file=stderr)
    debugger.register(app)
    while app:
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger.events
    assert debugger.errors

    e = test(raiseException=True)
    app.fire(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    app.flush()
    stderr.seek(0)
    s = stderr.read().strip()
    assert s.startswith("<error[*]")
    stderr.seek(0)
    stderr.truncate()

    debugger.events = False
    debugger.errors = False

    assert not debugger.events
    assert not debugger.errors

    e = test(raiseException=True)
    app.fire(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""
    stderr.seek(0)
    stderr.truncate()

    app.flush()
    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""


def test_IgnoreEvents():
    app = App()
    stderr = StringIO()
    debugger = Debugger(file=stderr)
    debugger.register(app)
    while app:
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger.events

    debugger.IgnoreEvents.extend(["test"])

    e = Event()
    app.fire(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    e = test()
    app.fire(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""
    stderr.seek(0)
    stderr.truncate()


def test_IgnoreChannels():
    app = App()
    stderr = StringIO()
    debugger = Debugger(file=stderr)
    debugger.register(app)
    while app:
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger.events
    debugger.IgnoreChannels.extend([("*", "test")])

    e = Event()
    app.fire(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    e = test()
    app.fire(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""
    stderr.seek(0)
    stderr.truncate()


def test_Logger_debug():
    app = App()
    logger = Logger()
    debugger = Debugger(logger=logger)
    debugger.register(app)
    while app:
        app.flush()

    e = Event()
    app.fire(e)
    app.flush()

    assert logger.msg == repr(e)


def test_Logger_error():
    app = App()
    logger = Logger()
    debugger = Debugger(logger=logger)
    debugger.register(app)
    while app:
        app.flush()

    e = test(raiseException=True)
    app.fire(e)
    app.flush()
    app.flush()
    assert logger.msg.startswith("ERROR <handler[*.test] (App.test)> (")
