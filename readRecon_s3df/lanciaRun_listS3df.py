from __future__ import print_function
import glob
import subprocess
import time

import lanciaReadReconS3df_v2 as readRecon


dict_merit={}
dict_met={}
dict_recon={}


def clean_folder(folder):
  
   cmd='mv '+folder+'/*/*.root '+folder+'/.'
   subprocess.call(cmd,shell=True)

   outfileList=glob.glob(folder+'/*/output.txt')
   for f in outfileList:
      splitted=f.split('/')
      #print(splitted)
      destination=folder+'/outSlurm_'+splitted[-2]+'.txt'
      cmd='mv '+f+' '+destination
      #print("cmd=",cmd)
      subprocess.call(cmd,shell=True)

   cmd='rm -rf '+folder+'/*/'
   subprocess.call(cmd,shell=True)


def check_running(folder):
   # check for the presence of lockfile in the given folder
   filename=folder+'/*/lockfile_*' 
   running=True

   f=glob.glob(filename)
   print("checking", filename," ",len(f)," running")
   if len(f)==0:
      running=False
   else:
      #print ("lock files list=",f)
      return running   

def read_merit_list(filename):

    n=0
    f=open(filename,'r')

    for line in f:
        n +=1
#        print (line[:-1].split())

        name=line[:-1].split()[0]
        #print("name=",name)
        #print("met=",line[:-1].split()[1])
        n_files=len(line[:-1].split() )-2
        dict_merit[name]=[]
        dict_met[name]=float(line[:-1].split()[1])
        for i in range (0, n_files):
            index=2+i
            dict_merit[name].append(line[:-1].split()[index])
       
       # if n>11:
       #     break


def read_recon_list(filename):

    n=0
    f=open(filename,'r')

    for line in f:
        n +=1
 #       print (line[:-1].split())

        name=line[:-1].split()[0]
        print("name=",name)
        n_files=len(line[:-1].split() )-1
        dict_recon[name]=[]
        for i in range (0, n_files):
            index=1+i
            dict_recon[name].append(line[:-1].split()[index])
       
      #  if n>11:
      #      break

def read_simpleList(filename,dict_path):
  
    f=open(filename,'r')
    #dict_merit={}
   
    for line in f: 
        print (line[:-1].split())
        path=line[:-1]
        name=line[:-1].split()[0][-25:-16]
        print("name=",name)
        print("path=",path)                                                     
        dict_path[name]=path




if __name__ == '__main__':
   
    #options:
    import argparse
    formatter = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(formatter_class=formatter)
    parser.add_argument('--reconList', required=True,  type=str,  help='list of xrootd path to recon files')
    parser.add_argument('--meritList', required=True,  type=str,  help='list of xrootd path to merit files')
    parser.add_argument('--outFolder', required=True,  type=str,  help='*absolute* path to output folder ')
    parser.add_argument('--use_slurm', required=True,  type=str,  help='1 if you want to run on slurm ')
    args = parser.parse_args()

    if (args.outFolder[0]!='/'):
       print("outFolder must be an absolute path (from /)")
       exit()

        


    read_simpleList(args.meritList,dict_merit)
    read_simpleList(args.reconList,dict_recon)

    #print(dict_merit)
    #print(dict_recon)



    
    outFolder_base=args.outFolder   #'/sdf/home/m/maldera/fermi-user/newRuns_v2Bad/'

    #nake a list of already processed runs (from folder names)
    already_done=glob.glob(args.outFolder+'/*')   
    done_r=[]
    for path in already_done:
      done_run=path.split('/')[-1]
      print ('already done... ',done_run)
      done_r.append(done_run)


    #loop sui run:
    n=0
    for run in dict_merit.keys():
      print ("processing run... ",run)
      if run in done_r:   # check if the run was already processed and skip it
         print ('already analyzed.... skipping')
         continue

      outFolder=outFolder_base+'/'+run+'/'   
      outFile='out_recon-'+run


      use_slurm=args.use_slurm
      readRecon.analizeRun(dict_recon[run],dict_merit[run],outFolder,outFile,use_slurm)
             
      time.sleep(15)



      while check_running(outFolder)==True:
         time.sleep(30)
         print("still running.... sleep")

      print ("run done!")
      clean_folder(outFolder)
      n+=1  
   # if n>2: break

    
    print ("this is the end... ")
