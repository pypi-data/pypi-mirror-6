# coding: utf-8
from __future__ import absolute_import, print_function

import os
from .application import load_router
from .daemon import daemon as _daemon


def start_server(mapper, addr, pid_file=None, daemon=False, server=None):
    # Start on daemon mode
    if daemon:
        _daemon()

    # load application and get host and PORT
    app = load_router(mapper)

    # write PID into the lock file.
    if pid_file:
        pid_file = os.path.abspath(os.path.expanduser(pid_file))
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))

    # Start the server.
    if server:
        server(addr, app)
    else:
        import eventlet
        from eventlet import wsgi
        eventlet.patcher.monkey_patch(os=True, select=True, socket=True, thread=True, time=True)

        # Create the wsgi application and start the server.
        sock = eventlet.listen(addr)
        wsgi.server(sock, app)
