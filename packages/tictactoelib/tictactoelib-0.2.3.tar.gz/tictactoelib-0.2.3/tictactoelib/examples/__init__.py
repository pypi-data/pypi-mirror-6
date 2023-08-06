import os

def _read(fn):
    fullpath = os.path.join(os.path.dirname(__file__), '%s.lua' % fn)
    return open(fullpath, 'rb').read()


dumb_player = _read('dumb_player')
err_syntax = _read('err_syntax')
err_divzero = _read('err_divzero')
err_badfun = _read('err_badfun')
err_oom = _read('err_oom')
err_timeout = _read('err_timeout')
err_nothing = _read('err_nothing')
