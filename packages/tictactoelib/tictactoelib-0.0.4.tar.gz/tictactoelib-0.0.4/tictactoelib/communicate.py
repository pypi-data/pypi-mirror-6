import os
import msgpack
import subprocess


def send_payload(fh, payload):
    length = len(payload)
    len_bin = bytes([length // 256, length % 256])
    fh.write(len_bin + payload)
    fh.flush()


def get_payload(fh):
    len_s = fh.read(2)
    if len_s == b'':
        return b''
    length = len_s[0] * 256 + len_s[1]
    return fh.read(length)


def run_interactive(source_x, source_o):
    msg = msgpack.packb([source_x, source_o])
    lua_ex = os.getenv("LUA")
    run_lua = os.path.join(os.path.dirname(__file__), 'run.lua')
    if lua_ex:
        server = [lua_ex, run_lua, '--server']
    else:
        server = [run_lua, '--server']
    args = dict(bufsize=0xffff, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    with subprocess.Popen(server, **args) as f:
        send_payload(f.stdin, msg)
        xo, stop = 'x', False
        while not stop:
            msg = get_payload(f.stdout)
            if msg == b'':
                yield xo, ('error', "Terminated unexpectedly"), ""
                stop = True
            else:
                [xo, moveresult, log] = msgpack.unpackb(msg)
                xo, log = xo.decode('utf8'), log.decode('utf8')
                if moveresult[0] == b'error':
                    yield xo, ('error', moveresult[1].decode('utf8')), ""
                    stop = True
                elif moveresult[0] == b'state_coords':
                    state = moveresult[1][0].decode('utf8')
                    coords = moveresult[1][1]
                    if state == 'draw' or state == 'x' or state == 'o':
                        stop = True
                    yield xo, ['state_coords', [state, coords]], ""
