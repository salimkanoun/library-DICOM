import numpy as np

def threshold_matrix(mask_array:np.ndarray, pet_array:np.ndarray, threshold:float) -> np.ndarray:
    """function to threshold a ndarray mask

    Args:
        mask_array (np.ndarray): [(z,x,y,c)]
        pet_array (np.ndarray): [(z,x,y)]
        threshold (float): [0.41, 2.5, 4.0 or other]

    Returns:
        [ndarray]: [threshold mask]
    """
   
    mask_array = mask_array.astype('int8')
    if threshold < 1 : 
        if len(mask_array.shape) != 3 :  #mask 4D 
            number_of_roi = mask_array.shape[3]
            liste = []
            for i in range(number_of_roi):
                new_mask = np.zeros((mask_array.shape[0],mask_array.shape[1], mask_array.shape[2] )).astype('uint8')
                suv_values = []
                x,y,z = np.where(mask_array[:,:,:,i] != 0)
                if len(x) != 0 : 
                    suv_values = pet_array[x,y,z].tolist()
                    seuil = np.max(suv_values) * threshold
                    new_mask[np.where((pet_array > seuil) & (mask_array[:,:,:,i] > 0))] = 1
                    liste.append(new_mask.astype('uint8'))
                else : liste.append(new_mask.astype('uint8'))
            return np.stack(liste, axis = 3).astype('uint8')   

        else : 
            maxi = np.max(mask_array)
            if maxi == 1.0 : 
                new_mask = np.zeros((mask_array.shape[0],mask_array.shape[1], mask_array.shape[2] )).astype('uint8')
                x,y,z = np.where(mask_array != 0)
                suv_values = pet_array[x,y,z].tolist()
                seuil = np.max(suv_values) * threshold
                new_mask[np.where((pet_array > seuil) & (mask_array > 0))] = 1
                return new_mask.astype('uint8')
            else :  
                number_of_roi = maxi
                new_mask = np.zeros((mask_array.shape[0],mask_array.shape[1], mask_array.shape[2] )).astype('uint8')
                for i in range(number_of_roi):
                    suv_values = []
                    x,y,z = np.where(mask_array == i+1)
                    suv_values = pet_array[x,y,z].tolist()
                    seuil = np.max(suv_values) * threshold

                    new_mask[np.where((pet_array > seuil) & (mask_array == i+1))] = i+1
                return new_mask.astype('uint8')

    else : 
        if len(mask_array.shape) != 3 :  #mask 4D 
            number_of_roi = mask_array.shape[3]
            liste = []
            for i in range(number_of_roi):
                new_mask = np.zeros((mask_array.shape[0],mask_array.shape[1], mask_array.shape[2] )).astype('uint8')
                seuil = threshold
                new_mask[np.where((pet_array > seuil) & (mask_array[:,:,:,i] > 0))] = 1
                liste.append(new_mask)
            return np.stack(liste, axis = 3)    

        else : 
            maxi = np.max(mask_array)
            if maxi == 1.0 : 
                new_mask = np.zeros((mask_array.shape[0],mask_array.shape[1], mask_array.shape[2] )).astype('uint8')
                seuil = threshold
                new_mask[np.where((pet_array > seuil) & (mask_array > 0))] = 1
                return new_mask.astype('uint8')
            else :  
                number_of_roi = maxi
                new_mask = np.zeros((mask_array.shape[0],mask_array.shape[1], mask_array.shape[2] )).astype('uint8')
                seuil = threshold
                for i in range(number_of_roi):
                    new_mask[np.where((pet_array > seuil) & (mask_array == i+1))] = i+1
                return new_mask.astype('uint8')





