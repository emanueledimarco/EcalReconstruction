#! /usr/bin/env python
from array import array
from math import *
import numpy, re, sys, os
import itertools as it
from datetime import datetime
import ROOT
ROOT.gROOT.SetBatch(True)
from PlotUtils import doLegend

from performances_mc import effSigma,printCanvas,printPlot,fitOneReso

ZMASS = 91.1876 # GeV

#def getOneMassHisto(tree,absetamin,absetamax,variable='R9Ele[0]',xmin=0,xmax=1.1,timeMin=-1,timeMax=-1,runRange=(-1,1e+6),name='r9'):
def getOneMassHisto(tree,absetamin,absetamax,variable='invMass_5x5SC',xmin=50,xmax=110,timeMin=-1,timeMax=-1,runRange=(-1,1e+6),name='mass'):
    canv = ROOT.TCanvas("canvreso","",1200,1200)
    canv.SetLeftMargin(0.15)
    canv.SetRightMargin(0.15)
    canv.SetBottomMargin(0.15)
    #if absetamax>1.5:
    #phasespace = '((abs(etaEle[0])>{etamin} && abs(etaEle[0])<{etamax}) || (abs(etaEle[1])>{etamin} && abs(etaEle[1])<{etamax}))'.format(etamin=absetamin,etamax=absetamax)
    phasespace = '(TMath::Max(abs(etaEle[0]),abs(etaEle[1]))>{etamin} && TMath::Max(abs(etaEle[0]),abs(etaEle[1]))<{etamax})'.format(etamin=absetamin,etamax=absetamax)
    #else:
    #phasespace = '(abs(etaEle[0])>{etamin} && abs(etaEle[0])<{etamax} && abs(etaEle[1])>{etamin} && abs(etaEle[1])<{etamax})'.format(etamin=absetamin,etamax=absetamax)        
    if timeMin>0 and timeMax>0:
        time = 'eventTime>{timemin} && eventTime<{timemax}'.format(timemin=timeMin,timemax=timeMax)
        nbins = 50
    else:
        time = '1'
        nbins = 200 if absetamax<1.3 else 100
    runRangeCut = 'runNumber>={rmin} && runNumber<={rmax}'.format(rmin=runRange[0],rmax=runRange[1])
    ## the following is used for the mass plot
    unconv     = 'fbremEle[0]>0 && fbremEle[0]<{fbremcut} && fbremEle[1]>0 && fbremEle[1]<{fbremcut}'.format(fbremcut=0.1 if absetamax<1.5 else 0.5)
    ## the following is used for the cluster shape history plot
    #unconv = '1'
    cut = '{c1} && {c2} && {c3} && {c4}'.format(c1=phasespace,c2=unconv,c3=time,c4=runRangeCut)
    #variable   = 'invMass_5x5SC'
    #variable   = 'invMass'
    #print "Now plotting ",variable,"  with cuts: ",cut
    nicename = cut.replace(">","gt").replace("<","lt").replace("&&","AND").replace(".","p").replace(" ","_").replace(")","").replace("(","").replace("[",'').replace("]",'').replace("!","NOT").replace('||','OR')
    histoname = '{name}_{cuts}'.format(name=name,cuts=nicename)
    histo = ROOT.TH1D(histoname,'',nbins,xmin,xmax)
    histo.GetXaxis().SetTitle("#it{m}_{ee}^{5x5} (GeV)")
    histo.GetYaxis().SetTitle("Entries")
    tree.Draw('{var}>>{hn}'.format(var=variable,hn=histoname),cut)
    return histo

def getMedian(histo):
    probSums = array('d',[0.5])
    quantiles = array('d',[0])
    histo.GetQuantiles(len(probSums),quantiles,probSums)
    return quantiles[0]

def getMaximumPosition(histo):
    binmax = histo.GetMaximumBin()
    return histo.GetXaxis().GetBinCenter(binmax)

def getFitPeak(histo):
    if histo.Integral()==0:
        return (0.0,0.0)
    res,func = fitOneReso(histo,"mass",-1,ROOT.kBlack,ROOT.kRed)
    return (res.Parameter(1), res.Parameter(2))
    
if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] tag1.txt tag2.txt [tagTimeIC.txt]")
    parser.add_option('-s',  "--step",    dest="step", type='string', default='history', help="step (can be 'histograms','history')")
    parser.add_option('-o',  "--outfile", dest="outfile", default='masses.root', help="name of the output file for the step 1 (default = masses.root)")    
    parser.add_option('-i',  "--infile", dest="infile",   default='masses.root', help="name of the input file with histograms")    
    parser.add_option(       "--runrange", dest="runRange", type=int, nargs=2, default=(277069, 277087), help="run range to be analyzed (default fill ")    
    (options, args) = parser.parse_args()
    
    ROOT.gStyle.SetOptStat(0)

    maindir = '/Users/emanuele/Work/data/cms/multifit/trees_ecalelf'
    weights_dir = 'DoubleEG-Run2016B-ZSkim-23Sep2016-weightsReco/'
    mf_dir = 'DoubleEG-Run2016B-ZSkim-23Sep2016'
    #mf_dir = 'Cal_Mar2017_ref_v2_etaScale'
    
    dirs = [weights_dir,mf_dir]
    recolabels = ['weights','multifit']
    hist_colors = {'weights':ROOT.kBlack, 'multifit':ROOT.kRed}
    hist_mkstyles = {'weights':ROOT.kOpenCircle, 'multifit':ROOT.kFullCircle}
    chains = {'weights': ROOT.TChain('selected'),
              'multifit': ROOT.TChain('selected') }

    bins_etafine   = [0,0.25,0.42,0.6,0.79,0.95]#,1.12,1.4442]
    bins_etacoarse = [0,1.5,2.5];
    ## bins_etafine used for the mass plot
    #bins_eta = bins_etafine
    ## bins_etacoarse used for the R9 history
    bins_eta = bins_etacoarse

    oneday = 24*60*60
    onehour = 60*60
    deltat = 5*onehour
    beginTime = 1466953984 # 26/06/2016 - start of fill 5045
    endTime = 1467088854 # 28/06/2016 - end of fill 5045

    beginTime = 1468948818 # 19/07/2016 - start of fill 5105
    endTime = 1469032179 # 20/07/2016 - end of fill 5105

    if options.step=='histograms':
        
        outfname = options.outfile
        outfile = ROOT.TFile(outfname,'recreate')
        
        for idir,d in enumerate(dirs):
            reco = recolabels[idir]
            print ("Resolution vs time: analyzing reconstruction algo: ",reco)
            #chains[reco].Add('{d1}/{d2}/DoubleEG*Run2016*.root'.format(d1=maindir,d2=d))
            chains[reco].Add('{d1}/{d2}/DoubleEG*Run2016E*.root'.format(d1=maindir,d2=d))
            time = beginTime
            while time<endTime:
                print("Date: ",datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S'))
                for ieb in range(len(bins_eta)-1):
                    subdet_idx = 0 if abs(bins_eta[ieb])<1.4442 else 1
                    start = time; stop = time+deltat
                    hist = getOneMassHisto(chains[reco],bins_eta[ieb],bins_eta[ieb+1],timeMin=start,timeMax=stop,runRange=options.runRange,name='mass_'+reco)
                    outfile.cd()
                    hist.Write()
                time += deltat
                #if time-beginTime>10: deltat=4*onehour
        outfile.Close()

    if options.step == 'history':
        if not os.path.isfile(options.infile):
            print ("ERROR! The input file ",options.infile," not found. Exiting.")
            sys.exit(1)

        histograms = {}
        hist_res = {}
        infile = ROOT.TFile(options.infile,"read")

        nTimePoints = 0
        for k in infile.GetListOfKeys():
            hname = k.GetName()
            histo = infile.Get(hname)
            tokens = hname.split('_')
            variable = tokens[0]; reco = tokens[1]
            startTime = tokens[-7].replace('eventTimegt',''); stopTime = tokens[-5].replace('eventTimelt','');
            print ("var = ",variable," reco = ",reco," start = ",startTime,"   stop = ",stopTime)
            #median,effsigma = (getMedian(histo),effSigma(histo))
            #median,effsigma = (getMaximumPosition(histo),effSigma(histo))
            #median,sigma = getFitPeak(histo)
            median,effsigma = (getMedian(histo),effSigma(histo))
            #print "integral = ",histo.Integral(),"  median = ",median,"    effsigma = ",effsigma
            subdet = 'EE' if 'NOT' in hname else 'EB'
            if subdet=='EB' and reco =='multifit': nTimePoints+=1
            histograms[(variable,reco,subdet,startTime,stopTime)] = histo
            hist_res[(variable,reco,subdet,startTime,stopTime)] = (median,effsigma)
        infile.Close()

        print ("estimators = ",hist_res)

        history = ROOT.TGraphErrors(nTimePoints/2)
        print ("nTimePoints = ",nTimePoints/2)
        history.GetXaxis().SetTimeDisplay(1)
        history.GetXaxis().SetTimeFormat("%H:%M")
        history.GetXaxis().SetTitle("Time during 20/07/2016 LHC fill")
        history.GetYaxis().SetTitle("Median of cluster R_{9}")
        history.GetYaxis().SetTitleOffset(0.3)
        
        graph = {}; graph_npoints = {}
        hist_colors = {'weights':ROOT.kBlack, 'multifit':ROOT.kRed}
        for subdet in ['EB','EE']:
            for reco in ['weights','multifit']:
                for est in ['median','sigma']:
                    graph[(reco,subdet,est)] = history.Clone('history_{reco}_{sub}_{est}'.format(reco=reco,sub=subdet,est=est))
                    graph_npoints[(reco,subdet,est)] = 0
                    graph[(reco,subdet,est)].SetTitle("")
                    graph[(reco,subdet,est)].SetMarkerStyle(ROOT.kFullCircle)
                    graph[(reco,subdet,est)].SetMarkerSize(2)
                    graph[(reco,subdet,est)].SetMarkerColor(hist_colors[reco])
                    graph[(reco,subdet,est)].SetLineColor(hist_colors[reco])
                    if est=='median':
                        graph[(reco,subdet,est)].SetMaximum(0.915)
                        graph[(reco,subdet,est)].SetMinimum(0.885)
                    else:
                        graph[(reco,subdet,est)].SetMaximum(5.0)
                        graph[(reco,subdet,est)].SetMinimum(4.5)
                        

                        
        for key,val in hist_res.iteritems():
            (variable,reco,subdet,start,stop) = key
            (median,effsigma) = val
            time = int((float(stop.replace('p0',''))+float(start.replace('p0','')))/2.) - beginTime
            print ("time = ",datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S'))
            median_norm = 1.
            sigma_norm = 1.0
            graph[(reco,subdet,'median')].SetPoint(graph_npoints[(reco,subdet,'median')],time,median/median_norm); 
            #graph[(reco,subdet,'median')].SetPoint(graph_npoints[(reco,subdet,'median')],time,median/median_norm); 
            #graph[(reco,subdet,'median')].SetPointError(graph_npoints[(reco,subdet,'sigma')],0,effsigma);
            graph_npoints[(reco,subdet,'median')]+=1
            graph[(reco,subdet,'sigma')].SetPoint(graph_npoints[(reco,subdet,'sigma')],time,effsigma/sigma_norm); graph_npoints[(reco,subdet,'sigma')]+=1
            print (key, "has values:", val)
            print (graph_npoints[(reco,subdet,'median')])
            
        for subdet in ['EB','EE']:
            for est in ['median','sigma']:
                plots = [ graph[(reco,subdet,est)] for reco in ['weights','multifit'] ]
                labels = ['weights','multifit']
                styles = ['p','p']
                leg = doLegend(plots,labels,styles,legBorder=False,corner='BR')
                nameplot = 'history_mass_{sub}_{est}'.format(sub=subdet,est=est)
                printPlot(plots, nameplot, sim=False, legend=leg)


                ## save also the graphs in a TFile to be compared with the lumi
                tfile = ROOT.TFile.Open(nameplot+'_graphs.root','recreate')
                for p in plots:
                    p.Write()
                tfile.Close()

    if options.step=='etaresol':

        bins_eta = bins_etafine
        mass_etafine = {}
        for idir,d in enumerate(dirs):
            reco = recolabels[idir]
            chains[reco].Add('{d1}/{d2}/DoubleEG*Run2016B*.root'.format(d1=maindir,d2=d))
            print ("Resolution vs Eta: analyzing reconstruction algo: ",reco)
            for ieb in range(len(bins_eta)-1):
                hist = getOneMassHisto(chains[reco],bins_eta[ieb],bins_eta[ieb+1],timeMin=0,timeMax=1E+10,name='mass_'+reco)
                hist.SetLineColor(hist_colors[reco])
                hist.SetMarkerColor(hist_colors[reco])
                hist.SetMarkerSize(2)
                hist.SetMarkerStyle(hist_mkstyles[reco])
                hist.Rebin(2)
                mass_etafine[(reco,ieb)] = hist
                
        # superimpose weights / MF
        resolVsEta = ROOT.TH1F('resolVsEta','',len(bins_eta)-1,array('f',bins_eta))
        resolVsEta.GetXaxis().SetTitle('#eta')
        resolVsEta.GetYaxis().SetTitle('Effective resolution (GeV)')
        resolVsEta.SetMarkerStyle(ROOT.kFullCircle)
        resolVsEta.SetMarkerSize(2)

        gapBand = resolVsEta.Clone('gapBand')
        gapBand.SetBinContent(5,100)
        gapBand.SetFillColor(ROOT.kGray+1)
        
        resolutionsEta = {}
        for lbl in recolabels:
            resolutionsEta[lbl] = resolVsEta.Clone('resolEta_'+lbl)
            resolutionsEta[lbl].SetMarkerSize(3)
            resolutionsEta[lbl].SetMarkerStyle(ROOT.kFullCircle if lbl=='multifit' else ROOT.kOpenCircle)
            resolutionsEta[lbl].SetMarkerColor(hist_colors[lbl])
            resolutionsEta[lbl].SetLineColor(hist_colors[lbl])

        resolQuadDiffEta = resolVsEta.Clone('resolQuadDiffEta_')
        resolQuadDiffEta.SetMarkerSize(3)
        resolQuadDiffEta.GetYaxis().SetTitle('#sigma_{eff}^{weights} (#minus) #sigma_{eff}^{multifit} (GeV)')
        resolQuadDiffEta.SetMarkerStyle(ROOT.kFullCircle)
        resolQuadDiffEta.SetMarkerColor(hist_colors['multifit'])
        resolQuadDiffEta.SetLineColor(hist_colors['multifit'])
        
        for ieb in range(len(bins_eta)-1):
            frames = []; labels = []; styles = []
            text = ['5x5 clusters']; colors = [ROOT.kBlack]
            for lbl in recolabels:
                key = (lbl,ieb)
                frames.append(mass_etafine[key])
                labels.append(lbl)
                styles.append('pe')
                resol = effSigma(mass_etafine[key])
                median = getMedian(mass_etafine[key])
                text.append("#sigma_{{ eff }}^{{ {label} }} / #it{{ m }} = {resol:.2f}%".format(resol=resol/ZMASS*100, label=lbl))
                colors.append(hist_colors[lbl])
                # fill the resolution vs ET histo
                resolutionsEta[lbl].SetBinContent(ieb+1,resol/ZMASS*100)
                resolutionsEta[lbl].SetBinError(ieb+1,0.001) # this is just to show the error on the X
                resolutionsEta[lbl].GetXaxis().SetTitle('max(|#eta_{1}|,|#eta_{2}|)')
                resolutionsEta[lbl].GetYaxis().SetTitle("#sigma_{eff}^{m5x5}/m (%)")
            namereso = 'plots/compZ_abseta{eta1}to{eta2}'.format(eta1=bins_eta[ieb],eta2=bins_eta[ieb+1])
            leg = doLegend(frames,labels,styles,legBorder=False,corner='BL')
            printPlot(frames, namereso, text, colors, sim=False, histopt='pe', legend=leg)
            
        # resolution vs ETA
        plots = []; labels = []; styles = []
        for k,h in resolutionsEta.items():
            labels.append(k)
            plots.append(h)
            styles.append('pe')
            if labels[0]=='multifit': # sort the legend as the other plots in the paper
                labels.reverse(); plots.reverse(); styles.reverse()
        leg = doLegend(plots,labels,styles,legBorder=False,corner='TL')
        printPlot(plots,"plots/resolutionZdataEta",histopt='pe',legend=leg,sim=False,yaxMin=4.4,yaxMax=5.3,gridy=True,bandPlot=None)
