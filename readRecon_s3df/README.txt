
Script per estrarre le informazioni dell ACD  dai files recon.


- readReconAcd.py
 stesso scrip che gira sulla farm rhel6-64.
 Crea un ttree  dove per ogni evento sono salvati:
 time (met)
 acdE_acdtile[89] vettore con energia vista da ciascuna tile	
 GltGemEngine
 GltGemSummary

 questo script genera un memory leak, quindi il run viene analizzato in pezzetti (70k eventi, modificabile nel codice)




- lanciaReadReconS3df_v2.py
processa un singolo run. lanciaReadReconS3df_v2.py lancia readReconAcd.py per i vari pezzi di un run, attraverso un container rhel6
(crea uno scrip bash che viene eseguito tramite slurm o sulla macchina locale, a seconda del valore dell'opzione use_slurm)

Esempio:
python  lanciaReadReconS3df_v2.py  --reconFile root://glast-rdr.slac.stanford.edu//glast/Data/Flight/Reprocess/P300/recon/r0263605997_v300_recon.root --meritFile root://glast-rdr.slac.stanford.edu//glast/Data/Flight/Reprocess/P300/merit/r0263605997_v300_merit.root --outRootFile suffissoFilesRoot --outDir absolute_path_output --use_slurm 1

se --use_slurm 0 -> i vari pezzi del run vengono letti in sequenza sulla macchina su cui si e' loggati
se --use_slurm 1 -> i vari pezzi del run vengono letti in parallelo sottomettendo i job con slurm (sistema di code su s3df)

vengono creati diversi files root nella directory specificata.
Ogni file root creato contiene un TTree (chiamato myTree) in cui per ogni evento vengono salvati:

- time ( met dalla variabile merit EvtElapsedTime )
- acdE_acdtile[64]  array con l'energia di ogni tile(dalla 0 alla 63). Tiles senza hit hanno energia 0
- GltGemEngine
- GltGemSummary



- lanciaRun_listS3df.py
analizza una lista di run.
richiede in input due liste di files, con i path xrootd dei file recon e merit.

Esempio:
python lanciaRun_listS3df.py --reconList reconlist.txt --meritList merits_list.txt --outFolder abasolutePathToOutFolder  --use_slurm 1

analizza un run per volta, aspettando che i vari "pezzi" in cui vine diviso il run abbiano finito (controllando l'esistenza di un lockfile nella cartella di output)
