from __future__ import print_function

import subprocess
import time
import glob

dict_merit={}
dict_met={}
dict_recon={}


def run_command(cmd):
   print ('going to run: ',cmd)
   subprocess.call(cmd,shell=True)

def crea_lockfile(folder):

  lockfilename=folder+'/lockfile.txt'
  run_command('echo aaa >'+lockfilename)
  

def crea_rootfile_list(folder):


   #crea file list...:
   rootfiles_list=folder+'/rootfile_list.txt'
   run_command('ls '+ folder+'out_reconGRB*_0?_v4cut.root > '+rootfiles_list)
   run_command('ls '+ folder+'out_reconGRB*_0??_v4cut.root >> '+rootfiles_list)
  
def check_running(folder):
   # check for the presence of lockfile in the given folder                                                               
   filename=folder+'/'+'lockfile*'
   running=True

   f=glob.glob(filename)
   print("checking", filename, "f = ",f)
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
       #     break"                                



###############################

# read merit list:
read_merit_list("BATgrb_runList_merit.txt")


base_dir='/nfs/farm/g/glast/g/CRE/test_sm/BATgrbs/'
binning=0.1

# get list of already done...
lfiles=glob.glob("/nfs/farm/g/glast/g/CRE/test_sm/BATgrbs/*/*bin0.1.root")
lnames=[a.split('/')[9] for a in lfiles ]
print("lnames=", lnames)



#loop sui GRBs:                                                                                                          
for grb in dict_merit.keys():
    print (grb)
    
    if grb in lnames:
       print('grb ',grb, ' already done.. ')
       continue

    folder=base_dir+grb+'/'

    print('folder=',folder)
    crea_rootfile_list(folder)
    crea_lockfile(folder)


    out_rootFile='ACDrates_'+grb+'_bin'+str(binning)+'.root'

    t0=dict_met[grb]


    cmd='bsub -o '+folder+'out_makeRates.txt -W 24:00   \"python /u/gl/maldera/ACDTransients/makeReconRates.py --listFile '+folder+'rootfile_list.txt --outfile '+folder+out_rootFile+' --binning ' +str(binning)+' --t0 '+str(t0)+' --outDir '+folder+'  --acdSizesFile /u/gl/maldera/ACDTransients/ACD_tiles_size2.txt  \"'

    run_command(cmd)
    #print("cmd bsub= ",cmd)
    time.sleep(2)


    
    while check_running(folder)==True:
       time.sleep(30)
       print("still running.... sleep")


#    break




