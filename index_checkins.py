#!/usr/bin/env python
# coding: utf-8

import sys, getopt
import os
import numpy as np
import sys 
import nmslib 
import time 
import math 
from gpsutils import get_cartesian
from gpsutils import convertToCartesian
from sklearn.neighbors import NearestNeighbors

def main(argv):

    DATA_FILE = None
    IDX_FILE = None
    M = 15
    efC = 100
    num_threads = 4

    try:
        opts, args = getopt.getopt(argv,"h:d:i:", ["datafile="])

        for opt, arg in opts:
            if opt == '-h':
                print ('index_checkins.py -d/--datafile= <datafile> -i/--index= <index file>')
                sys.exit()
            elif opt in ("-d", "--datafile"):
                DATA_FILE = arg
            elif opt in ("-i", "--indexfile"):
                IDX_FILE = arg

    except getopt.GetoptError:
        print ('usage: index_checkins.py -d <datafile> -i <indexfile>')
        sys.exit()

    if (DATA_FILE == None or IDX_FILE == None):
        print ('usage: index_checkins.py -d <datafile> -i <indexfile>')
        sys.exit()

    index_time_params = {'M': M, 'indexThreadQty': num_threads, 'efConstruction': efC, 'post' : 0}
    space_name='l2'

    gps_data_matrix = np.loadtxt(DATA_FILE)
    data_matrix = convertToCartesian(gps_data_matrix)

    index = nmslib.init(method='hnsw', space=space_name, data_type=nmslib.DataType.DENSE_VECTOR) 
    print ("Indexing data of the form {}".format(data_matrix[0]))

    index.addDataPointBatch(data_matrix)

    #Create the index
    start = time.time()
    index_time_params = {'M': M, 'indexThreadQty': num_threads, 'efConstruction': efC}
    index.createIndex(index_time_params, print_progress=True) 
    end = time.time() 
    print('Index-time parameters', index_time_params)
    print('Indexing time = %f' % (end-start))

    index.saveIndex(IDX_FILE, save_data=False)

if __name__ == "__main__":
    main(sys.argv[1:])

