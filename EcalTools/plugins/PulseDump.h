#ifndef __Analyzer_PulseDump_H__
#define __Analyzer_PulseDump_H__

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "DataFormats/EgammaReco/interface/SuperClusterFwd.h"
#include "DataFormats/HepMCCandidate/interface/GenParticleFwd.h"
#include "DataFormats/EcalRecHit/interface/EcalRecHitCollections.h"
#include "DataFormats/CaloRecHit/interface/CaloClusterFwd.h"

#include "SimDataFormats/Track/interface/SimTrackContainer.h"
#include "SimDataFormats/Vertex/interface/SimVertexContainer.h"

#include "TTree.h"

#include "DataFormats/EcalDigi/interface/EEDataFrame.h"
#include "DataFormats/EcalDigi/interface/EBDataFrame.h"
#include "DataFormats/EcalDigi/interface/EcalDigiCollections.h"


#include "CondFormats/EcalObjects/interface/EcalPedestals.h"
#include "CondFormats/EcalObjects/interface/EcalGainRatios.h"
#include "DataFormats/EcalDigi/interface/EEDataFrame.h"
#include "DataFormats/EcalDigi/interface/EBDataFrame.h"

#include "FWCore/Framework/interface/ESHandle.h"
#include "CondFormats/DataRecord/interface/EcalGainRatiosRcd.h"
#include "CondFormats/DataRecord/interface/EcalPedestalsRcd.h"
#include "CondFormats/EcalObjects/interface/EcalChannelStatus.h"
#include "CondFormats/DataRecord/interface/EcalChannelStatusRcd.h"

#include <memory>




class PulseDump : public edm::one::EDAnalyzer<> {
 public:    
  PulseDump(const edm::ParameterSet&);
  ~PulseDump() { }
  
  virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
  
 private:
  void FillRecHit(const EcalDataFrame& dataFrame,const EcalRecHit& rechit);

  uint32_t setFlagBits(const std::vector<std::vector<uint32_t> >& map, 
                        const uint32_t& status  );  
  
  edm::ESHandle<EcalPedestals> peds;
  edm::ESGetToken<EcalPedestals, EcalPedestalsRcd> pedsToken_;
  edm::ESHandle<EcalGainRatios>  gains;    
  edm::ESGetToken<EcalGainRatios, EcalGainRatiosRcd> gainsToken_; 
  edm::ESHandle<EcalChannelStatus> chStatus;
  edm::ESGetToken<EcalChannelStatus, EcalChannelStatusRcd> chStatusToken_;

  std::vector<int> v_chstatus_;  
  uint32_t flagmask_; // do not propagate channels with these flags on
  // Associate reco flagbit ( outer vector) to many db status flags (inner vector)
  std::vector<std::vector<uint32_t> > v_DB_reco_flags_;  
  
  
  edm::EDGetTokenT<EBDigiCollection>  ebDigiCollectionToken_; 
  edm::EDGetTokenT<EEDigiCollection>  eeDigiCollectionToken_; 

  edm::EDGetTokenT<EBRecHitCollection> ebhitcollToken_;
  edm::EDGetTokenT<EERecHitCollection> eehitcollToken_;

  double minAmplitudeBarrel_, minAmplitudeEndcap_;
  bool pedestalAnalysis_;

  TTree *_tree; //output tree
  
  int run_;
  int lumi_;
  unsigned int gain_;
  bool barrel_;
  int ietaix_;
  int iphiiy_;
  int iz_;
  double pedrms_;
  double pedval_;
  double pulse_[10];
  unsigned int rawid_;

  double ene_;
  double time_;
  double chi2_;
  int flag_kweird_;
  int flag_kdiweird_;
  
};

DEFINE_FWK_MODULE(PulseDump);

#endif
