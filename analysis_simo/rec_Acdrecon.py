
from __future__ import print_function, division
import ROOT
import numpy as np
import datetime
import time as tt

import array

from scipy.stats import norm
import scipy.interpolate

from astropy.time import Time
import astropy.coordinates

import compute_anglesFT2 


hist_names=['hist_top','hist_Xpos','hist_Xneg','hist_Ypos','hist_Yneg',  'histNorm_top',  'histNorm_Xpos', 'histNorm_Xneg','histNorm_Ypos', 'histNorm_Yneg']

met2Gps_offest=662342413.0
t_flare=0      
t0run=0  


def get_histos(f):


    print("Get histos start...")
    #print ("reading file: ",f)
    
    histos=[]
    #f=ROOT.TFile(filename,'read')
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


def rebin_histos(histos,n_rebin):
    """
    """
    histosRebinned=[ROOT.TH1F]*len(histos) 
    
    for i in range(0,len(hist_names)):
       histosRebinned[i]=histos[i].Rebin(n_rebin, histos[i].GetName()+'_rebin'+str(n_rebin) ) 
   
    return histosRebinned


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


def fit_bkg(hist,start,stop,x0,xf, ftype='pol3'):

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

    #bkg_func=ROOT.TF1("bkg_func","[0]+[1]*x+[2]*x*x+[3]*x*x*x",start, stop)
    bkg_func=ROOT.TF1("bkg_func",ftype,start, stop)

           
    #g.Fit('bkg_func',"MERW")
    g.Fit('bkg_func',"RW")

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

def integrate_and_subtractBkg_v2(hist, bkg_func, t0,tf,start,stop):   # bkg_func  is a ROOT.TF1

      n_bins= hist.GetNbinsX()
      integral=0.

      h_res=ROOT.TH1F("h_res","",2000, -20,20)
      h_signal=ROOT.TH1F("h_signal","",200, -2e-3,2e-3)
      
      
      for i in range (1,n_bins):

          x=hist.GetBinCenter(i)
          if (x>=t0 and x<=tf):
              
              y=hist.GetBinContent(i) -bkg_func.Eval(x)
              #print("Integrating... x=",x," bin = ",hist.GetBinContent(i)," bkg =",bkg_func.Eval(x))
              integral+=y
              h_signal.Fill(y)

          #if (x>tf):
          #    break
          elif( x>=start and x<stop ) :
          #else:    
              y=hist.GetBinContent(i) -bkg_func.Eval(x)
              h_res.Fill(y)
          
      return integral, h_res,h_signal        



def significance_trending(hist, hist_res, f_bkg,start,stop, sigma_limit=3):

     rms=hist_res.GetRMS()
     n_bins= hist.GetNbinsX()

     x_s=[]
     y_s=[]

     signal_starts=[]
     signal_stops=[]
     sigUp=0
     max_sigma=0
     x_sigmaMax=0
     for i in range (1,n_bins):
         x=hist.GetBinCenter(i)
         #if( x>=start and x<stop ) : 
         x=hist.GetBinCenter(i)
         s=(hist.GetBinContent(i)-f_bkg.Eval(x))/rms
         #if s>max_sigma:
         #    max_sigma=s
          #   x_sigmaMax=x
             
         if( x>=start and x<stop ) : 
             x_s.append(x)
             y_s.append(s)

             if s>max_sigma:  # cerco max sigma SOLO tra start e stop
                 max_sigma=s
                 x_sigmaMax=x
             

         if s>=sigma_limit and sigUp==0 :
            sigUp=1
            signal_starts.append(x)
         if s<sigma_limit and sigUp==1:
             sigUp=0
             signal_stops.append(hist.GetBinCenter(i-1) ) #l'ultimo bin e' il precedente, prendo il bin i-1
            

     if (sigUp==1):    # non trova mai la fine dell'ultimo intervallo... lo setto a mano all'ultimo bin
           signal_stops.append(hist.GetBinCenter(n_bins-1) )

     #print("signal start =", signal_starts, "  stops =",signal_stops)


     g=ROOT.TGraph(len(x_s),array.array('d', x_s),array.array('d',y_s))

     g.SetMarkerStyle(20)
     g.SetMarkerColor(4)
     g.GetXaxis().SetLabelSize(0.09)
     g.GetYaxis().SetLabelSize(0.05)
     
     g.GetYaxis().SetTitle("#sigma")
     g.GetYaxis().SetTitleSize(0.25)
     g.GetYaxis().SetTitleOffset(0.1)
       
     
     
     return g,  signal_starts, signal_stops,max_sigma, x_sigmaMax


#########
# sommo e riscalo...

def get_ymean(h):

    mean=0.
    for i in range (1,h.GetNbinsX()): 
        mean=mean+h.GetBinContent(i)

    mean=mean/float(h.GetNbinsX())    
    return mean


    
def scale_and_sum(histos):

    meanY=[0.]*10
    print(histos[0])

    hSum=histos[0].Clone()
    hSum.Reset()
    hSum.SetName('hsum')
    hSum.SetTitle('hsum')
    
    for i in range(5,10):
    #for i in range(5,6):
       
         meanY[i]=get_ymean(histos[i])
         print("i = ",i," mean =",meanY[i])
      
         hSum.Add(histos[i],1./meanY[i])


    return hSum 
         
  
              
# cerca intervallo:
def find_time_interval(histos, rebin, outRootFile,draw=0):

     histosRebin= rebin_histos(histos, rebin )
     hsum=scale_and_sum(histosRebin)
     bin_width=histosRebin[0].GetBinWidth(1)
     nbins=hsum.GetNbinsX()

     
     start=hsum.GetBinCenter(1)
     stop=hsum.GetBinCenter(nbins-1)

     #t0=start
     #tf=start
     #run  _521262842
     #t0=120 # RICERCA AUTOMATICA NON VA........  !!!!!! OKKIO <<<<==============================================================================
     #tf=160

     #run 526227285
     #t0=4480 # RICERCA AUTOMATICA NON VA........  !!!!!! OKKIO <<<<==============================================================================
     #tf=4540
     t0=4450
     tf=4650

     
    #run  526324173
    # t0=270 # RICERCA AUTOMATICA NON VA........  !!!!!! OKKIO <<<<==============================================================================
    # tf=310

     #run  526324173
    # t0=4080 # RICERCA AUTOMATICA NON VA........  !!!!!! OKKIO <<<<==============================================================================
     #tf=4150

     
          
     print("START = ",start, " STOP=",stop)
     

     # loop binnaggio... 

     for i in range (0,2): # iterazione fit e ricerca sengnale... 
         fitfuncform='pol3'
         sigmaCut=2
         if i==0:
            fitfuncform='pol1'
            sigmaCut=3
            #sigmaCut=norm.ppf(1-0.00135/float(nbins))
            #sigmaCut=norm.ppf(1-0.0135/float(nbins))
           
            print ("rebin=",rebin,"  nBins= ",nbins,"  sigmaCut=", sigmaCut)

            
            
         bkg_graphSum,bkg_funcSum=fit_bkg(hsum,start,stop,t0,tf,fitfuncform)
         integralSum, h_resSum, h_signalSum=  integrate_and_subtractBkg_v2(hsum  , bkg_funcSum,   t0,tf,start,stop)
         g_sigSum, s_startsSum , s_stopsSum, max_sigma, x_max =significance_trending(hsum , h_resSum, bkg_funcSum,start,stop, sigmaCut)
       
         print ('jj= ',jj,'  Rebin = ',n_rebin[jj],'  i= ',i, " len starts  =", len(s_startsSum), '  max sigificance=',max_sigma, "x_max=",x_max)
        
         # cerco intervallo che contine sigma_max:
         indice_max=0
         if  len(s_startsSum)==0:
                print("find_time_intervall: nessun intervallo trovato!")
                
         else:       
             for k in range (0, len(s_startsSum)):
            
                 if x_max>= s_startsSum[k] and  x_max<= s_stopsSum[k]:
                     indice_max=k
                     print ("k trovato = ",k, " start[k] =",s_startsSum[k], " stop[k]=",s_stopsSum[k], " x_max=",x_max )
                     break

              
              # RICERCA AUTOMATICA NON VA........  !!!!!! OKKIO commento ricerca adattiva <<<<==============================================================================
             #t0=s_startsSum[indice_max]-0.1
             #tf=s_stopsSum[indice_max]+0.1 
             
             
    
             
             start=max(t0-800,hsum.GetBinCenter(1))
             stop=tf+800


             print("nuovo t0=",t0,"  nuovo tf =",tf, " nuovo start=",start," nuovo stop=",stop)
        

        #Draw... 
         if draw==1:
             cTest2=ROOT.TCanvas('cTest2_'+str(n_rebin[jj] )+"_"+str(i),"",0)
             cTest2.Divide(1,3)
             cTest2.cd(1)
             h_resSum.Draw()
             cTest2.cd(2)
             hsum.Draw()
             bkg_graphSum.Draw("p")
             bkg_funcSum.Draw("samel")
             # h_resSum.Draw()
             cTest2.cd(3)
             g_sigSum.GetYaxis().SetRangeUser(-5,max_sigma+2)
             g_sigSum.Draw("ap")

             if  len(s_startsSum)>0:
                 l1=ROOT.TLine(s_startsSum[indice_max]-bin_width/2.,-5,s_startsSum[indice_max]-bin_width/2.,max_sigma+2)
                 l2=ROOT.TLine(s_stopsSum[indice_max]+bin_width/2.,-5,s_stopsSum[indice_max]+bin_width/2.,max_sigma+2)
                 l1.SetLineColor(2)
                 l2.SetLineColor(2)
                 l1.Draw("samel")
                 l2.Draw("samel")


             cTest2.Draw()
           #  a=raw_input("key [+ enter]  to continue... ")
             outRootFile.cd()
             cTest2.Write()
             
             
       
              
     return t0,tf,start,stop, max_sigma, x_max

           
 
 
#####################################################3
#   localization.... 
##########################################################
def test_localization(dict_signals, ft2_file_list,sky_binning=1., ts_type='std' ):
   import math

   print ('ts_type=',ts_type)
   
   #t_flare=300
   #t0run=526324173
    
   signals=list(dict_signals.keys()) #!!!!!!! trasformi in lista per p3... 
   #signals.sort()
   #signals.reverse()
   print ("signal sorted=",signals) 

   # scelgo top + x e y  con segnale maggiore
   dict_signalsReversed={}
   for i in range (0, len(signals)):
       dict_signalsReversed[ dict_signals[signals[i] ] ] =signals[i]
   
   print ("dict_signalReversed=",dict_signalsReversed) 

   S3=[0.]*3 
   S3[0]=dict_signalsReversed['top']
   S3[1]=max(dict_signalsReversed['Xpos'], dict_signalsReversed['Xneg'])
   S3[2]=max(dict_signalsReversed['Ypos'], dict_signalsReversed['Yneg'])
   
   
   # funzione per predere questi valori dell'ft2
   #inFiles=['r0521262842_ft2.fit']
   timeAll,z_raAll,z_decAll, x_raAll,x_decAll= compute_anglesFT2.read_FT2s(ft2_file_list)  # OKKIO, infiles e' una lista!!!

   print ("len time=",len(timeAll), "  len xra=",len(x_raAll)  )
   
   #loop dulle coppie ra, dec
   timeX=t_flare+t0run
  
  
   minTS=1000000000000.
   best_ra=1e6
   best_dec=1e6
   deg_step=sky_binning
   h_ts=ROOT.TH2F("h_ts","",int(360./deg_step),0,360, int(180./deg_step) ,-90,90)

   for dec_srg in range (-90,90, int(deg_step)) :
       for ra_srg in range (0,360,int(deg_step)):

            cosZ,cosXp,cosXn, cosYp,cosYn = compute_anglesFT2.computeAngles(ra_srg,dec_srg, z_raAll ,z_decAll, x_raAll,x_decAll)
         
            CosZ=ROOT.TGraph(len(timeAll),timeAll,cosZ ).Eval(timeX)
            #fCosZ=scipy.interpolate.interp1d(timeAll, cosZ)(timeX)  # identico all'Eval del TGraph
            CosXp=ROOT.TGraph(len(timeAll),timeAll,cosXp ).Eval(timeX)
            CosXn=ROOT.TGraph(len(timeAll),timeAll,cosXn).Eval(timeX)
            CosYp=ROOT.TGraph(len(timeAll),timeAll,cosYp ).Eval(timeX)
            CosYn=ROOT.TGraph(len(timeAll),timeAll,cosYn).Eval(timeX)

            dict_cos={"top":CosZ,"Xpos":CosXp,"Xneg":CosXn,"Ypos":CosYp,"Yneg":CosYn}


            #segnali norm per coseno angolo:
            sCorr=[0.,0.,0.,0.,0.]
            cosAll=[0.,0.,0.,0.,0.]
            neg_cos=0
            newTS=0
            for i in range (0,3):
           #for i in range (0,5):
               
                #s=signals[i]
                s=S3[i]
                label=dict_signals[s]
                cos=dict_cos[label]
                cosAll[i]=cos
                #sCorr[i]=s/abs(cos) # 4 minimi
                sCorr[i]=s/cos     # 2 minimi !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
                #if (cos<0 and label!='Xpos' ):
                if (cos<0 ):
                  neg_cos=1  
                  break 
                #print ("i = ",i," s=",s," labe=  ",label, " cos = ",cos  )
                
                 
                
             #escludo direzioni che danno uno dei coseni negativo (i.e. sono sulla faccia opposta)   
            if neg_cos==1:
                 continue


            sum2=sCorr[0]**2+sCorr[1]**2+sCorr[2]**2
            
            TS_new=((S3[0]-cosAll[0]*S3[2]/cosAll[2])**2)+((S3[1]-cosAll[1]*S3[2]/cosAll[2])**2) + ((S3[0]-cosAll[0]*S3[1]/cosAll[1])**2)+((S3[2]-cosAll[2]*S3[1]/cosAll[1])**2) +((S3[1]-cosAll[1]*S3[0]/cosAll[0])**2)+((S3[2]-cosAll[2]*S3[0]/cosAll[0])**2)

            TS_new_sum2=((S3[0]-cosAll[0]*S3[2]/cosAll[2])**2)+((S3[1]-cosAll[1]*S3[2]/cosAll[2])**2) + ((S3[0]-cosAll[0]*S3[1]/cosAll[1])**2)+((S3[2]-cosAll[2]*S3[1]/cosAll[1])**2) +((S3[1]-cosAll[1]*S3[0]/cosAll[0])**2)+((S3[2]-cosAll[2]*S3[0]/cosAll[0])**2)+sum2

         #new2
            #myTS=((S3[0]-cosAll[0]*S3[2]/cosAll[2])**2)+((S3[1]-cosAll[1]*S3[2]/cosAll[2])**2)
            #myTS= ((S3[0]-cosAll[0]*S3[1]/cosAll[1])**2)+((S3[2]-cosAll[2]*S3[1]/cosAll[1])**2)
           # myTS=((S3[1]-cosAll[1]*S3[0]/cosAll[0])**2)+((S3[2]-cosAll[2]*S3[0]/cosAll[0])**2)

        #NEW_v2
            TS_newV2=(sCorr[0]/sCorr[2]-sCorr[1]/sCorr[2])**2 + (sCorr[1]/sCorr[0]-sCorr[2]/sCorr[0])**2 +  (sCorr[0]/sCorr[1]-sCorr[2]/sCorr[1])**2

            
            #STD   
            TS_std=(sCorr[0]-sCorr[1])**2 +(sCorr[1]-sCorr[2])**2+ (sCorr[0]-sCorr[2])**2


           #myTS=(sCorr[0]-sCorr[1])**2 +(sCorr[0]-sCorr[2])**2+ (sCorr[0]-sCorr[3])**2+(sCorr[0]-sCorr[4])**2+(sCorr[1]-sCorr[2])**2+ (sCorr[1]-sCorr[3])**2+(sCorr[1]-sCorr[4])**2+(sCorr[2]-sCorr[3])**2+(sCorr[2]-sCorr[4])**2++(sCorr[3]-sCorr[4])**2
            
            
            
            #ALL
            TS_all=(sCorr[0]-sCorr[1])**2 +(sCorr[0]-sCorr[2])**2+ (sCorr[1]-sCorr[2])**2+sCorr[0]**2+sCorr[1]**2+sCorr[2]**2

            #ALL2
           #myTS=(sCorr[0]-sCorr[1])**2 +(sCorr[0]-sCorr[2])**2+ (sCorr[1]-sCorr[2])**2+sCorr[0]+sCorr[1]+sCorr[2]
           
            #sum Si2


            #myTS=sum2
            #myTS=TS_std
            #myTS=TS_all
           # myTS=TS_new_sum2
            # myTS=TS_newV2
           
            #myTS=TS_std * math.log10(sum2)
            myTS=-1000.
            
            if ts_type=='all':
                myTS=TS_all
                
            if ts_type=='std':
                myTS=TS_std
                
           
            h_ts.Fill(ra_srg,dec_srg,myTS)

          
        

            if myTS<minTS:
                minTS=myTS
                best_ra=ra_srg
                best_dec=dec_srg
                print("Nuovo_minimo: ",myTS," --->>>> ra = ",ra_srg, " dec = ",dec_srg, " sum2=",sum2, " TS_std=",TS_std, " TS_new=",TS_new, " TSnew*sqrt(sum2)",TS_new*sum2**0.5 )
        

   return best_ra,best_dec,h_ts    
            
            

def correction_coeff(bkg_func, t0,tf ):

    k=[1.]*10
    ref=bkg_func[5].Integral(t0,tf)/(tf-t0)

    for i in range(5,10):
        bkg_medio=bkg_func[i].Integral(t0,tf)/(tf-t0)
        k[i]=bkg_medio/ref

        print("i=",i," bkg_medio=",bkg_medio, " k[i]=",k[i]   )

    return k    
            
      


##############################################################################3
##############################################################################

if __name__ == '__main__':
    import argparse
    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=formatter)

    parser.add_argument('-in','--inFilesList', nargs='+' , type=str,  help='list of root file with rate histograms ', required=True)
    parser.add_argument('--base_dir', type=str,  help='common folder', )
    parser.add_argument('-ft2','--ft2List', nargs='+', type=str,  help=' list of ft2 files',required=True)
    parser.add_argument('-o','--out', type=str,  help='out root file name ',required=True)
    parser.add_argument('-t','--tflare', type=int,  help=' flare time ')
    parser.add_argument('-t0','--t0run', type=int,  help=' t0run ')
    parser.add_argument('-sb','--sky_binning', type=float,  help=' sky_binning')

    parser.add_argument('-k','--use_kCorr',action="store_true",  help='use k corrections')
    parser.add_argument('-ts','--myTS', type=str,  help=' type of localization variable: all,std ')
  

    args = parser.parse_args()

    print("files=",args.inFilesList)
    print("files=",args.ft2List)
    print("files=",args.out)
     
    if (args.myTS !='all' and args.myTS!='std'):
        print ('invalid myTS: ',args.myTS, '... exit!!!!')
        exit()
     
    print("USE Kcorr=",args.use_kCorr)
        

    # PARAMETRI
    files=args.inFilesList
    #base_dir='/home/maldera/FERMI/code/plotAcdRates/data/sf/521262842/'
    base_dir=args.base_dir
    #ft2_file_list=['r0521262842_ft2.fit']
    ft2_file_list=args.ft2List
    
#    name_outRootFile='provaOut.root'
    name_outRootFile= base_dir+ args.out
    t_flare=args.tflare
    t0run=args.t0run
    
    #t_flare=130
    #t0run=521262842   #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
      
    
    outRootFile=ROOT.TFile(name_outRootFile,"recreate")
    

    # to do: gestire il caso con piu' files...
    filename=base_dir+'/'+files[0]
    print ("in root file=",filename)
    f=ROOT.TFile(filename,'read')
    histos=get_histos(f)

    #### STEP 1: find binning and time interval
    # Search signals:
    #n_rebin=[1,2,4,8,16,32,64,128,256,512]
    #n_rebin=[8,16,32,64,128,256,512]
    n_rebin=[128]  #<<<<<<<<<<<============================================================================================== OKKIO
    
   
    #n_rebin=[1,2,4,8,20,40,60,80,100,120,140,160,180,200,220,240,260,280,300,340,360]

    i_max=-1
    maxSigmaAll=-1

    for jj in range(0,len(n_rebin) ):
   
        t0,tf,start,stop, max_sigma, x_max=  find_time_interval(histos, n_rebin[jj],outRootFile, draw=1)

        print("jj= ",jj," rebin = ",n_rebin[jj]," max_sigma= ",max_sigma, "  x_max=  ",x_max)
        
        if max_sigma>maxSigmaAll:
            maxSigmaAll=max_sigma
            i_max=jj
            
    

    print ("====>>>> imax= ",i_max, " n rebins max =  ",n_rebin[i_max], '  max significance=',maxSigmaAll)    
    t0,tf,start,stop, max_sigma, x_max=  find_time_interval(histos, n_rebin[i_max], outRootFile, draw=1)
    histos= rebin_histos(histos, n_rebin[i_max] )


    eval_time=t0+(tf-t0)/2.
    t_flare=eval_time  # relativo al t0run    # OKKIO inconsitenza tra il valore passato come arg e la meta' dell'intervallo segnale....
    
    ######### 
    # STEP 2: fit bkg and conpute signals
    #####

       
    #ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetTitleFontSize(0.1);

    bkg_graph=[0.]*10
    bkg_func=[0.]*10
    integral=[0.]*10

    h_res=[ROOT.TH1F]*10
    h_signal=[ROOT.TH1F]*10
    g=[ROOT.TGraph]*10


    # new way: bkg from fit 
    c2=ROOT.TCanvas('c2',"",0)
    c2.Divide(1,5)
    # histos
    c3=ROOT.TCanvas('c3',"",0)
    c3.Divide(1,5)

    #significance vs time?
    c4=ROOT.TCanvas('c4',"",0)
    c4.Divide(1,5)

    for j in range (5,10):

        c2.cd(j-4)
        histos[j].GetXaxis().SetRangeUser(start,stop)
        histos[j].Draw("perr")

        bkg_graph[j],bkg_func[j]=fit_bkg(histos[j],start,stop,t0,tf,'pol3')
        
        bkg_graph[j].Draw("*")
        bkg_func[j].Draw("samel")

        integral[j],h_res[j], h_signal[j]=  integrate_and_subtractBkg_v2(histos[j], bkg_func[j],   t0,tf,start,stop)
        c3.cd(j-4)
        h_res[j].Draw("")
        h_signal[j].SetLineColor(2)
        h_signal[j].Draw("sames")
   
        #significance?
        g[j], s_starts,s_stops, max_sigma, x_max =significance_trending(histos[j], h_res[j], bkg_func[j],start,stop)
        c4.cd(j-4)
        g[j].Draw("ap")
   
   
    #get correction coeff:
    k_corr=correction_coeff(bkg_func, t0,tf )


    
    dict_signals={}
   
    for j in range (5,10):

        print(histos[j].GetTitle()[:]," signal uncorrected =",integral[j] )
      
        if args.use_kCorr==True:
            integral[j]=integral[j]/k_corr[j]  #!!!!!!!!!!!!!!!!!!!!!11 <<<<<<<<<<<<================ nuova correzione!!!!!!!  kCorr
            print("Using k Corrections!!!")
            
        print(histos[j].GetTitle()[:]," signal=",integral[j] )
        dict_signals[integral[j]]=histos[j].GetTitle()[9:]
   
    print ("dict_signals= " , dict_signals)    

    outRootFile.cd()
    c2.Write()
    c3.Write()
    c4.Write()
   # outRootFile.Close()
    
    ######
    #STEP3:  run localization
    #######
    
    best_ra,best_dec,h_ts    =test_localization(dict_signals,ft2_file_list,args.sky_binning, args.myTS )

    c5=ROOT.TCanvas('c5',"",0)
    h_ts.GetZaxis().SetRangeUser(h_ts.GetMinimum()/10.,h_ts.GetMaximum()/10. )
    h_ts.SetContour(1000)
    h_ts.Draw("colz2")

    marker=ROOT.TMarker(best_ra,best_dec,20)
    marker.SetMarkerColor(2)
    marker.SetMarkerSize(2)
    marker.Draw("")

    print("best_ra=",best_ra," best_dec= ",best_dec)


    #coords SGR XXX 
    src_dec=21.9
    src_ra=293.7
    solar_flare=True #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    if solar_flare==True:
        # sun position...
        t_flareGPS=met2Gps_offest+t0run+t_flare
        t=Time(t_flareGPS, format='gps', scale='utc')

        print("time_flare= ",t.iso)
        sun_coords=astropy.coordinates.get_sun(t)

        src_ra=sun_coords.ra.deg
        src_dec=sun_coords.dec.deg

        print ("sun_ra= ",src_ra, "sun_dec= ",src_dec)

    # Draw source position
    markerTrueSrc=ROOT.TMarker(src_ra,src_dec,34)
    markerTrueSrc.SetMarkerColor(6)
    markerTrueSrc.SetMarkerSize(3)
    markerTrueSrc.Draw("")

    sep_angle=np.arccos(compute_anglesFT2.cosAngle(src_ra*ROOT.TMath.DegToRad()  ,src_dec*ROOT.TMath.DegToRad() ,best_ra*ROOT.TMath.DegToRad() ,best_dec*ROOT.TMath.DegToRad()) )*ROOT.TMath.RadToDeg()

    print ("angular sep=",sep_angle)

    #pt = ROOT.TPaveText(0.8,0.2  ,0.9,0.5,"NCD");
    pt = ROOT.TPaveText(.6,.25,.85,.35,"NDC");
    pt.SetBorderSize(1);
    pt.SetFillColor(0);
    pt.SetTextFont(42);
    pt.SetTextSize(0.025);
    pt.SetAllWith("","Align",12)

    myText='best_ra='+str(best_ra)+'  best_dec=  '+str(best_dec)
    pt.AddText(myText)
    myText='src_ra='+str('%0.2f'%src_ra)+'  src_dec=  '+str('%0.2f'%src_dec)
    pt.AddText(myText)  
    myText='angular sep =  '+ str('%0.2f'%sep_angle)
    pt.AddText(myText)  

    pt.SetAllWith("","Align",12)
  
    
    pt.Draw();
   
    outRootFile.cd()
    c5.Write()
    outRootFile.Close()
    


    print ("OKKIO!!1 t0 e tf messi a mano!!!")
    print ("OKKIO!!1 nrebin fissato!!!!")
