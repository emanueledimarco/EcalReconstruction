import sys
import os.path
import FWCore.ParameterSet.Config as cms

POPULATE_MC = False
FIRST_RUN_DATA = '2'

if POPULATE_MC: run = "mc"
else: 
    run     = sys.argv[2]
    txtfile =  sys.argv[3] # txt file prefix

print("reading txt file ",txtfile)

process = cms.Process("ProcessOne")
#process.load("CondCore.DBCommon.CondDBCommon_cfi")
process.load("CondCore.CondDB.CondDB_cfi")
process.CondDB.connect = 'sqlite_file:ecaltemplates_popcon_run_'+run+'.db'
process.CondDB.DBParameters.authenticationPath = '.'
process.CondDB.DBParameters.messageLevel=cms.untracked.int32(1)

process.MessageLogger = cms.Service("MessageLogger",
                                    debugModules = cms.untracked.vstring('*'),
                                    destinations = cms.untracked.vstring('cout')
                                    )

process.source = cms.Source("EmptyIOVSource",
                            firstValue = cms.uint64(1),
                            lastValue = cms.uint64(1),
                            timetype = cms.string('runnumber'),
                            interval = cms.uint64(1)
                            )

process.PoolDBOutputService = cms.Service("PoolDBOutputService",
    process.CondDB,
    logconnect = cms.untracked.string('sqlite_file:logecaltemplates_popcon_runs_'+run+'.db'),
    timetype = cms.untracked.string('runnumber'),
    toPut = cms.VPSet(cms.PSet(
        record = cms.string('EcalPulseShapesRcd'),
        tag = cms.string('EcalPulseShapes_data')
    ))
)

if os.path.isfile(txtfile)==False:
    print("WARNING: file ",txtfile," does not exist. Exiting... ")
    exit

process.Test1 = cms.EDAnalyzer("ExTestEcalPulseShapesAnalyzer",
    SinceAppendMode = cms.bool(True),
    record = cms.string('EcalPulseShapesRcd'),
    loggingOn = cms.untracked.bool(True),
    Source = cms.PSet(
        firstRun = cms.string('1' if POPULATE_MC else FIRST_RUN_DATA),
        inputFileName = cms.string(txtfile),
        previousTagFileName = cms.string("/afs/cern.ch/work/e/emanuele/public/ecal/pulseshapes_db/template_histograms_ECAL_Run2015C_lowPU.txt"), # if provided, for the missing crystals in the txt file above, uses the values here. If not, uses MC values below 
        EBPulseShapeTemplate = cms.vdouble (
            1.13979e-02, 7.58151e-01, 1.00000e+00, 8.87744e-01, 6.73548e-01, 4.74332e-01, 3.19561e-01, 2.15144e-01, 1.47464e-01, 1.01087e-01, 6.93181e-02, 4.75044e-02  # nominal
            ) ,
        EEPulseShapeTemplate = cms.vdouble (
            1.16442e-01, 7.56246e-01, 1.00000e+00, 8.97182e-01, 6.86831e-01, 4.91506e-01, 3.44111e-01, 2.45731e-01, 1.74115e-01, 1.23361e-01, 8.74288e-02, 6.19570e-02  # nominal
            )
        )
)


process.p = cms.Path(process.Test1)
