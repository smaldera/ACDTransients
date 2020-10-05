from __future__ import print_function
import glob
import subprocess
import time

dict_merit={}
dict_met={}
dict_recon={}


def check_running(folder):
   # check for the presence of lockfile in the given folder
   filename=folder+'/'+'lockfile_*' 
   running=True

   f=glob.glob(filename)
   print("checking", filename)
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
        #print("name=",name)
        n_files=len(line[:-1].split() )-1
        dict_recon[name]=[]
        for i in range (0, n_files):
            index=1+i
            dict_recon[name].append(line[:-1].split()[index])
       
      #  if n>11:
      #      break



read_merit_list("../tools/BATgrb_runList_merit.txt")        
read_recon_list("../tools/BATgrb_runList_recon.txt")        



#print(dict_merit)
#print(dict_recon)

#outFolder_base='/u/gl/maldera/plotAcdRates/BATgrbs/'
outFolder_base='/nfs/farm/g/glast/g/CRE/test_sm/BATgrbs/'
already_done=glob.glob('/nfs/farm/g/glast/g/CRE/test_sm/BATgrbs/*')

done_grbs=[]
for path in already_done:
   print ('already done... ',path[40:])
   done_grbs.append(path[40:])



#loop sui GRBs:

for grb in dict_merit.keys():
    print (grb)
    if grb in done_grbs:
       print ('already analyzed.... skipping')
       continue

    outFolder=outFolder_base+grb+'/'
    
    for i in range (0,len(dict_merit[grb])):
        outFile='out_recon'+grb+'_'+str(i)
        cmd='cd /u/gl/maldera/ACDTransients/read_recon/ &&   python   /u/gl/maldera/ACDTransients/read_recon/lanciaReadRecon.py  --reconFile ' +dict_recon[grb][i]+ '  --meritFile '+dict_merit[grb][i]+ ' --outRootFile '+  outFile + ' --outDir '+ outFolder +' --use_bsub 1'
        print (cmd)
        subprocess.call(cmd,shell=True)
        
        time.sleep(2)



        while check_running(outFolder)==True:
           time.sleep(30)
           print("still running.... sleep")
