
- CREARE i files root con gli hit di ogni acd tile:

source set_vars.sh


python lanciaReadRecon.py  --reconFile root://glast-rdr.slac.stanford.edu//glast/Data/Flight/Reprocess/P300/recon/r0263605997_v300_recon.root --meritFile root://glast-rdr.slac.stanford.edu//glast/Data/Flight/Reprocess/P300/merit/r0263605997_v300_merit.root --outRootFile  outFile --outDir new_dir --use_bsub 1

se --use_bsub 0 -> i vari pezzi del run vengnono letti in sequenza sulla macchina su cui si e' loggati
se --use_bsub 1 -> i vari pezzi del run vengnono letti in parallelo mandando sottomenttendo i job con bsub (molto piu' veloce!)




vengono creati diversi files root nella directory specificata.
Ogni file root creato contiene un TTree (chiamato myTree) in cui per ogni evento vengono salvati:

- time ( met dalla variabile merit EvtElapsedTime )
- acdE_acdtile[64]  array di dimesione 64 con l'energia di ogni tile(dalla 0 alla 63). Tiles senza hit hanno energia 0



