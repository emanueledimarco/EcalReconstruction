#ifndef __Analyzer_PulseTemplates_H__
#define __Analyzer_PulseTemplates_H__

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "Geometry/CaloGeometry/interface/CaloSubdetectorGeometry.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"

#include "DataFormats/EcalDigi/interface/EEDataFrame.h"
#include "DataFormats/EcalDigi/interface/EBDataFrame.h"
#include "DataFormats/EcalDigi/interface/EcalDigiCollections.h"
#include "DataFormats/EcalDigi/interface/EEDataFrame.h"
#include "DataFormats/EcalDigi/interface/EBDataFrame.h"
#include "DataFormats/EcalRecHit/interface/EcalRecHitCollections.h"

#include "CondFormats/EcalObjects/interface/EcalPedestals.h"
#include "CondFormats/EcalObjects/interface/EcalGainRatios.h"
#include "CondFormats/DataRecord/interface/EcalGainRatiosRcd.h"
#include "CondFormats/DataRecord/interface/EcalPedestalsRcd.h"
#include "CondFormats/EcalObjects/interface/EcalChannelStatus.h"
#include "CondFormats/DataRecord/interface/EcalChannelStatusRcd.h"

#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/ConsumesCollector.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/ESGetToken.h"

#include "TTree.h"
#include "TH1D.h"

#include <memory>


class PulseTemplates : public edm::one::EDAnalyzer<> {
public:    
  PulseTemplates(const edm::ParameterSet& conf);
  ~PulseTemplates() { }

  virtual void beginJob() ;
  virtual void beginRun(const edm::Run & iRun, const edm::EventSetup & iSetup );
  virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
  virtual void endRun(const edm::Run & iRun, const edm::EventSetup & iSetup ) ;
  virtual void endJob() ;

 private:
  void FillRecHit(const EcalDataFrame& dataFrame,const EcalRecHit& rechit);

  uint32_t setFlagBits(const std::vector<std::vector<uint32_t> >& map, 
                        const uint32_t& status  );  

  void writeTxtFile(int run);

  // fast alpha-beta fit from RecoLocalCalo 
  float PerformAnalyticFit(double* samples, int max_sample, double sigma_ped);
  void InitFitParameters(double* samples, int max_sample);
  double pulseShapeFunction(double t);
  std::vector<double> extrapolateSamples(int rawid);

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

  edm::ESGetToken<CaloSubdetectorGeometry, EcalEndcapGeometryRecord> theEndcapGeometryToken_;
  edm::ESGetToken<CaloSubdetectorGeometry, EcalBarrelGeometryRecord> theBarrelGeometryToken_;
  const CaloSubdetectorGeometry* theEndcapGeometry_;
  const CaloSubdetectorGeometry* theBarrelGeometry_;

  double minAmplitudeBarrel_, minAmplitudeEndcap_;
  double maxAmplitudeBarrel_, maxAmplitudeEndcap_;
  double maxChi2_;
  double minPeakSignificance_;
  bool amplitudeWeight_;
  std::vector<double> ebSimPulseShape_, eeSimPulseShape_;
  int minNHits_;
  double alphaBarrel_, alphaEndcap_, betaBarrel_, betaEndcap_;

  bool pedestalAnalysis_;

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

  // for the extrapolation
  double fAlpha_;    //parameter of the shape
  double fBeta_;     //parameter of the shape
  double fAmp_max_;  // peak amplitude
  double fTim_max_;  // time of the peak (in 25ns units)
  double fPed_max_;  // pedestal value
  double alphabeta_;
  bool doFit_;

  typedef std::map<unsigned int, std::vector<float> > tempmap;
  tempmap templates_ref_;
  std::map<int, std::vector<double> > templates_;
  std::map<int, std::vector<double> > templates_weight_;
  std::map<int, double> norm_average_;
  std::map<int, double> norm_counts_;
  std::map<int, unsigned int> rawIds_;
  std::map<int, int> iXs_;
  std::map<int, int> iYs_;
  std::map<int, int> iZs_;

  TH1D *ebSimPulseShapeH_, *eeSimPulseShapeH_;
  
};

DEFINE_FWK_MODULE(PulseTemplates);

#endif
