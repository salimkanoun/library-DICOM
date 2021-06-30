import pydicom
import numpy as np
from dicom_to_cnn.enums.TagEnum import *
from dicom_to_cnn.enums.SopClassUID import *

class Instance:
    """A class to represent a Dicom file 
    """

    def __init__(self, path:str, load_image:bool=True):
        """Construct a Dicom file object

        Args:
            path (str): [path of instance dicom]
            load_image (bool, optional): [choose to load only metadata or metadata+image]. Defaults to True.
        """
        self.path = path
        if (load_image) : self.__load_full_instance()
        else : self.__load_metadata()

    def __load_metadata(self):
        """load only metadata 
        """
        self.dicomData = pydicom.dcmread(self.path, stop_before_pixels=True, force=True)
    
    def __load_full_instance(self):
        """load metadata and image 
        """
        self.dicomData = pydicom.dcmread(self.path, force=True)
  
    def get_series_tags(self) -> dict :
        """method to gather series tags 

        Returns:
            [dict]: [dictionnary of every series tags and value]
        """
        series_tags={}
        for tag_address in TagsSeries:
            if tag_address.value in self.dicomData :
                series_tags[tag_address.name] = self.dicomData[tag_address.value].value
            else : series_tags[tag_address.name] = "Undefined"
        series_tags[ImageType.ImageType.name] = self.get_image_type()
        series_tags[PixelSpacing.PixelSpacing.name] = self.get_pixel_spacing()
        return series_tags

    def get_patients_tags(self) -> dict :
        """method to gather patient tags 

        Returns:
            [dict]: [dictionnary of every patient tags and value]
        """
        patient_tags={}
        for tag_address in TagsPatient:
            if tag_address.value in self.dicomData : 
                patient_tags[tag_address.name] = self.dicomData[tag_address.value].value
                if( type(self.dicomData[tag_address.value].value) != str):
                    #patient name return PersonName3 object, convert it to string
                    patient_tags[tag_address.name] = str(patient_tags[tag_address.name])
            else : patient_tags[tag_address.name] = "Undefined"
        return patient_tags

    def get_studies_tags(self) -> dict :
        """method to gather study tags 

        Returns:
            [dict]: [dictionnary of every study tags and value]
        """
        studies_tags={}
        for tag_address in TagsStudy:
            if tag_address.value in self.dicomData : studies_tags[tag_address.name] = self.dicomData[tag_address.value].value
            else : studies_tags[tag_address.name] = "Undefined"
        return studies_tags

    def get_instance_tags(self) -> dict :
        """method to gather instance tags 

        Returns:
            [dict]: [dictionnary of every instance tags and value]
        """
        instance_tags={}
        instance_tags['PixelSpacing'] = self.get_pixel_spacing()
        instance_tags['ImagePosition'] = self.get_image_position()
        instance_tags['ImageOrientation'] = self.get_image_orientation()
        instance_tags['RescaleSlope'] = self.get_rescale_slope()
        instance_tags['RescaleIntercept'] = self.get_rescale_intercept()
        instance_tags['SOPInstanceUID'] = self.get_SOPInstanceUID()
        return instance_tags

    def get_radiopharmaceuticals_tags(self) -> dict :
        """method to gather radiopharmaceutical tags 

        Returns:
            [dict]: [dictionnary of every radiopharmaceutical tags and value]
        """
        radiopharmaceuticals_tags={}
        radiopharmaceutical_sequence = []
        try :
            radiopharmaceutical_sequence = self.dicomData[0x00540016][0]
        except Exception: 
            print("no Radiopharmaceuticals tags")
        for tag_address in TagsRadioPharmaceuticals:
            if tag_address.value in radiopharmaceutical_sequence : radiopharmaceuticals_tags[tag_address.name] = radiopharmaceutical_sequence[tag_address.value].value
            else : radiopharmaceuticals_tags[tag_address.name] = "Undefined"

        return radiopharmaceuticals_tags
    
    def get_philips_private_tags(self) -> dict :
        """method to gather philips private tags 

        Returns:
            [dict]: [dictionnary of every philips private tags and value]
        """
        philips_tags={}
        for tag_address in PhilipsPrivateTags:
            if tag_address.value in self.dicomData : 
                philips_tags[tag_address.name] = float(self.dicomData[tag_address.value].value)
            else : philips_tags[tag_address.name] = "Undefined"
        return philips_tags

    def get_pet_correction_tags(self) -> dict :
        """method to gather pet correction tags 

        Returns:
            [dict]: [dictionnary of every pet correction tags and value]
        """
        if TagPTCorrection.CorrectedImage.value in self.dicomData :
            return list(self.dicomData[TagPTCorrection.CorrectedImage.value].value)
        else: return "Undefined"

    def get_sop_class_uid(self) -> str :
        """method to get sop class uid 

        Raises:
            Exception: [raise exception if undefined SOPClassUID]

        Returns:
            [str]: [return SOPClassUID value if defined]
        """
        if 'SOPClassUID' in self.dicomData.dir() : return self.dicomData.SOPClassUID
        else : raise Exception('Undefined SOP Class UID')

    def is_secondary_capture(self) -> bool :
        """check if SOPClassUID in CapturesSOPClass list

        Returns:
            [bool]: [return True if SOPCLassUID in CapturesSOPClass list, False instead]
        """
        return True if self.get_sop_class_uid in CapturesSOPClass else False

    def get_SOPInstanceUID(self) -> str:
        """get SOPInstanceUID value

        Returns:
            str: [description]
        """
        return self.dicomData[TagsInstance.SOPInstanceUID.value].value

    def get_rescale_slope(self) -> str:
        """get rescale slope value

        Returns:
            str: [description]
        """
        return self.dicomData[TagsInstance.RescaleSlope.value].value

    def get_rescale_intercept(self) -> str:
        """get rescale intercept value

        Returns:
            str: [description]
        """
        return self.dicomData[TagsInstance.RescaleIntercept.value].value

    def get_image_orientation(self) -> list:
        """get image orientation value x,y,z

        Returns:
            list: [description]
        """
        return list(self.dicomData[TagsInstance.ImageOrientation.value].value)
    
    def get_image_position(self) -> list:
        """get image position value x,y,z

        Returns:
            list: [description]
        """
        return list(self.dicomData[TagsInstance.ImagePosition.value].value)

    def get_pixel_spacing(self) -> list:
        """get pixel spacing value x,y

        Returns:
            list: [description]
        """
        return list(self.dicomData[PixelSpacing.PixelSpacing.value].value)    
        
    def get_image_type(self) -> list:
        """get Image type value 

        Returns:
            list: [description]
        """
        return list(self.dicomData[ImageType.ImageType.value].value)

    def get_series_instance_uid(self) -> str:
        """get Series Instance UID value

        Returns:
            str: [description]
        """
        return self.dicomData[TagsSeries['SeriesInstanceUID'].value].value
    
    def get_accession_number(self) -> str:
        """get Accession Number value

        Returns:
            str: [description]
        """
        return self.dicomData[TagsStudy['AccessionNumber'].value].value 

    def get_patient_name(self) -> str:
        """get Patient Name value

        Returns:
            str: [description]
        """
        return self.dicomData[TagsPatient['PatientName'].value].value

    def get_patient_id(self) -> str:
        """get patient ID value

        Returns:
            str: [description]
        """
        return self.dicomData[TagsPatient['PatientID'].value].value

    def get_patient_birth_date(self) -> str:
        """get Patient Birth Date value

        Returns:
            str: [description]
        """
        return self.dicomData[TagsPatient['PatientBirthDate'].value].value

    def get_patient_sex(self) -> str:
        """get Patient sex value

        Returns:
            str: [description]
        """
        return self.dicomData[TagsPatient['PatientSex'].value].value 

    def get_study_date(self) -> str:
        """get study date value

        Returns:
            str: [description]
        """
        return self.dicomData[TagsStudy['StudyDate'].value].value

    def get_study_description(self) -> str:
        """get Study Description value

        Returns:
            str: [description]
        """
        try : 
            return self.dicomData[TagsStudy['StudyDescription'].value].value 
        except Exception : 
            return ''

    def get_study_id(self) -> str:
        """get study id value

        Returns:
            str: [description]
        """
        return self.dicomData[TagsStudy['StudyID'].value].value 

    def get_study_instance_uid(self) -> str:
        """get study instance uid value

        Returns:
            str: [description]
        """
        return self.dicomData[TagsStudy['StudyInstanceUID'].value].value

    def get_study_time(self) -> str:
        """ get study time value 

        Returns:
            str: [description]
        """
        return self.dicomData[TagsStudy['StudyTime'].value].value

    def get_number_rows(self) -> str:
        """get number of rows value

        Returns:
            str: [description]
        """
        return self.dicomData.Rows

    def get_number_columns(self) -> str:
        """get number of columns value

        Returns:
            str: [description]
        """
        return self.dicomData.Columns

    def get_frame_of_reference_uid(self) -> str:
        """get frame of reference uid value

        Returns:
            str: [description]
        """
        return self.dicomData.FrameOfReferenceUID

    def get_acquisition_date(self) -> str:
        """get acquisition date value

        Returns:
            str: [description]
        """
        if "AcquisitionDate" in self.dicomData : 
            return self.dicomData.AcquisitionDate
        else : return "Undefined"
        
    def get_acquisition_time(self) -> str:
        """get acquisition time value

        Returns:
            str: [description]
        """
        if 'AcquisitionTime' in self.dicomData : 
            return self.dicomData.AcquisitionTime
        else : return "Undefined"

    def get_referring_physician_name(self) -> str:
        """get referring physician name value

        Returns:
            str: [description]
        """
        if "ReferringPhysicianName" in self.dicomData : return self.dicomData.ReferringPhysicianName
        else : return ''

    def get_specific_character_set(self) -> str:
        """get specific chracter set value

        Returns:
            str: [description]
        """
        if "SpecificCharacterSet" in self.dicomData : return self.dicomData.SpecificCharacterSet
        else : return ''

    def get_physicians_of_record(self) -> str:
        """geet physicians of record value

        Returns:
            str: [description]
        """
        if "PhysiciansOfRecord" in self.dicomData : return self.dicomData.PhysiciansOfRecord
        else : return ''
 
    def is_image_modality(self) -> bool :
        """check if SOPClassUID in sop values list 

        Returns:
            [bool]: [return True if SOPCLassUID in sop values list]
        """
        sop_values = set(item.value for item in ImageModalitiesSOPClass)
        return True if self.get_sop_class_uid() in sop_values else False

    def get_image_nparray(self) -> np.ndarray:
        """get instance image ndarray 

        Raises:
            Exception: [raise Exception if SOPClassUID not in sop values list]

        Returns:
            [ndarray]: [return instance image ndarray]
        """
        if self.is_image_modality() == False : 
            raise Exception('Not Image Modality')
        else:
            pixel_array = self.dicomData.pixel_array
            rescale_slope = self.get_rescale_slope()
            rescale_intercept = self.get_rescale_intercept()

            resultArray = ( pixel_array * rescale_slope) + rescale_intercept
            return resultArray



        


    




    

    