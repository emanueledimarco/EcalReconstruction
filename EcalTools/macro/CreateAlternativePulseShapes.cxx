#include <vector>
#include <string>
#include <fstream>

#include "TFile.h"
#include "TTree.h"
#include "THashList.h"
#include "TH2D.h"
#include "TCanvas.h"
#include "TString.h"
#include "TLegend.h"
#include "TPaveText.h"
#include "/Users/emanuele/Scripts/RooHZZStyle.C"

Double_t alphabeta( Double_t *x, Double_t * par)
{

  // par[0] = normalization
  // par[1] = alpha
  // par[2] = beta
  // par[3] = tmax
  // par[4] = pedestal
  
  double alphabeta = par[1]*par[2];

  double deltat = x[0]-par[3];
  double power_term = TMath::Power(1+deltat/par[1]/par[2],par[1]);
  double decay_term = TMath::Exp(-deltat/par[2]);
  double fcn;
  if(deltat>-alphabeta) fcn = par[0] * power_term * decay_term + par[4];
  else fcn = par[4];
  return fcn;
}

TH1D *simPulseShapeTemplate(int barrel) {

  double EBPulseShapeTemplate[12] = { 1.13979e-02, 7.58151e-01, 1.00000e+00, 8.87744e-01, 6.73548e-01, 4.74332e-01, 3.19561e-01, 2.15144e-01, 1.47464e-01, 1.01087e-01, 6.93181e-02, 4.75044e-02 };
  double EEPulseShapeTemplate[12] = { 1.16442e-01, 7.56246e-01, 1.00000e+00, 8.97182e-01, 6.86831e-01, 4.91506e-01, 3.44111e-01, 2.45731e-01, 1.74115e-01, 1.23361e-01, 8.74288e-02, 6.19570e-02 };
  
  TH1D *simPulseShape = new TH1D("simPulseShape","",15,0,15);

  int SAMPLES=15;
  int firstSignalSample=3;
  for(int i=0; i<SAMPLES; ++i) {
    if(i<firstSignalSample) simPulseShape->SetBinContent(i+1, 1E-10);
    else {
      simPulseShape->SetBinContent(i+1, (barrel ? EBPulseShapeTemplate[i-firstSignalSample] : EEPulseShapeTemplate[i-firstSignalSample]));
      simPulseShape->SetBinError(i+1, simPulseShape->GetBinContent(i+1)*0.01);
    }
  }

  return simPulseShape;

}

TH1D* makeSingleShiftedTemplate(double dt, TH1D* originalpulse, int EB) {

  TH1D *tempH = (TH1D*)originalpulse->Clone("tempH");
  TF1 *fitF = new TF1("alphabeta",alphabeta,0,15,5);

  double alpha = EB ? 1.250 : 1.283;
  double beta = EB ? 1.600 : 1.674;

  fitF->SetParNames("norm","#alpha","#beta","tmax","pedestal","raiset");
  fitF->FixParameter(0,1); // normalization
  fitF->SetParameter(1,alpha); // alpha
  fitF->SetParameter(2,beta); // beta
  fitF->SetParLimits(1,1.,2.); // alpha
  fitF->SetParLimits(2,1.,2.); // beta
  fitF->SetParameter(3,5.5); // tmax
  fitF->SetParLimits(3,5.,6.); // tmax
  fitF->FixParameter(4,0); // pedestal

  originalpulse->Fit("alphabeta","Q WW M","",3.2,15.0);
  
  // time for alphabeta function is in units of 25 ns
  double unitdt = dt/25.;

  int maxsample=5;
  double maxval=0;
  for(int i=0;i<15;++i) {
    double val = fitF->Eval(i+0.5-unitdt)/fitF->Eval(5.5);
    tempH->SetBinContent(i+1, val); 
    if(val>maxval) {
      maxval=val;
      maxsample=i;
    }
  }

  for(int i=0;i<15;++i) tempH->SetBinContent(i+1, tempH->GetBinContent(i+1)/maxval);

  delete fitF;
  return tempH;
}


void testIT(int EB, double dt) {

  TH1D *simTemp = simPulseShapeTemplate(EB);
  TH1D *shiftedTemp = makeSingleShiftedTemplate(dt,simTemp,EB);
  shiftedTemp->SetLineColor(kRed);
  simTemp->SetLineColor(kBlack);
  
  TCanvas *c1 = new TCanvas("c1","",1200,1200);
  simTemp->Draw();
  shiftedTemp->Draw("same");
  c1->SaveAs(Form("testIT_%s.pdf",(EB ? "EB":"EE")));

}


void makeTimeShiftedTemplates(double timeOffset, string templatesfile="tags/pi0_Run2015C_lowPU/template_histograms_ECAL_Run2015C_lowPU.txt") {

  ifstream tempdump;
  tempdump.open(templatesfile,  std::ifstream::in);

  ofstream outtxt(Form("template_histograms_ECAL_timeShifted_%fns.txt",timeOffset), ios::out | ios::trunc);

  unsigned int rawId;
  int iecal;
  double pulseshape[15];
  
  TH1D *pulseshapeH = new TH1D("pulseshape","",15,0,15);

  int icry = 0;
  while (tempdump.good()) {
    if(icry%1000==0) std::cout << "Analyzing crystal " << icry << std::endl;  
    tempdump >> iecal >> rawId ;
    for(int i=0;i<3;++i) pulseshape[i] = 0.0;
    for(int i=3;i<15;++i) tempdump >> pulseshape[i];

    for(int i=0;i<15;++i) {
      pulseshapeH->SetBinContent(i+1,pulseshape[i]);
      pulseshapeH->SetBinError(i+1, pulseshapeH->GetBinContent(i+1)*0.01);
    }

    
    outtxt.unsetf ( std::ios::floatfield ); 
    outtxt << iecal << "\t";
    outtxt << rawId << "\t";
    outtxt.precision(6);
    outtxt.setf( std::ios::fixed, std:: ios::floatfield ); // doublefield set to fixed

    float pdfval[12];
    TH1D *shiftedTemp = makeSingleShiftedTemplate(timeOffset, pulseshapeH, iecal);
    for(int iSample=3; iSample<15; iSample++) {
      pdfval[iSample-3] = shiftedTemp->GetBinContent(iSample+1);
      outtxt << pdfval[iSample-3] << "\t";
    }
    delete shiftedTemp;
    
    outtxt << std::endl;
    icry++;
  }

  outtxt.close();

}



void makeSimTimeShiftedTemplates(double timeOffset) {

  

  for(int isbarrel=1; isbarrel>-1; --isbarrel) {
    TH1D *pulseshapeH = simPulseShapeTemplate(isbarrel);
  
    float pdfval[12];
    TH1D *shiftedTemp = makeSingleShiftedTemplate(timeOffset, pulseshapeH, isbarrel);
    std::cout << "IS BARREL: " << isbarrel << std::endl;
    for(int iSample=3; iSample<15; iSample++) {
      pdfval[iSample-3] = shiftedTemp->GetBinContent(iSample+1);
      std::cout << pdfval[iSample-3] << ", ";
    }
    delete shiftedTemp;
    
    std::cout << std::endl;
  }

}

void makeAll(double minOffset=-5.0, double maxOffset=5.0, double step=0.250) {

  for(double offset=minOffset; offset<maxOffset; offset+=step) {
    std::cout << "MAKING SHIFTED TEMPLATES FOR SHIFT = " << offset << " ns..." << std::endl;
    makeTimeShiftedTemplates(offset);
  }

}

void makeSimAll(double minOffset=-5.0, double maxOffset=5.0, double step=0.250) {

  for(double offset=minOffset; offset<maxOffset; offset+=step) {
    std::cout << "MAKING SHIFTED TEMPLATES FOR SHIFT = " << offset << " ns..." << std::endl;
    makeSimTimeShiftedTemplates(offset);
  }

}
