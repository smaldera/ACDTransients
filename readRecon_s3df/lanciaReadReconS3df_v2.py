# lancia readReconAcd.py per creare ROOT TTrees con met e energia di ogni tile
# per ogni evento.
# Poiche'readReconAcd.py ha un memory leak (che non sono riuscito ad eliminare in nessun modo) il run viene spezzettato
#e per ogni blocco di eventi viene lanciata una istanza diversa di readReconAcd.py
# con 70k eventi si arriva a ~il 10% della ram usata

# usage:
# python lanciaReadRecon.py  --reconFile RECONFILE  (the input recon file)  --meritFile MERITFILE   (the input merit file) 
#  --outRootFile OUTROOTFILE  (the output root file (without extension!!))  --outDir OUTDIR  output dirctory (default: okkio, mettere path completo)  --use_bsub 1 or 0 to use batch queue (default: 0)


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




def lancia_readRecon(meritFile, reconFile, outFile, first,last,use_slurm,outDir):
    """
    """

    
    string2='python ~/readRecon_s3df/readReconAcd.py --reconFile '+reconFile+' --meritFile '+meritFile+' --outRootFile '+outFile+' --first '+ str(first)+' --last '+str(last)+ ' --outDir '+outDir
    print ("python command=",string2)
    with open('job.sh', 'w') as f:
            f.write(string2+'\n')
    f.close()    

    cmd='cat  myjob_template.sh job.sh >myjob.sh'
    subprocess.call(cmd,shell=True)

    
    cmd='mv myjob.sh '+outDir+'/.'
    subprocess.call(cmd,shell=True)


    cmd='cp runContainer_rhel6.sh  '+outDir+'/.'
    subprocess.call(cmd,shell=True)



    if use_slurm==0:
       """      
       """ 
       cmd='cd '+outDir+' &&  sh runContainer_rhel6.sh '
       subprocess.call(cmd,shell=True)

        
    else:
         cmd='cd '+outDir+' &&  sbatch runContainer_rhel6.sh '
         subprocess.call(cmd,shell=True)



def analizeRun(ReconFilePath,meritFilePath,outDir,outRootName,use_slurm):


    print("analizeRun:ReconFilePath=",ReconFilePath)
    print("analizeRun:MeritFilePath=",meritFilePath)
    print("analizeRun:outdir=",outDir)
    print("analizeRun:outRootName=",outRootName)
    print("analizeRun:sue_slurm=",use_slurm)
      




    #create outDir:                                                                                                                                                                          
    cmd='mkdir -p '+outDir
    print ("going to run:",cmd)
    subprocess.call(cmd,shell=True)
    numEvents = getNevents(meritFilePath)

    #maxEvents=10000.
    maxEvents=70000.

    nLoops=int(numEvents/maxEvents)

    for i in range(0,nLoops+1):


        outdir=outDir+'/'+str(i)
        if i<10:
            outdir=outDir+'/0'+str(i)


        cmd='mkdir -p '+outdir
        print('cmd= ',cmd)
        subprocess.call(cmd,shell=True)

       

        
        first=int(i*maxEvents)
        last=int((i+1)*maxEvents)
        if last>numEvents:
            last=numEvents

        lockfilename=outdir+'/lockfile_'+str(first)+'-'+str(last)
        cmd='echo aaa >'+lockfilename
        subprocess.call(cmd,shell=True)
                 
        print ("i=",i," first =",first," last=",last)

        outRootFile=outdir+'/'+outRootName+"_"+str(i)+'.root'
        if i<10: outRootFile=outdir+'/'+outRootName+"_0"+str(i)+'.root'

       

        lancia_readRecon(meritFilePath, ReconFilePath, outRootFile, first,last, use_slurm, outdir)


    

    
    


    

if __name__ == '__main__':
   
    #options:
    import argparse
    formatter = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(formatter_class=formatter)
    parser.add_argument('--reconFile', required=True,  type=str,  help='the input recon file')
    parser.add_argument('--meritFile', type=str,  help='the input merit file' , required=True)
    parser.add_argument('--outRootFile', type=str,  help='the output root file (without extension!!)', required=True)
    parser.add_argument('--outDir', type=str,  help='output dirctory', required=False, default='.')
    parser.add_argument('--use_slurm', type=int,  help='use batch queue [0-> no batch queue] ', required=False, default=1)
       
    args = parser.parse_args()
    

    ReconFilePath=args.reconFile  
    meritFilePath=args.meritFile  
    outRootName=args.outRootFile
    outDir=args.outDir

        
    #all the job is dome here:
    analizeRun(ReconFilePath,meritFilePath,outDir,outRootName,args.use_slurm)
