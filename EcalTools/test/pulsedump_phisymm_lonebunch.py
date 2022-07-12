import FWCore.ParameterSet.Config as cms
import re
process = cms.Process("PulseDump")

######## configure here #######
LoneBunch = False
###############################

process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.Geometry.GeometrySimDB_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('Configuration.StandardSequences.RawToDigi_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')

process.maxEvents = cms.untracked.PSet(  input = cms.untracked.int32(5000) )
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.MessageLogger.suppressWarning = cms.untracked.vstring( "triggerSelectionLoneBunch" )

process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )

from Configuration.AlCa.GlobalTag import GlobalTag as customiseGlobalTag
process.GlobalTag.globaltag = "123X_dataRun2_v1" #auto:run2_data
#process.GlobalTag.globaltag = "123X_dataRun3_Prompt_v1" #auto:run3_data_prompt


# process.GlobalTag = cms.ESSource("PoolDBESSource",
#                                  DBParameters = cms.PSet(
#         authenticationPath = cms.untracked.string(''),
#         authenticationSystem = cms.untracked.int32(0),
#         messageLevel = cms.untracked.int32(0),
#         security = cms.untracked.string('')
#         ),
#                                  DumpStat = cms.untracked.bool(False),
#                                  ReconnectEachRun = cms.untracked.bool(False),
#                                  RefreshAlways = cms.untracked.bool(False),
#                                  RefreshEachRun = cms.untracked.bool(False),
#                                  RefreshOpenIOVs = cms.untracked.bool(False),
#                                  connect = cms.string('frontier://FrontierProd/CMS_CONDITIONS'),
#                                  globaltag = cms.string('101X_dataRun2_v8'),
#                                  pfnPostfix = cms.untracked.string(''),
#                                  pfnPrefix = cms.untracked.string(''),
#                                  snapshotTime = cms.string(''),
                                 
#                                  toGet = cms.VPSet(
#         cms.PSet(record = cms.string("EcalPulseShapesRcd"),
#                  tag = cms.string("EcalPulseShapes_October2017_rereco_v3"),
#                  connect = cms.string("frontier://FrontierProd/CMS_CONDITIONS"),
#                  ),
#         cms.PSet(record = cms.string("EcalTimeCalibConstantsRcd"),
#                  tag = cms.string("EcalTimeCalibConstants_Legacy2017_v2"),
#                  connect = cms.string("frontier://FrontierProd/CMS_CONDITIONS"),
#                  ),
#         cms.PSet(record = cms.string("EcalIntercalibConstantsRcd"),
#                  tag = cms.string("EcalIntercalibConstants_Run1_Run2_V04_offline"),
#                  connect = cms.string("frontier://FrontierProd/CMS_CONDITIONS"),
#                  ),
#         cms.PSet(record = cms.string("ESEEIntercalibConstantsRcd"),
#                  tag = cms.string("ESEEIntercalibConstants_V05_offline"),
#                  connect = cms.string("frontier://FrontierProd/CMS_CONDITIONS"),
#                  ),
#         )
#                                  )


process.load('EcalReconstruction.EcalTools.pulseDump_cfi')

process.source = cms.Source("PoolSource",
                              fileNames = cms.untracked.vstring('/store/data/Run2018D/AlCaPhiSym/RAW/v1/000/320/934/00000/94CFC099-1C9A-E811-8F6A-FA163E8A9748.root')
                            )

process.TFileService = cms.Service("TFileService", fileName = cms.string("templates.root") )

# start from RAW format for more flexibility
#process.raw2digi_step = cms.Sequence(process.RawToDigi)

# reco
from RecoLocalCalo.EcalRecProducers.ecalMultiFitUncalibRecHit_cfi import ecalMultiFitUncalibRecHit
process.ecalMultiFitUncalibRecHitStream = ecalMultiFitUncalibRecHit.clone()
process.ecalMultiFitUncalibRecHitStream.EBdigiCollection = cms.InputTag("hltEcalPhiSymFilter","phiSymEcalDigisEB")
process.ecalMultiFitUncalibRecHitStream.EEdigiCollection = cms.InputTag("hltEcalPhiSymFilter","phiSymEcalDigisEE")

from RecoLocalCalo.EcalRecProducers.ecalRecHit_cfi import ecalRecHit
process.ecalRecHitStream = ecalRecHit.clone()
process.ecalRecHitStream.EBuncalibRecHitCollection = cms.InputTag("ecalMultiFitUncalibRecHitStream","EcalUncalibRecHitsEB")
process.ecalRecHitStream.EEuncalibRecHitCollection = cms.InputTag("ecalMultiFitUncalibRecHitStream","EcalUncalibRecHitsEE")
process.ecalRecHitStream.killDeadChannels = False
process.ecalRecHitStream.recoverEBFE = False
process.ecalRecHitStream.recoverEEFE = False
process.ecalLocalRecoSequenceAlCaStream = cms.Sequence (process.ecalMultiFitUncalibRecHitStream * process.ecalRecHitStream)


# TRIGGER RESULTS FILTER
process.StableParametersRcdSource = cms.ESSource( "EmptyESSource",
    iovIsRunNotTime = cms.bool( True ),
    recordName = cms.string( "L1TGlobalStableParametersRcd" ),
    firstValid = cms.vuint32( 1 )
)

process.GlobalParametersRcdSource = cms.ESSource( "EmptyESSource",
    iovIsRunNotTime = cms.bool( True ),
    recordName = cms.string( "L1TGlobalParametersRcd" ),
    firstValid = cms.vuint32( 1 )
)


process.StableParameters = cms.ESProducer( "StableParametersTrivialProducer",
   NumberL1IsoEG = cms.uint32( 4 ),
   NumberL1JetCounts = cms.uint32( 12 ),
   NumberPhysTriggersExtended = cms.uint32( 64 ),
   NumberTechnicalTriggers = cms.uint32( 64 ),
   NumberL1NoIsoEG = cms.uint32( 4 ),
   IfCaloEtaNumberBits = cms.uint32( 4 ),
   NumberL1CenJet = cms.uint32( 4 ),
   NumberL1TauJet = cms.uint32( 4 ),
   NumberL1Mu = cms.uint32( 4 ),
   NumberConditionChips = cms.uint32( 1 ),
   IfMuEtaNumberBits = cms.uint32( 6 ),
   NumberPsbBoards = cms.int32( 7 ),
   NumberPhysTriggers = cms.uint32( 512 ),
   PinsOnConditionChip = cms.uint32( 512 ),
   UnitLength = cms.int32( 8 ),
   NumberL1ForJet = cms.uint32( 4 ),
   WordLength = cms.int32( 64 ),
   OrderConditionChip = cms.vint32( 1 )
)

process.hltGtStage2ObjectMap = cms.EDProducer( "L1TGlobalProducer",
    L1DataBxInEvent = cms.int32( 5 ),
    JetInputTag = cms.InputTag( 'hltCaloStage2Digis','Jet' ),
    AlgorithmTriggersUnmasked = cms.bool( True ),
    EmulateBxInEvent = cms.int32( 1 ),
    ExtInputTag = cms.InputTag( "hltGtStage2Digis" ),
    AlgorithmTriggersUnprescaled = cms.bool( True ),
    Verbosity = cms.untracked.int32( 0 ),
    EtSumInputTag = cms.InputTag( 'hltCaloStage2Digis','EtSum' ),
    ProduceL1GtDaqRecord = cms.bool( True ),
    PrescaleSet = cms.uint32( 1 ),
    EGammaInputTag = cms.InputTag( 'hltCaloStage2Digis','EGamma' ),
    TriggerMenuLuminosity = cms.string( "startup" ),
    ProduceL1GtObjectMapRecord = cms.bool( True ),
    AlternativeNrBxBoardDaq = cms.uint32( 0 ),
    PrescaleCSVFile = cms.string( "prescale_L1TGlobal.csv" ),
    TauInputTag = cms.InputTag( 'hltCaloStage2Digis','Tau' ),
    BstLengthBytes = cms.int32( -1 ),
    MuonInputTag = cms.InputTag( 'hltGmtStage2Digis','Muon' )
)

process.triggerSelectionLoneBunch = cms.EDFilter( "HLTL1TSeed",
    L1SeedsLogicalExpression = cms.string( "L1_IsolatedBunch" ),
    #L1SeedsLogicalExpression = cms.string( "NOT L1_IsolatedBunch" ),
    L1EGammaInputTag = cms.InputTag( 'hltCaloStage2Digis','EGamma' ),
    L1JetInputTag = cms.InputTag( 'hltCaloStage2Digis','Jet' ),
    saveTags = cms.bool( True ),
    L1ObjectMapInputTag = cms.InputTag( "hltGtStage2ObjectMap" ),
    L1EtSumInputTag = cms.InputTag( 'hltCaloStage2Digis','EtSum' ),
    L1TauInputTag = cms.InputTag( 'hltCaloStage2Digis','Tau' ),
    L1MuonInputTag = cms.InputTag( 'hltGmtStage2Digis','Muon' ),
    L1GlobalInputTag = cms.InputTag( "hltGtStage2Digis" )
)



if LoneBunch:
    process.p = cms.Path(process.hltGtStage2ObjectMap *
                         process.triggerSelectionLoneBunch * 
                         process.bunchSpacingProducer *
                         process.ecalLocalRecoSequenceAlCaStream *
                         process.pulseDump )
else:
    process.p = cms.Path(process.bunchSpacingProducer *
                         process.ecalLocalRecoSequenceAlCaStream *
                         process.pulseDump )
