// -*- C++ -*-
//-----------------------------------------------------------------------
//
// Package:    
//      HiggsAnalysis/HiggsToWW2e
// Description:
//      Class CmsCaloClusterFiller
//      Simple class for dumping RECO (or AOD) contents to a ROOT tree
//      
// Original Author:  Emanuele Di Marco
//         Created:  Fri Apr  6 18:05:34 CEST 2007
//
//-----------------------------------------------------------------------

#ifndef CmsCaloClusterFiller_h
#define CmsCaloClusterFiller_h

#include "FWCore/Framework/interface/Event.h"
#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/DetId/interface/DetId.h"
#include "DataFormats/EcalRecHit/interface/EcalRecHitCollections.h"
#include "DataFormats/CaloRecHit/interface/CaloCluster.h"

#include "Geometry/CaloGeometry/interface/CaloGeometry.h"
#include "Geometry/CaloTopology/interface/CaloTopology.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"
#include "Geometry/Records/interface/CaloTopologyRecord.h"

#include "EcalReconstruction/EcalTools/interface/CmsTree.h"

#include <TTree.h>

struct CmsCaloClusterFillerData {
  // All the vectors that will store the stuff
  // going into the tree.
  vector<int>  *nCrystals;
  vector<float> *energy;
  vector<float> *eta, *theta, *phi;
  vector<float> *seedCrystalEnergy, *seedCrystalTime;

  int *nCluster;

public:
  void initialiseCandidate();
  void clear();
};


class CmsCaloClusterFiller {

public:

  // Constructors

  // Dump everything
  CmsCaloClusterFiller(CmsTree *, int maxCluster=500);


  // Destructor
  virtual ~CmsCaloClusterFiller();

  // Operators

  // run number and all of that --- to implement

  virtual void writeCollectionToTree(edm::InputTag collectionTag,
				     const edm::Event&, const edm::EventSetup&,
				     const std::string &columnPrefix, const std::string &columnSuffix,
				     bool dumpData=false);

  //! set the rechits for ECAL
  void setEcalHits( edm::InputTag EcalRecHits ) { EcalRecHits_ = EcalRecHits; }

protected:
  virtual void writeClusterInfo(const reco::CaloCluster *cand, 
                                const edm::Event&, const edm::EventSetup&,
                                const EcalRecHitCollection *EcalRecHits);

  virtual void treeClusterInfo(const std::string colPrefix, const std::string colSuffix);
  
  // Friends

  CmsCaloClusterFillerData *privateData_;

  CmsTree *cmstree;

  edm::InputTag EcalRecHits_;
  bool dumpSeed_;

  int maxCluster_;
  std::string *trkIndexName_;

  std::map<DetId, EcalRecHit> es_rechits_map_;
};

#endif // CmsCaloClusterFiller_h
