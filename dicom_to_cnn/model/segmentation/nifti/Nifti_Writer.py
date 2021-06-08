import SimpleITK as sitk 
import os
from library_dicom.model.reader.SeriesPT import SeriesPT
from dicom_to_cnn.model.segmentation.Abstract_Writer import Abstract_Writer

class Nifti_Writer(Abstract_Writer):
    """a class to convert a np.ndarray to a sitk.Image  
    """

    def __init__(self, mask_img:sitk.Image):
        """constructor

        Args:
            img_mask (sitk.Image) : [sitk.Image of shape (x,y,z)]
        """
        super().__init__(mask_img)

    def save_file(self, filename:str, directory_path:str):
        """method to save the new nifti file

        Args:
            filename (str): [name of the new nifti file]
            directory_path (str): [directory's path where to save the new nifti file]
        
        """
        
        sitk.WriteImage(self.mask_img, os.path.join(directory_path, filename))