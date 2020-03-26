#ifndef AlphaBetaFitter_H
#define AlphaBetaFitter_H

#include <cmath>
#include <fstream>
#include <string>
#include <sstream>
#include <vector>
#include <TH1F.h>
#include <TMath.h>
#include <TF1.h>
#include <TCanvas.h>
#include <TLatex.h>
#include "tdrstyle.C"

double alphabeta(double *x, double *par) {
  // par[0] = normalization
  // par[1] = alpha
  // par[2] = beta
  // par[3] = tmax
  // par[4] = pedestal
  
  double alphabeta = par[1]*par[2];
  double deltat = x[0]-par[3];
  double power_term = TMath::Power(1+deltat/par[1]/par[2], par[1]);
  double decay_term = TMath::Exp(-deltat/par[2]);
  double fcn=0;
  if (deltat > -alphabeta) fcn = par[0] * power_term * decay_term + par[4];
  else fcn = par[4];
  return fcn;
}

class AlphaBetaFitter {

public:

  enum AlphaBetaParameter { alpha, beta, T0 };

  // Constructor, destructor
  AlphaBetaFitter();
  ~AlphaBetaFitter() {}

  void fit(TH1F *histo,bool doEB,float pedestal=0,std::string canvasName="");
  void drawExtrapolatedTail() {_extrapTail = true;}
  double* getPars() {return _pars;}
  double* getErrs() {return _errs;}
  TF1*    getFcn() {return _fitF;}

protected:
  void setParameters(bool doEB, double pedestal);
  
  TF1 *_fitF;
  double _pars[4], _errs[4];
  bool _extrapTail;
};

AlphaBetaFitter::AlphaBetaFitter() {
  _fitF = new TF1("alphabeta",alphabeta,0,15,5);
  _fitF->SetParNames("norm","#alpha","#beta","tmax","pedestal");
  _fitF->SetLineColor(kAzure+8);
  _fitF->SetLineWidth(2);
  _extrapTail = false;
}

void AlphaBetaFitter::setParameters(bool doEB, double pedestal) {
  float alpha = doEB ? 1.250 : 1.283;
  float beta = doEB ? 1.600 : 1.674;
  _fitF->FixParameter(1,alpha);
  _fitF->FixParameter(2,beta);
  _fitF->FixParameter(0,1); // normalization
  _fitF->SetParameter(3,5.5);
  if(doEB) _fitF->SetParLimits(1,0.8,2.5);  // alpha
  else _fitF->SetParLimits(1,0.5,2.5);
  _fitF->SetParLimits(2,0.8,2.5);  // beta
  _fitF->SetParLimits(3,4,7); // tmax 
  _fitF->FixParameter(4,pedestal);
}

void AlphaBetaFitter::fit(TH1F *histo,bool doEB,float pedestal,std::string canvasName) {
  
  setParameters(doEB,pedestal);
  
  TCanvas *canv = 0;
  if(canvasName!="") {
    canv = new TCanvas("fitc","",600,600);
    canv->SetLeftMargin(0.15);
    canv->SetRightMargin(0.05);
    canv->SetBottomMargin(0.15);
    canv->SetTopMargin(0.10);
    histo->SetMarkerStyle(kFullSquare);
    histo->SetLineColor(kBlack);
    histo->GetXaxis()->SetTitle("Time sample");
    histo->GetXaxis()->SetTitleOffset(1.2);
    histo->GetXaxis()->SetTitleSize(0.05);
    histo->GetYaxis()->SetTitle("Normalized Amplitude");
    histo->GetYaxis()->SetTitleOffset(1.2);
    histo->GetYaxis()->SetTitleSize(0.05);
    histo->GetYaxis()->SetRangeUser(0,1.2);
  }

  TH1F *gapBand = (TH1F*)histo->Clone("gapBand");
  histo->Fit("alphabeta","M","same",0,10);
  if (_extrapTail) {
    gapBand->SetFillColor(kGray);
    gapBand->SetLineColor(0);
    for(int i=0; i<16; ++i) {
      histo->SetBinError(i,0.02*histo->GetBinContent(i));
      if(i>10) {
        histo->SetBinContent(i,_fitF->Eval(i-0.5));
        gapBand->SetBinContent(i,2);
      } else {
        gapBand->SetBinContent(i,0);
      }
    }
    gapBand->Draw("hist");
    // histogram in the readout
    TH1F *histoRead = (TH1F*)histo->Clone("histoRead");
    for (int ir=11; ir<16; ir++) {
      histoRead->SetBinContent(ir,-1);
    }
    histoRead->Draw("same pe0");

    // histogram outside the readout
    TH1F *histoOutRead = (TH1F*)histo->Clone("histoOutRead");
    for (int ir=0; ir<11; ir++) {
      histoOutRead->SetBinContent(ir,-1);
    }
    histoOutRead->SetMarkerStyle(kOpenSquare);
    histoOutRead->Draw("same pe0");
    //    histo->Draw("same pe0");
  }
  
  for(int p=1; p<4; ++p) {
    _pars[p-1] = _fitF->GetParameter(p);
    _errs[p-1] = _fitF->GetParError(p);
  }

  if(canvasName!="") {
    gROOT->LoadMacro("tdrstyle.C");
    setTDRStyle();
    gStyle->SetOptFit(0);
    _fitF->Draw("same");
    TLatex lat;
    lat.SetNDC(); lat.SetTextFont(42);
    lat.DrawLatex(0.17, 0.92, "#bf{CMS}");
    lat.DrawLatex(0.60, 0.92, "0.5 fb^{-1} (13 TeV)");
    TLatex labels;
    labels.SetNDC(); labels.SetTextFont(42); labels.SetTextSize(0.04);
    labels.DrawLatex(0.7,0.85, "#it{extrapolated}");
    labels.DrawLatex(0.2,0.85, "#it{readout}");
    canv->SaveAs(canvasName.c_str());
    delete canv;
    delete gapBand;
  }
}
#endif

