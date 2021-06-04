import numpy as np 
import SimpleITK as sitk 
from library_dicom.dicom_processor.model.reader.SeriesPT import SeriesPT

def convert_array_to_img(numpy_array:np.ndarray, serie_pet_object:SeriesPT):
        """method to convert np.ndarray of shape (z,y,x,c) into pixel vector sitk Image of shape (x,y,z), associated with a PET Series

        Returns:
            [sitk.Image]: [description]
        """
        instance_array = serie_pet_object.get_instances_ordered()
        sitk_img = sitk.GetImageFromArray(numpy_array, isVector = True) # [z,y,x,c] tjrs de taille 4, si une seule roi=> dernier channel =1
        sitk_img = sitk.Cast(sitk_img, sitk.sitkVectorUInt8)
        original_pixel_spacing = instance_array[0].get_pixel_spacing()
        original_direction = instance_array[0].get_image_orientation()
        sitk_img.SetDirection( (float(original_direction[0]), float(original_direction[1]), float(original_direction[2]), 
                                    float(original_direction[3]), float(original_direction[4]), float(original_direction[5]), 
                                    0.0, 0.0, 1.0) )
        sitk_img.SetOrigin( instance_array[0].get_image_position())
        sitk_img.SetSpacing( (original_pixel_spacing[0], original_pixel_spacing[1], serie_pet_object.get_z_spacing()) )
        return sitk_img