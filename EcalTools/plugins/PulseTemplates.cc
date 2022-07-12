#include "PulseTemplates.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "FWCore/Utilities/interface/isFinite.h"
#include "FWCore/Framework/interface/ConsumesCollector.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "Geometry/Records/interface/CaloTopologyRecord.h"
#include "Geometry/CaloTopology/interface/CaloTopology.h"
#include "Geometry/CaloTopology/interface/CaloSubdetectorTopology.h"
#include "CondFormats/DataRecord/interface/EcalChannelStatusRcd.h"
#include "CommonTools/Utils/interface/StringToEnumValue.h"
#include "DataFormats/Common/interface/Handle.h"
#include "CLHEP/Matrix/Vector.h"
#include "CLHEP/Matrix/SymMatrix.h"

#include <iostream>
#include <fstream>

PulseTemplates::PulseTemplates(const edm::ParameterSet& conf)
  : pedsToken_(esConsumes()),
    gainsToken_(esConsumes()),
    chStatusToken_(esConsumes()),
    theEndcapGeometryToken_(esConsumes(edm::ESInputTag("", "EcalEndcap"))),
    theBarrelGeometryToken_(esConsumes(edm::ESInputTag("", "EcalBarrel"))) {
  
  ebDigiCollectionToken_ = consumes<EBDigiCollection>(conf.getParameter<edm::InputTag>("barrelDigis"));
  eeDigiCollectionToken_ = consumes<EEDigiCollection>(conf.getParameter<edm::InputTag>("endcapDigis"));

  ebhitcollToken_  = consumes<EBRecHitCollection>(conf.getParameter<edm::InputTag> ("EBRecHitCollection"));
  eehitcollToken_  = consumes<EERecHitCollection>(conf.getParameter<edm::InputTag> ("EERecHitCollection"));
 
  minAmplitudeBarrel_ = conf.getParameter<double>("minAmplitudeBarrel");
  minAmplitudeEndcap_ = conf.getParameter<double>("minAmplitudeEndcap");
  maxAmplitudeBarrel_ = conf.getParameter<double>("maxAmplitudeBarrel");
  maxAmplitudeEndcap_ = conf.getParameter<double>("maxAmplitudeEndcap");

  minNHits_ = conf.getParameter<int>("minNHits");  
  maxChi2_ = conf.getParameter<double>("maxChi2");
  minPeakSignificance_ = conf.getParameter<double>("minPeakSignificance");
  amplitudeWeight_ = conf.getParameter<bool>("amplitudeWeight");

  alphaBarrel_ = conf.getParameter<double>("alphaBarrel");
  alphaEndcap_ = conf.getParameter<double>("alphaEndcap");
  betaBarrel_ = conf.getParameter<double>("betaBarrel");
  betaEndcap_ = conf.getParameter<double>("betaEndcap");

  ebSimPulseShape_ = conf.getParameter<std::vector<double>>("ebSimPulseShape");
  eeSimPulseShape_ = conf.getParameter<std::vector<double>>("eeSimPulseShape");

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
  

}

// ------------ method called once each job just before starting event loop  ------------
void PulseTemplates::beginJob() {

  // this is the reference template file. It is used only to put constraints on single hit timing information in a robust way
  // based on the ratio S_max / S_max-1
  int iseb;
  unsigned int detid;
  
  std::ifstream myfile;
  myfile.open("/afs/cern.ch/work/e/emanuele/public/ecal/pulseshapes_db/template_histograms_ECAL_Run2015C_lowPU.txt");
  if (myfile.is_open()) {
    while ( !myfile.eof() ) {
      myfile >> iseb;
      myfile >> detid;
      std::vector<float> samples;
      samples.resize(12);
      for(int s=0; s<12; ++s) myfile >> samples[s];
      templates_ref_[detid] = samples;
    }
    myfile.close();
  }
  else std::cout << "Unable to open file";   

  // build the simTemplate (used only in case of problems)
  ebSimPulseShapeH_ = new TH1D("ebSimPulseShapeH","",15,0,15);
  eeSimPulseShapeH_ = new TH1D("eeSimPulseShapeH","",15,0,15);
  
  int SAMPLES= EcalDataFrame::MAXSAMPLES + 5; // readout samples + 5 OOT 
  int firstSignalSample=3;
  for(int i=0; i<SAMPLES; ++i) {
    if(i<firstSignalSample) {
      ebSimPulseShapeH_->SetBinContent(i+1, 0.);
      ebSimPulseShapeH_->SetBinError(i+1, 0.);
      ebSimPulseShapeH_->SetBinContent(i+1, 0.);
      ebSimPulseShapeH_->SetBinError(i+1, 0.);
    }
    else {
      ebSimPulseShapeH_->SetBinContent(i+1, ebSimPulseShape_[i-firstSignalSample]);
      ebSimPulseShapeH_->SetBinError(i+1, 0.);
      eeSimPulseShapeH_->SetBinContent(i+1, eeSimPulseShape_[i-firstSignalSample]);
      eeSimPulseShapeH_->SetBinError(i+1, 0.);
    }
  }
}

void PulseTemplates::beginRun( const edm::Run & iRun, const edm::EventSetup & iSetup ) { }

void PulseTemplates::endRun( const edm::Run & iRun, const edm::EventSetup & iSetup ) {
  writeTxtFile(iRun.run());
}



// ------------ method called once each job just after ending the event loop  ------------
void  PulseTemplates::endJob() {
  writeTxtFile(run_);
  delete ebSimPulseShapeH_;
  delete eeSimPulseShapeH_;
}


void PulseTemplates::analyze(const edm::Event& e, const edm::EventSetup& es) {

  // initialize maps (once per job)
  if(templates_.size()==0)
  {
    theEndcapGeometry_ = &es.getData(theEndcapGeometryToken_);
    theBarrelGeometry_ = &es.getData(theBarrelGeometryToken_);
    for(auto& detid : theBarrelGeometry_->getValidDetIds(DetId::Ecal, EcalBarrel))
    {
        EBDetId ebid(detid);
        auto rawid = ebid.rawId();
        std::vector<double> templ;
        templ.resize(10, 0.);
        templates_[rawid] = templ;
        norm_average_[rawid] = 0.;
        norm_counts_[rawid] = 0;
        rawIds_[rawid] = rawid;
        iXs_[rawid] = ebid.ieta();
        iYs_[rawid] = ebid.iphi();
        iZs_[rawid] = 0;
    }
    for(auto& detid : theEndcapGeometry_->getValidDetIds(DetId::Ecal, EcalEndcap))
    {
        EEDetId eeid(detid);
        auto rawid = eeid.rawId();
        std::vector<double> templ;
        templ.resize(10, 0.);
        templates_[rawid] = templ;
        norm_average_[rawid] = 0.;
        norm_counts_[rawid] = 0;
        rawIds_[rawid] = rawid;
        iXs_[rawid] = eeid.ix();
        iYs_[rawid] = eeid.iy();
        iZs_[rawid] = eeid.zside();
    }
  }

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

void PulseTemplates::FillRecHit(const EcalDataFrame& dataFrame, const EcalRecHit& rechit) {

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
  
  if (!pedestalAnalysis_ && peaksig<minPeakSignificance_) return;

  double minAmplitude = barrel_ ? minAmplitudeBarrel_ : minAmplitudeEndcap_;
  double maxAmplitude = barrel_ ? maxAmplitudeBarrel_ : maxAmplitudeEndcap_;
  if(!pedestalAnalysis_ && (pulse_[5] < minAmplitude || pulse_[5] > maxAmplitude)) return;
    
  // associated rechit quantities
  ene_     = rechit.energy();
  time_    = rechit.time();
  chi2_    = rechit.chi2();
  
  flag_kweird_=0;
  flag_kdiweird_=0;
  if (rechit.checkFlag(EcalRecHit::kWeird)) flag_kweird_=1;
  if (rechit.checkFlag(EcalRecHit::kDiWeird)) flag_kdiweird_=1;

  if (flag_kweird_ || flag_kdiweird_) return;

  double weight = amplitudeWeight_ ? pow(pulse_[5],2) : 1.0;

  for(int iSample(0); iSample < 10; iSample++) 
    templates_[detid.rawId()][iSample] += pulse_[iSample]/maxamplitude * weight;
  norm_average_[detid.rawId()] += weight;
  norm_counts_[detid.rawId()] ++;
}

// Take our association map of dbstatuses-> recHit flagbits and return the apporpriate flagbit word
uint32_t PulseTemplates::setFlagBits(const std::vector<std::vector<uint32_t> >& map, 
                                     const uint32_t& status  ){
  
  for (unsigned int i = 0; i!=map.size(); ++i){
    if (std::find(map[i].begin(), map[i].end(),status)!= map[i].end()) 
      return 0x1 << i;
  }

  return 0;
}


void PulseTemplates::writeTxtFile(int run) {

  // text file to fill the DB objects with templates

  TString nameoutput = Form("template_histograms_ECAL_run_%d.txt",run);
  std::ofstream txtdumpfile;  
  txtdumpfile.open (nameoutput.Data(), std::ios::out | std::ios::trunc);

  int nCry=0;
  for(std::map<int, std::vector<double> >::iterator it=templates_.begin(); it!=templates_.end(); ++it) {
    unsigned int rawId = it->first;
    DetId detid(rawId);
    barrel_ = detid.subdetId()==EcalBarrel;  

    txtdumpfile.unsetf ( std::ios::floatfield ); 
    txtdumpfile << ( barrel_ ? 1 : 0 ) << "\t";
    txtdumpfile << iXs_[rawId] << "\t" << iYs_[rawId] << "\t" << iZs_[rawId] << "\t" << rawId << "\t" << norm_counts_[rawId] << "\t";
    txtdumpfile.precision(6);
    txtdumpfile.setf( std::ios::fixed, std::ios::floatfield ); // floatfield set to fixed
    
    std::cout << "Writing templates histogram. Barrel = " << barrel_ << ".  ix = " << iXs_[rawId] << "  iy = " << iYs_[rawId] << " got " << norm_counts_[rawId] << " events" << std::endl;

    float pdfval[12];

    TH1D *simTemplate = barrel_ ? ebSimPulseShapeH_ : eeSimPulseShapeH_;
    for(int iSample(3); iSample < 10; iSample++) {
      if(norm_counts_[rawId]>=minNHits_) 
        pdfval[iSample-3] = std::max((it->second)[iSample],0.) / norm_average_[rawId];
      else
        pdfval[iSample-3] = simTemplate->GetBinContent(iSample+1);
    }

    std::vector<double> extraSamples;
    if (norm_counts_[rawId]>=minNHits_) {
      extraSamples = extrapolateSamples(rawId);
    } else {
      std::cout << "Use SIM samples for rawId = " << rawId << std::endl;
      for(int iExtraSample(0); iExtraSample < 5; iExtraSample++) 
        extraSamples.push_back(simTemplate->GetBinContent(iExtraSample+11));
    }
    for(int iExtraSample(0); iExtraSample < 5; iExtraSample++) {
      pdfval[7+iExtraSample] = std::max(extraSamples[iExtraSample],0.);
    }

    for(int s=0;s<12;++s) txtdumpfile << pdfval[s]/pdfval[2] << "\t";
    txtdumpfile << std::endl;
    nCry++;
    
  }
  txtdumpfile.close();
}

double PulseTemplates::pulseShapeFunction(double t) {
  if (alphabeta_ <= 0)
    return ((double)0.);
  double dtsbeta, variable, puiss;
  double dt = t - fTim_max_;
  if (dt > -alphabeta_) {
    dtsbeta = dt / fBeta_;
    variable = 1. + dt / alphabeta_;
    puiss = pow(variable, fAlpha_);
    return fAmp_max_ * puiss * exp(-dtsbeta) + fPed_max_;
  }
  return fPed_max_;
}

void PulseTemplates::InitFitParameters(double* samples, int max_sample) {
  // in a first attempt just use the value of the maximum sample
  fAmp_max_ = samples[max_sample];
  fTim_max_ = max_sample;
  fPed_max_ = 0;

  //y=a*(x-xM)^2+b*(x-xM)+c
  float a = float(samples[max_sample - 1] + samples[max_sample + 1] - 2 * samples[max_sample]) / 2.;
  float b = float(samples[max_sample + 1] - samples[max_sample - 1]) / 2.;
  fTim_max_ = max_sample - b / (2 * a);
  fAmp_max_ = samples[max_sample] - b * b / (4 * a);
}

float PulseTemplates::PerformAnalyticFit(double* samples, int max_sample, double sigma_ped) {
  //int fValue_tim_max = max_sample;
  //! fit electronic function from simulation
  //! parameters fAlpha_ and fBeta_ are fixed and fit is providing the 3 following parameters
  //! the maximum amplitude ( fAmp_max_ )
  //! the time of the maximum  ( fTim_max_)
  //| the pedestal (fPed_max_)

  double chi2 = -1, db[3];

  //HepSymMatrix DM1(3) ; CLHEP::HepVector temp(3) ;

  int num_fit_min = (int)(max_sample - 1);
  int num_fit_max = (int)(max_sample + 3);

  if (num_fit_min < 0)
    num_fit_min = 0;
  //if (num_fit_max>=fNsamples-1) num_fit_max = fNsamples-2 ;
  if (num_fit_max >= EcalDataFrame::MAXSAMPLES) {
    num_fit_max = EcalDataFrame::MAXSAMPLES - 1;
  }

  double one_over_sigma = 1./sigma_ped;
  double func, delta;
  double variation_func_max = 0.;
  double variation_tim_max = 0.;
  double variation_ped_max = 0.;
  CLHEP::HepVector temp(3);
  CLHEP::HepSymMatrix DM1(3);

  //!          Loop on iterations 
  int fNb_iter = 4;
  for (int iter = 0; iter < fNb_iter; iter++) {
    //!          initialization inside iteration loop !
    chi2 = 0.;  //PROD.Zero() ;  DM1.Zero() ;

    for (int i1 = 0; i1 < 3; i1++) {
      temp[i1] = 0;
      for (int j1 = i1; j1 < 3; j1++) {
        DM1.fast(j1 + 1, i1 + 1) = 0;
      }
    }

    fAmp_max_ += variation_func_max;
    fTim_max_ += variation_tim_max;
    fPed_max_ += variation_ped_max;

    //! Then we loop on samples to be fitted
    for (int i = num_fit_min; i <= num_fit_max; i++) {
      //if(i>fsamp_edge_fit && i<num_fit_min) continue ; // remove front edge samples
      //! calculate function to be fitted
      func = pulseShapeFunction((double)i);
      //! then calculate derivatives of function to be fitted
      double dt = (double)i - fTim_max_;
      if (dt > -alphabeta_) {
        double dt_over_beta = dt / fBeta_;
        double variable = (double)1. + dt / alphabeta_;
        double expo = exp(-dt_over_beta);
        double power = pow(variable, fAlpha_);

        db[0] = one_over_sigma * power * expo;
        db[1] = fAmp_max_ * db[0] * dt_over_beta / (alphabeta_ * variable);
      } else {
        db[0] = 0.;
        db[1] = 0.;
      }
      db[2] = one_over_sigma;
      //! compute matrix elements DM1
      for (int i1 = 0; i1 < 3; i1++) {
        for (int j1 = i1; j1 < 3; j1++) {
          //double & fast(int row, int col);
          DM1.fast(j1 + 1, i1 + 1) += db[i1] * db[j1];
        }
      }
      //! compute delta
      delta = (samples[i] - func) * one_over_sigma;
      //! compute vector elements PROD
      for (int ii = 0; ii < 3; ii++) {
        temp[ii] += delta * db[ii];
      }
      chi2 += delta * delta;
    }  //! end of loop on samples

    int fail = 0;
    DM1.invert(fail);
    if (fail != 0.) {
      //just a guess from the value of the parameters in the previous interaction;
      edm::LogWarning("PulseTemplates::PerformAnalyticFit") << "FIT PROBLEM =====> determinant error --> No Fit Provided !";
      InitFitParameters(samples, max_sample);
      return -101;
    }
    //! compute variations of parameters fAmp_max and fTim_max
    CLHEP::HepVector PROD = DM1 * temp;
    //    std::cout<<"vector PROD: "<< PROD[0]<<" "<<PROD[1]<<" "<<PROD[2]<<std::endl;

    // Probably the fastest way to protect against
    // +-inf value in the matrix DM1 after inversion
    // (which is nevertheless flagged as successfull...)
    if (edm::isNotFinite(PROD[0])) {
      InitFitParameters(samples, max_sample);
      edm::LogWarning("PulseTemplates::PerformAnalyticFit") << "FIT PROBLEM =====> infinite detected --> No Fit Provided !";
      return -103;
    }

    variation_func_max = PROD[0];
    variation_tim_max = PROD[1];
    variation_ped_max = PROD[2];
    //chi2 = chi2/((double)nsamp_used - 3.) ;
  }  //!end of loop on iterations

  //!   protection again diverging/unstable fit
  if (variation_func_max > 2000. || variation_func_max < -1000.) {
    InitFitParameters(samples, max_sample);
    edm::LogWarning("PulseTemplates::PerformAnalyticFit") << "FIT PROBLEM =====> unstable fit --> No Fit Provided !";
    return -102;
  }

  //!      results of the fit are calculated
  fAmp_max_ += variation_func_max;
  fTim_max_ += variation_tim_max;
  fPed_max_ += variation_ped_max;

  // protection against unphysical results:
  // ampli mismatched to MaxSample, ampli largely negative, time off preselected range
  if (fAmp_max_ > 2 * samples[max_sample] || fAmp_max_ < -100 || fTim_max_ < 0 || 9 < fTim_max_) {
    edm::LogWarning("PulseTemplates::PerformAnalyticFit") << "FIT PROBLEM =====> unphysical result --> No Fit Provided !";
    // std::cout << "fAmp_max_ = " << fAmp_max_ << " > 2 * samples[max_sample] = " << samples[max_sample] << std::endl;
    // std::cout << "fTim_max_ = " << fTim_max_ << std::endl;
    InitFitParameters(samples, max_sample);
    return -104;
  }

  // std::cout <<"chi2: "<<chi2<<" ampl: "<<fAmp_max_<<" time: "<<fTim_max_<<" pede: "<<fPed_max_<<std::endl;
  return chi2;
}

std::vector<double> PulseTemplates::extrapolateSamples(int rawid) {
  int nSamplesRead = EcalDataFrame::MAXSAMPLES;
  int nSamplesExtra = 5;
  double samples[nSamplesRead];
  double maxsample(-1); // ADC value of maximal ped-subtracted sample
  int imax(-1);         // sample number of maximal ped-subtracted sample
  for(int iSample=0; iSample < nSamplesRead; iSample++) {
    samples[iSample] = templates_[rawid][iSample];
    if (samples[iSample] > maxsample) {
      maxsample = samples[iSample];
      imax = iSample;
    }
  }
  double pedSigma = 1./sqrt(norm_counts_[rawid]);

  DetId detid(rawid);
  if (detid.subdetId()==EcalBarrel) {
    fAlpha_ = alphaBarrel_;
    fBeta_  = betaBarrel_;
  } else {
    fAlpha_ = alphaEndcap_;
    fBeta_  = betaEndcap_;
  }
  alphabeta_ = fAlpha_ * fBeta_;
  
  InitFitParameters(samples,imax);
  double chi2 = PerformAnalyticFit(samples,imax,pedSigma);
  std::vector<double> extraSamples;
  for(int iExtraSample=nSamplesRead; iExtraSample < nSamplesRead + nSamplesExtra; iExtraSample++) {
    if (chi2>0)
      extraSamples.push_back(pulseShapeFunction((double)iExtraSample)/fAmp_max_);
    else
      extraSamples.push_back(detid.subdetId()==EcalBarrel ? ebSimPulseShape_[iExtraSample-3] : eeSimPulseShape_[iExtraSample-3]);
  }
  return extraSamples;
}
