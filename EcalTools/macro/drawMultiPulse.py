import ROOT
ROOT.gROOT.SetBatch(True)
from PlotUtils import doLegend
from performances_mc import printCanvas

ootcolors = [ROOT.kOrange-5,ROOT.kAzure-5,ROOT.kMagenta-3,ROOT.kGreen+2,ROOT.kGray+1,ROOT.kOrange+6,ROOT.kViolet-1]

## very fine dotted line
ROOT.gStyle.SetLineStyleString(10,"[4 4]")
ootstyle = 10

def printOnePlot(frames, name, text=[], histopts=[], legend=None, sim=True, yaxMin=None, yaxMax=None, gridx=False, gridy=False, ttext=None, ttext2=None):
    canv = ROOT.TCanvas("canv","",1200,900)
    canv.SetLeftMargin(0.15)
    canv.SetRightMargin(0.05)
    canv.SetBottomMargin(0.15)
    canv.SetTicks(1,1)
    ymax = yaxMax if yaxMax else max([f.GetMaximum() for f in frames])
    ymin = yaxMin if yaxMin else min([f.GetMinimum() for f in frames])
    if gridx: canv.SetGridx()
    if gridy: canv.SetGridy()
    for iframe,frame in enumerate(frames):
        print ("drawing frame ...",frame.GetName())
        if frame.InheritsFrom("TH1"):
            frame.SetMaximum(ymax*(1.10))
            frame.SetMinimum(ymin if yaxMin else 0)
        xax = frame.GetXaxis(); yax = frame.GetYaxis()
        xax.SetNdivisions(10,ROOT.kTRUE)
        xax.SetDecimals(1)    
        xax.SetTitleOffset(1.1); xax.SetTitleSize(0.06); xax.SetLabelSize(0.06)
        yax.SetTitleOffset(1.1); yax.SetTitleSize(0.06); yax.SetLabelSize(0.06)
        if len(histopts)==0:
            frame.Draw('' if iframe==0 else 'same')
        else:
            frame.Draw(histopts[iframe] if iframe==0 else 'same '+histopts[iframe])            
    if legend: legend.Draw()
    if ttext:
         ttext.SetTextAlign(21)
         ttext.SetTextSize(0.05)
         ttext.Draw()
    if ttext2:
         ttext2.SetTextAlign(21)
         ttext2.SetTextSize(0.06)
         ttext2.Draw()        
    printCanvas(canv, name, text, textSize=0.04, sim=sim)

def doPlot(hists,plotname):
    
    labeledHists = [0 for i in range(4)]
    for h in hists:
        if h.GetName()=='data':
            h.SetMarkerStyle(ROOT.kFullCircle)
            h.SetMarkerColor(ROOT.kBlack)
            h.SetMarkerSize(2)
            h.SetLineColor(ROOT.kBlack)
            labeledHists[3] = h
        elif h.GetName()=='total':
            h.SetLineWidth(5)
            h.SetLineColor(ROOT.kBlue+1)
            labeledHists[0] = h
        elif h.GetName()=='intime':
            h.SetLineColor(ROOT.kRed)
            h.SetLineWidth(2)
            h.SetLineStyle(7)
            labeledHists[1] = h
        else:
            ootn = int(h.GetName().split('oot')[-1])
            h.SetLineColor(ootcolors[ootn])
            h.SetLineStyle(3)
            h.SetLineWidth(2)
        h.GetXaxis().SetTitle('Time sample')
        h.GetYaxis().SetTitle('Energy (GeV)')
        h.SetMinimum(0)
        
    genericOOT = hists[0].Clone('genericoot')
    genericOOT.SetLineColor(ROOT.kGray+2)
    genericOOT.SetLineStyle(3)
    genericOOT.SetLineWidth(2)
    labeledHists[2] = genericOOT

    labels = ['Total','In-time','Out-of-time','Observed']
    styles = ['l','l','l','p']
    plotopts = ['hist' for i in range(len(hists)-1)] + ['pe X0']
    
    leg = doLegend(labeledHists,labels,styles,legBorder=False,corner='TL',legWidth=0.25,textSize=0.050)
    tt = ROOT.TLatex(0.25,0.52, '<PU> = 20')
    tt.SetNDC(); tt.SetTextFont(42)
    tt2 = ROOT.TLatex(0.83,0.79, 'Barrel' if 'EB' in plotname else 'Endcap')
    tt2.SetNDC(); tt2.SetTextFont(42)
    printOnePlot(hists, plotname, histopts=plotopts, yaxMin=-0.01, ttext=tt, ttext2=tt2, legend=leg)
    
def array2hist(arr,name,errors=[]):
    nbins = len(arr)
    h = ROOT.TH1F(name,'',nbins,-0.5,9.5)
    for i in range(nbins):
        h.SetBinContent(i+1,arr[i])
        if len(errors)==len(arr):
            h.SetBinError(i+1,errors[i])
    return h
            
def drawBarrel():

    data  = [0,0,0,3.2e-2, 9.1e-1,  1.20,  1.23,    1.09,    8.06e-1, 5.60e-1]
    #errdata = [3.9e-2 for i in range(10)] # removed because CWR comment
    errdata = [0 for i in range(10)]
    
    total = [0,0,0,8.9e-3, 8.97e-1, 1.18,  1.25,    1.06,    0.79   , 5.45e-1]
    IT    = [0,0,0,8.9e-3, 8.97e-1, 1.17,  1.05,    0.80,    5.57e-1, 3.66e-1]
    OOT0  = [0,0,0,0,     0,        3.7e-3,1.94e-1, 2.56e-1, 2.3e-1 , 1.73e-1]

    data   = array2hist(data,'data',errdata)
    total  = array2hist(total,'total')
    IT     = array2hist(IT,'intime')
    OOT0   = array2hist(OOT0,'oot0')

    hists = [total,IT,OOT0,data]
    doPlot(hists,"multifit_EB")

def drawEndcap():
    data = [2.51,   3.12,  3.11,  3.78,   6.75,  7.86,   6.89,  5.64,  4.38,  3.11]
    #errdata = [0.17 for i in range(10)] # removed because CWR comment
    errdata = [0 for i in range(10)]
    
    total = [2.52,  3.17,  3.00,  3.72,   6.73,   7.75,   6.92,   5.74,  4.33,  3.04]
    IT    = [0.00,  0.00,  0.00,  0.57,   3.86,   5.00,   4.55,   3.53,  2.50,  1.66]
    OOT0  = [0.00,  0.00,  0.00,  0.00,   0.00,   0.00,   0.01,   0.02,  0.01,  0.00]
    OOT1  = [2.29,  2.97,  2.70,  2.10,   1.49,   1.00,   0.63,   0.39,  0.24,  0.13]
    OOT2  = [0.21,  0.18,  0.14,  9.2e-2, 6.9e-2, 3.4e-2, 1.1e-2, 0.00,  0.00,  0.00]
    OOT3  = [0.00,  0.00,  0.13,  0.92,   1.19,   1.09,   0.84,   0.60,  0.39,  0.25]
    OOT4  = [0.00,  0.00,  0.00,  0.00,   0.08,   0.60,   0.76,   0.70,  0.54,  0.38]
    OOT5  = [0.00,  0.00,  0.00,  0.00,   0.00,   0.00,   5.7e-2, 4.7e-1, 6.2e-1, 5.6e-1]

    data  = array2hist(data,'data',errdata)
    total = array2hist(total,'total')
    IT     = array2hist(IT,'intime')
    OOT0   = array2hist(OOT0,'oot0')
    OOT1   = array2hist(OOT1,'oot1')
    OOT2   = array2hist(OOT2,'oot2')
    OOT3   = array2hist(OOT3,'oot3')
    OOT4   = array2hist(OOT4,'oot4')
    OOT5   = array2hist(OOT5,'oot5')

    hists = [total,IT,OOT0,OOT1,OOT2,OOT3,OOT4,OOT5,data]
    doPlot(hists,"multifit_EE")

    
if __name__ == "__main__":

    ROOT.gStyle.SetOptStat(0)
    drawBarrel()
    drawEndcap()
    
