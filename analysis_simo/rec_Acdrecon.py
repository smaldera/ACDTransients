
from __future__ import print_function, division
import ROOT
import numpy as np
import datetime
import time as tt

import array

hist_names=['hist_top','hist_Xpos','hist_Xneg','hist_Ypos','hist_Yneg',  'histNorm_top',  'histNorm_Xpos', 'histNorm_Xneg','histNorm_Ypos', 'histNorm_Yneg']


def get_histos(f):

    histos=[]
   # f=ROOT.TFile(filename,'read')
    for i in range(0,len(hist_names)):

        histos.append(f.Get(hist_names[i]))
        print ("type hist[i]",type(histos[i]))
        histos[i].SetMarkerColor(4)
        histos[i].SetLineColor(4)
        histos[i].SetMarkerStyle(20)
        histos[i].GetXaxis().SetLabelSize(0.09)
        histos[i].GetYaxis().SetLabelSize(0.05)
        histos[i].SetTitleSize(15)
   # f.Close()    
    return histos




def yDistr(hist,start,stop,x0,xf):

   n_bins= hist.GetNbinsX()
   massimo=hist.GetMaximum()
   minimo=hist.GetMinimum()
   name='rate_'+hist.GetTitle()
   
   h_yDistr=ROOT.TH1F(name,name,100,minimo,massimo)
   
   for i in range (1,n_bins):
       y=hist.GetBinContent(i)
       x=hist.GetBinCenter(i)

       if ( (x>start and x<stop) and (not(x>x0 and x<xf )) ): 
           h_yDistr.Fill(y)


   return h_yDistr     


def fit_bkg(hist,start,stop,x0,xf):

    xg=[]
    yg=[]
    yg_err=[]
    n_bins= hist.GetNbinsX()

    x_err=[(hist.GetBinCenter(3)-hist.GetBinCenter(2))/2.]
    
    for i in range(0,n_bins):

        x=hist.GetBinCenter(i)
        if ( (x>=start and x<=stop) and (not(x>x0 and x<xf )) ): 
             xg.append(x)
             yg.append(hist.GetBinContent(i))
             yg_err.append(hist.GetBinError(i))

        if (x>stop):
           break
    xg_err=[(hist.GetBinCenter(3)-hist.GetBinCenter(2))/2.]*len(xg)   
    g=ROOT.TGraphErrors(len(xg),array.array('d',xg),array.array('d',yg),array.array('d',xg_err),array.array('d',yg_err))

    bkg_func=ROOT.TF1("bkg_func","[0]+[1]*x",start, stop)
    bkg_func.SetParameter(0, 6.e-05)
    bkg_func.SetParameter(1, 0.)

    g.Fit('bkg_func',"MER")

    return g, bkg_func

     



       

def integrate_and_subtractBkg(hist, mean_bkg,   t0,tf):

      n_bins= hist.GetNbinsX()
      integral=0.
      for i in range (1,n_bins):
          y=hist.GetBinContent(i) -mean_bkg
          x=hist.GetBinCenter(i)
          
          if (x>=t0 and x<=tf):
              integral+=y

      return integral         

def integrate_and_subtractBkg_v2(hist, bkg_func,   t0,tf):   # bkg_func  is a ROOT.TF1

      n_bins= hist.GetNbinsX()
      integral=0.
      for i in range (1,n_bins):

          x=hist.GetBinCenter(i)
          if (x>=t0 and x<=tf):
              
              y=hist.GetBinContent(i) -bkg_func.Eval(x)
              print("Integrating... x=",x," bin = ",hist.GetBinContent(i)," bkg =",bkg_func.Eval(x))
              integral+=y

          if (x>tf):
              break
              
      return integral         









##############################################################################3
##############################################################################

  

#files=['grb_130427324_bin02_t0.root']
#anglesFileName='/home/maldera/FERMI/code/plotAcdRates/data/grbs/GRB_130427324/faces_angle_grb130427324.root'
#start=0
#stop=15
#t0=4
#tf=12


#files=['grb_16062594_bin02_t0.root']
#files=['grb_171010792_bin02_t0.root']

#files=['grb_180720598_bin02_t0.root']
#anglesFileName='/home/maldera/FERMI/code/plotAcdRates/data/grbs/GRB_180720598/faces_angle_grb180720598.root'
#start=-1
#stop=1
#t0=-0.2
#tf=0.1



#files=['sgr_bin1_t0.root']
files=['sgr_bin1_t0_ecut0.04.root']
anglesFileName='/home/maldera/FERMI/code/plotAcdRates/data/SGR_1935+2154/faces_angle_sgr.root'
base_dir='/home/maldera/FERMI/code/plotAcdRates/data/SGR_1935+2154/recon/sgr/'
start=-8
stop=60
t0=9
tf=20




#files=['grb_160821857_bin02_t0.root'] #???





#base_dir='/home/maldera/FERMI/code/plotAcdRates/'
filename=base_dir+files[0]


eval_time=t0+(tf-t0)/2.


f=ROOT.TFile(filename,'read')
histos=get_histos(f)


# get angles:

f_angles=ROOT.TFile.Open(anglesFileName)

g_angleZ=f_angles.Get('Z_angle')
g_angleXpos=f_angles.Get('Xpos_angle')
g_angleXneg=f_angles.Get('Xneg_angle')
g_angleYpos=f_angles.Get('Ypos_angle')
g_angleYneg=f_angles.Get('Yneg_angle')



angleZ=g_angleZ.Eval(eval_time)
angleXpos=g_angleXpos.Eval(eval_time)
angleXneg=g_angleXneg.Eval(eval_time)
angleYpos=g_angleYpos.Eval(eval_time)
angleYneg=g_angleYneg.Eval(eval_time)


######### 

#ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetTitleFontSize(0.1);

bkg_graph=[0.]*10
bkg_func=[0.]*10
integral=[0.]*10


# new way: bkg from fit 
c2=ROOT.TCanvas('c2',"",0)
c2.Divide(1,5)
for j in range (5,10):

   c2.cd(j-4)
   histos[j].GetXaxis().SetRangeUser(start,stop)
   histos[j].Draw("perr")

   bkg_graph[j],bkg_func[j]=fit_bkg(histos[j],start,stop,t0,tf)
   #bkg_graph[j]=g
   #bkg_func[j]=func
   
   bkg_graph[j].Draw("*")
   bkg_func[j].Draw("samel")

   integral[j]=  integrate_and_subtractBkg_v2(histos[j], bkg_func[j],   t0,tf)

   print(histos[j].GetTitle()," signal=",integral[j] )
  
   
   
   
""" 
# OLD WAY: bkg from histo
c3=ROOT.TCanvas('c3',"",0)
c3.Divide(2,3)
h_yDistr=[0.]*10
meanPed=[0.]*10
integral=[0.]*10
for j in range (5,10):
   c3.cd(j-4)
   #histos[j].GetXaxis().SetRangeUser(start,stop)
   h_yDistr[j]=yDistr(histos[j],start,stop,t0,tf)
   meanPed[j]=h_yDistr[j].GetMean()
   h_yDistr[j].Draw("hist")
   print ("mean ped =",meanPed[j])
  #integrate and subtract ped   OLD
   integral[j]=  integrate_and_subtractBkg(histos[j], meanPed[j],   t0,tf)
"""





   

sZ= integral[5]/np.cos(angleZ*ROOT.TMath.DegToRad() )
s_xPos= integral[6]
s_xNeg= integral[7]
s_yPos= integral[8]
s_yNeg= integral[9]




# OKKIO, ho scambito gli angoli!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
print ("\n \n s_z=",integral[5]," angle=",angleZ, " s_corr= ",sZ )
print ("s_xPos=",s_xPos," angle=",angleXpos, " s_corr= ",s_xPos/  np.cos(angleXpos*ROOT.TMath.DegToRad() ) )
print ("s_xNeg=",s_xNeg," angle=",angleXneg , " s_corr= ",s_xNeg/  np.cos(angleXneg*ROOT.TMath.DegToRad() )  )
print ("s_yPos=",s_yPos," angle=",angleYpos , " s_corr= ",s_yPos/  np.cos(angleYpos*ROOT.TMath.DegToRad() ) )
print ("s_yNeg=",s_yNeg," angle=",angleYneg, " s_corr= ",s_yNeg/  np.cos(angleYneg*ROOT.TMath.DegToRad() ) ,'\n \n' )





sX=s_xPos/np.cos(angleXpos*ROOT.TMath.DegToRad() )
if s_xPos<s_xNeg:
    sX=s_xNeg/np.cos(angleXneg*ROOT.TMath.DegToRad() )

    
sY=s_yPos/np.cos(angleYpos*ROOT.TMath.DegToRad() )
if s_yPos<s_yNeg:
    sY=s_yNeg/np.cos(angleYneg*ROOT.TMath.DegToRad() )



print("Sz corr= ",sZ)
print("Sx corr= ",sX)
print("Sy corr= ",sY)

    
