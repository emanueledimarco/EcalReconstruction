#! /usr/bin/env python
# example: ./submit_batch_pcl.py -p test_pcl --eos /eos/cms/store/group/dpg_ecal/comm_ecal/localreco/pulseshapes/2022/ --cfg pulseshapeTemplates_cfg.py runlist.txt 2018D

import os
import sys
import re
import time
import commands
import optparse
import datetime

def makeInputFiles(inputList, year, jobdir, options):
    inputRunListFile = open(inputList)
    inputruns = inputRunListFile.readlines()
    dataset = "/AlCaPhiSym/Run{year}-v1/RAW".format(year=year)
    filelistDir = '{jobdir}/runlists'.format(jobdir=jobdir)
    os.system('mkdir -p '+filelistDir)
    inputfiles = []
    for line in inputruns:
        run = line.rstrip()
        print("===> Making file list for RUN = ",run)
        cmd = 'dasgoclient --query "file, dataset=/AlCaPhiSym/Run{year}-v1/RAW run={run}" '.format(year=year,run=run)
        fileList = '{outdir}/run_{run}.txt'.format(outdir=filelistDir,run=run) 
        os.system('{cmd} > {fileList}'.format(cmd=cmd,fileList=fileList))
        inputfiles.append(fileList)
    return inputfiles

def makeCondorFile(jobdir, srcFiles, options):
    dummy_exec = open(jobdir+'/dummy_exec.sh','w')
    dummy_exec.write('#!/bin/bash\n')
    dummy_exec.write('bash $*\n')
    dummy_exec.close()
     
    condor_file_name = jobdir+'/condor_submit.condor'
    condor_file = open(condor_file_name,'w')
    condor_file.write('''Universe = vanilla
Executable = {de}
use_x509userproxy = True
Log        = {jd}/$(ProcId).log
Output     = {jd}/$(ProcId).out
Error      = {jd}/$(ProcId).error
getenv      = True
environment = "LS_SUBCWD={here}"
request_memory = 4000
+MaxRuntime = {rt}\n
'''.format(de=os.path.abspath(dummy_exec.name), jd=os.path.abspath(jobdir), rt=int(options.runtime*3600), here=os.environ['PWD'] ) )
    if os.environ['USER'] in ['mdunser', 'psilva']:
        condor_file.write('+AccountingGroup = "group_u_CMST3.all"\n\n\n')
    for sf in srcFiles:
        condor_file.write('arguments = {sf} \nqueue 1 \n\n'.format(sf=os.path.abspath(sf)))
    condor_file.close()
    return condor_file_name

def main():
#######################################
### usage  
#######################################
    usage = '''usage: %prog [opts] --cfg cmssw.py runslist era'''
    parser = optparse.OptionParser(usage=usage)
    now = datetime.datetime.now()
    defaultoutputdir='job_'+str(now.year)+str(now.month)+str(now.day)+"_"+str(now.hour)+str(now.minute)+str(now.second)
        
    parser.add_option('-q', '--queue',       action='store',     dest='queue',       help='run in batch in queue specified as option (default -q 8nh)', default='8nh')
    parser.add_option('-p', '--prefix',      action='store',     dest='prefix',      help='the prefix to be added to the output'                      , default=defaultoutputdir)
    parser.add_option('-c', '--create',      action='store_true',dest='create',      help='create only the jobs, do not submit them'                  , default=False)
    parser.add_option('-r', '--runtime',     action='store',     dest='runtime',     help='New runtime for condor resubmission in hours (default 8)'  , default=8, type='int');
    parser.add_option(      '--maxEvents',   action='store',     dest='maxEvents',   help='Maximum number of events to process per run (default all)' , default=-1, type='int');
    parser.add_option(      '--eos',         action='store',     dest='eos',         help='copy the output in the specified EOS path'                 , default='')
    parser.add_option(      '--cfg',         action='store',     dest='cfg',         help='the cfg to be run'                                         , default='pippo_cfg.py')
    (opt, args) = parser.parse_args()

    if len(args) != 2:
        print usage
        sys.exit(1)
    inputlist = args[0]
    era = args[1]

    runfilelists = makeInputFiles(inputlist,era,opt.prefix,opt)

    print "the outputs will be in the directory: "+opt.prefix

    jobdir = opt.prefix+"/"
    logdir = jobdir+"/log/"
    os.system("mkdir -p "+logdir)
    os.system("mkdir -p "+jobdir+"/src/")
    os.system("mkdir -p "+jobdir+"/cfg/")

    #look for the current directory
    #######################################
    pwd = os.environ['PWD']
    scramarch = os.environ['SCRAM_ARCH']
    #######################################

    srcfiles = []
    for ijob,fList in enumerate(runfilelists):
        iRunFilesF = open(fList)
        iRunFiles = iRunFilesF.readlines()
        iRunFiles = ["'"+f.rstrip()+"'" for f in iRunFiles]

        # prepare the cfg
        icfgfilename = pwd+"/"+opt.prefix+"/cfg/cmssw"+str(ijob)+"_cfg.py"
        icfgfile = open(icfgfilename,'w')
        icfgfile.write('import sys\n')
        cfgfile=open(opt.cfg,'r')
        stringtoreplace = ",".join(iRunFiles)
        #stringtoreplace = stringtoreplace[:-2] # remove the "," and the end of line for the last input
        stringtoreplace = 'fileNames = cms.untracked.vstring('+stringtoreplace+')\n#'
        maxEventsString = 'process.maxEvents = cms.untracked.PSet(  input = cms.untracked.int32({maxe}) )#'.format(maxe=opt.maxEvents)

        for line in cfgfile:
            line = re.sub(r'fileNames = cms.untracked.vstring',stringtoreplace, line.rstrip())
            line = re.sub(r'process.maxEvents = cms.untracked.PSet', maxEventsString, line.rstrip())
            icfgfile.write(line+'\n')

        icfgfile.close()

        # prepare the script to run
        psTagOutputTxt = 'template_histograms_ECAL_'+os.path.basename(fList)
        outputname = jobdir+"/src/submit_"+str(ijob)+".src"
        outputfile = open(outputname,'w')
        outputfile.write('#!/bin/bash\n')
        outputfile.write('export SCRAM_ARCH='+scramarch+'\n')
        outputfile.write('cd '+pwd+'\n')
        outputfile.write('eval `scramv1 runtime -sh`\n')
        outputfile.write('echo $PWD\n')
        outputfile.write('cmsRun '+icfgfilename+' \n')
        if(opt.eos!=''): 
            outputfile.write('xrdcp '+psTagOutputTxt+' root://eoscms/'+opt.eos+'/\n')
            outputfile.write('rm '+psTagOutputTxt+'\n')
        outputfile.close()
        logfile = logdir+"_"+str(ijob)+".log"
        scriptfile = pwd+"/"+outputname
        srcfiles.append(outputname)

    ## make the condor submission file (bulk submission)
    cf = makeCondorFile(jobdir,srcfiles,opt)
    subcmd = 'condor_submit {rf} '.format(rf = cf)
    if opt.create:
        print 'running dry, printing the commands...'
        print subcmd
    else:
        print 'submitting for real...'
        os.system(subcmd)

if __name__ == "__main__":
        main()

