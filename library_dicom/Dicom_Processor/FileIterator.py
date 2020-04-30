from library_dicom.Dicom_Processor.Series import Series
import os

def getSeriesPath(path):
    """Go through all the folder to find every series path

    Arguments:
        path {[string]} -- [Absolute path where the repertory is located]

    Returns:
        [list] -- [Path's list of every series]
    """

    seriesPath = []
    for (path, dirs, files) in os.walk(path): 
        if not (dirs) :
            seriesPath.append(path) 
    return seriesPath 


seriesPaths = getSeriesPath('/repertoire')

dicom1 = Series(seriesPaths[0]) #chemin de la premiere série
seriesInfo= dicom1.getSeriesDetails()
#SK OK pas mal tu peux maintenant essayer de boucler sur les series que tu trouve, checker leur contenu et remplir une variable
# qui va contenir un "abre" avec l'ID patient, en clé 1ere, les details du patient (nom) et un array de studies avec comme clé 1er leur series InstanceUID et leurs details puis une array de series
print(seriesInfo)
print(dicom1.isSeriesValid()) #test

#Ici on va faire un script