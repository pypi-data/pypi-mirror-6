import sys
import pstats

args = sys.argv[1:]
if len(args) > 0:
    fname = args[0]
else:
    fname = 'printreads-optionals.prof'

stats = pstats.Stats(fname)

# Clean up filenames for the report
stats.strip_dirs()

# Sort the statistics by the cumulative time spent in the function
stats.sort_stats('time')
stats.print_stats(20)

stats.sort_stats('cumulative')
stats.print_stats(25)
