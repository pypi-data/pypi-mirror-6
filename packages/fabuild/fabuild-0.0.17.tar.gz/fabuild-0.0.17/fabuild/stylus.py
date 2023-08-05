"""
build utilities for Stylus templates
"""
import logging

from .watch import watch as fab_watch
from .util import get_files, build_run

logger = logging.getLogger(__name__)


def stylus(cmd='stylus', fns=None, watch=False):
    """
    Compiles stylus templates

    :param cmd: The base command line string to call
    :param fns: function list to run on watch event
    :param watch: If true, watch for stylus file changes
    """

    logger.debug("Running stylus function.")

    files = [f for f in get_files('**.styl')]

    if files:
        build_run(cmd + ' ' + ' '.join(files))

    if watch:
        def callback(event, watcher):
            if event.src_path.endswith('.styl'):
                build_run(cmd + ' ' + event.src_path)
            if getattr(event, 'dest_path', '').endswith('.styl'):
                build_run(cmd + ' ' + event.dest_path)
        fab_watch(fns, '.', callback=callback,
                  recursive=True, throttle=0)

