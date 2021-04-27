import pydicom 
import numpy as np
from library_dicom.export_segmentation.tools.rtss_writer_tools import *

class StructureSetROISequence : 

    def __init__(self, mask_array, results, number_of_roi):
        self.mask_array = mask_array
        self.number_of_roi = number_of_roi
        self.results = results


    def create_StructureSetROISequence(self, pixel_spacing, ReferencedFrameOfReferenceUID) :
        StructureSetROISequence = pydicom.sequence.Sequence()

        for number_roi in range(1 , self.number_of_roi +1):
            dataset = pydicom.dataset.Dataset()
            dataset.ROINumber = number_roi
            dataset.ReferencedFrameOfReferenceUID = ReferencedFrameOfReferenceUID             
            dataset.ROIName = self.results['segmentAttributes'][0][number_roi-1]["SegmentDescription"]
            dataset.ROIVolume = str(self.get_roi_volume(number_roi, pixel_spacing))
            dataset.ROIGenerationAlgorithm = self.results['segmentAttributes'][0][number_roi-1]["SegmentAlgorithmType"]
            StructureSetROISequence.append(dataset)
        return StructureSetROISequence 
        
     
    def get_roi_volume(self, number_roi, pixel_spacing):
        number_pixel = 0
        if len(self.mask_array.shape) == 3 :
            _, x, _ = np.where(self.mask_array == number_roi)
        elif len(self.mask_array.shape) == 4 : 
            raise Exception ('4D array. Need a 3D array with [z,x,y]')
        number_pixel = len(x) #same as len(y) or len(z)
        volume_pixel = pixel_spacing[0] * pixel_spacing[1] * abs(pixel_spacing[2])
        volume_pixel = volume_pixel * 10**(-3) #mm3 to ml 
        roi_volume = number_pixel * volume_pixel 

        return np.round(roi_volume , 5)

