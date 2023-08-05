"""
Methods to use in fabfiles
"""
import functools

from fabric import api as fab


def build_docs(path="./docs/", command="make html"):
    import fabuild as fb

    with fab.lcd(path):
        fb.build_run(command)


def watch_docs(path="./docs/", src_path=None, command="make html"):
    import fabuild as fb

    watch_files = [
        dict(match="*.rst", ignore="*_build*", path=path),
    ]
    if src_path:
        watch_files.append(dict(match="*.py", path=src_path))

    build_fn = functools.partial(build_docs, path=path, command=command)
    fb.watch(build_fn, "./", files=watch_files, recursive=True)


def deploy(setup_file='./setup.py'):
    fab.local('vim {}'.format(setup_file))
    fab.local('python {} sdist upload'.format(setup_file))


def push():
    fab.local('git status')
    fab.local('git diff')
    ans = raw_input('Continue git push? [y/N]: ')
    if ans.lower().startswith('y'):
        fab.local('git add .')
        fab.local('git push')
