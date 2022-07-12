#! /usr/bin/env python
import os,sys
from math import *
import numpy as np
import ROOT as rt
rt.gROOT.SetBatch(True)

from ecalDetId import EcalDetId,etaRingMapping
from PlotUtils import customROOTstyle, customPalette, doLegend

SAFE_COLOR_LIST=[
rt.kBlack, rt.kRed, rt.kGreen+2, rt.kBlue, rt.kMagenta+1, rt.kOrange+7, rt.kCyan+1, rt.kGray+2, rt.kViolet+5, rt.kSpring+5, rt.kAzure+1, rt.kPink+7, rt.kOrange+3, rt.kBlue+3, rt.kMagenta+3, rt.kRed+2,
]+list(range(11,40))

class TagValidation:

    def loadTemplates(self,txtfile):
        data = np.genfromtxt(txtfile, delimiter=' ')
        return data
    
    def __init__(self,files,options,doEB=True):
        self.doEB = doEB
        self._options = options
        self.timeICs = {}
        self.timeOffsets = {}
        keys = ["current","ref"]
        tags = dict(zip(keys,files))
        self._allData = {}
        for k,v in tags.items():
            self._allData[k] = self.loadTemplates(v)
        self.ringmap = etaRingMapping()
        if "/AlphaBetaFitter_cc.so" not in rt.gSystem.GetLibraries():
            print("Load C++ Fitter")
            ph = os.path.abspath(os.environ['CMSSW_BASE']+'/src/EcalReconstruction/EcalTools/macro/AlphaBetaFitter.cc')
            rt.gROOT.ProcessLine(f".L {ph}+")
        self.abfitter = rt.AlphaBetaFitter(doEB);

    def setTimeOffset(self,ebval,eeval):
        self.timeOffsets['EB'] = ebval
        self.timeOffsets['EE'] = eeval
            
    def parseDic(self,rawdata):
        mydata = {}
        for item in rawdata:
            key = item[4]
            coor = item[:4]
            coor[0] = coor[3]==0
            val = item[-12:]
            mydata[key] = {"samples" : val, "coor" : coor}
        return mydata

    def printOnePlot(self, plot, canvas, outputName, drawopt="",profileY=False):
        fdir = self._options.printDir if hasattr(self._options,"printDir") else "./"
        if not os.path.exists(fdir):
            os.makedirs(fdir);
        #if os.path.exists("/afs/cern.ch"): os.system("cp /afs/cern.ch/user/g/gpetrucc/php/index.php "+fdir)
        canvas.cd()
        if "TGraph" in plot.ClassName():
            canvas.SetLeftMargin(0.20)
            plot.GetYaxis().SetTitleOffset(2)
            plot.Draw(drawopt if len(drawopt)>0 else "AP")
        elif "TH2" in plot.ClassName() or "TProfile2D" in plot.ClassName():
            canvas.SetRightMargin(0.20)
            plot.SetContour(100)
            plot.Draw("colz0" if len(drawopt)==0 else drawopt)
        else:
            plot.Draw(drawopt)
        for ext in self._options.printPlots.split(","):
            canvas.Print("%s/%s.%s" % (fdir, outputName, ext))
        if ("TH2" in plot.ClassName() or "TProfile2D" in plot.ClassName()) and profileY:
            canvas.SetRightMargin(0.10)
            if "EB" in outputName:
                profY = plot.ProfileY("%s_profY" % plot.GetName(), 0, -1, "s")
                profY.GetXaxis().SetTitle(plot.GetYaxis().GetTitle())
                profY.GetYaxis().SetTitle(plot.GetTitle())
            else:
                profY = rt.TProfile("%s_profIring" % plot.GetName(),"", 39, 0, 38, "s")
                z=1 if "plus" in outputName else -1
                for xbin in range(plot.GetNbinsX()+1):
                    for ybin in range(plot.GetNbinsY()+1):
                        iring = self.ringmap.getRing(False,xbin+1,ybin+1,z)
                        profY.Fill(iring,plot.GetBinContent(xbin,ybin))
                        profY.GetXaxis().SetTitle("#eta ring")
                        profY.GetYaxis().SetTitle(plot.GetTitle())
            profY.SetTitle("")
            profY.Draw()
            for ext in self._options.printPlots.split(","):
                canvas.Print("%s/%s_profIEta.%s" % (fdir, outputName, ext))
                        

    def do1dDiff(self):
        part = 'eb' if self.doEB else 'ee'
        rt.gStyle.SetOptStat(111111)
        refData = self.parseDic(self._allData["ref"])
        newData = self.parseDic(self._allData["current"])
        histos = []
        for s in range(12): 
            h = rt.TH1D(('%s_diff_1d_sample%d' % (part,s)),"",1000,-0.2,0.2)
            h.GetXaxis().SetTitle('sample_{%d}^{new}-sample_{%d}^{ref}' % (s,s))
            histos.append(h)
        for key, data in refData.items():
            partition = data['coor'][0]
            if key not in newData: continue
            if ((self.doEB and int(partition)==0) or (not self.doEB and int(partition)==1)): continue
            for s in range(12):
                histos[s].Fill(float((newData[key])['samples'][s])-float((refData[key])['samples'][s]))
                if (self._options.debugOutliers and s==1 and abs(float((newData[key])['samples'][s])-float((refData[key])['samples'][s]))>0.1):
                    print("big change for detid = ",detid)
        canv = rt.TCanvas("c","",1200,1200)
        canv.SetLogy()
        for s in range(12):
            self.printOnePlot(histos[s],canv,'%s_diff_1d_sample%d' % (part,s))

    def do2dDiff(self):
        part = 'eb' if self.doEB else 'ee'
        customROOTstyle()
        refData = self.parseDic(self._allData["ref"])
        newData = self.parseDic(self._allData["current"])
        histos = {}
        if self.doEB: histos['eb'] = []
        else: 
            histos['eeplus'] = []
            histos['eeminus'] = []
        for s in range(12): 
            if self.doEB:
                h = rt.TProfile2D(('%s_diff_2d_sample%d' % (part,s)),"",360,1,360,171,-85.5,85.5)
                h.GetXaxis().SetTitle('i#phi')
                h.GetYaxis().SetTitle('i#eta')
                h.SetTitle('sample_{%d}^{new}-sample_{%d}^{ref}' % (s,s))
                h.GetZaxis().SetRangeUser(-0.01,0.01)
                histos['eb'].append(h)
            else: 
                hplus = rt.TProfile2D(('%s_plus_diff_2d_sample%d' % (part,s)),"",100,1,100,100,1,100)
                hplus.GetXaxis().SetTitle('ix')
                hplus.GetYaxis().SetTitle('iy')
                hplus.SetTitle('sample_{%d}^{new}-sample_{%d}^{ref}' % (s,s))
                hplus.GetZaxis().SetRangeUser(-0.01,0.01)
                histos['eeplus'].append(hplus)
                hminus = hplus.Clone('%s_minus_diff_2d_sample%d' % (part,s))
                histos['eeminus'].append(hminus)

        for key, data in refData.items():
            partition = data['coor'][0]
            x,y,z = data['coor'][1:]

            if key not in newData: continue
            if ((self.doEB and int(partition)==0) or (not self.doEB and int(partition)==1)): continue
            if z==-999: continue
            if z==0: htofill = histos['eb']
            elif z==1: htofill = histos['eeplus']
            else: htofill = histos['eeminus']
            (ix,iy) = (y,x) if self.doEB else (x+1,y+1)
            for s in range(12):
                htofill[s].Fill(ix,iy,float(newData[key]['samples'][s])-float(data['samples'][s]))

        xsize = 1200
        ysize = int(xsize*170/360+0.1*xsize) if self.doEB else int(xsize*0.9)
        canv = rt.TCanvas("c","",xsize,ysize)

        for k,v in histos.items():
            for s in range(12):
                #(histos[k])[s].Draw("colz")
                #canv.SaveAs('%s_diff_2d_sample%d.pdf' % (k,s))
                self.printOnePlot( (histos[k])[s], canv, '%s_diff_2d_sample%d' % (k,s) )

    def loadTimeICs(self,txtfile):
        ret = {}
        for line in open(txtfile,'r'):
            item = line.split()
            (key,val) = (item[0],item[1])
            ret[key] = val
        return ret

    def do2dTime(self,currentTimeIC, newTimeIC=''):
        # FIXME
        part = 'EB' if self.doEB else 'EE'
        customROOTstyle()
        refData = self.parseDic(self._allData["ref"])
        newData = self.parseDic(self._allData["current"])
        of = rt.TFile.Open('%s_timeVals.root' % part,'recreate')
        histos = []
        histosDiff = []
        if self.doEB: 
            h = rt.TProfile2D(('%s_time' % part),"",360,1,360,171,-85.5,85.5)
            h.GetXaxis().SetTitle('i#phi')
            h.GetYaxis().SetTitle('i#eta')
            h.SetTitle('Time (ns)')
            h.GetZaxis().SetRangeUser(-1,1)
            histos.append(h)
            histosDiff.append(h.Clone(('%s_time_diff' % part)))
        else: 
            hplus = rt.TProfile2D(('%splus_time' % part),"",100,1,100,100,1,100)
            hplus.GetXaxis().SetTitle('ix')
            hplus.GetYaxis().SetTitle('iy')
            hplus.SetTitle('Time (ns)')
            hplus.GetZaxis().SetRangeUser(-1,1)
            histos.append(hplus)
            histosDiff.append(hplus.Clone(('%splus_time_diff' % part)))
            hminus = hplus.Clone('%sminus_time' % part)
            histos.append(hminus)
            histosDiff.append(hminus.Clone(('%sminus_time_diff' % part)))

        detids = EcalDetId('/afs/cern.ch/work/e/emanuele/public/ecal/pulseshapes_db/detids_ECAL.txt')

        # load the current time ICs (dump of the tag)
        self.timeICs = self.loadTimeICs(currentTimeIC)
        if len(newTimeIC)>0: newTimeICs = self.loadTimeICs(newTimeIC)

        histo = rt.TH1F("histo","",15,0,15)
        cryfit = 0
        for (partition,detid),samples in newData.items():
            key = (partition,detid)
            (x,y,z) = detids.xyz(detid)

            if detid not in self.timeICs: continue
            if ((self.doEB and int(partition)==0) or (not self.doEB and int(partition)==1)): continue
            if z==0 or z==1: 
                htofill = histos[0]
                hdifftofill = histosDiff[0]
            else: 
                htofill = histos[1]
                hdifftofill = histosDiff[1]
            (ix,iy) = (y,x) if self.doEB else (x,y)

            # fill the template and fit it
            for s in range(3):  histo.SetBinContent(s+1,0)
            for s in range(12): histo.SetBinContent(s+4,float((newData[key])[s]))
            self.abfitter.fit(histo)
            results = {'pars': abfitter.getPars(), 'errs': abfitter.getErrs()}
            currentCorr = float(self.timeICs[detid]) + self.timeOffsets[part]
            time = 25.*((results['pars'])[2]-5.5)
            correctedTime = time + currentCorr
            # print "detid = ",key," has time from fit [IC] = ",time, " [",currentCorr,"]"
            htofill.Fill(ix,iy,correctedTime)

            if len(newTimeIC)>0: 
                if detid not in newTimeICs: continue
                newCorr = float(newTimeICs[detid])
                # print '    correctedTime = ',correctedTime,"   newCorr = ",newCorr,"  diff = ", correctedTime - newCorr
                hdifftofill.Fill(ix,iy,correctedTime - newCorr)

            if cryfit % 1000 == 0: print('fitted ',cryfit,' templates')
            cryfit += 1

        xsize = 1200
        ysize = int(xsize*170/360+0.1*xsize) if self.doEB else int(xsize*0.9)
        of.cd()
        canv = rt.TCanvas("c","",xsize,ysize)
        for h in histos:
            #h.Draw("colz")
            #canv.SaveAs(h.GetName()+'.pdf')
            self.printOnePlot(h,canv,h.GetName())
            h.Write()
        for h in histosDiff:
            h.Write()
        of.Close()

    def timeFit(self,pulse,abfitter):
        histo = rt.TH1F("time","",15,0,15)
        # fill the template and fit it
        for s in range(3):  histo.SetBinContent(s+1,0)
        for s in range(12): 
            histo.SetBinContent(s+4,float(pulse[s]))
            histo.SetBinError(s+4,float(pulse[s])/sqrt(1000)) # about 1k entries per bin
        abfitter.fit(histo)
        results = {'pars': abfitter.getPars(), 'errs': abfitter.getErrs()}
        val = {}; err = {};
        for ip,par in enumerate(['alpha','beta','T0']):
            val[par] = (results['pars'])[ip]
            err[par] = (results['errs'])[ip]
            if par=="T0":
                val[par] = (val[par]-5.5)*25.
                err[par] = err[par]*25.
        histo.Delete()
        return (val,err)

    def do2dShapeDiff(self, absoluteShape=False):
        part = 'EB' if self.doEB else 'EE'
        customROOTstyle()
        refData = self.parseDic(self._allData["ref"])
        newData = self.parseDic(self._allData["current"])
        #of = rt.TFile.Open('%s_timeVals.root' % part,'recreate')
        histos = {}
        for ip,par in enumerate(['alpha','beta','T0']):
            (zmin,zmax) = (-0.03,0.03) if par!="T0" else (-1,1) # ns
            if par=="T0" and absoluteShape: (zmin,zmax) = (-5,5) # ns
            if self.doEB:
                h = rt.TProfile2D(('%s_%s' % (part,par)),"",360,1,360,171,-85.5,85.5)
                h.GetXaxis().SetTitle('i#phi')
                h.GetYaxis().SetTitle('i#eta')
                h.SetTitle('Time (ns)' if par=="T0" else '#Delta #{par}/#{par}'.format(par=par))
                h.GetZaxis().SetRangeUser(zmin,zmax)
                histos[par] = [h]
            else: 
                hz = []
                hplus = rt.TProfile2D(('%splus_%s' % (part,par)),"",100,1,100,100,1,100)
                hplus.GetXaxis().SetTitle('ix')
                hplus.GetYaxis().SetTitle('iy')
                hplus.SetTitle('Time (ns)' if par=="T0" else '#Delta #{par}/#{par}'.format(par=par))
                hplus.GetZaxis().SetRangeUser(zmin,zmax)
                hz.append(hplus)
                hminus = hplus.Clone('%sminus_%s' % (part,par))
                hz.append(hminus)
                histos[par] = hz

        cryfit = 0
        for key,data in newData.items():
            partition = data['coor'][0]
            x,y,z = data['coor'][1:]

            if not absoluteShape and key not in refData: continue
            if ((self.doEB and int(partition)==0) or (not self.doEB and int(partition)==1)): continue
            if z==-999: continue

            (ix,iy) = (y,x) if self.doEB else (x+1,y+1)

            (val,err) = self.timeFit(data['samples'],self.abfitter)
            (valRef,errRef) = self.timeFit(refData[key]['samples'],self.abfitter) if not absoluteShape else ({},{})

            for ip,par in enumerate(['alpha','beta','T0']):
                if z==0 or z==1: 
                    htofill = (histos[par])[0]
                else: 
                    htofill = (histos[par])[1]
                value = val[par]-valRef[par] if not absoluteShape else val[par]
                if par!="T0": value = value/valRef[par] if not absoluteShape else value
                #print "par = ",par," val1,2 = ",val[par]," ",valRef[par]," norm value = ",value
                #print "err1,2 = ",err[par]," ",errRef[par]
                htofill.Fill(ix,iy,value)

            if cryfit % 1000 == 0: print('fitted ',cryfit,' templates')
            cryfit += 1

        xsize = 1200
        ysize = int(xsize*170/360+0.1*xsize) if self.doEB else int(xsize*0.9)
        #of.cd()
        canv = rt.TCanvas("c","",xsize,ysize)
        for k,hvect in histos.items():
            for h in hvect:
                #h.Write()
                self.printOnePlot(h,canv,'{name}{absolute}'.format(name=h.GetName(),absolute='_absolute' if absoluteShape else ''),"",True)
        #of.Close()

    def historyPlot(self,detid,iovfiles):
        iovs = []
        for f in iovfiles: 
            print("Looking for crystal with rawID = ",detid," in the IOV file ",f,"...")
            data = self.parseDic(self.loadTemplates(f))
            pulsetemp = []
            for partition in ['0','1']:
                key = (partition,detid)
                if key in data: pulsetemp = data[key]
            if len(pulsetemp)==0: print("ERROR! Crystal with detid = ",detid," not found in the IOV file ",f,". Skipping point.")
            else: iovs.append(pulsetemp)


        canv = rt.TCanvas("c","",600,600)
        for s in range(12): 
            y = [float(pulsetemp[s]) for pulsetemp in iovs]
            x = [float(i+1) for i in range(len(y))]
            g = rt.TGraph(len(y),np.array(x),np.array(y))
            g.SetTitle("")
            avg = sum(y)/float(len(y))
            var = max(max(y)-avg,avg-min(y))
            g.GetYaxis().SetRangeUser(avg - 2*var,avg + 2*var)
            g.SetLineColor(SAFE_COLOR_LIST[s])
            g.SetMarkerColor(SAFE_COLOR_LIST[s])
            g.SetMarkerStyle(rt.kFullCircle)
            g.SetMarkerSize(1)
            g.GetXaxis().SetTitle("IOV in 2016")
            g.GetYaxis().SetTitle("sample %d value" % (4+s))
            self.printOnePlot(g,canv,"template_sample_%d" % s,"AP")


    def pulseComp(self,detid,pulse,pulseRef):
        customROOTstyle()
        hpulse = rt.TH1F("hpulse","",15,0,15)
        hpulseref = hpulse.Clone("hpulseref")
        # fill the template and fit it
        for s in range(3):  
            hpulse.SetBinContent(s+1,0)
            hpulseref.SetBinContent(s+1,0)
        for s in range(12): 
            hpulse.SetBinContent(s+4,float(pulse[s]))
            hpulseref.SetBinContent(s+4,float(pulseRef[s]))
        canvas = rt.TCanvas("c","",600,600)
        hpulseref.SetLineColor(rt.kBlue+2)
        hpulse.SetMarkerStyle(rt.kFullCircle)
        hpulseref.GetXaxis().SetTitle("sample")
        hpulseref.GetYaxis().SetTitle("a.u.")
        hpulseref.Draw("hist")
        hpulse.Draw("same p")
        fdir = self._options.printDir
        plots = [hpulse,hpulseref]; labels=['new','ref']; styles=['p','l']
        leg = doLegend(plots,labels,styles)
        leg.Draw()
        for ext in self._options.printPlots.split(","):
            canvas.Print("%s/pulse_id%s.%s" % (fdir,detid,ext))

    def do1dComparison(self,inputfile=None,maxPlots=10):
        part = 'eb' if self.doEB else 'ee'
        rt.gStyle.SetOptStat(111111)
        refData = self.parseDic(self._allData["ref"])
        newData = self.parseDic(self._allData["current"])

        detidsToCheck=[]
        if inputfile: 
            detidsToCheck=[line.rstrip() for line in open(inputfile,'r')]
            print("check ids = ",detidsToCheck)

        ipulse=0
        for (partition,detid),samples in refData.items():
            key = (partition,detid)
            if key not in newData: continue
            if len(detidsToCheck)>0 and detid not in detidsToCheck: continue
            if ((self.doEB and int(partition)==0) or (not self.doEB and int(partition)==1)): continue
            self.pulseComp(detid,newData[key],refData[key])
            if ipulse<maxPlots: ipulse += 1
            else: break

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] tag1.txt tag2.txt [tagTimeIC.txt]")
    parser.add_option("-p","--partition", dest="partition",  type="string", default="EB", help="partitions to be analysed: EB,EE")
    parser.add_option(     "--do1Ddiff",  dest="do1Ddiff",   action="store_true", help="make the 1D differences of the samples in the two tags")
    parser.add_option(     "--do2Ddiff",  dest="do2Ddiff",   action="store_true", help="make the 2D differences of the samples in the two tags")
    parser.add_option(     "--do2Dtime",  dest="do2Dtime",   action="store_true", help="make the 2D time map")
    parser.add_option(     "--do2DShapeDiff",  dest="do2DShapeDiff",   action="store_true", help="make the 2D shape difference map, only based on pulse shapes")
    parser.add_option(     "--do2DShape",  dest="do2DShape",   action="store_true", help="make the 2D shape map, only based on pulse shapes")
    parser.add_option(     "--do1Dpulses",  dest="do1Dpulses",   action="store_true", help="make the comparison of pulses in the same crystal for the two tags")
    parser.add_option("-t","--timeICs",   dest="timeICs",    type="string", default="", help="the file containing the time ICs")
    parser.add_option("--print", dest="printPlots", type="string", default="png,pdf,txt", help="print out plots in this format or formats (e.g. 'png,pdf,txt')");
    parser.add_option("--pdir", "--print-dir", dest="printDir", type="string", default="plots", help="print out plots in this directory");
    parser.add_option(     "--debugOutliers", dest="debugOutliers", action="store_true", help="print the hashed index of crystals which have a variation larger than 10% in raising sample");

    (options, args) = parser.parse_args()
    if len(args) < 2: raise(RuntimeError, 'Expecting at least two arguments')

    doEB = True if options.partition=='EB' else False
    
    tv = TagValidation(args,options,doEB=doEB)

    if options.do1Ddiff:
        tv.do1dDiff()

    if options.do2Ddiff:
        tv.do2dDiff()

    if options.do2DShapeDiff:
        tv.do2dShapeDiff()

    if options.do2DShape:
        tv.do2dShapeDiff(absoluteShape=True)
        
    if options.do1Dpulses:
        if len(args)==3:
            print("using ",args[2]," as the list of crystals to display")
            tv.do1dComparison(args[2])
        else: 
            tv.do1dComparison()

    currentTimeICs = '/afs/cern.ch/work/e/emanuele/public/ecal/timeICs_dump_EcalTimeCalibConstants__since_00253984_till_Run2016A.txt'
    if options.do2Dtime:
        # values in the GT 80X_dataRun2_Prompt_v8
        tv.setTimeOffset(-0.964168,0.347665)
        tv.do2dTime(currentTimeICs,options.timeICs)
