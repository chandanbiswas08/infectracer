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


def gram_schmidt(vectors):
    basis = []
    for v in vectors:
        w = v - sum( np.dot(v,b)*b  for b in basis )
        if (w > 1e-10).any():
            basis.append(w/np.linalg.norm(w))
    return np.array(basis)


def evaluateRecall_checkin(userid, userids, nn_ids, nn_distances, MAX_USER_ID, NUM_GHOST_USERS, K):
    # get the ground-truth
    rel_userids = []
    ghostuserid_start = MAX_USER_ID + 3 * NUM_GHOST_USERS * (userid - 1) + 1
    for i in range(0, NUM_GHOST_USERS):
        rel_userids.append(int(ghostuserid_start + i))

    # print ("rel({}) = {}".format(userid, rel_userids));
    max_ghost_nn_dist = -9999
    retr_userids = []
    for i in range(0, len(nn_ids)):
        retr_userids.append(int(userids[nn_ids[i]]))
        if int(userids[nn_ids[i]]) >= ghostuserid_start and int(
                userids[nn_ids[i]]) < ghostuserid_start + NUM_GHOST_USERS:
            if nn_distances[i] > max_ghost_nn_dist:
                max_ghost_nn_dist = nn_distances[i]

    for i in range(0, len(nn_ids)):
        if nn_distances[i] <= max_ghost_nn_dist and int(userids[nn_ids[i]]) <= MAX_USER_ID:
            rel_userids.append(int(userids[nn_ids[i]]))

    # print ("retr({}) = {}".format(userid, retr_userids));

    correct = set(rel_userids) & set(retr_userids)
    # print ("matches = {}".format(len(correct)));
    if len(retr_userids) == 0:
        return 0, 0
    else:
        return len(correct) / len(rel_userids), len(correct)/len(retr_userids) # recall precision value...


def evaluateRecall(rel_userids, userids, nn_ids):
    retr_userids = []
    for i in range(0, len(nn_ids)):
        retr_userids.append(int(userids[nn_ids[i]]))

    #print ("retr({}) = {}".format(userid, retr_userids));
    retr_userids = set(retr_userids)
    rel_userids = set(rel_userids)
    correct = rel_userids & retr_userids
    #print ("matches = {}".format(len(correct)));

    return len(correct)/len(rel_userids), len(correct)/len(retr_userids) # recall precision value...


def executeQueries(DATA_FILE, nbrs, userinfomap, userids, infected_users, MAX_USER_ID, NUM_GHOST_USERS, K, nn_gt, algo, checkin):
    net_recall = 0
    net_precision = 0
    total_queries = 0
    search_time = 0
    num_infected = len(infected_users)

    for infected_user in infected_users:
        query_locs = userinfomap[infected_user]
        distances = []
        nn_ids = []
        for query_data in query_locs:
            start = process_time()
            if algo == 'hnsw':
                nbd, nbd_dist = nbrs.knnQuery(query_data, k=K+1)
            else:
                nbd_dist, nbd = nbrs.kneighbors([query_data], return_distance=True, n_neighbors=K + 1)
            search_time += process_time() - start

            nn_ids = nn_ids + list(nbd)
            distances = distances + list(nbd_dist)
        nn_ids = list(np.asarray(nn_ids).flatten())
        distances = list(np.asarray(distances).flatten())
        if checkin == True:
            recall, precision = evaluateRecall_checkin(infected_user, userids, nn_ids, distances, MAX_USER_ID, NUM_GHOST_USERS, K)
        else:
            recall, precision = evaluateRecall(nn_gt[infected_user], userids, nn_ids)
        net_recall = net_recall + recall
        net_precision = net_precision + precision
        total_queries = total_queries + 1
    search_time = search_time / num_infected
    print('Number of users infected: %d \nK = %d \nSearch time = %f millisec/query \nAvg. Recall = %f' % (num_infected, K, round(search_time * 1000, 4), round(net_recall/total_queries, 4)))
    outf = open(DATA_FILE + '.out', 'a')
    outf.write('num_infected %d K %d Search time %f millisec Recall %f\n' % (num_infected, K, round(search_time * 1000, 4), round(net_recall/total_queries, 4)))
    outf.close()


def main(argv):
    DATA_FILE = None
    IDX_FILE = None
    MAX_USER_ID = 100000
    NUM_GHOST_USERS = 30
    FRACTION_INFECTED = 0.04
    nretrieve = 100
    gtfile = None
    algo = 'kd_tree'
    checkin = True
    load = False
    secure = False
    bins = 32
    depth_sb = 3
    num_sb = 5

    try:
        opts, args = getopt.getopt(argv,"h:d:s:n:k:g:t:a:c:l:", ["datafile=", "sick=", "nusers=", "nretrieve=", "nghostusers=", "gtfile=", "algo=", "checkin=", "load=", "secure=", "depth_sb=", "num_sb=", "bins="])

        for opt, arg in opts:
            if opt == '-h':
                print ('build_index.py -d/--datafile= <datafile> -s/--sick= <fraction sick> -n/--nusers= <nusers>')
                sys.exit()
            elif opt in ("-d", "--datafile"):
                DATA_FILE = arg
            elif opt in ("-s", "--sick"):
                FRACTION_INFECTED = float(arg)
            elif opt in ("-n", "--nusers"):
                MAX_USER_ID = int(arg)
            elif opt in ("-k", "--nretrieve"):
                nretrieve = int(arg)
            elif opt in ("-g", "--nghostusers"):
                NUM_GHOST_USERS = int(arg)
            elif opt in ("-t", "--gtfile"):
                gtfile = arg
            elif opt in ("-a", "--algo"):
                algo = arg
            elif opt in ("-c", "--checkin"):
                if arg == 'True':
                    checkin = True
                else:
                    checkin = False
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
        print ('usage: retrieve_susceptibles.py -d <datafile> -s <fraction_sick> -n/--nusers= <nusers>')
        sys.exit()

    if (DATA_FILE==None or MAX_USER_ID==0):
        print ('usage: retrieve_susceptibles.py -d <datafile> -s <sick_ratio [0, 1] (e.g. 0.01)> -n <#users>')
        sys.exit()

    if secure == True:
        if algo == 'hnsw':
            print('\n\nAlgorithm name PP-HNSW')
        else:
            print('\n\nAlgorithm name PP-KD-tree')
    else:
        if algo == 'hnsw':
            print('\n\nAlgorithm name HNSW')
        else:
            print('\n\nAlgorithm name KD-tree')

    
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

    nn_gt = {}
    if checkin == False:
        nn_gt = get_gt(gtfile)

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

    if algo == 'hnsw':
        nbrs = nmslib.init(method='hnsw', space='l2')
        if secure == True:
            IDX_FILE = DATA_FILE + '_' + str(secure) + '_' + str(depth_sb) + '_' + str(num_sb) + '_' + str(bins) + '.idx'
        else:
            IDX_FILE = DATA_FILE + '.idx'
        nbrs.loadIndex(IDX_FILE, load_data=False)
    else:
        if secure == True:
            tree_path = DATA_FILE + '_' + str(secure) + '_' + str(depth_sb) + '_' + str(num_sb) + '_' + str(bins) + '.nbd'
        else:
            tree_path = DATA_FILE + '.nbd'
        if os.path.exists(tree_path):
            print("Loading nbrs from pkl...")
            fp = open(tree_path, 'rb')
            nbrs = pickle.load(fp)
            fp.close()
        else:
            start = time.time()
            print('Creating nbrs...')
            nbrs = NearestNeighbors(algorithm=algo, metric='euclidean', leaf_size=100000, n_jobs=1).fit(data_matrix)
            end = time.time()

            print('Saving tree in pkl ...')
            fp = open(tree_path, 'wb')
            pickle.dump(nbrs, fp, protocol=4)
            fp.close()

            outf = open(DATA_FILE + '.out', 'a')
            outf.write('Tree building time = %f\n' % (end - start))
            outf.close()
            print('Tree building time = %f' % (end - start))

    unique_user_ids = list(range(0, MAX_USER_ID))
    search_time = 0
    print('Retrieval started ...')
    start = process_time()
    FRACTION_INFECTED = [FRACTION_INFECTED]
    # FRACTION_INFECTED = [0.01, 0.02, 0.03, 0.04]
    for FRAC in FRACTION_INFECTED:
        num_queries = int(len(unique_user_ids)*FRAC)
        # print ("Number of users infected: {}".format(num_queries))
        r.seed(SEED)
        r.shuffle(unique_user_ids)
        infected_users = r.sample(unique_user_ids, num_queries)

        # for nretrieve in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
        executeQueries(DATA_FILE, nbrs, userinfomap, userids, infected_users, MAX_USER_ID, NUM_GHOST_USERS, nretrieve, nn_gt, algo, checkin=checkin)
    search_time += process_time() - start
    print('Total retrieval time = %.2f sec' % search_time)

if __name__ == "__main__":
    global max_num_nn
    # main('-d data/trajectory_data_50_50_200_10000.txt -i simusers.idx -s 0.05 -n 10000 -k 20 -g 30 -t data/user_nn_50_50_200_10000.txt -a kd_tree -c False -l False --secure=True --depth_sb=4 --num_sb=1 --bins=10000'.split())
    # main('-d /media/hduser/ISIWork/Chandan/data/data.txt_30_1.ext -i /media/hduser/ISIWork/Chandan/data/data.txt_30_1.ext.idx -s 0.05 -n 266909 -k 10 -g 30 -t data/data.txt_30_1.ext.nn -a hnsw -c True -l True --secure=True --depth_sb=4 --num_sb=5 --bins=128'.split())
    main(sys.argv[1:])
