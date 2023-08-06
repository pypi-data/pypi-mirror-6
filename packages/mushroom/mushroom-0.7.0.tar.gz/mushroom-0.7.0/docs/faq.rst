.. _faq:

***
FAQ
***

Why is there no Python 3 support?
=================================

Mushoom is based on gevent_ which does not support Python 3.

.. _gevent: http://gevent.org/

Are there plans to support asyncio?
===================================

No. While asyncio_ is great, it depends on the use of ``yield from``.
This can results in a very unnatural program flow. The goal of mushroom
is to make asynchronous I/O as simple and natural as possible. asyncio
does not meet this criteria. This is the same reason why mushroom is
based on gevent_ and not Tornado_.

.. _asyncio: http://docs.python.org/dev/library/asyncio.html
.. _Tornado: http://www.tornadoweb.org/

Why is there no version 1.0 of mushroom?
========================================

Once mushroom is feature complete and provides a stable API
version 1.0 will be released. For this to happen all ``FIXME``,
``TODO`` and ``XXX`` markers need to be gone. The test coverage
and documentation need to be way better, too.

Is there Django support?
========================

Max "DebVortex" Brauer has written a django-mushroom_ package which
implements an easy to use ``runserver_with_mushroom`` managment command.

A future version of mushroom will provide its own intergration which will
be part of the mushroom distribution and work slightly different. The
official Django integration will provide tools to write custom management
commands.

.. _django-mushroom: https://github.com/DebVortex/django-mushroom

Can I get commercial support?
=============================

You can also get commercial support from the maintainer and his company
`Terreon GmbH`_.

.. _Terreon GmbH: http://terreon.de/
