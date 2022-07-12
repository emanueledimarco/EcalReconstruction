#! /usr/bin/env python
from array import array
from math import *
import numpy
import ROOT
ROOT.gROOT.SetBatch(True)

nsamples=10

def noiseAutocorr(partition='EB',gain=12):
    noisecorr = {}
    noisecorr[('EB',12)] = [1.00000, 0.71073, 0.55721, 0.46089, 0.40449,
                           0.35931, 0.33924, 0.32439, 0.31581, 0.30481 ]
    noisecorr[('EE',12)] = [1.00000, 0.71373, 0.44825, 0.30152, 0.21609,
                           0.14786, 0.11772, 0.10165, 0.09465, 0.08098 ]
    noisecorr[('EB',6)] = [1.00000, 0.70946, 0.58021, 0.49846, 0.45006,
                          0.41366, 0.39699, 0.38478, 0.37847, 0.37055 ]
    noisecorr[('EE',6)] = [1.00000, 0.71217, 0.47464, 0.34056, 0.26282,
                          0.20287, 0.17734, 0.16256, 0.15618, 0.14443 ]
    noisecorr[('EB',1)] = [1.00000, 0.73354, 0.64442, 0.58851, 0.55425,
                          0.53082, 0.51916, 0.51097, 0.50732, 0.50409 ]
    noisecorr[('EE',1)] = [1.00000, 0.72698, 0.62048, 0.55691, 0.51848,
                          0.49147, 0.47813, 0.47007, 0.46621, 0.46265 ]
    if (partition,gain) in noisecorr:
        return noisecorr[(partition,gain)]
    else:
        print ("ERROR! wrong partition: ", partition," or gain: ",gain)
        return []

def noiseCov(partition='EB',gain=12):
    autocorr = noiseAutocorr(partition,gain)
    covmat = numpy.zeros((nsamples,nsamples))
    for i in range(10):
        for j in range(10):
            vidx = abs(j-i)
            covmat[i,j]=autocorr[vidx]
    return covmat

def noiseCovTH2(partition='EB',gain=12):
    covmat = noiseCov(partition,gain)
    histo = ROOT.TH2D('covmat_{part}_gain{g}'.format(part=partition,g=gain),'',nsamples,0,nsamples,nsamples,0,nsamples)
    for i in range(10):
        for j in range(10):
            histo.SetBinContent(i+1,j+1,int(100*covmat[i,j]))
    return histo

def covMatAxisLabel(bin):
    label = 'S_{{ {idx} }}'.format(idx=bin)
    return label

if __name__ == "__main__":

    lat = ROOT.TLatex()
    lat.SetNDC(); lat.SetTextFont(42)

    # draw pulse covariance
    ROOT.gStyle.SetOptStat(0)
    ROOT.TColor.CreateGradientColorTable(2,
                                         array ("d", [0.00, 0.50, 1.00]),
                                         array ("d", [1.00, 1.00, 0.00]),
                                         array ("d", [0.70, 1.00, 0.34]),
                                         array ("d", [0.00, 1.00, 0.82]),
                                         #array ("d", [0.00, 1.00, 1.00]),
                                         #array ("d", [0.36, 1.00, 0.63]),
                                         #array ("d", [0.82, 1.00, 0.00]),
                                         255,  0.95)
    ROOT.TColor.InvertPalette()
    
    ROOT.gStyle.SetPaintTextFormat('.0f')
    canv = ROOT.TCanvas("canv","",1200,1200)
    canv.SetGridx()
    canv.SetGridy()
    canv.SetLeftMargin(0.18)
    canv.SetRightMargin(0.18)
    canv.SetBottomMargin(0.18)

    for part in ['EB','EE']:
        for gain in [1,6,12]:
            covmat = noiseCovTH2(part,gain)
            covmat.GetXaxis().SetTickLength(0.)
            covmat.GetYaxis().SetTickLength(0.)
            covmat.GetXaxis().LabelsOption("v")
            covmat.GetZaxis().SetRangeUser(0,1)
            covmat.SetMarkerSize(1.5)
            for xbin in range(nsamples):
                covmat.GetXaxis().SetBinLabel(xbin+1,covMatAxisLabel(xbin))
                covmat.GetYaxis().SetBinLabel(xbin+1,covMatAxisLabel(xbin))

            covmat.GetXaxis().SetTitleOffset(1.5)
            covmat.GetYaxis().SetTitleOffset(1.5)
            covmat.GetZaxis().SetTitleOffset(1.2)
            covmat.GetXaxis().SetTitleSize(0.05)
            covmat.GetYaxis().SetTitleSize(0.05)
            covmat.GetZaxis().SetTitleSize(0.05)


            covmat.GetXaxis().SetTitle('Time sample')
            covmat.GetYaxis().SetTitle('Time sample')
            covmat.GetZaxis().SetTitle('{subdet}  #bf{{#rho}}_{{noise}} (%)'.format(subdet = 'Barrel' if part=='EB' else 'Endcap') )
            covmat.GetZaxis().CenterTitle()
            covmat.Draw("colz text45")
            lat.DrawLatex(0.16, 0.92, '#bf{CMS}')
            lat.DrawLatex(0.70, 0.92, '(13 TeV)')
            canv.SaveAs('noisecorr_{p}_gain{g}.pdf'.format(p=part,g=gain))
