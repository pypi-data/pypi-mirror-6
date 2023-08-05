from __future__ import division

import numpy as np
from numpy import cos, sin
from progressbar import ProgressBar, Bar, ETA, Percentage

def progress_bar(n, info=''):
    """
    Return a default progress bar.

    """
    return ProgressBar(widgets=[info, Percentage(), Bar('=', '[', ']'),
                                ETA()], maxval=n).start()

def _rotateuv(uvin, th, ph, xi, inverse=False):
    """
    Rotate unit vector.

    Parameters
    ----------
    uvin : (n,3) array
        The unit vector to be rotated.

    """
    matrix = np.mat([[cos(xi)*cos(th)*cos(ph)-sin(xi)*sin(ph),
                      cos(xi)*cos(th)*sin(ph)+sin(xi)*cos(ph),
                      -cos(xi)*sin(th)],
                     [-sin(xi)*cos(th)*cos(ph)-cos(xi)*sin(ph),
                      -sin(xi)*cos(th)*sin(ph)+cos(xi)*cos(ph),
                      sin(xi)*sin(th)],
                     [sin(th)*cos(ph),
                      sin(th)*sin(ph),
                      cos(th)]])

    if inverse:
        matrix = matrix.I

    return np.einsum('ij,nj->ni', matrix, uvin)

def _compress_mask(mask):
    mask = mask.ravel()
    if len(mask) == 0:
        return ''
    output = ''
    old = mask[0]
    n = 1
    for new in mask[1:]:
        if new is not old:
            if n > 2:
                output += str(n)
            elif n == 2:
                output += '+' if old else '-'
            output += '+' if old else '-'
            n = 1
            old = new
        else:
            n += 1
    if n > 2:
        output += str(n)
    elif n == 2:
        output += '+' if old else '-'
    output += '+' if old else '-'
    return output

def _uncompress_mask(mask):
    i = 0
    l = []
    nmask = len(mask)
    while i < nmask:
        val = mask[i]
        if val == '+':
            l.append(True)
            i += 1
        elif val == '-':
            l.append(False)
            i += 1
        else:
            j = i + 1
            val = mask[j]
            while val not in ('+', '-'):
                j += 1
                val = mask[j]
            l.extend(int(mask[i:j]) * (True if val == '+' else False,))
            i = j + 1
    return np.array(l, bool)

