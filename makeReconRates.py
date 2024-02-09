# legge lista di file root generati da lanciaReadRecon.py e
# produce un file root con:
# istogrammi dei rates per ogni tiles, e mediati sulle 5 facce
# istogrammi dei rates  normalizzati  per ogni tiles, e mediati sulle 5 facce

# usage:
# python makeReconRates.py #  --listFile LISTFILE (txt file with list of root files)  --binning BINNING (binning in seconds)  --outfile OUTFILE     (outrootfile, default: out.root) --acdSizesFile ACDSIZESFILE  (files with acd tiles area, default=ACD_tiles_size2.txt),  --t0 T0  (t0, default: 0.0)

# esempio:
#python ../ACDTransients/makeReconRates.py --listFile fileList --binning 1 --outfile out.root --t0 0 --acdSizesFile ../ACDTransients/ACD_tiles_size2.txt 

# NB, la lista deve essere ordinata! (se  no la funzione get_time0_last non funziona... sarebbe da cambiare )
# es: ls outAcdReconRates_*_?_*.root >fileList
#     ls outAcdReconRates_*_??_*.root >>fileList


from __future__ import print_function, division
import ROOT
import numpy as np
import datetime
import time as tt

from lib.rates_stuff import *

dict_tileSize={}



def get_time0_last(tree):

     # TODO: qua si assume che il tree sia ordinato (ossia la prima entry corrisponda al met minore e l'ultima a quella maggiore...)
     # bisognerebbe cercare max e min  indipendentemente dall'ordine... 
     
     nEntries=tree.GetEntries()
     tree.GetEntry(0)
     time0=tree.time

     tree.GetEntry(nEntries-1)
     timeLast=tree.time

     return time0,timeLast





def mediaSides(hist_dict, identityFunc ):
     
     #top:
     hist_top=hist_dict[0].Clone()
     hist_top.SetTitle("top")
     hist_top.SetName("hist_top")
    
     hist_top.Reset()
     #hist_top.Sumw2()

     n=0.
     sum_area=0.
     for tileId in range (64, 88+1):
          hist_top.Add(hist_dict[tileId])
          n=n+1.
          sum_area=sum_area+1./dict_tileSize[tileId]
          
     hist_top.Divide(identityFunc, n  )        
     #hist_top.Divide(identityFunc, sum_area  )        


     #X+:
     hist_Xpos=hist_dict[0].Clone()
     hist_Xpos.SetTitle("Xpos")
     hist_Xpos.SetName("hist_Xpos")
     hist_Xpos.Reset()
     #hist_top.Sumw2()
     n=0.
     sum_area=0.
     for tileId in range (48, 63+1):
          hist_Xpos.Add(hist_dict[tileId])
          n=n+1.
          sum_area=sum_area+1./dict_tileSize[tileId]
     hist_Xpos.Divide(identityFunc, n  )
     #hist_Xpos.Divide(identityFunc, sum_area  )
    

     #Xneg
     #32 and tileId <= 47:
     hist_Xneg=hist_dict[0].Clone()
     hist_Xneg.SetTitle("Xneg")
     hist_Xneg.SetName("hist_Xneg")
     hist_Xneg.Reset()
     #hist_top.Sumw2()
     n=0.
     sum_area=0.
     
     for tileId in range (32, 47+1):
          hist_Xneg.Add(hist_dict[tileId])
          n=n+1.
          sum_area=sum_area+1./dict_tileSize[tileId]

     hist_Xneg.Divide(identityFunc, n  )  
     #hist_Xneg.Divide(identityFunc,sum_area   )  
     

     #Y+:
     hist_Ypos=hist_dict[0].Clone()
     hist_Ypos.SetTitle("Ypos")
     hist_Ypos.SetName("hist_Ypos")
     hist_Ypos.Reset()
     #hist_top.Sumw2()
     n=0.
     sum_area=0.
     #16 and tileId <=31
     for tileId in range (16, 31+1):
          hist_Ypos.Add(hist_dict[tileId])
          n=n+1.
          sum_area=sum_area+1./dict_tileSize[tileId]

     hist_Ypos.Divide(identityFunc, n  )
     #hist_Ypos.Divide(identityFunc, sum_area  )
    

     #Yneg
     hist_Yneg=hist_dict[0].Clone()
     hist_Yneg.SetTitle("Yneg")
     hist_Yneg.SetName("hist_Yneg")
     hist_Yneg.Reset()

     n=0.
     sum_area=0.
     #>= 0 and tileId<=15:
     for tileId in range (0, 15+1):
          hist_Yneg.Add(hist_dict[tileId])
          n=n+1.
          sum_area=sum_area+1./dict_tileSize[tileId]
     hist_Yneg.Divide(identityFunc, n  )  
     #hist_Yneg.Divide(identityFunc, sum_area  )  

     

     
     return hist_top, hist_Xpos, hist_Xneg, hist_Ypos, hist_Yneg
     

          







def do_work(fileSizes, outFileName ,listFile, binning, t0,Ecut):
   
    #dict_tileSize=fill_dictSizes(fileSizes)

    outRootFile=ROOT.TFile(outFileName, 'recreate')

    myTree=createTChain(listFile,'myTree')        

    time0,timeLast= get_time0_last(myTree)
    n_bins=int( (timeLast-time0)/binning ) 




    identityFunc=ROOT.TF1("identityFunc","1",time0-t0,timeLast-t0)


    # fill hist di tutti i triggers... serve per avere i rates normalizzati (i.e. acd occupancy)
    hist_triggers=ROOT.TH1F("hist_triggers","hist_triggers",n_bins,time0-t0,timeLast-t0)
    myString='time - '+str(t0)+'>> hist_triggers'
    myTree.Draw(myString,"","goff")
    hist_triggers.Sumw2()
    hist_triggers.Divide(identityFunc,binning)  # divido per larghezza bin => rate in Hz
     
    hist_dict={}
    histNorm_dict={}

    for tileID in range(0,89):

            
         hist_name='rate_tile'+str(tileID)
         hist_dict[tileID]=ROOT.TH1F(hist_name,hist_name,n_bins,time0-t0,timeLast-t0)

         string='time - '+str(t0)+' >> '+hist_name
         #cut="acdE_acdtile["+str(tileID)+"] >"+str(Ecut)  
         #cut="(acdE_acdtile["+str(tileID)+"])*(acdE_acdtile["+str(tileID)+"] >"+str(Ecut)+")"  
         #cut="(acdE_acdtile["+str(tileID)+"])*(acdE_acdtile["+str(tileID)+"] <0.1)"  # peso per energia con cut su Emax
       #  cut="(acdE_acdtile["+str(tileID)+"]>0) && (acdE_acdtile["+str(tileID)+"] <0.1)"  # cut Emin e  su Emax
         cut="(acdE_acdtile["+str(tileID)+"]>0.03) && (acdE_acdtile["+str(tileID)+"] <0.1)"  # cut Emin e  su Emax


         
        
         print("cut",cut)
         myTree.Draw(string,cut,"goff")
         #myTree.Project(string,cut)
         
         hist_dict[tileID].Sumw2()
         hist_dict[tileID].Divide(identityFunc,binning*dict_tileSize[tileID]) 
         hist_dict[tileID].GetXaxis().SetTitle('met-'+str(t0)) 
         
         
         histNorm_dict[tileID]=hist_dict[tileID].Clone()
         hist_nameNorm='NORMrate_tile'+str(tileID)
         histNorm_dict[tileID].SetName(hist_nameNorm)
         histNorm_dict[tileID].SetTitle(hist_nameNorm)
         histNorm_dict[tileID].GetXaxis().SetTitle('met-'+str(t0)) 
        
         
         histNorm_dict[tileID].Divide(hist_triggers)

         outRootFile.cd()
         hist_dict[tileID].Write()
         histNorm_dict[tileID].Write()
     





    hist_top, hist_Xpos, hist_Xneg, hist_Ypos, hist_Yneg =mediaSides(hist_dict, identityFunc )
    histNorm_top, histNorm_Xpos, histNorm_Xneg, histNorm_Ypos, histNorm_Yneg =mediaSides(histNorm_dict, identityFunc )

    histNorm_top.SetNameTitle('histNorm_top','histNorm_top')
    histNorm_Xpos.SetNameTitle('histNorm_Xpos','histNorm_Xpos')
    histNorm_Xneg.SetNameTitle('histNorm_Xneg','histNorm_Xneg')
    histNorm_Ypos.SetNameTitle('histNorm_Ypos','histNorm_Ypos')
    histNorm_Yneg.SetNameTitle('histNorm_Yneg','histNorm_Yneg')






    hist_triggers.Write()

    hist_top.Write()
    hist_Xpos.Write()
    hist_Xneg.Write()
    hist_Ypos.Write()
    hist_Yneg.Write()


    histNorm_top.Write()
    histNorm_Xpos.Write()
    histNorm_Xneg.Write()
    histNorm_Ypos.Write()
    histNorm_Yneg.Write()


    outRootFile.Close()



    


if __name__ == '__main__':
    import argparse
    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=formatter)

    parser.add_argument('--listFile', type=str,  help='txt file with list of root files ')
    parser.add_argument('--binning', type=float,  help='binning in seconds' )
    parser.add_argument('--outfile', type=str,  help='outrootfile ', default='out.root')
    parser.add_argument('--acdSizesFile', type=str, default='ACD_tiles_size2.txt',              help = 'file with acd tiles area')
    parser.add_argument('--t0', type=float, default=0.,              help = ' t0  ')
    parser.add_argument('--Ecut', type=float, default=0.,              help = 'min Energy required to count a hit  (default=0)')

    args = parser.parse_args()

    fileSizes=args.acdSizesFile
    outFileName=args.outfile
    listFile=args.listFile
    binning=args.binning
    t0=args.t0
    Ecut=args.Ecut

    print("going to run with:   ")
    print("outFileName= ",outFileName)
    print("listFile= ",listFile)
    print("binning= ",binning)
   
    print("fileSizes= ",fileSizes)
    print ('t0=',t0)
    
    dict_tileSize=fill_dictSizes(fileSizes)
    do_work(fileSizes, outFileName ,listFile, binning,t0,Ecut)
    


    print("... done, bye bye")
