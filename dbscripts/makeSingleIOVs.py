#! /usr/bin/env python
# USAGE: python makeSingleIOVs.py 355404 355444
import os
import sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == "__main__":

    eospath_automation = "/eos/cms/store/group/dpg_ecal/alca_ecalcalib/automation_prompt/pulseshapes/"
    dbdir="/afs/cern.ch/work/e/emanuele/public/ecal/pulseshapes_db_run3/"

    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] range1 range2...")
    parser.add_option("-p","--prefix", dest="prefix", type="string", default="template_histograms_ECAL_Run2018", help="Prefix for the file")
    parser.add_option("-b","--backup", dest="backup", action="store_true", default=False, help="Backup the file in the dir: {dbdir}".format(dbdir=dbdir))
    parser.add_option(     "--averageEE", dest="averageEE", action="store_true", default=False, help="average the inner endcap rings dynamically (default is average)")
    (options, args) = parser.parse_args()
    if len(args)<1: raise RuntimeError, 'Expecting at least one run range in the form runmin_runmax'

    rrange=args[:]
    prefix=options.prefix

    print bcolors.OKBLUE + "Now preparing the basic txt files..." + bcolors.ENDC
    start_run=rrange[0]
    end_run=rrange[-1]
    multipleIOVfile = "ecaltemplates_popcon_runs_%s_%s.db" % (start_run,end_run)
    for run in rrange:
        print bcolors.BOLD + ("Preparing txt file for run: [%s]" % run) + bcolors.ENDC
        inputtxt="{eos}/{run}/template_histograms_ECAL.txt".format(eos=eospath_automation,run=run)
        os.system("./stripTxtFile.sh {txt}".format(txt=inputtxt))
        txtfile="run%s_template_histograms_ECAL.txt" % run
        os.system("mv template_histograms_ECAL.txt %s" % txtfile)
        num_lines = sum(1 for line in open(txtfile))
        print bcolors.OKGREEN + "TXT file {txt} has {ncry} good crystals".format(txt=txtfile,ncry=num_lines) + bcolors.ENDC

        if options.averageEE:
            print bcolors.OKBLUE + "AVERAGING THE INNER ENDCAP RINGS WHICH HAVE NOT MUCH STATISTICS..." + bcolors.ENDC
            os.system("{cmsswbase}/src/EcalReconstruction/EcalTools/macro/averageEEInnerRingsPulses.py {txtfile}".format(cmsswbase=os.environ['CMSSW_BASE'],txtfile=txtfile))
            os.system("mv {base}.txt {base}_ee_original.txt; mv {base}_ee_averaged.txt {base}.txt".format(base= txtfile.replace('.txt','')))

        print bcolors.OKBLUE + "Now preparing the sqlite tag..." + bcolors.ENDC
        dbfile = "ecaltemplates_popcon_run_{run}.db".format(run=run)
        if os.path.isfile(dbfile):
            print "The sqlite file ",dbfile," is already existing here. Removing it and replacing not to append an IOV!"
            os.system("rm -f {dbfile}".format(dbfile=dbfile))
        os.system("cmsRun Ecal_PulseShapes_argv_cfg.py "+run+" "+txtfile)
        os.system("conddb --db ecaltemplates_popcon_run_{run}.db list EcalPulseShapes_data".format(run=run))
        os.system("conddb_import -f sqlite_file:ecaltemplates_popcon_run_{run}.db -i EcalPulseShapes_data -c sqlite_file:{multIOV} -b {run}".format(run=run,multIOV=multipleIOVfile))

        if options.backup:
            os.system("mv -i {txt} {dbdir}".format(txt=txtfile,dbdir=dbdir))
            os.system("mv -i {dbfile} {dbdir}".format(dbfile=dbfile,dbdir=dbdir))
            print bcolors.OKGREEN + "sqlite file ecaltemplates_popcon_run_{run}.db is in {dbdir}".format(run=run,dbdir=dbdir) + bcolors.ENDC
    
    
    print bcolors.OKBLUE +"Now checking the multiple IOV sqlite file:" + bcolors.ENDC
    os.system("conddb --db {multIOV} list EcalPulseShapes_data".format(multIOV=multipleIOVfile))

