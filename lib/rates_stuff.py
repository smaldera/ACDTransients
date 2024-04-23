


def createTChain(nomeFileList, treeName):
   import ROOT  
   chain=ROOT.TChain(treeName)  
     
   f=open(nomeFileList)
   
   for line in f:
        rootFile=line[0:-1]
        print("Tchain- adding file: ",rootFile)
        chain.Add(rootFile)


   return chain     



def fill_dictSizes(inFileName):

     f=open(inFileName,"r")

     print("randing file:  ",inFileName)
     
     dict_tileSize={}
     for line in f:
          splitted_line=line.split()
          tile=int(splitted_line[0])
          area=float(splitted_line[1])
          dict_tileSize[tile]=area

     return dict_tileSize    


