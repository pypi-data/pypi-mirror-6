"""
Contains code to monkey patch the livereload server to accept
a path argument for reloads
"""

from livereload.handlers import ForceReloadHandler, LiveReloadHandler

def monkey_patch_force_reload(self):
    """
    Monkey patching the force reload handler to support css
    """
    msg = {
        'command': 'reload',
        'path': self.get_argument('path', default=None) or '*',
        'liveCSS': True,
        'liveImg': True,

    }
    for waiter in LiveReloadHandler.waiters:
        try:
            waiter.write_message(msg)
        except:
            import logging
            logging.error('Error sending message', exc_info=True)
            LiveReloadHandler.waiters.remove(waiter)
    self.write('ok')

ForceReloadHandler._old_get = ForceReloadHandler.get
ForceReloadHandler.get = monkey_patch_force_reload
