.. _Python Programming Language: http://www.python.org/
.. _#circuits IRC Channel: http://webchat.freenode.net/?randomnick=1&channels=circuits&uio=d4
.. _FreeNode IRC Network: http://freenode.net
.. _Python Standard Library: http://docs.python.org/library/
.. _MIT License: http://www.opensource.org/licenses/mit-license.php
.. _Create an Issue: https://bitbucket.org/circuits/circuits/issue/new
.. _Mailing List: http://groups.google.com/group/circuits-users
.. _Project Website: http://circuitsframework.com/
.. _PyPi Page: http://pypi.python.org/pypi/circuits
.. _Read the Docs: http://circuits.readthedocs.org/en/latest/
.. _Downloads Page: https://bitbucket.org/circuits/circuits/downloads


circuits is a **Lightweight** **Event** driven and **Asynchronous**
**Application Framework** for the `Python Programming Language`_
with a strong **Component** Architecture.

circuits also includes a lightweight, high performance and scalable
HTTP/WSGI compliant web server as well as various I/O and Networking
components.

- Visit the `Project Website`_
- `Read the Docs`_
- Download it from the `Downloads Page`_

.. image:: https://pypip.in/v/circuits/badge.png
   :target: https://crate.io/packages/circuits/
   :alt: Latest PyPI version

.. image:: https://pypip.in/d/circuits/badge.png
   :target: https://crate.io/packages/circuits/
   :alt: Number of PyPI downloads

.. image:: https://jenkins.shiningpanda-ci.com/prologic/job/circuits/badge/icon
   :target: https://jenkins.shiningpanda-ci.com/prologic/job/circuits/
   :alt: Build Status

.. image:: https://requires.io/bitbucket/circuits/circuits-dev/requirements.png?branch=default
   :target: https://requires.io/bitbucket/circuits/circuits-dev/requirements/?branch=default
   :alt: Requirements Status


Examples
--------


Hello
.....


.. code:: python

    #!/usr/bin/env python

    """circuits Hello World"""

    from circuits import Component, Event


    class hello(Event):
        """hello Event"""


    class App(Component):

        def hello(self):
            """Hello Event Handler"""

            print("Hello World!")

        def started(self, component):
            """Started Event Handler

            This is fired internally when your application starts up and can be used to
            trigger events that only occur once during startup.
            """

            self.fire(hello())  # Fire hello Event

            raise SystemExit(0)  # Terminate the Application

    App().run()


Echo Server
...........


.. code:: python

    #!/usr/bin/env python

    """Simple TCP Echo Server

    This example shows how you can create a simple TCP Server (an Echo Service)
    utilizing the builtin Socket Components that the circuits library ships with.
    """

    from circuits import handler, Debugger
    from circuits.net.sockets import TCPServer


    class EchoServer(TCPServer):

        @handler("read")
        def on_read(self, sock, data):
            """Read Event Handler

            This is fired by the underlying Socket Component when there has been
            new data read from the connected client.

            ..note :: By simply returning, client/server socket components listen
                      to ValueChagned events (feedback) to determine if a handler
                      returned some data and fires a subsequent Write event with
                      the value returned.
            """

            return data

    # Start and "run" the system.
    # Bind to port 0.0.0.0:9000
    app = EchoServer(9000)
    Debugger().register(app)
    app.run()


Hello Web
.........


.. code:: python

    #!/usr/bin/env python

    from circuits.web import Server, Controller


    class Root(Controller):

        def index(self):
            """Index Request Handler

            Controller(s) expose implicitly methods as request handlers.
            Request Handlers can still be customized by using the ``@expose``
            decorator. For example exposing as a different path.
            """

            return "Hello World!"

    app = Server(("0.0.0.0", 9000))
    Root().register(app)
    app.run()


More `examples <https://bitbucket.org/circuits/circuits/src/tip/examples/>`_...



Features
--------

- event driven
- concurrency support
- component architecture
- asynchronous I/O components
- no required external dependencies
- full featured web framework (circuits.web)
- coroutine based synchronization primitives


Requirements
------------

- circuits has no dependencies beyond the `Python Standard Library`_.


Supported Platforms
-------------------

- Linux, FreeBSD, Mac OS X, Windows
- Python 2.6, 2.7, 3.2, 3.3
- pypy 2.0, 2.1, 2.2


Installation
------------

The simplest and recommended way to install circuits is with pip.
You may install the latest stable release from PyPI with pip::

    > pip install circuits

If you do not have pip, you may use easy_install::

    > easy_install circuits

Alternatively, you may download the source package from the
`PyPi Page`_ or the `Downloads Page`_ extract it and install using::

    > python setup.py install


You can also install th
`latest-development version <https://bitbucket.org/circuits/circuits-dev/get/tip.tar.gz#egg=circuits-dev>`_ using pip with ``pip install circuits==dev``.


License
-------

circuits is licensed under the `MIT License`_.


Feedback
--------

We welcome any questions or feedback about bugs and suggestions on how to
improve circuits. Let us know what you think about circuits. `@pythoncircuits <http://twitter.com/pythoncircuits>`_.

Do you have suggestions for improvement? Then please `Create an Issue`_
with details of what you would like to see. I'll take a look at it and
work with you to either incorporate the idea or find a better solution.


Community
---------

There is also a small community of circuits enthusiasts that you may
find on the `#circuits IRC Channel`_ on the `FreeNode IRC Network`_
and the `Mailing List`_.


Changes
-------


circuits-3.0.dev
................

- 10th Year Release
- Improved Documentation
- Improved API.
- More Examples.


