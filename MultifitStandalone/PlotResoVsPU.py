#! /usr/bin/env python
import ROOT
import root_numpy as rtnp
from PlotUtils import doLegend

def effSigma(histo):
    xaxis = histo.GetXaxis()
    nb = xaxis.GetNbins()
    xmin = xaxis.GetXmin()
    ave = histo.GetMean()
    rms = histo.GetRMS()
    total=histo.Integral()
    if total < 100:
        print(("effsigma: Too few entries to compute it: ", total))
        return 0.
    ierr=0
    ismin=999
    rlim=0.683*total
    bwid = xaxis.GetBinWidth(1)
    nrms=int(rms/bwid)
    if nrms > nb/10: nrms=int(nb/10) # Could be tuned...
    widmin=9999999.
    for iscan in range(-nrms,nrms+1): # // Scan window centre
        ibm=int((ave-xmin)/bwid)+1+iscan
        x=(ibm-0.5)*bwid+xmin
        xj=x; xk=x;
        jbm=ibm; kbm=ibm;
        bin=histo.GetBinContent(ibm)
        total=bin
        for j in range(1,nb):
            if jbm < nb:
                jbm += 1
                xj += bwid
                bin=histo.GetBinContent(jbm)
                total += bin
                if total > rlim: break
            else: ierr=1
            if kbm > 0:
                kbm -= 1
                xk -= bwid
                bin=histo.GetBinContent(kbm)
                total+=bin
            if total > rlim: break
            else: ierr=1
        dxf=(total-rlim)*bwid/bin
        wid=(xj-xk+bwid-dxf)*0.5
        if wid < widmin:
            widmin=wid
            ismin=iscan
    if ismin == nrms or ismin == -nrms: ierr=3
    if ierr != 0: print(("effsigma: Error of type ", ierr))
    return widmin

def getOne(reco,npu,energy,includeITasTrue=False,eta="0.0"):
    tf = ROOT.TFile('data/reco_{suffix}signal_{ene}GeV_eta_{eta}_pu_{npu}.root'.format(suffix='wgt_' if reco=='weights' else '',ene=energy,eta=eta,npu=npu))
    tree = tf.Get('amplitudes')
    xmin,xmax = (0.9,1.02) if energy>10 else (0.9,1.4)
    histo  = ROOT.TH1F('resol','',500,xmin,xmax)

    ## note: amplitudeTruth = true E + in-time PU (with this will estimate only the effect of the IT PU)
    if includeITasTrue:
        tree.Draw("amplitude/amplitudeTruth>>resol")
    else:
        tree.Draw("amplitude/{ene}>>resol".format(ene=energy))

    mean = histo.GetMean()
    meanerr = histo.GetMeanError()
    rms = histo.GetRMS()
    effs = effSigma(histo)
    
    # gaussf = ROOT.TF1('gaussf','gaus',mean-3*rms,mean+3*rms)
    # gaussf.SetParameter(1,mean)
    # gaussf.SetParameter(2,rms)
    # histo.Fit('gaussf')

    # m = gaussf.GetParameter(1)
    # me = gaussf.GetParError(1)
    # s = gaussf.GetParameter(2)
    # se = gaussf.GetParError(2)

    return (mean,meanerr,effs,0)

def plotOneEnergy(Energy):
    ROOT.gStyle.SetOptStat(0)

    canv = ROOT.TCanvas("canv","",1200,1200)
    canv.SetGridx()
    canv.SetGridy()
    canv.SetLeftMargin(0.17)
    canv.SetRightMargin(0.1)
    canv.SetBottomMargin(0.15)

    purange = list(range(0,61,5))

    graphs = {}
    graphs[('multifit','itfalse')] = ROOT.TGraphErrors(len(purange))
    graphs[('multifit','itfalse')].SetTitle("")
    graphs[('multifit','ittrue')] = ROOT.TGraphErrors(len(purange))
    graphs[('multifit','ittrue')].SetTitle("")
    graphs[('weights','itfalse')] = ROOT.TGraphErrors(len(purange))
    graphs[('weights','itfalse')].SetTitle("")
    graphs[('weights','ittrue')] = ROOT.TGraphErrors(len(purange))
    graphs[('weights','ittrue')].SetTitle("")

    offset = {}
    if Energy<10:
        offset['weights'] = 8e-3
        offset['multifit'] = 0
    else:
        offset['weights'] = 3.4e-4
        offset['multifit'] = 0
    
    for i,pu in enumerate(purange):
        print(("testing PU = ",pu))

        for reco in ['weights','multifit']:
            for itpu in ['ittrue','itfalse']:
                useItInEtrue = itpu=='ittrue'
                vals = getOne(reco,pu,Energy,useItInEtrue,'0.0')
                graphs[(reco,itpu)].SetPoint     (i,pu,(vals[2]/vals[0]-offset[reco])*100)
                graphs[(reco,itpu)].SetPointError(i,0,(vals[3]/vals[0])*100)

        
    graphs[('weights','itfalse')].SetMarkerStyle(ROOT.kFullCircle)
    graphs[('weights','itfalse')].SetMarkerSize(1.5)
    graphs[('weights','itfalse')].Draw("ACPE")
    
    graphs[('weights','ittrue')].SetMarkerStyle(ROOT.kOpenCircle)
    graphs[('weights','ittrue')].SetMarkerSize(1.5)
    graphs[('weights','ittrue')].Draw("CPE")

    graphs[('multifit','itfalse')].SetMarkerStyle(ROOT.kFullSquare)
    graphs[('multifit','itfalse')].SetMarkerColor(ROOT.kRed)
    graphs[('multifit','itfalse')].SetLineColor(ROOT.kRed)
    graphs[('multifit','itfalse')].SetMarkerSize(1.5)
    graphs[('multifit','itfalse')].Draw("CPE")

    graphs[('multifit','ittrue')].SetMarkerStyle(ROOT.kOpenSquare)
    graphs[('multifit','ittrue')].SetMarkerColor(ROOT.kRed)
    graphs[('multifit','ittrue')].SetLineColor(ROOT.kRed)
    graphs[('multifit','ittrue')].SetMarkerSize(1.5)
    graphs[('multifit','ittrue')].Draw("CPE")


    xax = graphs[('weights','itfalse')].GetXaxis(); yax = graphs[('weights','itfalse')].GetYaxis()
    if Energy>10:
        yax.SetRangeUser(0.04,0.12)
    else:
        yax.SetRangeUser(0.5,4.0)
    yax.SetDecimals()
    xax.SetTitleOffset(1.1); xax.SetTitleSize(0.05)
    yax.SetTitleOffset(1.5); yax.SetTitleSize(0.05)
    xax.SetTitle('Number of pileup interactions')
    yax.SetTitle('Single crystal amplitude #sigma_{eff} (%)')

    plots = [graphs[('weights','itfalse')],graphs[('weights','ittrue')],graphs[('multifit','itfalse')],graphs[('multifit','ittrue')]]
    labels = ['weights','weights, only OOT PU','multifit','multifit, only OOT PU']
    styles = ['p','p','p','p']
    leg = doLegend(plots,labels,styles,legBorder=False,legWidth=0.5,textSize=0.05,corner='TL')
    
    lat = ROOT.TLatex()
    lat.SetNDC(); lat.SetTextFont(42)
    lat.DrawLatex(0.19, 0.92, '#bf{CMS}')
    lat.DrawLatex(0.73, 0.92, '(13 TeV)')
    lat.DrawLatex(0.19,0.20, 'E = {ene} GeV'.format(ene=Energy))

    ## another tlatex to make the font smaller
    lat2 = ROOT.TLatex()
    lat2.SetNDC(); lat2.SetTextFont(42); lat2.SetTextSize(0.04)
    lat2.DrawLatex(0.30, 0.92, '#it{Standalone simulation}')

    canv.SaveAs("resol_vs_pu_{ene}GeV.pdf".format(ene=Energy))
    canv.SaveAs("resol_vs_pu_{ene}GeV.png".format(ene=Energy))
    

if __name__ == "__main__":

    ## toys done for 2 or 50 GeV
    energies = [2,50]
    for ene in energies:
        plotOneEnergy(ene)
    
