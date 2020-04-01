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


def genRandomQuery(min_time, max_time):
    MIN_LAT, MAX_LAT = -20, 20
    MIN_LONG, MAX_LONG = -20, 20
    
    lat = r.randrange(MIN_LAT, MAX_LAT)
    long = r.randrange(MIN_LONG, MAX_LONG)
    t = r.randrange(min_time, max_time)
    
    x, y, z = get_cartesian(lat, long)    
    return [x, y, z, t-min_time]


K=3
def execRandomLocQueries():
    for i in range (0, 10):  
        query_data = genRandomQuery(1333476006, 1334096862)
        print ("Query: {}".format(query_data))

        nn_info = index.knnQuery(query_data, k=K)
        nn_ids = nn_info[0]
        distances = nn_info[1]

        for i in range(0, K):
            print ("{}: {}".format(nn_ids[i], distances[i]))


def executeQueries(index, userinfomap, userids, infected_users):
    for infected_user in infected_users:
        print ("Infected user: {}".format(infected_user))
        query_locs = userinfomap[infected_user]

        for query_data in query_locs:
            print ("Query location: {}".format(query_data))

            nn_info = index.knnQuery(query_data, k=K)
            nn_ids = nn_info[0]
            distances = nn_info[1]
            for i in range(0, K):
                print ("Suspectible User = {}, distance from infected = {}".format(int(userids[nn_ids[i]]), distances[i]))
        

def main(argv):
    DATA_FILE = None
    IDX_FILE = None
    FRACTION_INFECTED = 0

    try:
        opts, args = getopt.getopt(argv,"h:d:i:s:", ["datafile=", "indexfile=", "sick="])

        for opt, arg in opts:
            if opt == '-h':
                print ('index_checkins.py -d/--datafile= <datafile> -i/--index= <index file> -s/--sick = <fraction sick>')
                sys.exit()
            elif opt in ("-d", "--datafile"):
                DATA_FILE = arg
            elif opt in ("-i", "--indexfile"):
                IDX_FILE = arg
            elif opt in ("-s", "-sick"):
                FRACTION_INFECTED = float(arg)

    except getopt.GetoptError:
        print ('usage: index_checkins.py -d <datafile> -i <indexfile> -s <fraction_sick>')
        sys.exit()

    if (DATA_FILE == None or IDX_FILE == None or FRACTION_INFECTED == 0):
        print ('usage: index_checkins.py -d <datafile> -i <indexfile> -s <sick_ratio [0, 1] (e.g. 0.01)>')
        sys.exit()

    print ("Reading data file...")
    gps_data_matrix = np.loadtxt(DATA_FILE)
    print ("Loading user ids...")
    userids = loadusers(gps_data_matrix)
    print ("Loading user data...")
    userinfomap = loadUserMap(gps_data_matrix)

    unique_user_ids = []
    for userid in userinfomap:
        unique_user_ids.append(userid)

    num_queries = int(len(unique_user_ids)*FRACTION_INFECTED)
    print ("Number of users infected: {}".format(num_queries))

    infected_users = r.sample(unique_user_ids, num_queries)
        
    index = nmslib.init(method='hnsw', space='l2')
    index.loadIndex(IDX_FILE, load_data=False)

    executeQueries(index, userinfomap, userids, infected_users)

if __name__ == "__main__":
    main(sys.argv[1:])
