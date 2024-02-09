from __future__ import print_function, division
import ROOT
import numpy as np
import datetime
import time as tt

from lib.rates_stuff import *

dict_tileSize={}






def mediaSides(hist_dict, identityFunc ):


     print("mediasides: ",dict_tileSize)
   
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
          
     #hist_top.Divide(identityFunc, n  )        
     hist_top.Divide(identityFunc, sum_area  )        


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
     #hist_Xpos.Divide(identityFunc, n  )
     hist_Xpos.Divide(identityFunc, sum_area  )
    

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

     #hist_Xneg.Divide(identityFunc, n  )  
     hist_Xneg.Divide(identityFunc,sum_area   )  
     

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

     #hist_Ypos.Divide(identityFunc, n  )
     hist_Ypos.Divide(identityFunc, sum_area  )
    

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
     #hist_Yneg.Divide(identityFunc, n  )  
     hist_Yneg.Divide(identityFunc, sum_area  )  

     

     
     return hist_top, hist_Xpos, hist_Xneg, hist_Ypos, hist_Yneg
     

          




def do_work( outFileName ,listFile,acdSizesFile ):
   
 #   dict_tileSize=fill_dictSizes(acdSizesFile)

    print("mediasides: ",dict_tileSize)
   
    
    outRootFile=ROOT.TFile(outFileName, 'recreate')
    myTree=createTChain(listFile,'myTree')        

    emin=0.01
    emax=10
    nbins=2500
    binning=(emax-emin)/float(nbins)
    
    histSpectrumAll=ROOT.TH1F('histSpectrumAll',"spectrumAllTiles",nbins,emin,emax)

    
    histSpectrum_dict={}

    hEpeak=ROOT.TH1F('hEpeak',"lowE peak",50,0.01,0.1)
    identityFunc=ROOT.TF1("identityFunc","1",emin-1,emax+1) 

    for tileID in range(0,89):

       
         
         
         hist_name='spectrum_tile'+str(tileID)
         histSpectrum_dict[tileID]=ROOT.TH1F(hist_name,hist_name,nbins,emin,emax)

         string='(acdE_acdtile['+str(tileID)+']) >> '+hist_name
         cut="acdE_acdtile["+str(tileID)+"] >0"
         print("cut",cut)
         myTree.Draw(string,cut,"goff")
         histSpectrum_dict[tileID].GetXaxis().SetTitle('E [MeV]??') 
         histSpectrum_dict[tileID].Divide(identityFunc,binning*dict_tileSize[tileID]) 


         peakE= histSpectrum_dict[tileID].GetBinCenter( histSpectrum_dict[tileID].GetMaximumBin() )
         hEpeak.Fill(peakE)
         
         
         histSpectrumAll.Add( histSpectrum_dict[tileID])
         
         outRootFile.cd()
         histSpectrum_dict[tileID].Write()
         
     






    hEpeak.Write()     
    histSpectrumAll.Write()


    #spettrim medi sides

    hist_top, hist_Xpos, hist_Xneg, hist_Ypos, hist_Yneg =mediaSides(histSpectrum_dict, identityFunc )
    
    hist_top.Write()
    hist_Xpos.Write()
    hist_Xneg.Write()
    hist_Ypos.Write()
    hist_Yneg.Write()

    outRootFile.Close()



    


if __name__ == '__main__':
    import argparse
    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=formatter)

    parser.add_argument('--listFile', type=str,  help='txt file with list of root files ')
    parser.add_argument('--outfile', type=str,  help='outrootfile ', default='out.root')
    parser.add_argument('--acdSizesFile', type=str, default='ACD_tiles_size2.txt',              help = 'file with acd tiles area')

    args = parser.parse_args()

    
    outFileName=args.outfile
    listFile=args.listFile
    acdSizesFile=args.acdSizesFile

    print("going to run with:   ")
    print("outFileName= ",outFileName)
    print("listFile= ",listFile)
    print("acdSizesFile= ",acdSizesFile)
    
    dict_tileSize=fill_dictSizes(acdSizesFile)
  
    do_work(outFileName ,listFile,acdSizesFile)
    


    print("... done, bye bye")
