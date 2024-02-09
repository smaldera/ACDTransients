from __future__ import print_function, division


import astropy.io.fits as pyfits
import ROOT
import numpy as np
import array


  
def read_FT2s(inFiles):

  timeAll=np.array([],dtype=np.float64)
  z_raAll=np.array([],dtype=np.float64)
  z_decAll=np.array([],dtype=np.float64) 
  x_raAll=np.array([],dtype=np.float64)
  x_decAll=np.array([],dtype=np.float64)

  
  for filename in inFiles:
 
     print ("filename = ",filename) 
     ft2data   = pyfits.getdata(filename)
     
     fitsStart = ft2data.field('START')
     #fitsStop  = ft2data.field('STOP')
     #fitsDQ   = ft2data.field('DATA_QUAL')
     #fitsFermiConfig=ft2data.field('LAT_CONFIG')
     z_ra=  ft2data.field('RA_SCZ')
     z_dec=ft2data.field('DEC_SCZ')
     x_ra=ft2data.field('RA_SCX')
     x_dec=ft2data.field('DEC_SCX')
     
      
     timeAll=np.append(timeAll,fitsStart)
     z_raAll=np.append(z_raAll,z_ra)
     z_decAll=np.append(z_decAll,z_dec)
     x_raAll=np.append(x_raAll,x_ra)
     x_decAll=np.append(x_decAll,x_dec)

     return timeAll,z_raAll,z_decAll, x_raAll,x_decAll
     


def cosAngle(ra1,dec1,ra2,dec2):

     
    coseno=np.sin(dec1)*np.sin(dec2)+np.cos(dec1)*np.cos(dec2)*np.cos( (ra2)- (ra1)  )
    return coseno



  
def spherical2cartesian(theta, phi):  # in radians!!!

   r=1.
   x=r*np.sin(theta)*np.cos(phi)
   y=r*np.sin(theta)*np.sin(phi)
   z=r*np.cos(theta)
   
   return (x,y,z) 


def cartesian2spherical(x,y,z):

  r2=np.power(x,2)+np.power(y,2)+np.power(z,2)
  r=np.power(r2,0.5)    
  theta=np.arccos(z/r)
  phi=np.arctan2(y,x) 
  #print("R=",r) # se tutto e' giusto deve essere *sempre* 1
  return (r,theta,phi)
  
 
def cross_product(a,b): # v1, v2 tuple 3d  di np.array

 
  x=a[2-1]*b[3-1]-a[3-1]*b[2-1] 
  y=a[3-1]*b[1-1]-a[1-1]*b[3-1]
  z=a[1-1]*b[2-1]-a[2-1]*b[1-1]

  return (x,y,z)

  
def computeAngles(ra_srg,dec_srg, z_ra ,z_dec, x_ra,x_dec):  # ra_srg,dec_srg scalari,   x e z dirs, np.arrays!!



  
   deg2Rad=ROOT.TMath.DegToRad()
   """
   ra_srg*= deg2Rad
   dec_srg*= deg2Rad
   z_ra*= deg2Rad
   z_dec*= deg2Rad
   x_ra*= deg2Rad
   x_dec*= deg2Rad
   """

   ra_srg  = ra_srg*deg2Rad
   dec_srg=  dec_srg*deg2Rad
   z_ra=     z_ra*deg2Rad
   z_dec=    z_dec *deg2Rad
   x_ra=     x_ra*deg2Rad
   x_dec=    x_dec*deg2Rad


   
   xneg_ra=x_ra+180.*ROOT.TMath.DegToRad()
   xneg_dec=-x_dec   

   #trovare ra, dec asse Y
   pi=ROOT.TMath.Pi()
   x_theta=pi/2.-x_dec
   z_theta=pi/2.-z_dec
   
   xAxis_cart=spherical2cartesian(x_theta,x_ra) #tuple di np.array
   zAxis_cart=spherical2cartesian(z_theta,z_ra)

   # la mia funzione e numpy.cross danno lo stesso risultato!
 #  yAxis_cart=cross_product(xAxis_cart,zAxis_cart) # questo da -y !!!!! 
   yAxis_cart=cross_product(zAxis_cart, xAxis_cart)  
  
   #yAxis_cart=np.cross(xAxis_cart,zAxis_cart,axisa=0, axisb=0, axisc=0)
   #yAxis_cart=np.cross(zAxis_cart,xAxis_cart,axisa=0, axisb=0, axisc=0)  
   
   yAxis_spherical=cartesian2spherical(yAxis_cart[0],yAxis_cart[1],yAxis_cart[2])
     
   y_ra= yAxis_spherical[2]
   y_dec=pi/2.-yAxis_spherical[1]

   #print ("y_ra=",y_ra)
   
   
   yneg_ra=y_ra+180.*ROOT.TMath.DegToRad()
   yneg_dec=-y_dec   


   

   # test: asse negativo invertendo i le componenti cartesiane ( a la sarac)
#   yAxis_sphericalNEG=cartesian2spherical(-yAxis_cart[0],-yAxis_cart[1],-yAxis_cart[2])
#   yneg_ra2=yAxis_sphericalNEG[2]
#   yneg_dec2= pi/2.-yAxis_sphericalNEG[1]
  

   #TEST: calcolo -y come XxZ
#   yNegAxis_cart=cross_product(xAxis_cart, zAxis_cart)  
#   yNegAxis_spherical=cartesian2spherical(yNegAxis_cart[0],yNegAxis_cart[1],yNegAxis_cart[2])
#   yneg_ra3=yNegAxis_spherical[2]
#   yneg_dec3= pi/2.-yNegAxis_spherical[1]

   #print("yNeg mio ra=",yneg_ra[1]," dec = ",yneg_dec[1])
   #print("yNeg sarac ra=",yneg_ra2[1]," dec = ",yneg_dec2[1])
   #print("yNeg XxZ ra=",yneg_ra3[1]," dec = ",yneg_dec3[1])
   
   
   
  
   cosZ=cosAngle(ra_srg,dec_srg,z_ra,z_dec)
   cosXp=cosAngle(ra_srg,dec_srg, x_ra, x_dec)
   cosXn=cosAngle(ra_srg,dec_srg, xneg_ra, xneg_dec)
   cosYp=cosAngle(ra_srg,dec_srg, y_ra, y_dec)
   cosYn=cosAngle(ra_srg,dec_srg, yneg_ra, yneg_dec)


   # some  checks: 
   """
   cosXZ=cosAngle(x_ra, x_dec,z_ra,z_dec)
   print("TEST: ANGOLI XZ =",np.arccos(cosXZ[0:10])*ROOT.TMath.RadToDeg()  )
   
   cosXY=cosAngle(x_ra, x_dec,y_ra,y_dec)
   print("TEST:ANGOLI XY =",np.arccos(cosXY[0:10])*ROOT.TMath.RadToDeg()  )

   cosZY=cosAngle(z_ra, z_dec,y_ra,y_dec)
   print("TEST:ANGOLI ZY =",np.arccos(cosZY[0:10])*ROOT.TMath.RadToDeg()  )
   
   cosXXneg=cosAngle(x_ra, x_dec,xneg_ra,xneg_dec)
   print("TEST:ANGOLI XXneg =",np.arccos(cosXXneg[0:10])*ROOT.TMath.RadToDeg()  )
   
   cosYXneg=cosAngle(y_ra, y_dec,xneg_ra,xneg_dec)
   print("TEST:ANGOLI YXneg =",np.arccos(cosYXneg[0:10])*ROOT.TMath.RadToDeg()  )
   """


   
   return cosZ, cosXp, cosXn, cosYp, cosYn



   

if __name__ == '__main__':

  # GRB  130427324  AKA    GRB 130427A:
  #baseDir='/home/maldera/FERMI/code/plotAcdRates/data/grbs/GRB_130427324/'
  #inFiles =[baseDir+'r0388740704_ft2.fit']
  #ra_srg=173.148
  #dec_srg=27.709
  ####RA = 173.148, Dec = +27.709, LAT
  #t0=388741629.42
  #outRootfile_name=baseDir+'faces_angle_grb130427324.root'


  #GRB180720598  aka GRB 180720B
 # baseDir='/home/maldera/FERMI/code/plotAcdRates/data/grbs/GRB_180720598/'
 # inFiles =[baseDir+'gll_pt_p202_r0553785736_v001.fit']
 # ra_srg=0.058
 # dec_srg=-2.95
  #### RA, Dec = 0.58, -2.95 (J2000)  LAT
#  t0=553789304.65000
#  outRootfile_name=baseDir+'faces_angle_grb180720598.root'


 #GRB 090510
  #baseDir='/home/maldera/FERMI/code/plotAcdRates/data/grbs/GRB_0905510/'
  #inFiles =[baseDir+'r0263605997_ft2.fit']
  #ra_srg=333.400
  #dec_srg=-26.767
  #### RA, Dec = 333.400, -26.767  (J2000)  LAT
  #t0=263607781
  #outRootfile_name=baseDir+'faces_angle_grb090510.root'
  
  #GRB 220307A
  baseDir='/home/maldera/FERMI/code/plotAcdRates/data/grbs/GRB_230307A/'
  inFiles =[baseDir+'r0699894574_ft2seconds.fit']
  ra_srg=60.86
  dec_srg=-75.38
  t0=699896658
  outRootfile_name=baseDir+'faces_angle_grb220307A.root'
 


  #SGR  
#  ra_srg=293.7
#  dec_srg=21.9
#  baseDir='/home/maldera/FERMI/code/plotAcdRates/data/SGR_1935+2154/'
#  inFiles =[baseDir+'r0609702020_ft2.fit']
#  t0=609705184
#  outRootfile_name=baseDir+'faces_angle_sgr.root'

  
  timeAll,z_raAll,z_decAll, x_raAll,x_decAll=read_FT2s(inFiles)
  cosZ,cosXp,cosXn, cosYp,cosYn =computeAngles(ra_srg,dec_srg, z_raAll ,z_decAll, x_raAll,x_decAll)


  timeAll=timeAll-t0  
  zAngle=np.arccos(cosZ)*ROOT.TMath.RadToDeg()
  xpAngle=np.arccos(cosXp)*ROOT.TMath.RadToDeg()
  xnAngle=np.arccos(cosXn)*ROOT.TMath.RadToDeg()
  ypAngle=np.arccos(cosYp)*ROOT.TMath.RadToDeg()
  ynAngle=np.arccos(cosYn)*ROOT.TMath.RadToDeg()

 
  timeArr=array.array('d',timeAll)    # trasformo in array per plot con root (non riesco a fare TGraph con i numpy array... :( )!!!
 # z_raArr=array.array('d',z_raAll)    #           ""
  zAngleArr=array.array('d',zAngle)   #           "" 
  xpAngleArr=array.array('d',xpAngle) #           ""
  xnAngleArr=array.array('d',xnAngle) #           ""
  ypAngleArr=array.array('d',ypAngle) #           ""
  ynAngleArr=array.array('d',ynAngle) #           ""
 

     

  rootOutFile=ROOT.TFile(outRootfile_name,"recreate")
  if len(timeAll)!=0:
    g=ROOT.TGraph(len(timeAll),timeArr,zAngleArr)
    gXp=ROOT.TGraph(len(timeAll),timeArr,xpAngleArr)
    gXn=ROOT.TGraph(len(timeAll),timeArr,xnAngleArr)
    gYp=ROOT.TGraph(len(timeAll),timeArr,ypAngleArr)
    gYn=ROOT.TGraph(len(timeAll),timeArr,ynAngleArr)
     
         
    g.SetMarkerStyle(20)
    gXp.SetMarkerStyle(20)
    gXn.SetMarkerStyle(20)
    gYp.SetMarkerStyle(20)
    gYn.SetMarkerStyle(20)

    g.SetMarkerColor(4)
    gXp.SetMarkerColor(2)
    gXn.SetMarkerColor(3)
    gYp.SetMarkerColor(6)
    gYn.SetMarkerColor(1)

    g.SetLineColor(4)
    gXp.SetLineColor(2)
    gXn.SetLineColor(3)
    gYp.SetLineColor(6)
    gYn.SetLineColor(1)

    g.SetLineWidth(2)
    gXp.SetLineWidth(2)
    gXn.SetLineWidth(2)
    gYp.SetLineWidth(2)
    gYn.SetLineWidth(2)
   

    g.SetName('Z_angle')
    gXp.SetName('Xpos_angle')
    gXn.SetName('Xneg_angle')
    gYp.SetName('Ypos_angle')
    gYn.SetName('Yneg_angle')
    
    g.Write()
    gXp.Write()
    gXn.Write()
    gYp.Write()
    gYn.Write()


    # draw in a new TCanvas
    c1=ROOT.TCanvas("c1","",0)

    g.GetYaxis().SetTitle("OffAxis Angle [deg]")
    g.SetTitle("Off Axis angles  ")   
    g.Draw("apl")
    gXp.Draw('pl')
    gXn.Draw('pl')
    gYp.Draw('pl')
    gYn.Draw('pl')

    
    l=ROOT.TLegend(0.5,0.5,0.85,0.85)
    l.AddEntry(g,'Z  off axis angle ','pl')
    l.AddEntry(gXp,'+X - off axis angle ','pl')
    l.AddEntry(gXn,'-X - off axis angle ','pl')
    l.AddEntry(gYp,'+Y - off axis angle ','pl')
    l.AddEntry(gYn,'-Y - off axis angle ','pl')
    l.Draw()

    c1.Write()
    
  rootOutFile.Close()




  
