#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Created on Tue Nov 10 20:27:00 2023

@author: Martin NDONG
"""
from scan import Scan
import numpy as np
import pydicom


"""
Scan
"""
class Ct2mcnp:
    "The Ct2mcnp class converts a CT matrix into MCNP format."

    def __init__(self,path1,path2,transX=0,transY=0,transZ=0):

        self.path1 = path1
        self.path2 = path2
        
        self.transX=transX
        self.transY=transY
        self.transZ=transZ

        self.thickness = Scan(self.path1).properties(parameter="thickness",num_slice=0)
        self.pixel_size = Scan(self.path1).properties(parameter="pixel_size",num_slice=0)
        self.resolution = Scan(self.path1).properties(parameter="resolution",num_slice=0)
        self.slice_number = Scan(self.path1).properties(parameter="slice_number",num_slice=0)
         
    def properties(self,parameter=None):
             
        # (material, desinty, uh)

        dict = {"Air" : (0.001 , -1000),
                "Lung_inhale" : (0.2 , -807.18),
                "Lung_Exhale" : (0.5 , -509.29),
                "Adipose" : (0.96 , -64.56),
                "Breast" : (0.99 , -33.26),
                "Insert_Eau" : (1 , -5.56),
                "Muscle" : (1.06 , 43.2),
                "Liver" : (1.07 , 54.75),
                "Bone1" : (1.16 , 257.01),
                "Bone2" : (1.53 , 982.65),
                "Os dense" : (1.82 , 1488.36),
                "Titane" : (4.51 , 3061.32)}
        return dict[parameter]


    def  uh(self):

        uh_liste =[] 
        for matrice in reversed(Scan(self.path1).get_scan()):
            for ligne in reversed(matrice):
                uh_liste.extend(ligne) 
        return uh_liste
    
    def uh2density(self):

        dsty_univ=[]
        dsty=[]
        dsty_un=set()
        

        u_h = [-1025, -807.18, -509.29, -64.56, -33.26, -5.56, 43.2, 54.75, 257.01, 982.65, 1488.36, 3061.32]
        density = [0.001, 0.2, 0.5, 0.96, 0.99, 1, 1.06, 1.07, 1.16, 1.53, 1.82, 4.51]
        for element in self.uh():
            dst = np.interp(element, u_h, density)
            dsty.append(dst)

        for element in dsty:
            dsty_un.add(element)
        dsty_un=sorted(dsty_un)

        for k in range(len(dsty_un)):
            dsty_univ.append((dsty_un[k],k+1))

        for j in range(len(dsty_univ)):

            for i in range(len(dsty)):
                if dsty[i] == dsty_univ[j][0]: 
                    dsty[i] = dsty_univ[j][1]
        return  dsty,dsty_univ
    

    def cell_card(self):
        

        text1="Only CT scans converted to MCNP format/the rest to be completed."
        text2="cell cards"
        text3="Bodies"
        text4="Physic / Material"
        dsty,dsty_univ=self.uh2density()
        material = 0
        xmin, xmax, ymin, ymax, zmin, zmax=-self.pixel_size[0],0,-self.pixel_size[1],0,-self.thickness,0
        t=1

        with open(self.path2, 'w') as fichier:
   
            fichier.write(f"c  {text1:_^100}\n")
            fichier.write(f"c  {text2:_^30}\n")
            

            for i in range(len(dsty_univ)):

                if 0.001<=dsty_univ[i][0]< 0.2:
                    material=1
                if 0.2<=dsty_univ[i][0]< 0.5:
                    material=2
                if 0.5<=dsty_univ[i][0]< 0.96:
                    material=3
                if 0.96<=dsty_univ[i][0]< 0.99:
                    material=4
                if 0.99<=dsty_univ[i][0]< 1:
                    material=5
                if 1<=dsty_univ[i][0]< 1.06:
                    material=6
                if 1.06<=dsty_univ[i][0]< 1.07:
                    material=7
                if 1.07<=dsty_univ[i][0]< 1.16:
                    material=8
                if 1.16<=dsty_univ[i][0]< 1.53:
                    material=9
                if 1.53<=dsty_univ[i][0]< 1.82:
                    material=10
                if 1.82<=dsty_univ[i][0]<= 4.51:
                    material=11
                if dsty_univ[i][0]>= 4.51:
                    material=12

                fichier.write("{}   {}  {}  -999999  u = {}  imp:n=1\n".format(dsty_univ[i][1], material, -dsty_univ[i][0], dsty_univ[i][1]))
                #fichier.write("{}   {}  {}  #{}  u = {}  imp:n=1\n".format(dsty_univ[i][1]+3000, material, -dsty_univ[i][0],dsty_univ[i][1], dsty_univ[i][1]))

            fichier.write("101010  0   -999999    fill=111111   imp:n = 1\n")
            fichier.write("777777  0   999999    imp:n = 0  $ Uniquement si exterieur matrice non definie\n")
            fichier.write("111111   0   -1  u = 111111    lat = 1   imp:n = 1\n")
            fichier.write("       "+"fill =  {}:{} {}:{} {}:{}\n".format(-self.resolution[0]/2,(self.resolution[0]/2)-1,-self.resolution[1]/2,(self.resolution[1]/2)-1,-int(self.slice_number/2),int(self.slice_number/2)))
            fichier.write("       ")

            for i in range(len(dsty)):
                    fichier.write("{} ".format(dsty[i]))
                    if i==20*t:
                        t=t+1
                        fichier.write("\n")
                        fichier.write("      ")

                                      
            fichier.write("\n")
            fichier.write("\n")

            fichier.write(f"c  {text3:_^30}\n")

            fichier.write("999999  RPP {} {} {} {} {} {}\n".format(self.transX - (self.pixel_size[0]*self.resolution[0])/2, self.transX + (self.pixel_size[0]*self.resolution[0])/2, self.transY - (self.pixel_size[0]*self.resolution[1])/2, self.transY + (self.pixel_size[0]*self.resolution[1])/2, self.transZ - (self.thickness*self.slice_number)/2, self.transZ + (self.thickness*self.slice_number)/2))
            fichier.write("1   RPP {} {} {} {} {} {}\n".format(self.transX + xmin, self.transX + xmax, self.transY + ymin, self.transY + ymax, self.transZ - (self.thickness/2), self.transZ + (self.thickness/2)))
            
            
            fichier.write("\n")
            
            fichier.write(f"c  {text4:_^30}\n")
            
            fichier.write("c Material 1\n")                   
            fichier.write("c    Name air\n")                                 
            fichier.write("c    Density [0.001,0.2[ (gm/cm^3)\n")            
            fichier.write("c    Mode n p e h\n")      
            fichier.write("c\n")                
            fichier.write("m1    7014.24c          -0.78\n") 
            fichier.write("      8016.24c          -0.22\n")   
            fichier.write("c\n")   
            
            fichier.write("c Material 2\n")                   
            fichier.write("c    Name Lung inhale\n")                                 
            fichier.write("c    Density [0.2,0.5[ (gm/cm^3)\n")            
            fichier.write("c    Mode n p e h\n")      
            fichier.write("c\n")   
            fichier.write("m2      1001.24c          -0.103   6000.24c          -0.105   7014.24c          -0.031\n")                          
            fichier.write("        8016.24c          -0.749   11023.60c          -0.002   15031.24c          -0.002\n")
            fichier.write("        16032.60c         -0.003   17000.60c         -0.003   19000.60c         -0.002\n")   
            fichier.write("c\n")
            
            fichier.write("c Material 3\n")                   
            fichier.write("c    Name Lung exhale\n")                                 
            fichier.write("c    Density [0.5,0.96[ (gm/cm^3)\n")            
            fichier.write("c    Mode n p e h\n")      
            fichier.write("c\n")   
            fichier.write("m3      1001.24c          -0.103   6000.24c          -0.105   7014.24c          -0.031\n")                          
            fichier.write("        8016.24c          -0.749   11023.60c          -0.002   15031.24c          -0.002\n")
            fichier.write("        16032.60c         -0.003   17000.60c         -0.003   19000.60c         -0.002\n")   
            fichier.write("c\n")    
            
            fichier.write("c Material 4\n")                   
            fichier.write("c    Name Adipose\n")                                 
            fichier.write("c    Density [0.96,0.99[ (gm/cm^3)\n")            
            fichier.write("c    Mode n p e h\n")      
            fichier.write("c\n")   
            fichier.write("m4      1001.24c          -0.113   6000.24c          -0.113   7014.24c          -0.009\n")                          
            fichier.write("        8016.24c          -0.308   11023.60c          -0.001   16032.60c          -0.001\n")
            fichier.write("        17000.60c         -0.001\n")   
            fichier.write("c\n")   
            
            fichier.write("c Material 5\n")                   
            fichier.write("c    Name Breast\n")                                 
            fichier.write("c    Density [0.99,1[ (gm/cm^3)\n")            
            fichier.write("c    Mode n p e h\n")      
            fichier.write("c\n")   
            fichier.write("m5      1001.24c          -0.108   6000.24c          -0.356   7014.24c          -0.022\n")                          
            fichier.write("        8016.24c          -0.509   15031.24c          -0.002  16032.60c          -0.001\n")
            fichier.write("        17000.60c         -0.002\n")   
            fichier.write("c\n") 
            
            fichier.write("c Material 6\n")                   
            fichier.write("c    Name Insert eau\n")                                 
            fichier.write("c    Density [1,1.06[ (gm/cm^3)\n")            
            fichier.write("c    Mode n p e h\n")      
            fichier.write("c\n")   
            fichier.write("m6      1001.24c          -0.106    6000.24c         -0.284   7014.24c          -0.026\n")                          
            fichier.write("        8016.24c          -0.578    15031.24c         -0.001   16032.60c         -0.002\n")
            fichier.write("        17000.60c         -0.002   19000.60c         -0.001\n")    
            fichier.write("c\n")  
            
            fichier.write("c Material 7\n")                   
            fichier.write("c    Name Muscle\n")                                 
            fichier.write("c    Density [1.06,1.07[ (gm/cm^3)\n")            
            fichier.write("c    Mode n p e h\n")      
            fichier.write("c\n")   
            fichier.write("m7      1001.24c          -0.103   6000.24c          -0.134   7014.24c          -0.030\n")                          
            fichier.write("        8016.24c          -0.723   11023.60c         -0.002   15031.24c          -0.002\n")
            fichier.write("        16032.60c         -0.002   17000.60c         -0.002   19000.60c         -0.002\n")    
            fichier.write("c\n")        
               
            fichier.write("c Material 8\n")                   
            fichier.write("c    Name Liver\n")                                 
            fichier.write("c    Density [1.07,1.16[ (gm/cm^3)\n")            
            fichier.write("c    Mode n p e h\n")      
            fichier.write("c\n")   
            fichier.write("m8      1001.24c          -0.089   6000.24c          -0.423   7014.24c          -0.027\n")                          
            fichier.write("        8016.24c          -0.363   11023.60c         -0.001   15031.24c          -0.030\n")
            fichier.write("        16032.60c         -0.001   17000.60c         -0.001   19000.60c         -0.001\n")
            fichier.write("        20000.24c         -0.045\n")
            fichier.write("c\n") 
            
            fichier.write("c Material 9\n")                   
            fichier.write("c    Name Bone1\n")                                 
            fichier.write("c    Density [1.16,1.53[ (gm/cm^3)\n")            
            fichier.write("c    Mode n p e h\n")      
            fichier.write("c\n")   
            fichier.write("m9      1001.24c          -0.056   6000.24c          -0.265   7014.24c          -0.036\n")                          
            fichier.write("        8016.24c          -0.405   11023.60c          -0.001  15031.24c          -0.073\n")
            fichier.write("        16032.60c         -0.003   12000.60c         -0.002   20000.24c         -0.159\n")
            fichier.write("c\n")           
            
            fichier.write("c Material 10\n")                   
            fichier.write("c    Name Bone2\n")                                 
            fichier.write("c    Density [1.53,1.82[ (gm/cm^3)\n")            
            fichier.write("c    Mode n p e h\n")      
            fichier.write("c\n")   
            fichier.write("m10     1001.24c          -0.036   6000.24c          -0.165   7014.24c          -0.042\n")                          
            fichier.write("        8016.24c          -0.432   11023.60c          -0.001  15031.24c          -0.100\n") 
            fichier.write("        16032.60c         -0.003   12000.60c         -0.002   20000.24c         -0.001\n")
            fichier.write("c\n")
            
            fichier.write("c Material 11\n")                   
            fichier.write("c    Name Os dense\n")                                 
            fichier.write("c    Density [1.82,1=4.51[ (gm/cm^3)\n")            
            fichier.write("c    Mode n p e h\n")      
            fichier.write("c\n")   
            fichier.write("m11     1001.24c          -0.034   6000.24c          -0.155   7014.24c          -0.042\n")                          
            fichier.write("        8016.24c          -0.435   11023.60c         -0.001  15031.24c          -0.103\n") 
            fichier.write("        16032.60c         -0.003   12000.60c         -0.002   20000.24c         -0.225 \n")
            fichier.write("c\n")             
            
            
            fichier.write("c Material 12\n")                   
            fichier.write("c    Name Titane\n")                                 
            fichier.write("c    Density [4.51,[ (gm/cm^3)\n")            
            fichier.write("c    Mode n p e h\n")      
            fichier.write("c\n")   
            fichier.write("m12     22048.24c        -1.0")


