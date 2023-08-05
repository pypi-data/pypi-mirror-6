"""
Contains utilities to watch files and run commands on file updates
"""
import datetime
import logging

from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

from util import get_files, register_keep_alive, run_function_list


logger = logging.getLogger(__name__)


def normalize_files_dict(files, path):
    """
    Sets up the paths for files dictionaries that will be ran through
    get_files

    get_files call with a dict must specify a path anyway.

    :param files: the files dict/list of dicts to update
    :param path: The path to add if it's missing
    :return: void
    """
    # If files is a dict and no path is specified, set the path on files.
    if isinstance(files, dict) and 'path' not in files:
        files['path'] = path
    # If files is a list of dicts and no path is specified on any of them, set the path for all
    # missing path information
    elif isinstance(files, list) and isinstance(files[0], dict):
        for f in files:
            if 'path' not in f:
                f['path'] = path


def watch(fns, path, files=None, run_immediately=True,
          recursive=False, throttle=1, keep_alive=True, poll_timeout=0, callback=None, handler=None):
    """

    Runs the given function list when items at path change

    :param fns: function list that will be run when path changes. Can be either a
                dict with 3 keys: fn, args, kwargs
                OR can be a partial function (using functools.partial)
                OR can be a list of either/both of those things.
    :param path: The path for the watchdog to observe
    :param files: The files to watch. File list will be retrieved using util.get_files,
                  If this is a dict and no path is specified, path will be passed in to files.
    :param run_immediately: True to run all functions immediately
    :param recursive: true to watch files in path recursively
    :param throttle: number of seconds to throttle each run
    :param keep_alive: true to keep build script alive for this watch
    :param poll_timeout: In certain setups, such as vagrant, FS notifications don't work.
                         Set this to a positive integer to force polling the FS.
                         This will also set the default blocking timeout.
    :param callback: Callback to run after function list
    :param handler: the watch handler to use

    """

    logger.debug("Registering watch function")

    if not path:
        raise Exception("Must specify a path to watch")

    if run_immediately:
        run_function_list(fns)

    if files:
        normalize_files_dict(files, path)

    def predicate(event, watcher):
        if watcher.files is None:
            return True
        files = get_files(watcher.files)

        return event.src_path in files or getattr(event, 'dest_path', None) in files

    handler = handler or WatchHandler(fns,
                                      throttle=throttle,
                                      files=files,
                                      callback=callback,
                                      predicate=predicate)

    observer = PollingObserver(timeout=poll_timeout) if poll_timeout else Observer()
    observer.schedule(handler, path=path, recursive=recursive)
    observer.start()

    if keep_alive:
        register_keep_alive()


class WatchHandler(FileSystemEventHandler):
    """
    Default watch handler class
    """
    def __init__(self, fns, files=None, throttle=1, callback=None, predicate=None):
        """
        initialize watch handler
        :param fns: function list to run on event
        :param callback: function to call
        """
        self.fns = fns
        self.files = files
        self.callback = callback
        self.predicate = predicate
        self.throttle = throttle
        self.last_run = None

    def dispatch(self, event):
        """Dispatches events to the appropriate methods.

        :param event:
            The event object representing the file system event.
        :type event:
            :class:`FileSystemEvent`
        """
        logger.debug("Got {} watch dispatch for path {}. Event Type: {}".format(
                event.event_type,
                event.src_path,
                str(event.event_type)
            )
        )

        if self.last_run:
            if (datetime.datetime.now() - self.last_run).total_seconds() <= self.throttle:
                logger.debug("Throttle time not elapsed - not running event")
                return

        if self.predicate and not self.predicate(event, self):
            return

        super(WatchHandler, self).dispatch(event)

    def on_any_event(self, event):
        """
        Run the functions on any event
        """
        logger.info("Got {} event for path {}. Event Type: {}".format(event.event_type,
            event.src_path, str(event.event_type)))

        try:
            self.last_run = datetime.datetime.now()

            run_function_list(self.fns)
            if self.callback:
                self.callback(event, self.fns)
        except:
            logger.exception(
                "An error occurred in watch. Event {} for {}".format(event.event_type,
                                                                     event.src_path),
                )


