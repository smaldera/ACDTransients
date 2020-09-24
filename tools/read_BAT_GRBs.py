from __future__ import print_function
import subprocess


#reads GRB list (at the moment only  from swift-BAT, but could add others), finds the corresponding files (merit and recon)
# and writes them in two files:
# grb_runList_merit.txt: ( content: GRB_name, trigger_met, merit_files)
# grb_runList_recon.txt: ( content: GRB_name,  recon_files)                                                                                    

# search for runs containing trigger_met-T100start, trigger_met+T100stop (in some cases we need two runs)
#(filenames are hardcoded... )




def dataCat_string(start,stop, group):



	dataPath='/Data/Flight/Level1/LPA'
	#dataPath_old='/'

	if start<459947003:
          dataPath='/Data/Flight/Reprocess/P300'   # reprocess
  

        cmd="/afs/slac.stanford.edu/u/gl/glast/datacatalog/prod/datacat find --group "+group+" --show-non-ok-locations --filter nMetStart<"+str(start)+"&&nMetStop>="+str(stop)+" "+dataPath 


        return cmd   


def run_dataCatFind(start,stop,group):
	cmd=dataCat_string(start,stop, group)
	pipe=subprocess.Popen(cmd.split(" "),stdout=subprocess.PIPE)
	out=pipe.communicate()[0]
	
	return out[:-1]  # tolgo il newline finale
	




def search_runs(grb_name,met,fout,fout_recon,met_start, met_stop):

	run1=run_dataCatFind(met_start,met_stop,"MERIT")
	run1_recon=run_dataCatFind(met_start,met_stop,"RECON")

	if run1=="":
            print ("nessun run comprende start e stop")
	    runStart=run_dataCatFind(met_start,met_start,"MERIT")
	    runStop=run_dataCatFind(met_stop,met_stop,"MERIT")

	    runStart_recon=run_dataCatFind(met_start,met_start,"RECON")
	    runStop_recon=run_dataCatFind(met_stop,met_stop,"RECON")


	    print("    run start = ",runStart)
	    print("    run stop=",runStop)


	    print (grb_name," ",runStart," ",runStop)
	    print (" -> recon: ",runStart_recon," ",runStop_recon)



	    if (runStart!="" or runStop!=""):
			  fout.write(grb_name+" "+str(met)+" "+runStart+" "+runStop+'\n')
			  fout.flush()
                          fout_recon.write(grb_name+" "+runStart_recon+" "+runStop_recon+'\n')
                          #dict_runs[grb_name]=[runStart,runStop]
			  fout_recon.flush()


	else:
            #dict_runs[grb_name]=[run1]
	    print (grb_name," ",run1)
	    fout.write(grb_name+" "+str(met)+" "+run1+'\n')
	    fout.flush()
	    print (grb_name," ",run1_recon)
	    fout_recon.write(grb_name+" "+run1_recon+'\n')
	    fout_recon.flush()





def parse_swiftBAT(ll):


   import urllib2
   target_url="https://swift.gsfc.nasa.gov/results/batgrbcat/summary_cflux/summary_general_info/summary_burst_durations.txt"
   data = urllib2.urlopen(target_url)

   for line in data:
        argv=line.split()
        if argv[0][0]=="#" or argv[4]=='|' :
                continue
        else:
                #print (argv)                                                                                                                     
                grb_name=argv[0]
                try:
			met=float(argv[4])
		except:
		    print("exception, met=",argv[4])
		    continue

                Tstart=0.
                try:
                   Tstart=float(argv[6])
                except:
                   print("exception, start=",argv[6])
                Tstop=0.
                try:
                  Tstop=float(argv[8])
                except:
                   print("exception, stop=",argv[6])
                   Tstart=0.
		   
		met_start=met+Tstart
                met_stop=met+Tstop

                print (argv[0]," MET=",argv[4],"  met_start=",met_start," met stop=", met_stop)
   
		my_dict={"grb_name":grb_name, "met":met,"start":met_start,"stop":met_stop}
		
		ll.append(my_dict)

   return ll




################
if __name__ == "__main__":

  #aout files:
  fout=open('grb_runList_merit.txt','w+')
  fout_recon=open('grb_runList_recon.txt','w+')
  ll=[]       

  # step 1: read swift GRB, and store their times in a list of dictionaries (ll)
  ll=parse_swiftBAT(ll)


  # setp2L: loop over the list and search runs for each GRB (and write them to file)
  for i in range (0,len(ll) ):

	 met=ll[i]["met"]
	 stop=ll[i]['stop']
	 start=ll[i]['start']
	 grb_name=ll[i]['grb_name']


	 if met< 236563201:
		print("before LAT launch! skipping.... ") 
		continue 
	 
	 print("========>>> ",grb_name, "met=",met," start =",start," stop=",stop)
	 search_runs(grb_name,met,fout,fout_recon,start, stop)     



  fout.close()
  fout_recon.close()



  print("...all done!")
  
