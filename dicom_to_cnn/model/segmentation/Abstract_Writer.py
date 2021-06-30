import SimpleITK as sitk 
import abc 

class Abstract_Writer(metaclass = abc.ABCMeta) : 
    """abstract class to write segmentation
    """

    @abc.abstractmethod
    def save_file(self, filename:str, directory_path:str) -> None :
        pass 

