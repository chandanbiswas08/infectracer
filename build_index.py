#!/usr/bin/env python
# coding: utf-8

import getopt
import os
import numpy as np
import sys 
import nmslib
import time
import datetime
import math
import pickle
from gpsutils_trajectory import get_cartesian
from gpsutils_trajectory import convertToCartesian
from gpsutils_trajectory import get_quantized_vec
from gpsutils_trajectory import superbit_hyperplanes
from gpsutils_trajectory import loadSecureUserMap
from gpsutils_trajectory import loadUserMap
from gpsutils_trajectory import load_data
from gpsutils_trajectory import save_variables
from gpsutils_trajectory import load_variables
import subprocess
from subprocess import PIPE

def main(argv):

    DATA_FILE = None
    IDX_FILE = None
    M = 10
    efC = 100
    num_threads = 12
    space_name='l2'
    load = False
    secure = False
    bins = 32
    depth_sb = 3
    num_sb = 5

    try:
        opts, args = getopt.getopt(argv,"h:d:s:m:e:t:l:", ["datafile=", "space=", "m=", "efc=", "threads=", "load=", "secure=", "depth_sb=", "num_sb=", "bins="])

        for opt, arg in opts:
            if opt == '-h':
                print ('build_index.py -d/--datafile= <datafile> -s/--space= <space>')
                sys.exit()
            elif opt in ("-d", "--datafile"):
                DATA_FILE = arg
            elif opt in ("-s", "--space"):
                space_name = arg
            elif opt in ("-m"):
                M = int(arg)
            elif opt in ("-e", "--efC"):
                efC = int(arg)
            elif opt in ("-t", "--threads"):
                num_threads = int(arg)
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
        print ('usage: build_index.py -d <datafile>')
        sys.exit()

    if (DATA_FILE == None):
        print ('usage: build_index.py -d <datafile>')
        sys.exit()

    now = datetime.datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    outf = open(DATA_FILE + '.out', 'a')
    outf.write('%s\nAlgorithm name hnsw M: %d efc: %d\nData file name %s\n\n' % (dt_string, M, efC, DATA_FILE))
    # print(subprocess.run(['lscpu']))
    proc = subprocess.run(['lscpu'], stdout=PIPE, stderr=PIPE)
    mc_info = proc.stdout.splitlines()
    for line in mc_info:
        outf.write(line.decode("utf-8") + '\n')
    outf.write('\n')
    outf.close()

    index_time_params = {'M': M, 'indexThreadQty': num_threads, 'efConstruction': efC, 'post' : 2}
    print('Index-time parameters', index_time_params)
    index = nmslib.init(method='hnsw', space=space_name, data_type=nmslib.DataType.DENSE_VECTOR)

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

    print ("Indexing data of the form {}".format(data_matrix[0]))

    index.addDataPointBatch(data_matrix)

    #Create the index
    start = time.time()
    index.createIndex(index_time_params, print_progress=True)
    print('Saving index ...')
    if secure == True:
        IDX_FILE = DATA_FILE + '_' + str(secure) + '_' + str(depth_sb) + '_' + str(num_sb) + '_' + str(bins) + '.idx'
    else:
        IDX_FILE = DATA_FILE + '.idx'
    index.saveIndex(IDX_FILE, save_data=False)
    end = time.time()
    print('Indexing time = %f Sec' % (end - start))
    outf = open(DATA_FILE + '.out', 'a')
    outf.write('Indexing time = %f Sec\n' % (end - start))
    outf.close()


if __name__ == "__main__":
    # main('-d data/data.txt.ext -i data/data.txt.ext.idx --space=l2 -m 10 -e 100 -t 1 --secure=True --depth_sb=3 --num_sb=5 --bins=32'.split())
    main(sys.argv[1:])

