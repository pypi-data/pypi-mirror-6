import glob
import re

#######################################################################
# file naming conventions 

manifest = lambda index:  index + ".manifest"
seq      = lambda index:  index + ".seq"
nextpos  = lambda index:  index + ".nextpos"
pos      = lambda index:  index + ".pos"
lcp      = lambda index:  index + ".lcp"
lcp1     = lambda index:  index + ".lcp1"
lcp1x    = lambda index:  index + ".lcp1x"
lcp2     = lambda index:  index + ".lcp2"
lcp2x    = lambda index:  index + ".lcp2x"
bwt      = lambda index:  index + ".bwt"
occ      = lambda index,occrate:  index + "." + str(occrate) + ".occ"
rindex   = lambda index:  index + ".rindex"

lcp_names = {0:lcp, 1:lcp1, 2:lcp2, -1:lcp1, -2:lcp2}
lcp_xnames = {0:None, 1:lcp1x, 2:lcp2x, -1:lcp1x, -2:lcp2x}


def occtables(iname):
    """return a sorted list of tuples (occrate, filename)
    of all existing .occ files for index 'iname'"""
    def decorated(fname):
        """return the tuple (occrate, fname) filename fname,
        e.g., (123,xxx.123.occ) from xxx.123.occ"""
        return (int(re.search(r"\.(\d+)\.occ$", fname).group(1)), fname)
    fnames = glob.glob("{}.*.occ".format(iname))
    occtables = [decorated(fname) for fname in fnames]
    occtables.sort()
    return occtables
