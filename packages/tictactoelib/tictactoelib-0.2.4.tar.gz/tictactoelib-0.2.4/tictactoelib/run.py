#!/usr/bin/env python3
"""This file mimics run.lua in interactive mode"""


import sys

from .communicate import run_interactive


def get_source(filename):
    return open(filename, "r").read()


def main():
    if len(sys.argv) != 3:
        err = "Usage: %s player1.lua player2.lua\n" % sys.argv[0]
        print (err, file=sys.stderr)
        sys.exit(1)

    source_x, source_o = get_source(sys.argv[1]), get_source(sys.argv[2])

    for xo, moveresult, log in run_interactive(source_x, source_o):
        if moveresult[0] == 'error':
            print ("error during %s: %s" % (xo, moveresult[1]))
        elif moveresult[0] == 'state_coords':
            places = [str(p) for p in moveresult[1][1]]
            state = moveresult[1][0]
            print ("%s placed (%s)" % (xo, "; ".join(places)))
            if state == 'draw' or state == 'x' or state == 'o':
                print ("%s won" % state)


if __name__ == '__main__':
    main()
