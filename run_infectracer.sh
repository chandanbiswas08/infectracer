#!/usr/bin/env bash
for ghost_users_num in 5 10 15 20
do
    for EPSILON_radius in 1 2 4 8 16 32
    do
        sh addusers.sh data/data.txt $ghost_users_num $EPSILON_radius
        python index_checkins.py -d data/data.txt.ext -i simusers.idx
        FRACTION_INFECTED=0.01
        nretrieve=5
#        for FRACTION_INFECTED in 0.001 0.01 0.02 0.03 0.04 0.05
#        do
#            for nretrieve in 5 10 15 20
#            do
                echo "ghost_users_num=$ghost_users_num, EPSILON_radius=$EPSILON_radius, FRACTION_INFECTED=$FRACTION_INFECTED, nretrieve=$nretrieve"
                python retrieve_susceptibles.py -d data/data.txt.ext -i simusers.idx -s $FRACTION_INFECTED -n 266909 -k $nretrieve -g $ghost_users_num
#            done
#        done
    done
done
