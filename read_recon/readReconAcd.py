# uses mertiItils (by LucaB.) to read recon and merit file and creates a root TTree
# with time and energy in each ACD tiles of every event in the interval [first, last] 
# path to recon, merit, outputfile  and the first and last event are passed as argumetns from command line:
#
#OKKIO: this script causes a memory leak... used ram increases with time!!! For this reason split the runs in bunches of ~50k events (~10% memory usage at the end)
#PS: di solito viene  lanciato da lanciaReadRecon.py



from __future__ import print_function, division

import ROOT
import sys
import os
import numpy as np
import gc

from multiprocessing import Process, Queue

sys.path.append('/u/gl/maldera/meritUtils/python/')

from pReconInterface  import *
from ACD_MAP_DICT     import *







if __name__ == '__main__':

    import argparse
    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=formatter)

    parser.add_argument('--reconFile', required=True,  type=str,  help='the input recon file')

    parser.add_argument('--meritFile', type=str,  help='the input merit file' , required=True)

    parser.add_argument('--outRootFile', type=str,  help='the output root file', required=True)



    parser.add_argument('--first', type=int,  help='first event', required=True)
    parser.add_argument('--last', type=int,  help='last event', required=True)
    

    args = parser.parse_args()


    ReconFilePath=args.reconFile  
    meritFilePath=args.meritFile 


    r = pReconInterface(ReconFilePath,meritFilePath)


    numEvents = r.getEntries()


   ################
   # Set up out file
   # -time
   # -acd_tile_energy[]
   # -acd_hit_tile[]
    time=np.array([0],'d')

    #acdHit_acdtile=np.array([0]*89,'d')
    acdE_acdtile=np.array([0]*89,'d')


    outFile_name=args.outRootFile


    outRootFile=ROOT.TFile(outFile_name,"recreate")

    mytree=ROOT.TTree('myTree','myTree')
    mytree.Branch('time',time,'time/d')
   # mytree.Branch('acdHit_acdtile',acdHit_acdtile,'acdHit_acdtile[89]/d')
    mytree.Branch('acdE_acdtile',acdE_acdtile,'acdE_acdtile[89]/d')


    first=args.first
    last=args.last

        

    for entry  in range (first, last):

    
    
        r.getEntry(entry)
        
        # same cut as in DQM -> select phisical envets (no ROI, no periodic, no exteral no sollecited?)
        gemSummary=r.getMeritValue('GltGemSummary')
        if (int(gemSummary)&30)==0:
            continue


        acdRecon = r.getAcdRecon()
   
        hitCol=acdRecon.getHitCol()
        nAcdHits=hitCol.GetEntriesFast()
        #print("collectionEntries=", nAcdHits)
    
        

        time[0]=r.getMeritValue('EvtElapsedTime')
        
        #azzera vettori acdHit e acdE
        #acdHit_acdtile=acdHit_acdtile*0.
        acdE_acdtile=acdE_acdtile*0.
    
    

    
        for i in range(nAcdHits):
            hit = hitCol[i]
            tileNumber = hit.getId().getId()
        
 
            tileId     = ACD_MAP_DICT[tileNumber]
            if tileId>88:  # escludo ribbons!
                continue

            #slow signal (pha)
            #Veto threshold is 0.45MIPs, hit threshold is 0.01 MIPs
            #pulseHeight = 0.5*(hit.getMips(0) + hit.getMips(1))
            #pulseHeight2 = hit.getMips()
        
            tileEnergy= hit.getTileEnergy()
        
        
            #acdHit_acdtile[tileId]=1.
            acdE_acdtile[tileId]=tileEnergy

            del hit
            #fast signal
            #triggerVetoBit_0 = ((hit.getFlags(0) >> 1) & 0x1)
            #triggerVetoBit_1 = ((hit.getFlags(1) >> 1) & 0x1)
        
        ################## end loop hits    


        outRootFile.cd() 
        mytree.Fill() 

        if entry%1000 ==0:
            print("event=",entry)
  

            #    del hitCol
            #    del acdRecon
    

    outRootFile.cd()
    mytree.Write()
    outRootFile.Close()



    
