Handlers
========


Explicit Event Handlers
-----------------------


Event Handlers are methods of components that are invoked when a matching
event is dispatched. These can be declared explicitly on a
:class:`~circuits.core.components.BaseComponent` or
:class:`~circuits.core.components.Component` or by using the
:func:`~circuits.core.handlers.handler` decorator.

.. literalinclude:: examples/handler_annotation.py
   :language: python
   :linenos:

:download:`Download handler_annotation.py <examples/handler_annotation.py>`

The handler decorator on line 14 turned the method ``_on_started`` into an
event handler for the event ``started``.

When defining explicit event handlers in this way, it's convention to
use the following pattern::
   
   @handler("foo")
   def _on_foo(self, ...):
      ...

This makes reading code clear and concise and obvious to the reader 
that the method is not part of the class's public API
(*leading underscore as per Python convention*) and that it is invoked
for events of type ``SomeEvent``.

The optional keyword argument "``channel``" can be used to attach the
handler to a different channel than the component's channel
(*as specified by the component's channel attribute*).

Handler methods must be declared with arguments and keyword arguments that
match the arguments passed to the event upon its creation. Looking at the
API for :class:`~circuits.core.events.Started` you'll find that the
component that has been started is passed as an argument to its constructor.
Therefore, our handler method must declare one argument (*Line 15*).

The ``@handler(...)`` decorator accepts other keyword arguments that 
influence the behavior of the event handler and its invocation. Details can
be found in the API description of :func:`~circuits.core.handlers.handler`.


Implicit Event Handlers
-----------------------


To make things easier for the developer when creating many event handlers
and thus save on some typing, the :class:`~circuits.core.components.Component`
can be used and subclassed instead which provides an implicit mechanism for
creating event handlers.

Basically every method in the component is automatically and implicitly
marked as an event handler with ``@handler(<name))`` where ``<name>>`` is
the name of each method applied.

The only exceptions are:

- Methods are start with an underscore ``_``.
- Methods already marked explicitly with the ``@handler(...)`` decorator.

.. note::
   You can specify that a method not be an event handler by marking it with
   ``@handler(False)``.
