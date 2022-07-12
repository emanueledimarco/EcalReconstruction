#include "PulseDump.h"
#include "DataFormats/EgammaReco/interface/SuperCluster.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "RecoEcal/EgammaCoreTools/interface/EcalClusterTools.h"
#include "Geometry/Records/interface/CaloTopologyRecord.h"
#include "Geometry/CaloTopology/interface/CaloTopology.h"
#include "Geometry/CaloTopology/interface/CaloSubdetectorTopology.h"
#include "DataFormats/CaloRecHit/interface/CaloCluster.h"
#include "DataFormats/ParticleFlowReco/interface/PFCluster.h"
#include "CondFormats/DataRecord/interface/EcalChannelStatusRcd.h"
#include "CommonTools/Utils/interface/StringToEnumValue.h"


#include "DataFormats/Common/interface/Handle.h"


PulseDump::PulseDump(const edm::ParameterSet& conf)
  : pedsToken_(esConsumes()),
    gainsToken_(esConsumes()),
    chStatusToken_(esConsumes()) {
  
  // for AlCaP0 stream
  // ebDigiCollectionToken_ = consumes<EBDigiCollection>(edm::InputTag("dummyHits","dummyBarrelDigis"));
  // eeDigiCollectionToken_ = consumes<EEDigiCollection>(edm::InputTag("dummyHits","dummyEndcapDigis"));

  // for phi symmetry stream
  // ebDigiCollectionToken_ = consumes<EBDigiCollection>(edm::InputTag("hltEcalPhiSymFilter","phiSymEcalDigisEB"));
  // eeDigiCollectionToken_ = consumes<EEDigiCollection>(edm::InputTag("hltEcalPhiSymFilter","phiSymEcalDigisEE"));

  ebDigiCollectionToken_ = consumes<EBDigiCollection>(conf.getParameter<edm::InputTag>("barrelDigis"));
  eeDigiCollectionToken_ = consumes<EEDigiCollection>(conf.getParameter<edm::InputTag>("endcapDigis"));

  ebhitcollToken_  = consumes<EBRecHitCollection>(conf.getParameter<edm::InputTag> ("EBRecHitCollection"));
  eehitcollToken_  = consumes<EERecHitCollection>(conf.getParameter<edm::InputTag> ("EERecHitCollection"));
  
  minAmplitudeBarrel_ = conf.getParameter<double>("minAmplitudeBarrel");
  minAmplitudeEndcap_ = conf.getParameter<double>("minAmplitudeEndcap");

  pedestalAnalysis_ = conf.getParameter<bool>("pedestalAnalysis");
  
  // Traslate string representation of flagsMapDBReco into enum values 
  const edm::ParameterSet & p=conf.getParameter< edm::ParameterSet >("flagsMapDBReco");
  std::vector<std::string> recoflagbitsStrings = p.getParameterNames();
  v_DB_reco_flags_.resize(32); 

  for (unsigned int i=0;i!=recoflagbitsStrings.size();++i){
    EcalRecHit::Flags recoflagbit = (EcalRecHit::Flags)
      StringToEnumValue<EcalRecHit::Flags>(recoflagbitsStrings[i]);
    std::vector<std::string> dbstatus_s =  
      p.getParameter<std::vector<std::string> >(recoflagbitsStrings[i]);
    std::vector<uint32_t> dbstatuses;
    for (unsigned int j=0; j!= dbstatus_s.size(); ++j){
      EcalChannelStatusCode::Code  dbstatus  = (EcalChannelStatusCode::Code)
        StringToEnumValue<EcalChannelStatusCode::Code>(dbstatus_s[j]);
      dbstatuses.push_back(dbstatus);
    }

    v_DB_reco_flags_[recoflagbit]=dbstatuses;
  }  

  flagmask_=0;
  flagmask_|=    0x1<<EcalRecHit::kNeighboursRecovered;
  flagmask_|=    0x1<<EcalRecHit::kTowerRecovered;
  flagmask_|=    0x1<<EcalRecHit::kDead;
  flagmask_|=    0x1<<EcalRecHit::kKilled;
  flagmask_|=    0x1<<EcalRecHit::kTPSaturated;
  flagmask_|=    0x1<<EcalRecHit::kL1SpikeFlag;   
  flagmask_|=    0x1<<EcalRecHit::kNoisy;
  flagmask_|=    0x1<<EcalRecHit::kFaultyHardware;
  

  edm::Service<TFileService> fs;
  
  _tree = fs->make<TTree>("pulse_tree",""); 
  
  _tree->Branch("run",&run_);
  _tree->Branch("lumi",&lumi_);
  _tree->Branch("barrel",&barrel_);
  _tree->Branch("gain",&gain_);
  _tree->Branch("pedrms",&pedrms_);
  _tree->Branch("pedval",&pedval_);
  _tree->Branch("ietaix",&ietaix_);
  _tree->Branch("iphiiy",&iphiiy_);
  _tree->Branch("iz",&iz_);
  _tree->Branch("pulse",&pulse_,"pulse[10]/D");
  _tree->Branch("rawid",&rawid_);

  _tree->Branch("ene",             &ene_);
  _tree->Branch("time",            &time_);
  _tree->Branch("chi2",            &chi2_);
  _tree->Branch("flag_kweird",     &flag_kweird_);
  _tree->Branch("flag_kdiweird",   &flag_kdiweird_);
  
}


void PulseDump::analyze(const edm::Event& e, const edm::EventSetup& es) {
  
  run_ = e.id().run();
  lumi_ = e.luminosityBlock();

  gains = es.getHandle(gainsToken_);
  peds = es.getHandle(pedsToken_);
  chStatus = es.getHandle(chStatusToken_);
  
  edm::Handle< EBDigiCollection > pEBDigis;
  edm::Handle< EEDigiCollection > pEEDigis;  
  
  e.getByToken( ebDigiCollectionToken_, pEBDigis);
  e.getByToken( eeDigiCollectionToken_, pEEDigis);
  
  edm::Handle<EcalRecHitCollection> EBHits;
  edm::Handle<EcalRecHitCollection> EEHits;

  e.getByToken(ebhitcollToken_,EBHits);
  e.getByToken(eehitcollToken_,EEHits);

  for(EBDigiCollection::const_iterator itdg = pEBDigis->begin(); itdg != pEBDigis->end(); ++itdg) {
    EcalRecHitCollection::const_iterator rhItrEB= EBHits->begin();
    while(rhItrEB != EBHits->end() && rhItrEB->id() != itdg->id()) rhItrEB++;
    if(rhItrEB != EBHits->end())    
      FillRecHit(*itdg,*rhItrEB);
  }

  for(EEDigiCollection::const_iterator itdg = pEEDigis->begin(); itdg != pEEDigis->end(); ++itdg) {
    EcalRecHitCollection::const_iterator rhItrEE= EEHits->begin();
    while(rhItrEE != EEHits->end() && rhItrEE->id() != itdg->id()) rhItrEE++;
    if(rhItrEE != EEHits->end())    
      FillRecHit(*itdg,*rhItrEE);
  }

  
}

void PulseDump::FillRecHit(const EcalDataFrame& dataFrame, const EcalRecHit& rechit) {
   
  const unsigned int nsample = EcalDataFrame::MAXSAMPLES;
  
  double maxamplitude = -std::numeric_limits<double>::max();
  
  double pedval = 0.;
  double pedrms = 0.;
  
  unsigned int gain = 12;
  
  
  const EcalPedestals::Item * aped = 0;
  const EcalMGPAGainRatio * aGain = 0;
  
  DetId detid = dataFrame.id();
  barrel_ = detid.subdetId()==EcalBarrel;  
  
  EcalChannelStatusMap::const_iterator chit = chStatus->find(detid);
  EcalChannelStatusCode::Code  dbstatus = chit->getStatusCode();  
  
  // check for channels to be excluded from reconstruction
  if ( v_chstatus_.size() > 0) {
      
      std::vector<int>::const_iterator res = 
                  std::find( v_chstatus_.begin(), v_chstatus_.end(), dbstatus );
      if ( res != v_chstatus_.end() ) return;
      
  }
  
  uint32_t flagBits = setFlagBits(v_DB_reco_flags_, dbstatus);  
  if (flagmask_ & flagBits) return;
  
  if (!barrel_) {
          unsigned int hashedIndex = EEDetId(detid).hashedIndex();
          aped  = &peds->endcap(hashedIndex);
          aGain = &gains->endcap(hashedIndex);
  } else {
          unsigned int hashedIndex = EBDetId(detid).hashedIndex();
          aped  = &peds->barrel(hashedIndex);
          aGain = &gains->barrel(hashedIndex);
  }

  // dynamic pedestal
  double dyn_pedestal = 0.;
  for(unsigned int iSample = 0; iSample < 3; iSample++) {
    const EcalMGPASample &sample = dataFrame.sample(iSample);
    dyn_pedestal += (double)(sample.adc())/3.;
  }

  for(unsigned int iSample = 0; iSample < nsample; iSample++) {
    
    const EcalMGPASample &sample = dataFrame.sample(iSample);
    
    double amplitude = 0.;
    int gainId = sample.gainId();
    
    double pedestal = 0.;
    double pederr = 0.;
    double gainratio = 1.;
        
    if (gainId==0 || gainId==3) {
      pedestal = aped->mean_x1;
      pederr = aped->rms_x1;
      gainratio = aGain->gain6Over1()*aGain->gain12Over6();
      gain = 1;
    }
    else if (gainId==1) {
      pedestal = aped->mean_x12;
      pederr = aped->rms_x12;
      gainratio = 1.;
      gain = 12;
    }
    else if (gainId==2) {
      pedestal = aped->mean_x6;
      pederr = aped->rms_x6;
      gainratio = aGain->gain12Over6();
      gain = 6;
    }

    // overwrite the pedestal from DB with the pedestal from pre-samples
    //    std::cout << "db ped = " << pedestal << "\tdyn pedestal = " << dyn_pedestal << std::endl;
    pedestal = dyn_pedestal;
    if(!pedestalAnalysis_) amplitude = ((double)(sample.adc()) - pedestal) * gainratio;
    else amplitude = (double)(sample.adc());

    if (gainId == 0) {
      //saturation
      gain = 0;
      if(!pedestalAnalysis_) amplitude = (4095. - pedestal) * gainratio;
    }
        
    pulse_[iSample] = amplitude;
    
    if (amplitude>maxamplitude) {
    //if (iSample==5) {
      maxamplitude = amplitude;
      pedval = pedestal;
      pedrms = pederr*gainratio;
    }    
        
  }
  
  
  gain_ = gain;
  pedrms_ = pedrms;
  pedval_ = pedval;
  
  double peaksig = pulse_[5]/pedrms_;
  
  if (!pedestalAnalysis_ && peaksig<10.) return;

  double minAmpl = barrel_ ? minAmplitudeBarrel_ : minAmplitudeEndcap_;
  if(!pedestalAnalysis_ && pulse_[5] < minAmpl) return;
  
  if (barrel_) {
    EBDetId ebid(detid);
    ietaix_ = ebid.ieta();
    iphiiy_ = ebid.iphi();
    iz_ = 0;
    rawid_ = ebid.rawId();
  }
  else {
    EEDetId eeid(detid);
    ietaix_ = eeid.ix();
    iphiiy_ = eeid.iy();
    iz_ = eeid.zside();  
    rawid_ = eeid.rawId();
  }
  
  // associated rechit quantities
  ene_     = rechit.energy();
  time_    = rechit.time();
  chi2_    = rechit.chi2();
  
  flag_kweird_=0;
  flag_kdiweird_=0;
  if (rechit.checkFlag(EcalRecHit::kWeird)) flag_kweird_=1;
  if (rechit.checkFlag(EcalRecHit::kDiWeird)) flag_kdiweird_=1;

  _tree->Fill();
  
  
  
  
  
}

// Take our association map of dbstatuses-> recHit flagbits and return the apporpriate flagbit word
uint32_t PulseDump::setFlagBits(const std::vector<std::vector<uint32_t> >& map, 
                                             const uint32_t& status  ){
  
  for (unsigned int i = 0; i!=map.size(); ++i){
    if (std::find(map[i].begin(), map[i].end(),status)!= map[i].end()) 
      return 0x1 << i;
  }

  return 0;
}
