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

    if out:
        import os
        if not os.path.exists(out):
            os.makedirs(out)

    files = [f for f in get_files('**.styl')]

    if files:
        build_run(cmd + ' ' + ' '.join(files))

    if watch:
        def callback(event, watcher):
            import os
            path = None
            if event.src_path.endswith('.styl'):
                path = event.src_path
            elif getattr(event, 'dest_path', '').endswith('.styl'):
                path = event.dest_path

            if path:
                if out and root_name:
                    folders = path.partition(root_name)[2]
                    run_cmd = cmd + " --out " + os.path.join(out, folders)
                elif out:
                    run_cmd = cmd + " --out " + out

                build_run(run_cmd + ' ' + path)

        fab_watch(fns, '.', callback=callback, recursive=True, throttle=0)

