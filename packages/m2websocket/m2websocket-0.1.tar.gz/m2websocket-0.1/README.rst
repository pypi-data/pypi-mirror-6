m2websocket
===========

Makes handling websockets with Mongrel2 and Python easy.

This module was built for `First
Opinion <http://firstopinionapp.com>`__.

Example
-------

Typical websocket *hello world* example, creating an echo server:

.. code:: python

    from m2websocket import Connection

    conn = Connection("tcp://localhost:port", "tcp://localhost:port")

    while True:
        req = conn.recv_frame()
        conn.reply_websocket(req, req.body, req.opcode)

Yup, that's all there is to it, much easier than `this
example <https://github.com/zedshaw/mongrel2/blob/master/examples/ws/python/echo.py>`__.

You can see a working example of the echo server (with a working
mongrel2 conf file and python script) by looking in the ``example/``
directory in the Github repo.

Install it
----------

Use Pip:

::

    pip install m2websocket

License
-------

MIT
