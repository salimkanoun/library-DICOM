import numpy as np
import SimpleITK as sitk 
import matplotlib.pyplot as plt
from skimage.feature import peak_local_max
from skimage.segmentation import watershed
import scipy.ndimage
from skimage import morphology


class Watershed:
    """A class to generate subsegmentation mask with a watershed model
    """

    def __init__(self, binary_img:sitk.Image, pet_img:sitk.Image):
        """constructor

        Args:
            binary_img (sitk.Image): [binary segmentation sitk.Image (x,y,z) ]
            pet_img (sitk.Image): [pet sitk.Image associated (x,y,z)]
        """
        self.binary_img = binary_img
        self.pet_img = pet_img
        self.binary_array = sitk.GetArrayFromImage(self.binary_img) #(z,y,x)
        self.pet_array = sitk.GetArrayFromImage(self.pet_img) # (z,y,x)
        self.generated_connected_component_img()

    def generated_connected_component_img(self) -> None :
        """method to generate a first labelled img and its np.ndarray by connected component
        """
        self.labelled_img = sitk.ConnectedComponent(self.binary_img)
        self.labelled_array = sitk.GetArrayFromImage(self.labelled_img) #(z,y,x)
        self.number_of_cc = int(np.max(self.labelled_array))

    def get_suv_values_matrix(self, label:int) -> np.ndarray:
        """method to get a new SUV ndarray for a chosen label

        Args:
            label ([int]): [a chosen label]

        Returns:
            [np.ndarray]: [description]
        """
        new_matrix_pet = np.zeros(self.labelled_array.shape) #(z,y,x)
        new_matrix_pet[np.where(self.labelled_array == label)] = self.pet_array[np.where(self.labelled_array== label)]
        return new_matrix_pet

    def get_mask_roi_matrix(self, label:int) -> np.ndarray:
        """method to get a new ROI ndarray for a chosen label

        Args:
            label (int): [a choosen label]

        Returns:
            [np.ndarray]: [description]
        """
        new_matrix_roi = np.zeros(self.labelled_array.shape)
        new_matrix_roi[np.where(self.labelled_array == label)] = 1
        return new_matrix_roi.astype(np.uint8)

    def get_distance_map(self, array:np.ndarray) -> np.ndarray:
        """generate distance map of a given array

        Args:
            array (np.ndarray): [np.ndarray (z,y,x)]

        Returns:
            [np.ndarray]: [return distance map of the given array]
        """
        return scipy.ndimage.distance_transform_edt(array)

    def get_local_peak(self, distance_map:np.ndarray) -> np.ndarray:
        """calculate local peak from a given distance map (np.ndarray)

        Args:
            distance_map (np.ndarray): [a 3D ndarray/distance map (z,y,x)]

        Returns:
            [np.ndarray]: [return a np.ndarray with local peak points (= 1)]
        """
        spacing = []
        pet_spacing = self.pet_img.GetSpacing()
        spacing.append(float(pet_spacing[0]) * 10**(-1))
        spacing.append(float(pet_spacing[1]) * 10**(-1))
        spacing.append(float(pet_spacing[2]) * 10**(-1))     
        min_dist = int(2/np.mean(spacing))
        return peak_local_max(distance_map, indices = False, min_distance=min_dist)


    def define_marker_array(self, localMax:np.ndarray) -> tuple:
        """method to attribute a label on every local peak points

        Args:
            localMax (np.ndarray): [a np.ndarray with local peak points (z,y,x)]

        Returns:
            [tuple]: [return a labelled local peak points np.ndarray and the number of local peak points]
        """
        marker_array, num_features = scipy.ndimage.label(localMax) 
        return marker_array.astype(np.uint8), num_features
 

    def applied_watershed_model(self) -> sitk.Image : 
        """applied watershed model process

        Returns:
            [sitk.Image]: [return the watershed labelled sitk.Image]
        """
        new_coordonates = []
        pet_spacing = self.pet_img.GetSpacing()
        volume_voxel = pet_spacing[0] * pet_spacing[1] * pet_spacing[2] * 10**(-3) #in ml 
        labels = np.arange(1, self.number_of_cc+1, 1)
        for label in labels: 
            pixel_roi = int(len(np.where(self.labelled_array == label)[0]))
            volume_roi = pixel_roi * volume_voxel 
            if volume_roi < int(30) : 
                new_coordonates.append(np.where(self.labelled_array == label))
            else : 
                suv_values= self.get_suv_values_matrix(label)
                localMax = self.get_local_peak(suv_values) 
                marker_array, num_features = self.define_marker_array(localMax)
                if num_features != 0 : 
                    new_label_mask = watershed(image=-suv_values, markers=marker_array, mask=suv_values)
                    new_label_mask = new_label_mask.astype(np.uint8)
                    for new_label in range(1, num_features + 1):
                        if len(np.where(new_label_mask == new_label)[0]) != 0 : 
                            new_coordonates.append(np.where(new_label_mask == new_label))
            
        number_total_of_label = len(new_coordonates)
        watershed_array = np.zeros(self.binary_array.shape)
        for coordonate, label in zip(new_coordonates, np.arange(1, number_total_of_label+1, 1)):
            watershed_array[coordonate] = label 
        pet_spacing = self.pet_img.GetSpacing()
        pet_direction = self.pet_img.GetDirection()
        pet_origin = self.pet_img.GetOrigin()

        watershed_img = sitk.GetImageFromArray(watershed_array)
        watershed_img.SetSpacing(pet_spacing)
        watershed_img.SetOrigin(pet_origin)
        watershed_img.SetDirection(pet_direction)
        
        return watershed_img
        


    @classmethod
    def remove_small_roi(cls, binary_img:sitk.Image, pet_img:sitk.Image) -> sitk.Image:
        """function to remove ROI under 30 ml on a binary sitk.Image

        Args:
            binary_img (sitk.Image): [sitk.Image of size (z,y,x)]
            pet_img (sitk.Image): [sitk.Image of the PET, size (z,y,x)]

        Raises:
            Exception: [raise Exception if not a 3D binary mask]

        Returns:
            [sitk.Image]: [Return cleaned image]
        """

        binary_array = sitk.GetArrayFromImage(binary_img)
        if len(binary_array.shape) != 3 or int(np.max(binary_array)) != 1 : 
            raise Exception("Not a 3D binary mask, need to transform into 3D binary mask")
        else : 
            pet_spacing = pet_img.GetSpacing()
            pet_origin = pet_img.GetOrigin()
            pet_direction = pet_img.GetDirection()
            labelled_img = sitk.ConnectedComponent(binary_img)
            stats = sitk.LabelIntensityStatisticsImageFilter()
            stats.Execute(labelled_img, pet_img)
            labelled_array = sitk.GetArrayFromImage(labelled_img).transpose()
            number_of_label = stats.GetNumberOfLabels()
            volume_voxel = pet_spacing[0] * pet_spacing[1] * pet_spacing[2] * 10**(-3) #in ml 
            for i in range(1, number_of_label + 1) :
                volume_roi = stats.GetNumberOfPixels(i) * volume_voxel
                if volume_roi < float(30) : 
                    x,y,z = np.where(labelled_array == i)
                    for j in range(len(x)):
                        labelled_array[x[j], y[j], z[j]] = 0
            new_binary_array = np.zeros((labelled_array.shape))
            new_binary_array[np.where(labelled_array != 0)] = 1
            new_binary_img = sitk.GetImageFromArray(new_binary_array.transpose().astype(np.uint8))
            new_binary_img.SetOrigin(pet_origin)
            new_binary_img.SetSpacing(pet_spacing)
            new_binary_img.SetDirection(pet_direction)
            return new_binary_img
