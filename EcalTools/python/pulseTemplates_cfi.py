import FWCore.ParameterSet.Config as cms

pulseTemplates = cms.EDAnalyzer("PulseTemplates",
    ChannelStatusToBeExcluded = cms.vstring(   'kNoisy',
                                               'kNNoisy',
                                               'kFixedG6',
                                               'kFixedG1',
                                               'kFixedG0',
                                               'kNonRespondingIsolated',
                                               'kDeadVFE',
                                               'kDeadFE',
                                               'kNoDataNoTP',),
                            
    # reco flags association to DB flag
    flagsMapDBReco = cms.PSet(
        kGood  = cms.vstring('kOk','kDAC','kNoLaser','kNoisy'),
        kNoisy = cms.vstring('kNNoisy','kFixedG6','kFixedG1'),
        kNeighboursRecovered = cms.vstring('kFixedG0',
                                                                                   'kNonRespondingIsolated',
                                                                                   'kDeadVFE'),
        kTowerRecovered = cms.vstring('kDeadFE'),
        kDead           = cms.vstring('kNoDataNoTP')
        ),
    barrelDigis = cms.InputTag("hltEcalPhiSymFilter","phiSymEcalDigisEB"),
    endcapDigis = cms.InputTag("hltEcalPhiSymFilter","phiSymEcalDigisEE"),
    EBRecHitCollection = cms.InputTag("ecalRecHitStream","EcalRecHitsEB"),
    EERecHitCollection = cms.InputTag("ecalRecHitStream","EcalRecHitsEE"),
    minAmplitudeBarrel = cms.double(15),
    minAmplitudeEndcap = cms.double(20),
    maxAmplitudeBarrel = cms.double(10000),
    maxAmplitudeEndcap = cms.double(10000),
    minNHits = cms.int32(10),
    maxTimeShift = cms.double(5.0),
    maxChi2 = cms.double(20),
    minPeakSignificance = cms.double(10),
    amplitudeWeight = cms.bool(False),

    alphaBarrel = cms.double(1.138),
    alphaEndcap = cms.double(1.890),
    betaBarrel  = cms.double(1.655),
    betaEndcap  = cms.double(1.400),

    ebSimPulseShape = cms.vdouble( 1.13979e-02, 7.58151e-01, 1.00000e+00, 8.87744e-01, 6.73548e-01, 4.74332e-01, 3.19561e-01, 2.15144e-01, 1.47464e-01, 1.01087e-01, 6.93181e-02, 4.75044e-02 ),
    eeSimPulseShape = cms.vdouble( 1.16442e-01, 7.56246e-01, 1.00000e+00, 8.97182e-01, 6.86831e-01, 4.91506e-01, 3.44111e-01, 2.45731e-01, 1.74115e-01, 1.23361e-01, 8.74288e-02, 6.19570e-02 ),

    pedestalAnalysis = cms.bool(False)
)
