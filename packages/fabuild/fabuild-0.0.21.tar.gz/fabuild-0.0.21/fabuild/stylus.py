"""
build utilities for Stylus templates
"""
import logging

from .watch import watch as fab_watch
from .util import get_files, build_run

logger = logging.getLogger(__name__)


def stylus(cmd='stylus', out=None, fns=None, watch=False, root_name=None):
    """
    Compiles stylus templates

    :param cmd: The base command line string to call
    :param fns: function list to run on watch event
    :param watch: If true, watch for stylus file changes
    :param out: Stylus output directory
    :param root_name: If specified, a folder with this name will
                      be used as a "root" of the styles.  Any styles
                      found under this root will keep their folder
                      structure
    """

    logger.debug("Running stylus function.")

    files = [f for f in get_files('**.styl')]

    if files:
        for f in files:
            _run_stylus_command(cmd, out, root_name, f)

    if watch:

        def callback(event, watcher):
            path = None
            if event.src_path.endswith('.styl'):
                path = event.src_path
            elif getattr(event, 'dest_path', '').endswith('.styl'):
                path = event.dest_path

            if path:
                _run_stylus_command(cmd, out, root_name, path)

        def predicate(event, watcher):
            if event.src_path.endswith('.styl'):
                return True
            elif getattr(event, 'dest_path', '').endswith('.styl'):
                return True
            return False

        fab_watch(fns=fns, callback=callback, throttle=1, predicate=predicate)


def _run_stylus_command(cmd, out, root_name, path):
    import os
    if out:
        if root_name and root_name + '/' in path:
            # /root_name/1/2/test.styl
            # 1/2/test.styl
            # 1/2
            folders = path.partition(root_name + '/')[2].rpartition('/')[0]
            if folders:
                out = os.path.join(out, folders)

        if not os.path.exists(out):
            os.makedirs(out)

        cmd = cmd + " --out " + out

    build_run(cmd + ' ' + path)
