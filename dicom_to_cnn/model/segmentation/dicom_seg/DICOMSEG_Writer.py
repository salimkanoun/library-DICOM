import pydicom_seg 
import pydicom 
import numpy as np 
import os
from dicom_to_cnn.tools.export_segmentation.generate_dict import *
from dicom_to_cnn.model.segmentation.Abstract_Writer import Abstract_Writer
import SimpleITK as sitk 


class DICOMSEG_Writer(Abstract_Writer):
    """a class to write a DICOMSEG file
    """

    def __init__(self, mask_img:sitk.Image, serie_path:str):
        """constructor

        Args:
            img_mask ([sitk.Image]): [sitk img of segmentation, [x,y,z]]
            serie_path ([str]): [Serie path related to DICOMSEG file]
        """
        self.mask_img = mask_img
        self.serie_path = serie_path

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
        if len(description) > 16 : self.serie_description = description[0:16]
        else : self.serie_description =  description 

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


    def __generate_dict_json(self, directory_path:str) -> str:
        """method to generate dict with metainfo for DICOM SEG file and save it as json file

        Args:
            directory_path (str): [directory's path where to save the json file with metainfo]

        Returns:
            [str]: [return the path of the json generated]
        """
        number_of_roi = int(np.max(sitk.GetArrayFromImage(self.mask_img)))
        results = generate_dict(number_of_roi, self.dict_name, self.serie_description, self.body_part, self.roi_name_dict, interpreted_type=None)
        self.results = results
        json_path = save_dict_as_json(results, directory_path)
        return json_path 

    def dicom_seg_writer(self, directory_path:str) -> pydicom.FileDataset:
        """method to write a DICOMSEG file from a segmentation

        Args:
            directory_path (str): [directory's path where to save the json file with metainfo]

        Returns:
            [pydicom.FileDataset]: [return the new DICOMSEG]
        """
        json_path = self.__generate_dict_json(directory_path)

        segmentation = self.mask_img
        dicom_file = os.listdir(self.serie_path)
        dicom_series_paths = [os.path.join(self.serie_path, x) for x in dicom_file]
        source_images = [
            pydicom.dcmread(x, stop_before_pixels=True)
            for x in dicom_series_paths]

        template = pydicom_seg.template.from_dcmqi_metainfo(json_path)

        writer = pydicom_seg.MultiClassWriter(
                template=template,
                inplane_cropping=False,  # Crop image slices to the minimum bounding box on
                                        # x and y axes. Maybe not supported by other frameworks.
                skip_empty_slices=True,  # Don't encode slices with only zeros
                skip_missing_segment=False,  # If a segment definition is missing in the
                                            # template, then raise an error instead of
                                            # skipping it.
            )

        dcm = writer.write(segmentation, source_images)
        os.remove(json_path)
        return dcm


    def save_file(self, filename:str, directory_path:str) -> None :
        """method to save the new DICOMSEG file

        Args:
            filename (str): [name of the new DICOMSEG file]
            directory_path (str): [directory's path where to save the new DICOMSEG file]

        """
        dcm = self.dicom_seg_writer(directory_path)
        dcm.save_as(os.path.join(directory_path, filename))