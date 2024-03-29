# lancia readReconAcd.py per creare ROOT TTrees con met e energia di ogni tile
# per ogni evento.
# Poiche'readReconAcd.py ha un memory leak (che non sono riuscito ad eliminare in nessun modo) il run viene spezzettato
#e per ogni blocco di eventi viene lanciata una istanza diversa di readReconAcd.py
# con 70k eventi si arriva a ~il 10% della ram usata

# usage:
# python lanciaReadRecon.py  --reconFile RECONFILE  (the input recon file)  --meritFile MERITFILE   (the input merit file) 
#                      --outRootFile OUTROOTFILE  (the output root file (without extension!!))  --outDir OUTDIR  output dirctory (default: .)    --use_bsub 1 or 0 to use batch queue (default: 0)


# se l'opzione --bsub e' !=0, lancia i vari blocchi in parallelo con bsub

#PS:  source set_vars.sh  prima eseguire 


from __future__ import print_function, division

import ROOT
import os
import subprocess


def getNevents(meritFile):
    f=ROOT.TFile.Open(meritFile)
    MeritTuple=f.Get('MeritTuple')
    n=MeritTuple.GetEntries()
    f.Close()
    print ("getNevents: n",n)
    return n




def lancia_readRecon(meritFile, reconFile, outFile, first,last,use_bsub,outDir):
    """
    """
    print("use_bsub=",use_bsub)
    
    if use_bsub==0:
        cmd='python readReconAcd.py --reconFile '+reconFile+' --meritFile '+meritFile+' --outRootFile '+outFile+' --first '+ str(first)+' --last '+str(last)+ ' --outDir '+outDir

    else:
         outLogName=outFile[:-5]+'_out.txt'
         cmd='bsub -W 68:00 -o '+outLogName+'  python readReconAcd.py --reconFile '+reconFile+' --meritFile '+meritFile+' --outRootFile '+outFile+' --first '+ str(first)+' --last '+str(last) + ' --outDir '+outDir

    print('cmd= ',cmd)
    subprocess.call(cmd,shell=True) # qua lancia il sottoprocesso
 

if __name__ == '__main__':
   
    #options:
    import argparse
    formatter = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(formatter_class=formatter)
    parser.add_argument('--reconFile', required=True,  type=str,  help='the input recon file')
    parser.add_argument('--meritFile', type=str,  help='the input merit file' , required=True)
    parser.add_argument('--outRootFile', type=str,  help='the output root file (without extension!!)', required=True)
    parser.add_argument('--outDir', type=str,  help='output dirctory', required=False, default='.')
    parser.add_argument('--use_bsub', type=int,  help='use batch queue [0-> no batch queue] ', required=False, default=0)
       
    args = parser.parse_args()
    

    ReconFilePath=args.reconFile  
    meritFilePath=args.meritFile  

    outdir=args.outDir
    outRootName=args.outRootFile

    
    #create outDir:
    cmd='mkdir -p '+outdir
    print ("going to run:",cmd) 
    subprocess.call(cmd,shell=True)
    
       
    outFileName= outdir+'/'+outRootName 
        
    numEvents = getNevents(meritFilePath)
    maxEvents=70000.

    nLoops=int(numEvents/maxEvents)

    
    for i in range(0,nLoops+1):
        
        first=int(i*maxEvents)
        last=int((i+1)*maxEvents)
        if last>numEvents:
            last=numEvents

        print ("i=",i," first =",first," last=",last)
        
        outRootFile=outFileName+str(i)+'_v4cut.root'


        lancia_readRecon(meritFilePath, ReconFilePath, outRootFile, first,last, args.use_bsub, args.outDir)
