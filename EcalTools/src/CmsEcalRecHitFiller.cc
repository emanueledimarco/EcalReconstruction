//---------------------------------------------------------------------------
//
// Description:
//       Package:   HtoWWTreeDumper
//       Class:     CmsEcalRecHitFiller
//
// Original Author:  Emanuele Di Marco
//-----------------------------------------------------------------------

// system include files
#include <memory>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "DataFormats/EcalDetId/interface/EcalDetIdCollections.h"
#include "DataFormats/EcalRecHit/interface/EcalRecHitCollections.h"
#include "Geometry/CaloGeometry/interface/CaloGeometry.h"
#include "Geometry/CaloGeometry/interface/CaloSubdetectorGeometry.h"
#include "Geometry/CaloTopology/interface/CaloTopology.h"
#include "Geometry/CaloTopology/interface/CaloSubdetectorTopology.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"
#include "Geometry/Records/interface/CaloTopologyRecord.h"
#include "RecoCaloTools/Navigation/interface/CaloNavigator.h"

#include "EcalReconstruction/EcalTools/interface/CmsTree.h"
#include "EcalReconstruction/EcalTools/interface/CmsEcalRecHitFiller.h"

using namespace edm;
using namespace reco;

//		----------------------------------------
// 		-- Public Function Member Definitions --
//		----------------------------------------

//----------------
// Constructors --
//----------------


CmsEcalRecHitFiller::CmsEcalRecHitFiller(CmsTree *cmsTree, int maxHits):  privateData_(new CmsEcalRecHitFillerData)
{
  cmstree=cmsTree;
  trkIndexName_ = new std::string("n");
  maxHits_=maxHits;
  privateData_->initialise();
}

//--------------
// Destructor --
//--------------

CmsEcalRecHitFiller::~CmsEcalRecHitFiller() 
{
  // delete here the vector ptr's  
  delete privateData_->eta;
  delete privateData_->phi;
  delete privateData_->ix;
  delete privateData_->iy;
  delete privateData_->energy;
  delete privateData_->time;
  delete privateData_->timeerror;
  delete privateData_->swissX;
  delete privateData_->r9;
  delete privateData_->chi2;
}


//-------------
// Methods   --
//-------------

// Set boolean control options for quantities that are written out


void CmsEcalRecHitFiller::writeCollectionToTree(edm::InputTag collectionTag,
                                                const edm::Event& iEvent, const edm::EventSetup& iSetup,
                                                const std::string &columnPrefix, const std::string &columnSuffix,
                                                bool dumpData) 
{
  
  Handle<EcalRecHitCollection> collectionHandle;
  try { iEvent.getByLabel(collectionTag, collectionHandle); }
  catch ( cms::Exception& ex ) { edm::LogWarning("CmsEcalRecHitFiller") << "Can't get RecHit Collection: " << collectionTag; }
  const EcalRecHitCollection *collection = collectionHandle.product();

  bool isEB = (collectionTag.label().find("EB")!=std::string::npos);
  
  edm::ESHandle<CaloTopology> theCaloTopology;
  iSetup.get<CaloTopologyRecord>().get(theCaloTopology); 

  const CaloSubdetectorTopology* theSubdetTopology   = (isEB) ? 
    theCaloTopology->getSubdetectorTopology(DetId::Ecal,EcalBarrel) :
    theCaloTopology->getSubdetectorTopology(DetId::Ecal,EcalEndcap);

  edm::ESHandle<CaloGeometry> theCaloGeometry;
  iSetup.get<CaloGeometryRecord>().get(theCaloGeometry);

  const CaloSubdetectorGeometry * theSubdetGeometry = (isEB) ? 
    theCaloGeometry->getSubdetectorGeometry(DetId::Ecal,EcalBarrel) :
    theCaloGeometry->getSubdetectorGeometry(DetId::Ecal,EcalEndcap);

  privateData_->clear();
  
  if(collection) 
    {
      if((int)collection->size() > maxHits_)
	{
	  edm::LogError("CmsEcalRecHitFiller") << "Track length " << collection->size() 
                                               << " is too long for declared max length for tree "
                                               << maxHits_ 
                                               << ". Collection will be truncated ";
	}
      
      EcalRecHitCollection::const_iterator cand;
      for(cand=collection->begin(); cand!=collection->end(); cand++) 
	{
	  // fill basic kinematics
	  writeEcalRecHitInfo(&(*cand),collection,isEB,theSubdetTopology,theSubdetGeometry);
	}
    }
  
  // The class member vectors containing the relevant quantities 
  // have all been filled. Now transfer those we want into the 
  // tree 
  int blockSize = (collection) ? collection->size() : 0;
  std::string nCandString = columnPrefix+(*trkIndexName_)+columnSuffix; 
  cmstree->column(nCandString.c_str(),blockSize,0,"Reco");

  treeEcalRecHitInfo(columnPrefix,columnSuffix);

  if(dumpData) cmstree->dumpData();

}






void CmsEcalRecHitFiller::writeEcalRecHitInfo(const EcalRecHit *cand, 
                                              const EcalRecHitCollection *collection,
                                              bool isEB,
                                              const CaloSubdetectorTopology *pTopology,
                                              const CaloSubdetectorGeometry *pGeometry) {

  auto cell = pGeometry->getGeometry(cand->detid());
    
  CaloNavigator<DetId> cursorE = CaloNavigator<DetId>(cand->detid(), pTopology );
      
  float s4 = 0; 
  float s8 = 0;
  float swissX = 0.;
  float recR9 = 0.;
      
  cursorE.home();
  float e1 = recHitEnergyECAL( *cursorE, collection );
      
  cursorE.offsetBy( 1, 0 );
  s4 += recHitEnergyECAL( *cursorE, collection ) ;
      
  cursorE.home();
  cursorE.offsetBy( -1, 0 );
  s4 += recHitEnergyECAL( *cursorE, collection ) ;
      
  cursorE.home();
  cursorE.offsetBy( 0, 1 );   
  s4 += recHitEnergyECAL( *cursorE, collection ) ;
      
  cursorE.home();
  cursorE.offsetBy( 0, -1 );
  s4 += recHitEnergyECAL( *cursorE, collection ) ;
      
  if ( e1 == 0 ) swissX = 0;
  else swissX = 1 - s4 / e1;
      
  // make rechit R9
  s8 = s4;
  cursorE.home();
  cursorE.offsetBy( 1, 1 );
  s8 += recHitEnergyECAL( *cursorE, collection ) ;
      
  cursorE.home();
  cursorE.offsetBy( 1, -1 );
  s8 += recHitEnergyECAL( *cursorE, collection ) ;
      
  cursorE.home();
  cursorE.offsetBy( -1, 1 );
  s8 += recHitEnergyECAL( *cursorE, collection ) ;
      
  cursorE.home();
  cursorE.offsetBy( -1, -1 );
  s8 += recHitEnergyECAL( *cursorE, collection ) ;
      
  if ( e1 == 0 ) recR9 = 0;
  else recR9 = 1-s8/e1;

  privateData_->energy ->push_back ( cand->energy() );
  privateData_->time   ->push_back ( cand->time() );
  privateData_->timeerror ->push_back ( cand->timeError() );
  privateData_->swissX ->push_back ( swissX );
  privateData_->r9     ->push_back ( recR9 );
  privateData_->chi2   ->push_back ( cand->chi2() );
      
  if(isEB) {
    EBDetId detId = cand->id();
    privateData_->ix->push_back( detId.ieta() );
    privateData_->iy->push_back( detId.iphi() );
  } else {
    EEDetId detId = cand->id();
    privateData_->ix->push_back( detId.ix() );
    privateData_->iy->push_back( detId.iy() );
  }

  if(cell != 0)   {
    GlobalPoint position = cell->getPosition();
    privateData_->eta->push_back(position.eta());
    privateData_->phi->push_back(position.phi());
  } else {
    privateData_->eta->push_back( 999 );
    privateData_->phi->push_back( 999 );
  }
}


void CmsEcalRecHitFiller::treeEcalRecHitInfo(const std::string colPrefix, const std::string colSuffix) 
{
  std::string nCandString = colPrefix+(*trkIndexName_)+colSuffix;
  cmstree->column((colPrefix+"eta"+colSuffix).c_str(), *privateData_->eta, nCandString.c_str(), 0, "Reco");
  cmstree->column((colPrefix+"phi"+colSuffix).c_str(), *privateData_->phi, nCandString.c_str(), 0, "Reco");
  cmstree->column((colPrefix+"ix"+colSuffix).c_str(), *privateData_->ix, nCandString.c_str(), 0, "Reco");
  cmstree->column((colPrefix+"iy"+colSuffix).c_str(), *privateData_->iy, nCandString.c_str(), 0, "Reco");
  cmstree->column((colPrefix+"energy"+colSuffix).c_str(), *privateData_->energy, nCandString.c_str(), 0, "Reco");
  cmstree->column((colPrefix+"time"+colSuffix).c_str(), *privateData_->time, nCandString.c_str(), 0, "Reco");
  cmstree->column((colPrefix+"timeerror"+colSuffix).c_str(), *privateData_->timeerror, nCandString.c_str(), 0, "Reco");
  cmstree->column((colPrefix+"chi2"+colSuffix).c_str(), *privateData_->chi2, nCandString.c_str(), 0, "Reco");
  cmstree->column((colPrefix+"swissX"+colSuffix).c_str(), *privateData_->swissX, nCandString.c_str(), 0, "Reco");
  cmstree->column((colPrefix+"r9"+colSuffix).c_str(), *privateData_->r9, nCandString.c_str(), 0, "Reco");
}

void CmsEcalRecHitFillerData::initialise() 
{
  ix = new vector<float>; 
  iy = new vector<float>;
  eta = new vector<float>; 
  phi = new vector<float>;
  energy = new vector<float>;
  time = new vector<float>;
  timeerror = new vector<float>;
  chi2 = new vector<float>;
  swissX = new vector<float>;
  r9 = new vector<float>;
}

void CmsEcalRecHitFillerData::clear() 
{
  ix->clear(); 
  iy->clear();
  eta->clear(); 
  phi->clear();
  energy->clear();
  time->clear();
  timeerror->clear();
  chi2->clear();
  swissX->clear();
  r9->clear();
}

float CmsEcalRecHitFiller::recHitEnergyECAL(DetId id, const EcalRecHitCollection *recHits)
{
  if ( id == DetId(0) ) {
    return 0;
  } else {
    EcalRecHitCollection::const_iterator it = recHits->find( id );
    if ( it != recHits->end() ) {
      return (*it).energy();
    } else {
      return 0;
    }
  }
  return 0;
}
