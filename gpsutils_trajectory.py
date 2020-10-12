import numpy as np
import pickle
import os

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


def load_data(dataset, pp=False, b=None, num_bin=None):
    # build a hashmap of users
    useridmap = dict()
    min_time = dataset[0][3]
    userids = []
    cartesian_list = []

    for data in dataset:
        userid = data[0]
        userids.append(userid)
        lat = data[1]
        lon = data[2]
        time = data[3]

        x, y, z = get_cartesian(lat, lon)
        t = time - min_time

        vec = [x, y, z, t]
        if pp == True:
            vec = get_quantized_vec(b, [vec], num_bin)[0]
        cartesian_list.append(vec)

        if not userid in useridmap:
            useridmap[userid] = []

        useridmap[userid].append(vec)

    return np.asarray(userids), useridmap, np.asarray(cartesian_list)


def superbit_hyperplanes(d, n, l):
    #  Super-Bit depth n must be [1 .. d] and number of Super-Bit l in [1 ..
    #  The resulting code length k = n * l
    #  The K vectors are orthogonalized in L batches of N vectors
    #  @param d data space dimension
    #  @param n Super-Bit depth [1 .. d]
    #  @param l number of Super-Bit [1 ..
    #  @param seed to use for the random number generator

    if d < 0:
        print('Dimension d must be >= 1')
        exit(0)
    if n < 1 or n > d:
        print('Super-Bit depth N must be 1 <= N <= d')
        exit(0)
    if l < 1:
        print('Number of Super-Bit L must be >= 1')
        exit(0)

    # Input: Data space dimension d, Super-Bit depth 1 <= N <= d,
    # number of Super-Bit L >= 1,
    # resulting code length K = N * L
    #
    # Generate a random matrix H with each element sampled independently
    # from the normal distribution
    # N (0, 1), with each column normalized to unit length.
    # Denote H = [v1, v2, ..., vK].
    np.random.seed(12345)
    code_length = n * l
    v = np.random.normal(size=(code_length, d))
    for i in range(code_length):
        v[i] = v[i] / np.linalg.norm(v[i])

    w = np.zeros((code_length, d))
    for i in range(l):
        for j in range(1, n+1):
            w[i * n + j - 1] = v[i * n + j - 1]
            for k in range(1, j):
                w[i * n + j - 1] = w[i * n + j - 1] - np.dot(w[i * n + k - 1], v[i * n + j - 1]) * w[i * n + k - 1]
            w[i * n + j - 1] = w[i * n + j - 1] / np.linalg.norm(w[i * n + j - 1])
    return w


def get_quantized_vec(b, v, num_bin):
    q = []
    for i in range(len(v)):
        v[i] = v[i] / np.linalg.norm(v[i])
        proj = np.dot(b, v[i])
        proj = proj / np.linalg.norm(proj)
        proj = np.ceil(proj * num_bin) / num_bin
        q.append(proj)
    q = np.asarray(q)
    return q

def loadSecureUserMap(hyp, userinfomap, num_bin):
    # build a hashmap of users
    for userid in userinfomap:
        proj_map = []
        for i in range(len(userinfomap[userid])):
            v = userinfomap[userid][i]
            v = v / np.linalg.norm(v)
            proj = np.dot(hyp, v)
            proj = proj / np.linalg.norm(proj)
            proj = np.ceil(proj * num_bin) / num_bin
            proj_map.append((proj))
        userinfomap[userid] = proj_map
    return userinfomap

def get_gt(gtfile):
    nn_gt = {}
    fp_gt = open(gtfile, 'r')
    lines = fp_gt.readlines()
    fp_gt.close()
    for i in range(len(lines)):
        line = lines[i].split(sep='\t')
        nn_gt[int(line[0])] = [int(i) for i in line[1].strip().split()]
    return nn_gt

def save_variables(DATA_FILE, userids, userinfomap, data_matrix, secure=False, depth_sb=None, num_sb=None, bins=None):
    userids_path = DATA_FILE + '_userids' + '.pkl'
    if secure == False:
        data_matrix_path = DATA_FILE + '_cartesian' + '.pkl'
        userinfomap_path = DATA_FILE + '_userinfomap' + '.pkl'
    else:
        data_matrix_path = DATA_FILE + '_quantized_' + str(depth_sb) + '_' + str(num_sb) + '_' + str(bins) + '.pkl'
        userinfomap_path = DATA_FILE + '_quantized_userinfomap_' + str(depth_sb) + '_' + str(num_sb) + '_' + str(bins) + '.pkl'

    print('Saving userids in pkl ...')
    fp = open(userids_path, 'wb')
    pickle.dump(userids, fp, protocol=4)
    fp.close()

    print('Saving quantized vec in pkl ...')
    fp = open(data_matrix_path, 'wb')
    pickle.dump(data_matrix, fp, protocol=4)
    fp.close()

    print('Saving quantized userinfomap in pkl ...')
    fp = open(userinfomap_path, 'wb')
    pickle.dump(userinfomap, fp, protocol=4)
    fp.close()

    if secure == True:
        print('Quantized data shape %s Number of bins %d\n' % (str(np.shape(data_matrix)), bins))
        outf = open(DATA_FILE + '.out', 'a')
        outf.write('Quantized data shape %s Number of bins %d\n' % (str(np.shape(data_matrix)), bins))
        outf.close()


def load_variables(DATA_FILE, secure=False, depth_sb=None, num_sb=None, bins=None):
    success = False
    userids_path = DATA_FILE + '_userids' + '.pkl'

    if secure == False:
        data_matrix_path = DATA_FILE + '_cartesian' + '.pkl'
        userinfomap_path = DATA_FILE + '_userinfomap' + '.pkl'
    else:
        data_matrix_path = DATA_FILE + '_quantized_' + str(depth_sb) + '_' + str(num_sb) + '_' + str(bins) + '.pkl'
        userinfomap_path = DATA_FILE + '_quantized_userinfomap_' + str(depth_sb) + '_' + str(num_sb) + '_' + str(bins) + '.pkl'
    # print([userids_path, data_matrix_path, userinfomap_path])
    if os.path.exists(userids_path) and \
            os.path.exists(data_matrix_path) and \
            os.path.exists(userinfomap_path):
        success = True

    if success == True:
        print("Loading user ids from pkl...")
        fp = open(userids_path, 'rb')
        userids = pickle.load(fp)
        fp.close()

        print("Loading data matrix from pkl...")
        fp = open(data_matrix_path, 'rb')
        data_matrix = pickle.load(fp)
        fp.close()

        print("Loading userinfomap from pkl...")
        fp = open(userinfomap_path, 'rb')
        userinfomap = pickle.load(fp)
        fp.close()

        if secure == True:
            print('Quantized data shape %s Number of bins %d\n' % (str(np.shape(data_matrix)), bins))
            outf = open(DATA_FILE + '.out', 'a')
            outf.write('Quantized data shape %s Number of bins %d\n' % (str(np.shape(data_matrix)), bins))
            outf.close()
        return success, userids, userinfomap, data_matrix
    else:
        return success, [], [], []
