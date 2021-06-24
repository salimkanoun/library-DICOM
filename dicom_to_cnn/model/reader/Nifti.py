import SimpleITK as sitk 
import numpy as np 

class Nifti : 
    """a class to read a nifti image, resample it 
    """

    def __init__(self, nifti_img_path:str):
        """constructor

        Args:
            nifti_img_path (str): [path of a nifti image with shape (x,y,z)]
        """
        self.nifti_img_path = nifti_img_path
        self.nifti_img = sitk.ReadImage(self.nifti_img_path) #shape (x,y,z)

    def resample(self, shape_matrix:tuple = (256, 256, 1024), shape_physic=(700, 700, 2000)) -> np.ndarray:
        """function to resample sitk image of shape (x,y,z), put it in a bigger and empty np.ndarray

        Args:
            shape_matrix (tuple) : [size of the new matrix/sitk image (number of pixel), shape (x,y,z)].
            shape_physic (tuple) : [physical size of the new matrix/sitk image, (in mm), shape (x,y,z)].
        Returns:
            [np.ndarray]: [return corresponding resampled np.ndarray]
        """
        spacing = self.nifti_img.GetSpacing()
        origin = self.nifti_img.GetOrigin()
        direction = self.nifti_img.GetDirection()
        size = self.nifti_img.GetSize()
        #target spacing, and size
        spacing_x = shape_physic[0]/shape_matrix[0] #mm
        spacing_y = shape_physic[1]/shape_matrix[1] #mm 
        spacing_z = shape_physic[2]/shape_matrix[2] #mm

        true_x = size[0] * spacing[0] #mm
        true_y = size[1] * spacing[1] #mm 
        true_z = size[2] * spacing[2] #mm

        new_size_x = int((true_x * shape_matrix[0]) / shape_physic[0]) #pixel
        new_size_y = int((true_y * shape_matrix[1]) / shape_physic[1]) #pixel
        new_size_z = int((true_z * shape_matrix[2]) / shape_physic[2]) #pixel

        #applied transformation
        transformation = sitk.ResampleImageFilter()
        transformation.SetOutputDirection(direction)
        transformation.SetOutputOrigin(origin)
        transformation.SetSize((new_size_x, new_size_y, new_size_z))
        transformation.SetOutputSpacing((spacing_x, spacing_y, spacing_z))
        transformation.SetInterpolator(sitk.sitkLinear)
        new_img = transformation.Execute(self.nifti_img) 
        result = sitk.GetArrayFromImage(new_img) #[z,y,x]
        center = [int(shape_matrix[2]/2), int(shape_matrix[1]/2),  int(shape_matrix[1]/2)]
        z = int(result.shape[0]/2)
        y = int(result.shape[1]/2)
        x = int(result.shape[2]/2)
        sommet_x = center[2] - x 
        sommet_y = center[1] - y 
        sommet_z = center[0] - z
        new_array = np.zeros((shape_matrix[2], shape_matrix[1], shape_matrix[0]))
        if result.shape[1] != shape_matrix[1] : 
            new_array[sommet_z:sommet_z+result.shape[0], sommet_y:sommet_y + result.shape[1], sommet_x:sommet_x + result.shape[2]] = result
        else : 
            new_array[sommet_z:sommet_z+result.shape[0],0:shape_matrix[1], 0:shape_matrix[0]] = result
        return new_array


