import os

def _read(fn):
    fullpath = os.path.join(os.path.dirname(__file__), '%s.lua' % fn)
    return open(fullpath, 'rb').read()


player1 = _read('player1')
err_syntax = _read('err_syntax')

__all__ = ['player1', 'err_syntax']
