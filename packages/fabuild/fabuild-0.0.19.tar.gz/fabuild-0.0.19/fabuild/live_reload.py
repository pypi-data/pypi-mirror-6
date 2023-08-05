"""
Integration with LiveReload server
"""
import logging
import thread

from livereload import server

from .util import register_keep_alive


logger = logging.getLogger(__name__)
DEFAULT_PORT = 5500


def live_reload(files=None, port=DEFAULT_PORT):
    """
    Start python livereload server, watching
    the given files

    :param files: Files to watch
    :param port: Port to run server on
    :return: void
    """
    def run_server():
        logger.info("Loading livereload server on port %d", port)
        s = server.Server()
        for f in files or []:
            s.watch(f)
        s.serve(port=port)
    thread.start_new_thread(run_server, ())
    register_keep_alive()


def live_reload_watch(files=None, port=DEFAULT_PORT, throttle=3, fns=None, reload=True):
    """
    Start python livereload server, watching
    the given files using fabuild's watch function.  This
    allows for greater control over when/how the live reload
    server functions.

    :param files: Files to watch
    :param port: Port to run server on
    :param fns: Function list to run on watch trigger
    :param reload: True to reload immediately
    :param throttle: Throttling for watch event
    :return: void
    """
    # Monkey patch livereload handler
    from .monkey import livereload_forcehandler
    from .watch import watch

    def run_server():
        logger.info("Loading livereload server on port %d", port)
        s = server.Server()
        s.watch('')
        s.serve(port=port)
    thread.start_new_thread(run_server, ())

    def reload_file(event, fns):
        from requests import get
        import urllib
        import logging
        logging.info("Reloading from file: %s", event.src_path)
        path = urllib.urlencode(dict(path=event.src_path))
        get('http://127.0.0.1:%d/forcereload?%s' % (port, path))

    if reload:
        from requests import get
        get('http://127.0.0.1:%d/forcereload' % (port))

    watch(fns, ".", files=files, callback=reload_file,
          recursive=True, throttle=throttle, keep_alive=True)


