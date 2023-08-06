from .communicate import run_interactive

def compete(source_x, source_o):
    """Fights two source files.

    Returns either:
    * ('ok', 'x' | 'draw' | 'o', gameplay)
    * ('error', ERROR_STRING, GAMEPLAY)

    ERROR_STRING := utf8-encoded string (up to 40k chars)
    GAMEPLAY := [ NUM ]
    NUM := 1..81 | 0

    NUM=1 means the move resulted in error (then ERROR_STRING is non-empty)
    GAMEPLAY is never more than 255 characters long:
      len(",".join(map(str, range(1, 81)))) == 230
    """

    gameplay = []
    for xo, moveresult, log in run_interactive(source_x, source_o):
        if moveresult[0] == 'error':
            return 'error', moveresult[1], gameplay + [0]
        elif moveresult[0] == 'state_coords':
            gameplay.append(coords_to_num(moveresult[1][1]))
            state = moveresult[1][0]
            if state == 'draw' or state == 'x' or state == 'o':
                return 'ok', state, gameplay


def coords_to_num(coords):
    """
    >>> coords_to_num((1,1,1,1))
    1
    >>> coords_to_num((3,3,3,3))
    81
    >>> coords_to_num((1,1,1,3))
    3
    >>> coords_to_num((1,3,1,1))
    7
    >>> coords_to_num((3,3,3,1))
    79
    >>> coords_to_num((3,3,2,2))
    71
    >>> coords_to_num((2,1,1,1))
    28
    >>> coords_to_num((2,2,2,2))
    41
    """
    x1, y1, x2, y2 = coords
    row, col = (x1-1) * 3 + x2, (y1-1) * 3 + y2  # row,col on 9x9 board
    return (row-1) * 9 + col
