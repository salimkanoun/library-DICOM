import pydicom
import datetime
import random 
import os 
import numpy as np 
import tempfile 
import SimpleITK as sitk 
from skimage.measure import label 
from dicom_to_cnn.model.segmentation.Abstract_Writer import Abstract_Writer
from dicom_to_cnn.model.reader.Series import Series
from dicom_to_cnn.model.segmentation.rtstruct.StructureSetROISequence import StructureSetROISequence
from dicom_to_cnn.model.segmentation.rtstruct.RTROIObservationsSequence import RTROIObservationsSequence
from dicom_to_cnn.model.segmentation.rtstruct.ROIContourSequence import ROIContourSequence
from dicom_to_cnn.model.segmentation.rtstruct.ReferencedFrameOfReferenceSequence import *
from dicom_to_cnn.tools.export_segmentation.generate_dict import *


class RTSS_Writer(Abstract_Writer):
    """A class to write a DICOM RTSTRUCT file
    """
    
    def __init__(self, mask_img:sitk.Image, serie_path:str):
        """constructor
        Args:
            mask ([sitk.Image]): [3D sitk.Image of segmentation (x,y,z), labelled or not]
            serie_path ([str]): [Serie path related to RTSTRUCT file ]
        """
        #SERIE
        self.mask_img = mask_img#GetSize() = [x,y,z]
        serie = Series(serie_path)
        self.instances = serie.get_instances_ordered()

        #Get list of every sop instance uid from associated serie
        self.list_all_SOPInstanceUID = serie.get_all_SOPInstanceIUD()

        #MASKs
        self.mask_array = sitk.GetArrayFromImage(self.mask_img) #shape = [z,x,y]
        self.mask_array = self.__clean_mask()
        self.image_position = self.mask_img.GetOrigin()
        self.pixel_spacing = self.mask_img.GetSpacing()
        self.image_direction = self.mask_img.GetDirection()

        #get number of ROI 
        self.number_of_roi = int(np.max(self.mask_array))


    def setDictName(self, name:str) -> str : 
        """set the dict name 

        Args:
            name (str): [dict name]

        """
        self.dict_name = name

    def setBodyPartExaminated(self, name:str) -> str : 
        """set the body part examinated

        Args:
            name (str): [name of the body part]

        """
        if len(name) > 16 : self.body_part =  name[0:16]
        else : self.body_part = name 

    def setSeriesDescription(self, description:str) -> str : 
        """set the study description of the exam

        Args:
            description (str): [study description]


        """
        if len(description) > 16 : self.serie_description =  description[0:16]
        else : self.serie_description = description 

    def setRTROIInterpretedType(self, dictionnary:dict) -> dict : 
        """set a dict for the RTROIInterpretedType value for each ROI

        Args:
            dictionnary (dict): [{1 : value,
                                  2 : value, 
                                  etc }]

        """ 
        self.roi_type_dict = dictionnary

    def setAutoRTROIInterpretedType(self)-> dict : 
        """set an auto dict with RTROIINterpretedType value 

            generated dict  {1 : '', 
                            2 : '', 
                            etc }]
        """
        number_of_roi = int(np.max(self.mask_array))
        dictionnary = {}
        for i in range(1, number_of_roi+1):
            dictionnary[i] = str('')
        self.roi_type_dict = dictionnary

    def setRoiName(self, dictionnary:dict) -> dict : 
        """set a dict for ROI Name, for each ROI

        Args:
            dictionnary (dict): [{1 : 'name roi 1', 
                                  2:'name roi 2', 
                                 etc }]

        """
        self.roi_name_dict = dictionnary

    def setAutoRoiName(self) -> dict : 
        """set an auto dict with ROI Name value 

            generated dict  {1 : 'ROI 1', 
                            2 : 'ROI 2', 
                                etc }]
        """
        mask_array = sitk.GetArrayFromImage(self.mask_img)
        number_of_roi = int(np.max(mask_array))
        dictionnary = {}
        for i in range(1, number_of_roi+1):
            dictionnary[i] = str("ROI {}".format(i+1))
        self.roi_name_dict =  dictionnary

    def __generate_dict_json(self) -> str:
        results = generate_dict(self.number_of_roi, self.dict_name, self.serie_description, self.body_part, self.roi_name_dict, interpreted_type=self.roi_type_dict)
        self.results = results

    def __clean_mask(self) -> np.ndarray:
        """a function to clean mask : remove pixel (=1) when there is less than 3 pixels (=1) in slice

        Args:
            mask (np.ndarray): [mask of shape [z,y,x]]

        Returns:
            [ndarray]: [return the cleaned mask in shape [z,y,x]]
        """
        number_of_roi = int(np.max(self.mask_array))
        binary_mask = np.where(self.mask_array>0, 1, 0)
        
        empty_mask = np.zeros((self.mask_array.shape))
        for s in range(self.mask_array.shape[0]) : 
            slice = binary_mask[s, :, :]
            if int(np.max(binary_mask[s,:,:])) == 0 : 
                empty_mask[s, :, :] = slice
            else : 
                lw, num = label(slice, connectivity=2, return_num=True) #lw = 2D slice 
                item = np.arange(1, num+1).tolist()
                area = []
                for it in item : 
                    area.append(len(np.where(lw== it)[0]))
                for ar in area : 
                    feature = area.index(ar) + 1 
                    if int(ar) < 3 : 
                        x,y = np.where(lw == feature)
                        lw[x,y] = 0 
                empty_mask[s, :, :] = lw 
        matrix = np.where(empty_mask>0, 1, 0)
        #labelled again 
        label_ = 1
        for i in range(1, number_of_roi+1):
            z,y,x = np.where((matrix > 0) & (self.mask_array == i))
            if len(z) == 0 : 
                pass 
            else : 
                matrix[np.where((matrix > 0) & (self.mask_array == i))] = label_ 
                label_ += 1 
        return matrix

    def generates_file_meta(self) -> tuple:
        """
            Generates required values for file meta information
            List of tags :
                  - FileMetaInformationGroupLength':
                  - FileMetaInformationVersion'    :
                  - MediaStorageSOPClassUID'       :
                  - MediaStorageSOPInstanceUID'    :
                  - TransferSyntaxUID'             :
                  - ImplementationClassUID'        :

        Returns: 
            (tuple): [return file_meta and MediaStorageSOPInstanceUID of the new RTSTRUCT]
        """


        file_meta = pydicom.dataset.FileMetaDataset()
        file_meta.FileMetaInformationGroupLength = 166
        file_meta.FileMetaInformationVersion = b'\x00\x01'
        file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.481.3' # RT Structure Set Storage
        file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
        file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian #pydicom.uid.ImplicitVRLittleEndian 
        file_meta.ImplementationClassUID =  pydicom.uid.PYDICOM_IMPLEMENTATION_UID #'1.2.246.352.70.2.1.7'
        
        return file_meta, file_meta.MediaStorageSOPInstanceUID


    def set_tags(self) -> None:
        """ generate required values from associated dicom serie
            
            List of tags :
                  - AccessionNumber'       :
                  - PatientBirthDate'      :
                  - PatientBirthTime'      :
                  - PatientID'             :
                  - PatientName'           :
                  - PatientSex'            :
                  - PhysiciansOfRecord'    :
                  - ReferringPhysicianName':
                  - SpecificCharacterSet'  :
                  - StudyDate'             :
                  - StudyDescription'      :
                  - StudyID'               :
                  - StudyInstanceUID'      :
                  - StudyTime'             : 
        """     
        #from the serie 
        self.dataset.AccessionNumber = self.instances[0].get_accession_number()
        self.dataset.PatientBirthDate = self.instances[0].get_patient_birth_date()
        self.dataset.PatientID = self.instances[0].get_patient_id()
        self.dataset.PatientName = self.instances[0].get_patient_name()
        self.dataset.PatientSex = self.instances[0].get_patient_sex()
        self.dataset.PhysiciansOfRecord = self.instances[0].get_physicians_of_record()
        self.dataset.ReferringPhysicianName = self.instances[0].get_referring_physician_name()
        self.dataset.SpecificCharacterSet = self.instances[0].get_specific_character_set()
        self.dataset.StudyDate = self.instances[0].get_study_date()
        self.dataset.StudyDescription = self.instances[0].get_study_description()
        self.dataset.StudyID = self.instances[0].get_study_id()
        self.dataset.StudyInstanceUID = self.instances[0].get_study_instance_uid()
        self.dataset.StudyTime = self.instances[0].get_study_time()

        #specific new tags for the serie 
        self.dataset.ApprovalStatus = 'UNAPPROVED'
        self.dataset.Manufacturer   = ''
        dt = datetime.datetime.now()
        self.dataset.InstanceCreationDate = dt.strftime('%Y%m%d')
        self.dataset.InstanceCreationTime = dt.strftime('%H%M%S.%f')
        self.dataset.InstanceNumber = '1'
        self.dataset.Modality = 'RTSTRUCT'
        self.dataset.ReviewDate = '' #because UNAPPROVED
        self.dataset.ReviewTime = '' #because UNAPPROVED
        self.dataset.ReviewerName = '' #because UNAPPROVED
        self.dataset.SeriesDescription = self.results["SeriesDescription"]
        self.dataset.SeriesInstanceUID = pydicom.uid.generate_uid()
        self.dataset.SeriesNumber = random.randint(0,1e3)
        self.dataset.SOPClassUID = '1.2.840.10008.5.1.4.1.1.481.3' 
        self.dataset.SOPInstanceUID = self.file_meta.MediaStorageSOPInstanceUID
        self.dataset.StructureSetDate = dt.strftime('%Y%m%d')
        self.dataset.StructureSetDescription = self.results["SeriesDescription"]
        self.dataset.StructureSetLabel = self.results["SeriesDescription"]
        self.dataset.StructureSetTime = dt.strftime('%H%M%S.%f')

    #StructureSetROISequence
    def set_StructureSetROISequence(self) -> None :
        """method to set StructureSetROISequence from RTSTRUCT file 
        """
        referenced_frame_of_reference_uid = self.instances[0].get_frame_of_reference_uid()
        self.dataset.StructureSetROISequence = StructureSetROISequence(self.mask_array, self.results, self.number_of_roi).create_StructureSetROISequence(self.pixel_spacing, referenced_frame_of_reference_uid)
        
    #RTROIObservationSequence
    def set_RTROIObservationSequence(self) -> None :
        """method to set RTROIObservationSequence from RTSTRUCT file
        """
        self.dataset.RTROIObservationsSequence = RTROIObservationsSequence(self.results, self.number_of_roi).create_RTROIObservationsSequence()
        
    #ROIContourSequence 
    def set_ROIContourSequence(self)-> None:
        """method to set ROIContourSequence from RTSTRUCT file 
        """
        referenced_sop_class_uid = self.instances[0].get_sop_class_uid()
        self.dataset.ROIContourSequence = ROIContourSequence(self.mask_array, self.mask_img, self.number_of_roi).create_ROIContourSequence(referenced_sop_class_uid, self.list_all_SOPInstanceUID)

    #ReferencedFrameOfReferenceSequence 
    def set_ReferencedFrameOfReferenceSequence(self) -> None:
        """method to set ReferencedFrameOfReferenceSequence from RTSTRUCT file
        """
        frame_of_reference_uid = self.instances[0].get_frame_of_reference_uid()
        series_instance_uid = self.instances[0].get_series_instance_uid()
        study_instance_uid = self.instances[0].get_study_instance_uid()
        sop_class_uid = self.instances[0].get_sop_class_uid()
        self.dataset.ReferencedFrameOfReferenceSequence = create_ReferencedFrameOfReferenceSequence(frame_of_reference_uid, sop_class_uid, self.list_all_SOPInstanceUID, series_instance_uid, study_instance_uid)


    def rtstruct_writer(self):
        #generate dictionnary with parameter inside from 'generate_dict.py'
        self.__generate_dict_json()

        #RTSTRUCT FILE 
        #creation file_meta 
        self.file_meta, self.file_meta.MediaStorageSOPInstanceUID = self.generates_file_meta()
        suffix = '.dcm'
        filename_little_endian = tempfile.NamedTemporaryFile(suffix=suffix).name
        self.dataset = pydicom.dataset.FileDataset(filename_little_endian, {}, file_meta=self.file_meta, preamble=b"\0" * 128)

        #Add the data element in FileDataset
        self.set_tags()
        self.set_StructureSetROISequence()
        self.set_RTROIObservationSequence()
        self.set_ROIContourSequence()
        self.set_ReferencedFrameOfReferenceSequence()
        
        # Set the transfer syntax
        self.dataset.is_little_endian = True
        self.dataset.is_implicit_VR = False 

    def save_file(self, filename:str, directory_path:str) -> None :
        """method to save the RTSTRUCT file

        Args:
            filename (str): [name of the RTSTRUCT file]
            directory_path (str): [directory's path where to save the RTSTRUCT file]

        """
        self.rtstruct_writer()
        self.dataset.save_as(os.path.join(directory_path, filename), write_like_original=False)


        
        

    
