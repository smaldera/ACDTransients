# plotta i rates per  le 5 facce del file "file_name"
# nome del file hardcoded... 


from __future__ import print_function, division
import ROOT
import numpy as np
import datetime
import time as tt







def addPoints(gFinal,g):

    n=g.GetN()
    n_original=gFinal.GetN()

    for i in range(0,n):
        
        x = ROOT.Double()
        y = ROOT.Double()

        yErr = ROOT.Double()
 
        g.GetPoint(i,x,y)
        yErr=g.GetErrorY(i)
        
        gFinal.SetPoint(n_original+i,x,y)
        gFinal.SetPointError(n_original+i,0,yErr)
    
    return gFinal







file_name='sgr_bin1_t0.root'
start=-50
stop=200
base_dir='/home/maldera/FERMI/code/plotAcdRates/data/SGR_1935+2154/recon/sgr/'


hist_names=['hist_top','hist_Xpos','hist_Xneg','hist_Ypos','hist_Yneg',  'histNorm_top',  'histNorm_Xpos', 'histNorm_Xneg','histNorm_Ypos', 'histNorm_Yneg']
histos=[]



#for infile in files:
filename=base_dir+file_name
print ('opening file:',filename)
f=ROOT.TFile(filename,'read')
for i in range(0,len(hist_names)):

    histos.append(f.Get(hist_names[i]))
 #   print ("type hist[i]",type(histos[i]))
    histos[i].SetMarkerColor(4)
    histos[i].SetLineColor(4)
    histos[i].SetMarkerStyle(20)
    histos[i].GetXaxis().SetLabelSize(0.09)
    histos[i].GetXaxis().SetTitle('met-')
   
    histos[i].GetYaxis().SetLabelSize(0.08)
    histos[i].SetTitleSize(15)
    





######### 

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetTitleFontSize(0.1)

c1=ROOT.TCanvas('c1',"",0)
c1.Divide(1,5)
c1.cd(1)

for j in range (0,5):

   c1.cd(j+1)
   histos[j].GetXaxis().SetRangeUser(start,stop)
   histos[j].Draw("perr")



c2=ROOT.TCanvas('c2',"",0)
c2.Divide(1,5)
for j in range (5,10):

   c2.cd(j-4)
   histos[j].GetXaxis().SetRangeUser(start,stop)
   histos[j].Draw("perr")



