"""
Integration with LiveReload server
"""
import logging
import thread

from livereload import server

from .util import register_keep_alive

logger = logging.getLogger(__name__)
DEFAULT_PORT = 5500


def live_reload(files=None, port=DEFAULT_PORT, throttle=3, fns=None, callback=None):
    """
    Start python livereload server, watching
    the given files using fabuild's watch function.  This
    allows for greater control over when/how the live reload
    server functions.

    :param files: Files to watch
    :param port: Port to run server on
    :param fns: Function list to run on watch trigger
    :param callback: Custom callback on watch trigger
    :param throttle: Throttling for watch event
    :return: void
    """
    # Monkey patch livereload handler
    from .monkey.livereload_forcehandler import patch; patch()
    from .watch import watch
    from requests import get
    import urllib

    def run_server():
        logger.info("Loading livereload server on port %d", port)
        s = server.Server()
        s.watch('')
        s.serve(port=port)
    thread.start_new_thread(run_server, ())

    def reload_file(event, fns):
        path = urllib.urlencode(dict(path=event.src_path))
        get('http://127.0.0.1:%d/forcereload?%s' % (port, path))
        if callback:
            callback(event, fns)

    watch(fns, ".", files=files, callback=reload_file,
          recursive=True, throttle=throttle, keep_alive=True)


def live_reload_simple(port=DEFAULT_PORT):
    """
    Start python livereload server, watching
    the given files

    :param files: Files to watch
    :param port: Port to run server on
    :return: void
    """
    def run_server():
        logger.info("Loading livereload server on port %d", port)
        server.Server().serve(port=port)
    thread.start_new_thread(run_server, ())
    register_keep_alive()


