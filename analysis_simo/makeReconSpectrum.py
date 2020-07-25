from __future__ import print_function, division
import ROOT
import numpy as np
import datetime
import time as tt

dict_tileSize={}







def createTChain(nomeFileList, treeName):

   chain=ROOT.TChain(treeName)  
     
   f=open(nomeFileList)
   
   for line in f:
        rootFile=line[0:-1]
        print("Tchain- adding file: ",rootFile)
        chain.Add(rootFile)


   return chain     




def do_work( outFileName ,listFile):
   


    outRootFile=ROOT.TFile(outFileName, 'recreate')

    myTree=createTChain(listFile,'myTree')        

#    time0,timeLast= get_time0_last(myTree)
#    n_bins=int( (timeLast-time0)/binning ) 
#    identityFunc=ROOT.TF1("identityFunc","1",time0-t0,timeLast-t0)

    histSpectrumAll=ROOT.TH1F('histSpectrumAll',"spectrumAllTiles",25,0.01,0.1)

   # myTree.Draw('acdE_acdtile',cut,"goff")
    
    histSpectrum_dict={}

    hEpeak=ROOT.TH1F('hEpeak',"lowE peak",50,0.01,0.1)
    
    for tileID in range(0,89):

         #dict_tileSize[tileID]=1. #!!!!!!!!!!!!!!!!!!!!!!!! <<<<<<<<<<<<<<<<<<<<<<<==============
         
         
         hist_name='spectrum_tile'+str(tileID)
         histSpectrum_dict[tileID]=ROOT.TH1F(hist_name,hist_name,25,0.01,0.1)

         string='(acdE_acdtile['+str(tileID)+']) >> '+hist_name
         cut="acdE_acdtile["+str(tileID)+"] >0"
         print("cut",cut)
         myTree.Draw(string,cut,"goff")
         histSpectrum_dict[tileID].GetXaxis().SetTitle('E [MeV]??') 


         peakE= histSpectrum_dict[tileID].GetBinCenter( histSpectrum_dict[tileID].GetMaximumBin() )
         hEpeak.Fill(peakE)
         
         
         histSpectrumAll.Add( histSpectrum_dict[tileID])
         
         outRootFile.cd()
         histSpectrum_dict[tileID].Write()
         
     






    hEpeak.Write()     
    histSpectrumAll.Write()



    outRootFile.Close()



    


if __name__ == '__main__':
    import argparse
    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=formatter)

    parser.add_argument('--listFile', type=str,  help='txt file with list of root files ')
    parser.add_argument('--outfile', type=str,  help='outrootfile ', default='out.root')

    args = parser.parse_args()

    
    outFileName=args.outfile
    listFile=args.listFile
   

    print("going to run with:   ")
    print("outFileName= ",outFileName)
    print("listFile= ",listFile)
       
    do_work(outFileName ,listFile)
    


    print("... done, bye bye")
