import array
import os
import time


## array utilities

def number_of_items_in_file(f, typecode):
    """return the size of file f, in units given by typecode (as for array.array).
    Either f is a string (filename) or a seekable open filelike object."""
    isize = array.array(typecode).itemsize
    if isinstance(f,str):
        bytelen = os.path.getsize(f)
    else:  # assume that f is a file object
        fp = f.tell()
        f.seek(0,os.SEEK_END)
        bytelen = f.tell()
        f.seek(fp)
    if bytelen % isize != 0:
        raise TypeError("file size does not match typecode")
    return bytelen // isize


def filled_array(typecode, n, value=0, bsize=(1<<22)):
    """returns a new array with given typecode
    (eg, "l" for long int, as in the array module)
    with n entries, initialized to the given value (default 0)
    """
    a = array.array(typecode, [value]*bsize)
    x = array.array(typecode)
    r = n
    while r >= bsize:
        x.extend(a)
        r -= bsize
    x.extend([value]*r)
    return x

def ensure_array(a, fname, typecode="l"):
    """if array a is None, allocate and read it from fname"""
    if a is None:
        a = array.array(typecode)
        items = number_of_items_in_file(fname,typecode)
        with open(fname,"rb") as fa:
            a.fromfile(fa, items)
    elif not isinstance(a, array.array):
        raise TypeError("a must be None or an array.array")
    return a

def typecode_unsigned(n):
    """return the smallest typecode for an array with unsigned values up to n"""
    if n < (1<<8):  return "B"
    if n < (1<<16):  return "H"
    if n < (1<<32):  return "I"  # may not work on small systems
    if n < (1<<64):  return "L"  # may not work on small systems
    raise ValueError("would need more than 64 bits")


# FASTA
def readfasta(f):
    """
    Read a FASTA file and returns an iterator over tuples: (comment, sequence).
    f must be an open file object.
    The returned sequence is a str object, as is the comment/header.
    """
    first = True
    wholefile = f.read()
    assert '\r' not in wholefile, "Sorry, currently don't know how to deal with files that contain \\r linebreaks"
    all = wholefile.split('\n>')
    for part in all:
        lines = part.split('\n')
        desc = lines[0] if not first else lines[0][1:]
        first = False
        del lines[0]
        seq = ''.join(lines)
        yield (desc, seq)


#######################################################################
# clock for timing

class TicToc():
    """a clock, call tic() to start, call toc() to obtain time since tic()"""
    def __init__(self):
        self.tic()
    def tic(self):
        self.zero = time.time()
    def toc(self):
        return "@{:.2f}".format(time.time() - self.zero)

#######################################################################

dontprint = lambda *args, **kwargs: None
