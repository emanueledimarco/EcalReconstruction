#! /usr/bin/env python
import os

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] filelist.txt")
    parser.add_option("-c","--create", dest="create",  action="store_true", default=False, help="do not submit jobs, only show the submission command")
    (options, args) = parser.parse_args()
    if len(args) < 1: raise RuntimeError, 'Expecting at least the filelist as argument'

# CUSTOMIZE THE RUN RANGES HERE
ranges = {
    283863:284035,
    283171:283835,
    282408:283067,
    281616:282092
    }

pwd = os.getcwd()

for start,stop in ranges.iteritems():
    comm = 'bsub -q 2nd -J '+str(start)+'_'+str(stop)+' -o psana_runs_'+str(start)+'_'+str(stop)+'.log '+pwd+'/submitPulseShapeAnalysisOneRange.sh '+str(start)+' '+str(stop)+' '+args[0]
    if options.create: print comm
    else: os.system(comm)

print 'DONE.'
