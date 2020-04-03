#!/usr/bin/env python
# coding: utf-8

import numpy as np 
import sys, getopt
import os
import sys 
import nmslib 
import time 
import math 
import random as r
from gpsutils import get_cartesian
from gpsutils import loadusers
from gpsutils import loadUserMap

K=5 # to retrieve
NUM_GHOST_USERS=5
SEED=12345

def genRandomQuery(min_time, max_time):
    MIN_LAT, MAX_LAT = -20, 20
    MIN_LONG, MAX_LONG = -20, 20
    
    lat = r.randrange(MIN_LAT, MAX_LAT)
    long = r.randrange(MIN_LONG, MAX_LONG)
    t = r.randrange(min_time, max_time)
    
    x, y, z = get_cartesian(lat, long)    
    return [x, y, z, t-min_time]


def evaluateRecall(userid, userids, nn_ids, MAX_USER_ID):
    # get the ground-truth
    rel_userids = []
    ghostuserid_start = MAX_USER_ID + NUM_GHOST_USERS*(userid-1) + 1;
    for i in range(0, NUM_GHOST_USERS):
        rel_userids.append(int(ghostuserid_start + i));

    #print ("rel({}) = {}".format(userid, rel_userids));

    retr_userids = []
    for i in range(0, K):
        retr_userids.append(int(userids[nn_ids[i]]))

    #print ("retr({}) = {}".format(userid, retr_userids));

    correct = set(rel_userids) & set(retr_userids);
    #print ("matches = {}".format(len(correct)));
 
    return len(correct)/len(rel_userids) # recall value...

def execRandomLocQueries():
    for i in range (0, 10):  
        query_data = genRandomQuery(1333476006, 1334096862)
        print ("Query: {}".format(query_data))

        nn_info = index.knnQuery(query_data, k=K)
        nn_ids = nn_info[0]
        distances = nn_info[1]

        for i in range(0, K):
            print ("{}: {}".format(nn_ids[i], distances[i]))


def executeQueries(index, userinfomap, userids, infected_users, MAX_USER_ID):
    net_recall = 0
    total_queries = 0

    start = time.time()

    for infected_user in infected_users:
        #print ("Infected user: {}".format(infected_user))
        query_locs = userinfomap[infected_user]

        for query_data in query_locs:
            #print ("Query location: {}".format(query_data))

            nn_info = index.knnQuery(query_data, k=K+1)
            nn_ids = nn_info[0]
            nn_ids = nn_ids[1:]
            #distances = nn_info[1]
            #distances = distances[1:]
            #for i in range(0, K):  # the first retrieved should be the query itself... ignore it
            #    print ("Suspectible User = {}, distance from infected = {}".format(int(userids[nn_ids[i]]), distances[i]))

            recall = evaluateRecall(infected_user, userids, nn_ids, MAX_USER_ID);
            net_recall = net_recall + recall
            total_queries = total_queries + 1
            #print ("Recall({}) = {}".format(infected_user, recall));
        
    end = time.time() 
    print('Search time = %f' % round(end-start, 4))
    print ("Avg. Recall = {}".format(round(net_recall/total_queries, 4)));  # this is also safe coz only one data per user...

def main(argv):
    DATA_FILE = None
    IDX_FILE = None
    FRACTION_INFECTED = 0

    try:
        opts, args = getopt.getopt(argv,"h:d:i:s:n:", ["datafile=", "indexfile=", "sick=", "nusers="])

        for opt, arg in opts:
            if opt == '-h':
                print ('index_checkins.py -d/--datafile= <datafile> -i/--index= <index file> -s/--sick= <fraction sick> -n/--nusers= <nusers>')
                sys.exit()
            elif opt in ("-d", "--datafile"):
                DATA_FILE = arg
            elif opt in ("-i", "--indexfile"):
                IDX_FILE = arg
            elif opt in ("-s", "--sick"):
                FRACTION_INFECTED = float(arg)
            elif opt in ("-n", "--nusers"):
                MAX_USER_ID = int(arg)

    except getopt.GetoptError:
        print ('usage: index_checkins.py -d <datafile> -i <indexfile> -s <fraction_sick> -n/--nusers= <nusers>')
        sys.exit()

    if (DATA_FILE==None or IDX_FILE==None or FRACTION_INFECTED==0 or MAX_USER_ID==0):
        print ('usage: index_checkins.py -d <datafile> -i <indexfile> -s <sick_ratio [0, 1] (e.g. 0.01)> -n <#users>')
        sys.exit()

    print ("Reading data file...")
    gps_data_matrix = np.loadtxt(DATA_FILE)
    print ("Loading user ids...")
    userids = loadusers(gps_data_matrix)
    print ("Loading user data...")
    userinfomap = loadUserMap(gps_data_matrix)

    unique_user_ids = list(range (1, MAX_USER_ID+1)); # only the real users... not the ghost (simulated) ones...

    num_queries = int(len(unique_user_ids)*FRACTION_INFECTED)
    print ("Number of users infected: {}".format(num_queries))

    r.seed(SEED)
    r.shuffle(unique_user_ids)
    infected_users = r.sample(unique_user_ids, num_queries)
        
    index = nmslib.init(method='hnsw', space='l2')
    index.loadIndex(IDX_FILE, load_data=False)

    executeQueries(index, userinfomap, userids, infected_users, MAX_USER_ID)

if __name__ == "__main__":
    main(sys.argv[1:])
