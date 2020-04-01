import numpy as np

def get_cartesian(lat=None, lon=None):
    lat, lon = np.deg2rad(lat), np.deg2rad(lon)
    R = 6371 # radius of the earth
    x = R * np.cos(lat) * np.cos(lon)
    y = R * np.cos(lat) * np.sin(lon)
    z = R *np.sin(lat)
    return x,y,z


def convertToCartesian(dataset):    
    cartesian_list = []    
    min_time = dataset[0][3]
    
    for data in dataset:
        lat = data[1]
        lon = data[2]
        time = data[3]
        
        x, y, z = get_cartesian(lat, lon)
        t = time - min_time
        
        cartesian_list.append([x, y, z, t])
    
    cartesian_data = np.asarray(cartesian_list)    
    return cartesian_data

def loadusers(dataset):

    userids = []
    for data in dataset:
        userids.append(data[0])

    return np.asarray(userids)

def loadUserMap(dataset):
    #build a hashmap of users
    useridmap = dict()
    min_time = dataset[0][3]

    for data in dataset:
        userid = data[0]
        lat = data[1]
        lon = data[2]
        time = data[3]

        x, y, z = get_cartesian(lat, lon)
        t = time - min_time
   
        if not userid in useridmap:
            useridmap[userid] = []

        useridmap[userid].append([x, y, z, t])

    return useridmap
