#! /usr/bin/env python
import ROOT
ROOT.gROOT.SetBatch(True)

from PlotUtils import doLegend

def getOneReso(ibx):

    c = ROOT.TCanvas("c","",1200,1200)
    c.SetLeftMargin(0.17)
    c.SetRightMargin(0.1)
    c.SetBottomMargin(0.15)

    enecut = 0.100 # GeV (44 MeV is the input noise)

    hreso = ROOT.TH1F('hreso','',400,0,2)
    iamp = ibx+5
    fullcut = 'BX0{plus}{ibx}>=0 && BX0{plus}{ibx}<2800 && (amp[{iamp}]-{truea})>0 && (amp[{iamp}]-{truea})/energyPU[BX0{plus}{ibx}]<2 && energyPU[BX0{plus}{ibx}]>{cut}'.format(plus='+' if ibx>=0 else '',ibx=ibx,cut=enecut,iamp=iamp,truea=E if ibx==0 else 0)
    var = '(amp[{iamp}]-{truea})/energyPU[BX0{plus}{ibx}]'.format(iamp=iamp,truea=E if ibx==0 else 0,plus='+' if ibx>=0 else '',ibx=ibx,cut=enecut)
    print ("Plotting: ",var,"  with fullcut = ",fullcut)
    tree.Draw('{v}>>hreso'.format(v=var),fullcut)
    mean = hreso.GetMean()
    meanerr = hreso.GetMeanError()
    rms = hreso.GetRMS()

    binmax = hreso.GetMaximumBin()
    xmax = hreso.GetXaxis().GetBinCenter(binmax)
    xmaxerr = hreso.GetBinWidth(1)/2.
    
    hreso.SetMarkerStyle(ROOT.kFullCircle)
    hreso.SetMarkerSize(3)
    hreso.SetMarkerColor(ROOT.kAzure+8)
    hreso.GetXaxis().SetTitle("A^{{PU}}_{{{i}}}/A^{{true}}_{{BX={ibx}}}".format(i=ibx+5,ibx=ibx))
    hreso.GetYaxis().SetTitle("Events")
    hreso.GetXaxis().SetTitleOffset(1.1);
    hreso.GetXaxis().SetTitleSize(0.05)
    hreso.Draw('pe1')

    lat = ROOT.TLatex()
    lat.SetNDC(); lat.SetTextFont(42)
    lat.DrawLatex(0.19, 0.92, '#bf{CMS} Simulation')
    lat.DrawLatex(0.73, 0.92, '(13 TeV)')
    lat.DrawLatex(0.25,0.80, 'BX = {i}'.format(i=ibx))
    lat.DrawLatex(0.25,0.75, 'mean = {mean:.1f}'.format(mean=mean))
    lat.DrawLatex(0.25,0.71, 'mode = {mode:.1f}'.format(mode=xmax))
    lat.DrawLatex(0.25,0.67, 'RMS = {r:.2f}'.format(r=rms))
    
    for ext in ['pdf','png']:
        c.SaveAs(("resolutiuon_bx{i}.{ext}".format(i=ibx,ext=ext)).replace('-','m'))
    
    return (mean,meanerr,xmax,xmaxerr,rms)

def plotPUSpectrum(tree):

    c = ROOT.TCanvas("c","",1200,1200)
    c.SetLeftMargin(0.17)
    c.SetRightMargin(0.1)
    c.SetBottomMargin(0.15)
    c.SetLogy()
#    c.SetLogx()
    c.SetTicks()
    
    hpu = ROOT.TH1F('hpu','',200,0.0,100)
    hpu.SetMarkerStyle(ROOT.kFullCircle)
    hpu.SetMarkerSize(1)
    hpu.SetLineColor(ROOT.kBlack)
    
    tree.Draw("energyPU>>hpu","energyPU>0.05")

    hpu.GetXaxis().SetTitle('OOT pileup energy / crystal (GeV)')
    hpu.GetYaxis().SetTitle("Events")
    hpu.GetXaxis().SetTitleOffset(1.1);
    hpu.GetXaxis().SetTitleSize(0.05)
    hpu.GetXaxis().SetRangeUser(0.05,100)
    hpu.GetYaxis().SetTitleSize(0.05)
    hpu.Draw('peX0')

    plots  = [hpu]
    labels = ['simulated deposit']
    styles = ['pe']
    leg = doLegend(plots,labels,styles,legBorder=False,corner='TC')

    lat = ROOT.TLatex()
    lat.SetNDC(); lat.SetTextFont(42)
    lat.DrawLatex(0.19, 0.92, '#bf{CMS} #it{Simulation}')
    lat.DrawLatex(0.73, 0.92, '(13 TeV)')

    for ext in ['pdf','png']:
        c.SaveAs("pu_spectrum.{ext}".format(ext=ext))
    
if __name__ == "__main__":

    tf = ROOT.TFile("data/reco_signal_50GeV_eta_0.0_pu_40_manyevents_ooutpubias.root")
    tree = tf.Get("amplitudes")

    ROOT.gStyle.SetOptStat(0)

    plotPUSpectrum(tree)
    
    bias_gr = ROOT.TGraphErrors(10)
    bias_gr.SetTitle('')
    mode_gr = ROOT.TGraphErrors(10)
    mode_gr.SetTitle('')
    
    E = 50 # to be subtracted by the total fitted amplitude
    
    for i,ibx in enumerate(range(-5,5)):
        mean,meanerr,mode,modeerr,res = getOneReso(ibx)
        bias_gr.SetPoint(i,ibx,mean)
        bias_gr.SetPointError(i,0,meanerr)
        mode_gr.SetPoint(i,ibx,mode)
        mode_gr.SetPointError(i,0,modeerr)
        
    canv = ROOT.TCanvas("canv","",1200,1200)
    canv.SetGridx()
    canv.SetGridy()
    canv.SetLeftMargin(0.17)
    canv.SetRightMargin(0.1)
    canv.SetBottomMargin(0.15)
    canv.SetTicks(1,1)
    
    bias_gr.SetMarkerStyle(ROOT.kFullCircle)
    bias_gr.SetMarkerSize(2)
    bias_gr.SetMarkerColor(ROOT.kRed+2)
    mode_gr.SetMarkerStyle(ROOT.kFullCircle)
    mode_gr.SetMarkerSize(3)
    mode_gr.SetLineWidth(4)
    mode_gr.Draw("APE")
    ymin,ymax = 0.95,1.05
    mode_gr.SetMaximum(ymax)
    mode_gr.SetMinimum(ymin)
    #bias_gr.Draw("AP")
    xax = mode_gr.GetXaxis(); yax = mode_gr.GetYaxis()
    xax.SetRangeUser(-6,5)
    xax.SetNdivisions(10,ROOT.kTRUE)
    yax.SetRangeUser(ymin,ymax)
    yax.SetDecimals()
    xax.SetTitleOffset(1.1); xax.SetTitleSize(0.06)
    yax.SetTitleOffset(1.3); yax.SetTitleSize(0.06)
    xax.SetTitle("Bunch crossing")
    yax.SetTitle("#it{A}_{BX}^{PU} / #it{A}_{BX}^{true}")

    lat = ROOT.TLatex()
    lat.SetNDC(); lat.SetTextFont(42)
    lat.DrawLatex(0.19, 0.92, '#bf{CMS}')
    lat.DrawLatex(0.73, 0.92, '(13 TeV)')

    ## another tlatex to make the font smaller
    lat2 = ROOT.TLatex()
    lat2.SetNDC(); lat2.SetTextFont(42); lat2.SetTextSize(0.04)
    lat2.DrawLatex(0.30, 0.92, '#it{Standalone simulation}')

    lat3 = ROOT.TLatex()
    lat3.SetNDC(); lat3.SetTextFont(42)
    lat3.DrawLatex(0.60,0.23, '<PU> = 40')
    
    plots  = [mode_gr]
    labels = ['multifit']
    styles = ['pe']
    leg = doLegend(plots,labels,styles,legBorder=False,corner='TC')

    # horizontal line at 1
    line = ROOT.TLine()
    line.SetLineWidth(2)
    line.DrawLine(-6, 1, 5, 1)
    
    for ext in ['pdf','png','root']:
        canv.SaveAs("ootpu_bias.{ext}".format(ext=ext))

