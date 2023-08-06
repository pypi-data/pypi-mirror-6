#!/usr/bin/env python3

import os
import sys
import msgpack
import subprocess


def get_source(filename):
    return open(filename, "r").read()


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


def main():
    if len(sys.argv) != 3:
        err = "Usage: %s player1.lua player2.lua\n" % sys.argv[0]
        print (err, file=sys.stderr)
        sys.exit(1)

    f1, f2 = sys.argv[1], sys.argv[2]
    source_x, source_o = get_source(f1), get_source(f2)
    msg = msgpack.packb([source_x, source_o])
    run_lua = os.path.join(os.path.dirname(__file__), 'run.lua')
    f = subprocess.Popen([run_lua, '--server'],
                         bufsize=0xffff,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE
    )
    send_payload(f.stdin, msg)

    xo, stop = 'x', False
    while not stop:
        msg = get_payload(f.stdout)
        if msg == b'':
            print ("Terminated unexpectedly during %s" % xo)
            stop = True
        else:
            [xo, moveresult, log] = msgpack.unpackb(msg)
            xo, log = xo.decode('utf8'), log.decode('utf8')
            if moveresult[0] == b'error':
                print ("%s error: %s" % (xo, moveresult[1].decode('utf8')))
            elif moveresult[0] == b'state_coords':
                places = [str(p) for p in moveresult[1][1]]
                state = moveresult[1][0].decode('utf8')
                print ("%s placed (%s)" % (xo, "; ".join(places)))
                if state == 'draw' or state == 'x' or state == 'o':
                    print ("%s won" % state)
                    stop = True


if __name__ == '__main__':
    main()
