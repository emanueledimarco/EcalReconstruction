#include "TH1.h"
#include "TMath.h"
#include "TF1.h"
#include "TH2.h"
#include "TH2F.h"

#include "TLegend.h"
#include "TCanvas.h"
#include "TProfile.h"
#include "TColor.h"
#include "TGraph.h"

#include "RooHZZStyle.C"

void PlotPedNice(){

  TStyle *mystyle = RooHZZStyle("ZZ");
  mystyle->cd();

  TFile f("histoPedEB.root");
  TGraph *ped0 =(TGraph*)f.Get("ped0");
  TGraph *ped1 =(TGraph*)f.Get("ped1");
  TGraph *ped2 =(TGraph*)f.Get("ped2");
  TGraph *ped3 =(TGraph*)f.Get("ped3");
  TGraph *ped4 =(TGraph*)f.Get("ped4");
  TGraph *ped5 =(TGraph*)f.Get("ped5");
  TGraph *ped6 =(TGraph*)f.Get("ped6");
  TGraph *ped7 =(TGraph*)f.Get("ped7");
  TGraph *ped8 =(TGraph*)f.Get("ped8");
  TGraph *ped9 =(TGraph*)f.Get("ped9");
  TGraph *ped10 =(TGraph*)f.Get("ped10");
  TGraph *ped11 =(TGraph*)f.Get("ped11");
  TGraph *ped12 =(TGraph*)f.Get("ped12");
  TGraph *ped13 =(TGraph*)f.Get("ped13");
  TGraph *ped14 =(TGraph*)f.Get("ped14");
  TGraph *ped15 =(TGraph*)f.Get("ped15");
  TGraph *ped16 =(TGraph*)f.Get("ped16");
  TGraph *pedm0 =(TGraph*)f.Get("pedm0");
  TGraph *pedm1 =(TGraph*)f.Get("pedm1");

   
  gStyle->SetPaintTextFormat(".2f");
  TCanvas c1("c1","c1",1200,1200);
  c1.SetGridx();
  c1.SetGridy();
  c1.SetLeftMargin(0.15);
  c1.SetRightMargin(0.10);
  c1.SetBottomMargin(0.15);
  c1.SetTopMargin(0.10);
    


  ped0->SetLineWidth(4);
  ped1->SetLineWidth(4);
  ped2->SetLineWidth(4);
  ped3->SetLineWidth(4);
  ped4->SetLineWidth(4);
  ped5->SetLineWidth(4);
  ped6->SetLineWidth(4);
  ped7->SetLineWidth(4);
  ped8->SetLineWidth(4);
  ped9->SetLineWidth(4);
  ped10->SetLineWidth(4);
  ped11->SetLineWidth(4);
  ped12->SetLineWidth(4);
  ped13->SetLineWidth(4);
  ped14->SetLineWidth(4);
  ped15->SetLineWidth(4);
  ped16->SetLineWidth(4);

  ped0->SetMarkerSize(2.0);
  ped1->SetMarkerSize(2.0);
  ped2->SetMarkerSize(2.0);
  ped3->SetMarkerSize(2.0);
  ped4->SetMarkerSize(2.0);
  ped5->SetMarkerSize(2.0);
  ped6->SetMarkerSize(2.0);
  ped7->SetMarkerSize(2.0);
  ped8->SetMarkerSize(2.0);
  ped9->SetMarkerSize(2.0);
  ped10->SetMarkerSize(2.0);
  ped11->SetMarkerSize(2.0);
  ped12->SetMarkerSize(2.0);
  ped13->SetMarkerSize(2.0);
  ped14->SetMarkerSize(2.0);
  ped15->SetMarkerSize(2.0);
  ped16->SetMarkerSize(2.0);

  ped0->GetXaxis()->SetTitleOffset(1.3);
  ped0->GetXaxis()->SetTitle("Date (year/month)");
  ped0->GetYaxis()->SetTitle("Noise (ADC counts)");
  ped0->GetXaxis()->SetTimeDisplay(1);
  ped0->GetXaxis()->SetNdivisions(406);
  ped0->GetXaxis()->SetLabelSize(0.04);
  ped0->GetXaxis()->SetLabelOffset(0.02);
  ped0->GetYaxis()->SetLabelSize(0.04);
  ped0->GetXaxis()->SetTitleSize(0.05);
  ped0->GetYaxis()->SetTitleSize(0.05);
  ped0->GetYaxis()->SetDecimals();

  ped0->GetXaxis()->SetTimeFormat("%Y/%m");
  ped0->GetXaxis()->LabelsOption("v");
  ped0->GetXaxis()->SetTimeOffset(0,"gmt");
  ped0->SetLineColor(kGreen+4);
  ped0->SetMinimum(1.0);
  ped0->SetMaximum(3.5);
  ped0->Draw("A P");

  ped1->SetMarkerColor(kGreen+3);
  ped1->Draw(" P SAME");

  ped2->SetMarkerColor(kGreen+2);
  ped2->Draw(" P SAME");

  ped3->SetMarkerColor(kGreen+1);
  ped3->Draw(" P SAME");

  ped4->SetMarkerColor(kGreen);
  ped4->Draw(" P SAME");

  ped5->SetMarkerColor(kSpring+10);
  ped5->Draw(" P SAME");

  ped6->SetMarkerColor(kYellow);
  ped6->Draw(" P SAME");

  ped7->SetMarkerColor(kOrange);
  ped7->Draw(" P SAME");

  ped8->SetMarkerColor(kOrange-3);
  ped8->Draw(" P SAME");

  ped9->SetMarkerColor(kOrange+9);
  ped9->Draw(" P SAME");

  ped10->SetMarkerColor(kRed+2);
  ped10->Draw(" P SAME");

  ped11->SetMarkerColor(kRed+1);
  ped11->Draw(" P SAME");

  ped12->SetMarkerColor(kRed);
  ped12->Draw(" P SAME");

  ped13->SetMarkerColor(kPink-5);
  ped13->Draw(" P SAME");

  ped14->SetMarkerColor(kPink);
  ped14->Draw(" P SAME");


  ped16->SetMarkerColor(kMagenta-10);
  ped16->Draw(" P SAME");

  ped15->SetMarkerColor(kViolet+1);
  ped15->Draw(" P SAME");

  TLatex lat;
  lat.SetNDC(); 
  lat.SetTextFont(42);
  lat.DrawLatex(0.16, 0.93, "#bf{CMS} ");
  lat.DrawLatex(0.60, 0.93, "159 fb^{-1} (13 TeV)");
  lat.DrawLatex(0.68, 0.83, "Barrel");
  auto legend = new TLegend(0.16,0.54,0.65,0.89,NULL,"brNDC");
  legend->SetBorderSize(0);
  legend->SetTextSize(0.035);
  legend->SetTextFont(42);
  legend->SetNColumns(2);

  legend->AddEntry("ped0","0.00#leq|#eta|<0.09","l");
  legend->AddEntry("ped1","0.09#leq|#eta|<0.17","l");
  legend->AddEntry("ped2","0.17#leq|#eta|<0.26","l");
  legend->AddEntry("ped3","0.26#leq|#eta|<0.35","l");
  legend->AddEntry("ped4","0.35#leq|#eta|<0.43","l");
  legend->AddEntry("ped5","0.43#leq|#eta|<0.52","l");
  legend->AddEntry("ped6","0.52#leq|#eta|<0.61","l");
  legend->AddEntry("ped7","0.61#leq|#eta|<0.70","l");
  legend->AddEntry("ped8","0.70#leq|#eta|<0.78","l");
  legend->AddEntry("ped9","0.78#leq|#eta|<0.87","l");
  legend->AddEntry("ped10","0.87#leq|#eta|<0.96","l");
  legend->AddEntry("ped11","0.96#leq|#eta|<1.04","l");
  legend->AddEntry("ped12","1.04#leq|#eta|<1.13","l");
  legend->AddEntry("ped13","1.13#leq|#eta|<1.22","l");
  legend->AddEntry("ped14","1.22#leq|#eta|<1.31","l");
  legend->AddEntry("ped15","1.31#leq|#eta|<1.39","l");
  legend->AddEntry("ped16","1.39#leq|#eta|#leq1.48","l");
  legend->Draw();

  f.Close(); 

  c1.Print("myped.pdf");
  c1.Print("myped.C");


  gStyle->SetPaintTextFormat(".2f");
   TCanvas c2("c2","c2",1200,1200);
   c2.SetGridx();
   c2.SetGridy();
   c2.SetLeftMargin(0.15);
   c2.SetRightMargin(0.10);
   c2.SetBottomMargin(0.15);
   c2.SetTopMargin(0.10);

   pedm0->GetXaxis()->SetTitleOffset(1.3);
   pedm0->GetXaxis()->SetTitle("Date (year/month)");
   pedm0->GetYaxis()->SetTitle("Pedestal mean (ADC counts)");
   pedm0->GetXaxis()->SetTimeDisplay(1);
   pedm0->GetXaxis()->SetNdivisions(405);
   pedm0->GetXaxis()->SetLabelSize(0.04);
   pedm0->GetYaxis()->SetLabelSize(0.04);
   pedm0->GetXaxis()->SetTitleSize(0.05);
   pedm0->GetXaxis()->SetLabelOffset(0.02);
   pedm0->GetYaxis()->SetTitleSize(0.05);
   pedm0->GetYaxis()->SetNdivisions(405);
   pedm0->GetYaxis()->SetTitleFont(42);

   pedm0->GetXaxis()->SetTimeFormat("%Y/%m");
   pedm0->GetXaxis()->LabelsOption("v");
   pedm0->GetXaxis()->SetTimeOffset(0,"gmt");
   pedm0->SetMarkerColor(kGreen+4);
   pedm0->SetMarkerSize(0.4);
   pedm0->SetMarkerStyle(24);
   pedm0->SetMinimum(200.0);
   pedm0->SetMaximum(208.0);
   pedm0->Draw("A P");

   pedm1->SetMarkerSize(0.4);
   pedm1->SetMarkerStyle(20);
   pedm1->SetMarkerColor(kRed+3);
   pedm1->Draw(" P SAME");

   lat.DrawLatex(0.16, 0.93, "#bf{CMS} ");
   lat.DrawLatex(0.60, 0.93, "159 fb^{-1} (13 TeV)");
   lat.DrawLatex(0.65, 0.83, "Barrel");
   auto legend2 = new TLegend(0.55,0.17,0.87,0.35,NULL,"brNDC");
   legend2->SetBorderSize(0);
   legend2->SetTextFont(42);
   legend2->SetTextSize(0.038);
   
   TLegendEntry *entry2=legend2->AddEntry("entry2","Non-collision runs","p");
   entry2->SetMarkerColor(kRed+3);
   entry2->SetMarkerStyle(20);
   entry2->SetMarkerSize(1.5);
   TLegendEntry *entry=legend2->AddEntry("entry","Collision runs","p");
   entry->SetMarkerColor(kGreen+4);
   entry->SetMarkerStyle(24);
   entry->SetMarkerSize(1.5);

   legend2->Draw();

   TPad *subpad = new TPad("subpad","",0.17,0.55,0.60,0.89); subpad->Draw(); subpad->cd(); 
   subpad->SetLeftMargin(0.18);
   subpad->SetRightMargin(0.12);
   TGraph * inset_pedm0 = (TGraph*)pedm0->Clone("inset_pedm0");
   //inset_pedm0->GetXaxis()->SetTitle("Time");
   //inset_pedm0->GetYaxis()->SetTitle("Pedestal Mean (ADC counts)");
   inset_pedm0->GetXaxis()->SetTimeDisplay(1);
   inset_pedm0->GetXaxis()->SetNdivisions(404);
   inset_pedm0->GetXaxis()->SetLabelSize(0.1);
   inset_pedm0->GetXaxis()->SetLabelOffset(0.05);
   inset_pedm0->GetYaxis()->SetLabelSize(0.1);
   inset_pedm0->GetYaxis()->SetDecimals();
   inset_pedm0->GetXaxis()->SetTitleSize(0.10);
   inset_pedm0->GetYaxis()->SetTitleSize(0.10);


   inset_pedm0->GetXaxis()->SetTimeFormat("%d");
   inset_pedm0->GetXaxis()->LabelsOption("v");
   inset_pedm0->GetXaxis()->SetTimeOffset(0,"gmt");
   inset_pedm0->GetXaxis()->SetRangeUser(1533427260.,1533427260.+2*24*60*60);
   inset_pedm0->SetMarkerColor(kGreen+4);
   inset_pedm0->SetMarkerSize(1.0);
   inset_pedm0->SetMarkerStyle(24);
   inset_pedm0->SetMinimum(204.0);
   inset_pedm0->SetMaximum(206.0);
   inset_pedm0->Draw("A P");

   TLatex lat2;
   lat2.SetNDC(); 
   lat2.SetTextFont(42);
   lat2.SetTextSize(0.1);
   lat2.DrawLatex(0.45, 0.8, "August 2018");

   TGraph * inset_pedm1 = (TGraph*)pedm1->Clone("inset_pedm1");
   inset_pedm1->SetMarkerSize(1.0);
   inset_pedm1->SetMarkerStyle(20);
   inset_pedm1->SetMarkerColor(kRed+3);
   inset_pedm1->Draw(" P SAME");

   c2.Print("myped2.pdf");
   c2.Print("myped2.C");

}

