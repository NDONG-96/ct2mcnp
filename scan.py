#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""

Created on Tue Nov 10 20:27:00 2023

@author: Martin NDONG
"""



"""
    Packages / Libraries
"""

import os
import glob
import numpy as np
import pydicom

"""
###     CT-Scan
"""
class Scan : 

    # Initialisation
    def __init__(self,folder_path):
        #
        self.folder = folder_path
        self.position = self._order_slice_from_position()
        # 
        self.axis_dict = {"x":0,"y":1,"z":2}

    """
    """
    # Z position array
    def _z_position(self):

        z_res = self.properties("thickness")
        z_pos = self.properties("image_position")[-1]
        z_size = self.properties("slice_number")

        return np.arange(z_pos,z_pos+(z_res*z_size),z_res)
    
    """
    """
    # CT file list sorted by number 
    def get_file_list(self):

        return sorted(glob.glob(f"{self.folder}/CT*.dcm"),key=lambda f : int(''.join(filter(str.isdigit, f)))) # tri de la liste des CT
    
    # Get slice 
    def get_slice(self,num_slice=0):

        return pydicom.dcmread(self.get_file_list()[self.position.index(num_slice)])
    
    # CT properties
    def properties(self,parameter=None,num_slice=0):

        dict = {"slice_number" : len(self.get_file_list()),
                "resolution" : tuple(self.get_slice(num_slice).pixel_array.shape),
                "pixel_size" : self.get_slice(num_slice).PixelSpacing,
                "thickness" : float(self.get_slice(num_slice).SliceThickness),
                "image_position" : self.get_slice(num_slice).ImagePositionPatient,
                "z_position" : float(self.get_slice(num_slice).SliceLocation),
                "UH_factor" : float(self.get_slice(num_slice).RescaleIntercept)}

        return dict[parameter]

    # Order slice index
    def _order_slice_from_position(self):

        position = []

        #
        for file in self.get_file_list():
            position.append(pydicom.dcmread(file).SliceLocation)
        #step=1
        step = pydicom.dcmread(self.get_file_list()[0]).SliceThickness

        true_position = np.arange(min(position),min(position)+(len(self.get_file_list())*step),step)

        index_position = [list(true_position).index(i) for i in position] # return une liste d'index classées selon la liste dans position

        return index_position
    
    # Get axis position array
    def get_axis_position(self,axis="x"):

        axis_index = self.axis_dict[axis]
        file = self.get_slice()

        #
        if axis in ["x","y"]:
            position = [round(file.ImagePositionPatient[axis_index]+(i*file.PixelSpacing[axis_index]),2) for i in range(file.pixel_array.shape[axis_index]+1)]
        else : 
            position = [file.ImagePositionPatient[axis_index]+(i*file.SliceThickness) for i in range(len(self.get_file_list()))] # 

        return position
    
    # Get slice index from position
    def get_slice_index_from_position(self,position=0):

        return self.get_axis_position(axis="z").index(position)
    
    # Get scan 
    def get_scan(self):

        # File list and true position index
        files = self.get_file_list()

        # Init matrix
        matrix = self.get_slice(num_slice=0).pixel_array
        matrix = np.expand_dims(matrix,axis=0)

        for i in range(1,len(files)):
            matrix = np.stack((*matrix,self.get_slice(num_slice=i).pixel_array))

        return matrix + self.properties("UH_factor")
