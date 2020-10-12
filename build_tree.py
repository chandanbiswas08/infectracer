#!/usr/bin/env python
# coding: utf-8

import numpy as np
import sys, getopt
import os
import sys
import nmslib
import time
import datetime
from time import process_time
import math
import random as r
from gpsutils_trajectory import get_quantized_vec
from gpsutils_trajectory import superbit_hyperplanes
from gpsutils_trajectory import loadSecureUserMap
from gpsutils_trajectory import get_gt
from gpsutils_trajectory import get_cartesian
from gpsutils_trajectory import loadusers
from gpsutils_trajectory import loadUserMap
from gpsutils_trajectory import convertToCartesian
from gpsutils_trajectory import load_data
from gpsutils_trajectory import save_variables
from gpsutils_trajectory import load_variables
from sklearn.neighbors import KDTree
from sklearn.neighbors import NearestNeighbors
from scipy.linalg import orth
import pickle
import subprocess
from subprocess import PIPE

SEED=12345
np.random.seed(SEED)


def main(argv):
    DATA_FILE = None
    algo = 'kd_tree'
    load = False
    secure = False
    bins = 32
    depth_sb = 3
    num_sb = 5

    try:
        opts, args = getopt.getopt(argv,"h:d:l:", ["datafile=", "load=", "secure=", "depth_sb=", "num_sb=", "bins="])

        for opt, arg in opts:
            if opt == '-h':
                print ('build_tree.py -d/--datafile= <datafile> -i/--index= <index file> -s/--sick= <fraction sick> -n/--nusers= <nusers>')
                sys.exit()
            elif opt in ("-d", "--datafile"):
                DATA_FILE = arg
            elif opt in ("-l", "--load"):
                if arg == 'True':
                    load = True
                else:
                    load = False
            elif opt in ("--secure"):
                if arg == 'True':
                    secure = True
                else:
                    secure = False
            elif opt in ("--depth_sb"):
                depth_sb = int(arg)
            elif opt in ("--num_sb"):
                num_sb = int(arg)
            elif opt in ("--bins"):
                bins = int(arg)

    except getopt.GetoptError:
        print ('usage: build_tree.py -d <datafile> --load <True/False> --secure <True/False>')
        sys.exit()

    if (DATA_FILE==None):
        print ('usage: build_tree.py -d <datafile>')
        sys.exit()

    print('\n\nAlgorithm name %s' % algo)
    print('Data file name %s' % DATA_FILE)
    now = datetime.datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    outf = open(DATA_FILE + '.out', 'a')
    outf.write('\n\n%s\nAlgorithm name %s\nData file name %s\n\n' % (dt_string, algo, DATA_FILE))
    # print(subprocess.run(['lscpu']))
    proc = subprocess.run(['lscpu'], stdout=PIPE, stderr=PIPE)
    mc_info = proc.stdout.splitlines()
    for line in mc_info:
        outf.write(line.decode("utf-8") + '\n')
    outf.write('\n')
    outf.close()

    if load == True:
        success, userids, userinfomap, data_matrix = load_variables(DATA_FILE, secure, depth_sb, num_sb, bins)
    else:
        success, userids, userinfomap, data_matrix = False, [], [], []

    if success == False:
        print ("Reading data file...")
        data_matrix = np.loadtxt(DATA_FILE)
        if secure == True:
            hyp = superbit_hyperplanes(4, depth_sb, num_sb)     #Assuming after cartesian conversion data_dim=4
            userids, userinfomap, data_matrix = load_data(data_matrix, secure, hyp, bins)
            save_variables(DATA_FILE, userids, userinfomap, data_matrix, secure, depth_sb, num_sb, bins)
        else:
            userids, userinfomap, data_matrix = load_data(data_matrix)
            save_variables(DATA_FILE, userids, userinfomap, data_matrix)

    if secure == True:
        tree_path = DATA_FILE + '_' + str(secure) + '_' + str(depth_sb) + '_' + str(num_sb) + '_' + str(bins) + '.nbd'
    else:
        tree_path = DATA_FILE + '.nbd'

    start = time.time()
    print('Creating nbrs...')
    nbrs = NearestNeighbors(algorithm=algo, metric='euclidean', leaf_size=100000, n_jobs=1).fit(data_matrix)
    end = time.time()

    print('Saving tree in pkl ...')
    fp = open(tree_path, 'wb')
    pickle.dump(nbrs, fp, protocol=4)
    fp.close()

    outf = open(DATA_FILE + '.out', 'a')
    outf.write('Tree building time = %f Sec\n' % (end - start))
    outf.close()
    print('Tree building time = %f Sec' % (end - start))


if __name__ == "__main__":
    global max_num_nn
    # main('-d data/trajectory_data_50_50_200_10000.txt -i simusers.idx -s 0.05 -n 10000 -k 20 -g 30 -t data/user_nn_50_50_200_10000.txt -a kd_tree -c False -l False --secure=True --depth_sb=4 --num_sb=1 --bins=10000'.split())
    # main('-d /media/hduser/ISIWork/Chandan/data/data.txt_30_1.ext -i /media/hduser/ISIWork/Chandan/data/data.txt_30_1.ext.idx -s 0.05 -n 266909 -k 10 -g 30 -t data/data.txt_30_1.ext.nn -a hnsw -c True -l True --secure=True --depth_sb=4 --num_sb=5 --bins=128'.split())
    main(sys.argv[1:])
