// -*- C++ -*-
//-----------------------------------------------------------------------
//
// Package:    
//      HiggsAnalysis/HiggsToWW2e
// Description:
//      Class CmsSuperClusterFiller
//      Simple class for dumping RECO (or AOD) contents to a ROOT tree
//      
// Original Author:  Emanuele Di Marco
//         Created:  Fri Apr  6 18:05:34 CEST 2007
//
//-----------------------------------------------------------------------

#ifndef CmsSuperClusterFiller_h
#define CmsSuperClusterFiller_h

#include "FWCore/Framework/interface/Event.h"
#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/DetId/interface/DetId.h"
#include "DataFormats/EcalRecHit/interface/EcalRecHitCollections.h"
#include "DataFormats/CaloRecHit/interface/CaloCluster.h"
#include "DataFormats/EgammaReco/interface/BasicCluster.h"
#include "DataFormats/EgammaReco/interface/SuperClusterFwd.h"
#include "DataFormats/EgammaReco/interface/SuperCluster.h"

#include "Geometry/CaloGeometry/interface/CaloGeometry.h"
#include "Geometry/CaloTopology/interface/CaloTopology.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"

#include "EcalReconstruction/EcalTools/interface/CmsTree.h"

#include <TTree.h>

struct CmsSuperClusterFillerData {
  // All the vectors that will store the stuff
  // going into the tree.
  vector<int>  *nBC, *nCrystals;
  vector<float> *rawEnergy, *energy, *seedClusterEnergy;
  vector<float> *eta, *theta, *phi;
  vector<float> *seedCrystalEnergy, *seedCrystalTime;

  int *nSC;

public:
  void initialiseCandidate();
  void clear();
};


class CmsSuperClusterFiller {

public:

  // Constructors

  // Dump everything
  CmsSuperClusterFiller(CmsTree *, int maxSC=500);


  // Destructor
  virtual ~CmsSuperClusterFiller();

  // Operators

  // run number and all of that --- to implement

  virtual void writeCollectionToTree(edm::InputTag collectionTag,
				     const edm::Event&, const edm::EventSetup&,
				     const std::string &columnPrefix, const std::string &columnSuffix,
				     bool dumpData=false);

  //! set the rechits for ECAL
  void setEcalHits( edm::InputTag EcalRecHits ) { EcalRecHits_ = EcalRecHits; }

protected:
  virtual void writeSCInfo(const reco::SuperCluster *cand, 
			   const edm::Event&, const edm::EventSetup&,
                           const EcalRecHitCollection *EcalRecHits);

  virtual void treeSCInfo(const std::string colPrefix, const std::string colSuffix);
  
  // Friends

  CmsSuperClusterFillerData *privateData_;

  CmsTree *cmstree;

  edm::InputTag EcalRecHits_;

  int maxSC_;
  std::string *trkIndexName_;

  std::map<DetId, EcalRecHit> es_rechits_map_;
};

#endif // CmsSuperClusterFiller_h
