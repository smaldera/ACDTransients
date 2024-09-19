

import numpy as np
from matplotlib import pyplot as plt

dict_merit={}
dict_met={}
dict_recon={}

def read_simpleList(filename,dict_path):

    f=open(filename,'r')
    #dict_merit={}                                                                                                                                                                           

    for line in f:
        #print (line[:-1].split())
        path=line[:-1]
        name=line[:-1].split()[0][-25:-16]
       # print("name=",name)
       # print("path=",path)
        dict_path[name]=path




def leggi_duOut(du_file):

    f=open(du_file,'r')
    wrongs=0.
    tot=0.
    bad_runs=[]
    
    for line in f:
        spl=line[:-1].split()
        if len(spl[1])<2: continue
        print (spl)
        #   print("size=",spl[0])
        unit=spl[0][-1]
        #   print(unit)
        size=spl[0][:-1]
        #    print("size=",size)

        factor=1
        if unit=='M': factor=1e6
        if unit=='K': factor=1e3
        if unit=='G': factor=1e9
        dimension=-1
        if factor==1:
            dimension=int(spl[0])*factor/1e6
        else:      
        
            dimension=float(size)*factor/1e6

        run_id=spl[1][2:]
        print ("run_id=",run_id," Mb=",dimension)
      
        tot+=1
        if dimension<2:
            wrongs+=1
            bad_runs.append(run_id)
    f.close()    
    print("ntot=",tot," n. wrong",wrongs," => ",wrongs/tot )
    return bad_runs




du_file='out_du2.txt'
bad_runs=leggi_duOut(du_file)

#print(bad_runs)
read_simpleList('last_merit.txt',dict_merit)
read_simpleList('last_recon.txt',dict_recon)

out_meritListName='bad_merits.txt'
out_reconListName='bad_recons.txt'

f_merit=open(out_meritListName, 'w')
f_recon=open(out_reconListName, 'w')


for run in bad_runs:
   # print (run)
   # print("merit=",dict_merit[run] )
    #print("recon=",dict_recon[run] )
    f_merit.write(dict_merit[run] +'\n')
    f_recon.write(dict_recon[run] +'\n')
   
    # with open(out_meritListName, 'w+') as f:
   #    f.write(dict_merit[run] +'\n')
   # f.close()    
   # with open(out_reconListName, 'w+') as f:
   #         f.write(dict_recon[run] +'\n')
f_merit.close()    
f_recon.close()    


    
    

