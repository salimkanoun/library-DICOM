import numpy as np
import os
from os.path import basename,splitext
import SimpleITK as sitk 

from library_dicom.dicom_processor.model.reader.Instance import Instance
from library_dicom.dicom_processor.model.NiftiBuilder import NiftiBuilder
from library_dicom.dicom_processor.enums.TagEnum import *
from library_dicom.dicom_processor.enums.SopClassUID import *

class Series():
    """ A class representing a series Dicom
    """
    
    def __init__(self, path):
        """Construct a Dicom Series Object

        Arguments:
            path {String} -- [Absolute Path where Dicom Series is located (hirachical Dicoms)]
        """

        self.path = path
        self.file_names = os.listdir(path)
        self.number_of_files = len(self.file_names)

    def get_number_of_files(self):
        return self.number_of_files
    
    def get_first_instance_metadata(self):
        firstFileName = self.file_names[0]
        return Instance(os.path.join(self.path,firstFileName), load_image=True)


    def get_series_details(self):
        """Read the first dicom in the folder and store Patient / Study / Series
        informations

        Returns:
            [dict] -- [Return the details of a Serie from the first Dicom]
        """
        self.series_details = {}
        self.patient_details = {}
        self.study_details = {}

        dicomInstance = self.get_first_instance_metadata()

        self.series_details = dicomInstance.get_series_tags()
        self.patient_details = dicomInstance.get_patients_tags()
        self.study_details = dicomInstance.get_studies_tags()
        self.instance_details = dicomInstance.get_instance_tags()
        self.sop_class_uid = dicomInstance.get_sop_class_uid()
        self.is_image_series = dicomInstance.is_image_modality()

        return {
            'series' : self.series_details,
            'study' : self.study_details,
            'patient' : self.patient_details,
            'path' : self.path,
            'files' : self.number_of_files,
            'instance' : self.instance_details
        }

    def is_series_valid(self):
        firstDicomDetails = self.get_series_details()
        #Le tag number of slice n'est que pour PT et NM, pas trouvé d'autre tag fiable pour les autres series
        if firstDicomDetails['series']['NumberOfSlices']!="Undefined" and firstDicomDetails['series']['NumberOfSlices'] != len(self.file_names):
            print('wrong number of slice')
            return False

        for fileName in self.file_names:
            dicomInstance = Instance(os.path.join(self.path, fileName), load_image=False)
            if (dicomInstance.get_series_tags()['SeriesInstanceUID'] != firstDicomDetails['series']['SeriesInstanceUID']):
                print('Not same Series Instance UID')
                return False
        
        return True
        
    def is_image_modality(self):
        return self.get_first_instance_metadata().is_image_modality()

    def is_primary_image(self):
        return ( "PRIMARY" in self.series_details['ImageType'])

    def is_localizer_series(self):
        return ( "LOCALIZER" in self.series_details['ImageType'])


    def get_instances_ordered(self):
        instance_array = [Instance(os.path.join(self.path, file_name), load_image=True) for file_name in self.file_names]
        instance_array.sort(key=lambda instance_array:int(instance_array.get_image_position()[2]))
        self.instance_array = instance_array
        return instance_array 


    def get_numpy_array(self):
        if self.is_image_modality == False : return

        pixel_data = [instance.get_image_nparray() for instance in self.instance_array]
        np_array = np.stack(pixel_data,axis=-1)
        return np_array


    def get_z_positions(self):
        Z_positions = [ instance.get_image_position()[2] for instance in self.instance_array ]
        return Z_positions

    
    def get_z_spacing(self):
        """ called by __getMetadata """
        Z_positions = [ instance.get_image_position()[2] for instance in self.instance_array ]
        #print(Z_positions)
        
        initial_z_spacing = round(abs(Z_positions[0] - Z_positions[1]), 1)
        for i in range(2,len(Z_positions)):

            z_spacing = round(abs(Z_positions[i - 1] - Z_positions[i]), 1)
            if z_spacing < initial_z_spacing - float(0.1) or z_spacing > initial_z_spacing + float(0.1) :
                try : 
                    raise Exception('Unconstant Spacing')
                except Exception : 
                    return('Unconstant Spacing') #alerte #return
        return np.mean(self.calculate_z_spacing(round_=False))
        


    def calculate_z_spacing(self, round_): 
        Z_positions = [ instance.get_image_position()[2] for instance in self.instance_array ]
        spacing = []

        if round_ == False : 
            initial_z_spacing = Z_positions[0] - Z_positions[1]
            spacing.append(initial_z_spacing)
            for i in range(2,len(Z_positions)):
                z_spacing = Z_positions[i - 1] - Z_positions[i]
                spacing.append(z_spacing)

            return spacing

        else : 
            #print(abs(Z_positions[0] - Z_positions[1]))
            initial_z_spacing = round(abs(Z_positions[0] - Z_positions[1]), 1)
            spacing.append(initial_z_spacing)
            for i in range(2,len(Z_positions)):
                z_spacing = round(abs(Z_positions[i - 1] - Z_positions[i]), 1)
                spacing.append(z_spacing)  

            return spacing 



    def export_nifti(self, file_path, mask = None):
        #modality = self.get_modality()

        if (mask is None) : 
            
            #nifti_builder = NiftiBuilder(self)
            #nifti_builder.save_nifti(file_path, mode=mode, mask=None)
            sitk_img = sitk.GetImageFromArray( np.transpose(self.get_numpy_array(), (2,0,1) ))

            original_pixel_spacing = self.instance_array[0].get_pixel_spacing()
            
            original_direction = self.instance_array[0].get_image_orientation()
            sitk_img.SetDirection( (float(original_direction[0]), float(original_direction[1]), float(original_direction[2]), 
                                    float(original_direction[3]), float(original_direction[4]), float(original_direction[5]), 
                                    0.0, 0.0, 1.0) )
            sitk_img.SetOrigin( self.instance_array[0].get_image_position() )
            sitk_img.SetSpacing( (original_pixel_spacing[0], original_pixel_spacing[1], self.get_z_spacing()) )
            sitk.WriteImage(sitk_img, file_path)


        else : 
            
            #nifti_builder = NiftiBuilder(self)
            #nifti_builder.save_nifti(file_path, mode='mask', mask=mask)

            number_of_roi = mask.shape[3] #tjrs de taille 4, si une seule roi=> dernier channel =1
            slices = []
            for number_roi in range(number_of_roi) : 
                slices.append(np.transpose(mask[:,:,:,number_roi], (2,0,1)))
                
            mask_4D = np.stack(slices, axis = 3)
            sitk_img = sitk.GetImageFromArray(mask_4D, isVector = True)
            sitk_img = sitk.Cast(sitk_img, sitk.sitkVectorUInt8)
            
            original_pixel_spacing = self.instance_array[0].get_pixel_spacing()
            original_direction = self.instance_array[0].get_image_orientation()
            sitk_img.SetDirection( (float(original_direction[0]), float(original_direction[1]), float(original_direction[2]), 
                                    float(original_direction[3]), float(original_direction[4]), float(original_direction[5]), 
                                    0.0, 0.0, 1.0) )
            sitk_img.SetOrigin( self.instance_array[0].get_image_position() )
            sitk_img.SetSpacing( (original_pixel_spacing[0], original_pixel_spacing[1], self.get_z_spacing()) )
            sitk.WriteImage(sitk_img, file_path)

    def get_all_SOPInstanceIUD(self):
        liste = []
        for instance in self.instance_array : 
            #instanceData = Instance(os.path.join(self.path,filename), load_image=True)
            liste.append(instance.get_SOPInstanceUID())
        return liste 


    def get_all_acquisition_time(self):
        liste = []
        for filename in self.file_names : 
            instanceData = Instance(os.path.join(self.path,filename), load_image=True)
            liste.append(instanceData.get_acquisition_time())
        return sorted(liste)



    def get_size_matrix(self):
        size = []
        data = self.get_first_instance_metadata()
        x = data.get_number_rows()
        size.append(x)
        y = data.get_number_columns()
        size.append(y)
        z = len(self.get_all_SOPInstanceIUD())
        size.append(z)
        return size



    