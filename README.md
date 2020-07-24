# ACDTransients

CREARE ISTOGRAMMI RATES:

1) leggere file recon (a slac):


source set_vars.sh


python  read_recon/lanciaReadRecon.py  --reconFile root://glast-rdr.slac.stanford.edu//glast/Data/Flight/Reprocess/P300/recon/r0263605997_v300_recon.root --meritFile root://glast-rdr.slac.stanford.edu//glast/Data/Flight/Reprocess/P300/merit/r0263605997_v300_merit.root --outRootFile  outFile --outDir new_dir --use_bsub 1

se --use_bsub 0 -> i vari pezzi del run vengnono letti in sequenza sulla macchina su cui si e' loggati
se --use_bsub 1 -> i vari pezzi del run vengnono letti in parallelo mandando sottomenttendo i job con bsub (molto piu' veloce!)


vengono creati diversi files root nella directory specificata.
Ogni file root creato contiene un TTree (chiamato myTree) in cui per ogni evento vengono salvati:

- time ( met dalla variabile merit EvtElapsedTime )
- acdE_acdtile[64]  array di dimesione 64 con l'energia di ogni tile(dalla 0 alla 63). Tiles senza hit hanno energia 0


2) creare istogrammi (raw e normalizzati) per tutte le tiles e mediati sulle facce:

  python  makeReconRates.py --listFile fileList --binning 1 --outfile out.root --t0 0 --acdSizesFile ACD_tiles_size2.txt 

# fileList e' l'elendo dei files generati da lanciaReadRecon.py
# NB, la lista deve essere ordinata! (se  no la funzione get_time0_last non funziona... sarebbe da cambiare )
# es: ls outAcdReconRates_*_?_*.root >fileList
#     ls outAcdReconRates_*_??_*.root >>fileList




########################

fig_Acdrecon.py -> plotta (root) i rates salvati nel file generato da makeReconRates.py
                 (il nome del file e' hardcoded per ora)

