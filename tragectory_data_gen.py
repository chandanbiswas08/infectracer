# Python code for 2D random walk.
import random
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
from rearrange_user_nn_file import rearrange_nn

random.seed(1234)
neg_inf = -999999
# max_step = 2000
min_step = 100
# num_user = 1000000
# max_x = 500
# max_y = 500

space_time = {}
users = {}


def find_nn(t, x, y):
    nn = space_time[t][x][y]
    try:
        nn = nn + space_time[t][x][y+1]
    except Exception:
        pass
    try:
        nn = nn + space_time[t][x-1][y+1]
    except Exception:
        pass
    try:
        nn = nn + space_time[t][x-1][y]
    except Exception:
        pass
    try:
        nn = nn + space_time[t][x-1][y-1]
    except Exception:
        pass
    try:
        nn = nn + space_time[t][x][y-1]
    except Exception:
        pass
    try:
        nn = nn + space_time[t][x+1][y-1]
    except Exception:
        pass
    try:
        nn = nn + space_time[t][x+1][y]
    except Exception:
        pass
    try:
        nn = nn + space_time[t][x+1][y+1]
    except Exception:
        pass
    return nn


def rand_walk(user_id, start_x, start_y, start_t, num_steps, fp_out, max_step, max_x, max_y):
    next_x = start_x
    next_y = start_y
    next_t = start_t
    fp_out.write('%d %d %d %d\n' % (user_id, next_x, next_y, next_t))

    users[user_id] = {}
    users[user_id][next_t] = [next_x, next_y]
    for i in range(1, num_steps):
        next_t = start_t + i
        val = random.randint(1, 8)
        if val == 1:
            next_x = next_x + 1      #E
        elif val == 2:
            next_x = next_x + 1      #NE
            next_y = next_y + 1
        elif val == 3:
            next_y = next_y + 1      #N
        elif val == 4:
            next_x = next_x - 1      #NW
            next_y = next_y + 1
        elif val == 5:
            next_x = next_x - 1      #W
        elif val == 6:
            next_x = next_x - 1      #SW
            next_y = next_y - 1
        elif val == 7:
            next_y = next_y - 1      #S
        else:
            next_x = next_x + 1      #SE
            next_y = next_y - 1

        if next_x == max_x:
            next_x = max_x - 1
        if next_y == max_y:
            next_y = max_y - 1
        if next_x == -max_x - 1:
            next_x = -max_x
        if next_y == -max_y - 1:
            next_y = -max_y

        users[user_id][next_t] = [next_x, next_y]
        fp_out.write('%d %d %d %d\n' % (user_id, next_x, next_y, next_t))
        if next_t >= max_step - 1:
            break
    return


def create_tragectory_data(max_step, num_user, max_x, max_y):
    fp_out = open('data/trajectory_data_' + str(max_x) + '_' + str(max_y) + '_' + str(max_step) + '_' + str(num_user) + '.txt', 'w')
    for user_id in range(num_user):
        # print('create tragectory user_id %d'%user_id)
        start_x = random.randint(-max_x, max_x-1)
        start_y = random.randint(-max_y, max_y-1)
        star_t = random.randint(0, max_step-min_step)
        rand_walk(user_id, start_x, start_y, star_t, max_step, fp_out, max_step, max_x, max_y)
    fp_out.close()
    return


def get_user_nn(max_step, num_user, max_x, max_y):
    user_nn = {}
    gt_path = 'data/user_nn_' + str(max_x) + '_' + str(max_y) + '_' + str(max_step) + '_' + str(num_user) + '.txt'
    fp_usernn = open(gt_path,'w')
    for t in space_time:
        # print('getting user nn timestep %d'%t)
        for x in space_time[t]:
            for y in space_time[t][x]:
                for user_id in space_time[t][x][y]:
                    nn = find_nn(t, x, y)
                    try:
                        user_nn[user_id] = user_nn[user_id] + nn
                    except:
                        user_nn[user_id] = []
                        user_nn[user_id] = user_nn[user_id] + nn
    for user_id in user_nn:
        user_nn[user_id] = np.unique(np.array(user_nn[user_id]))
        fp_usernn.write('%d\t' % user_id)
        for i in range(len(user_nn[user_id])):
            fp_usernn.write('%d ' % user_nn[user_id][i])
        fp_usernn.write('\n')
    fp_usernn.close()
    rearrange_nn(gt_path)


def create_nn_gt(max_step, num_user, max_x, max_y):
    fp_tra = open('data/trajectory_data_' + str(max_x) + '_' + str(max_y) + '_' + str(max_step) + '_' + str(num_user) + '.txt', 'r')
    line = fp_tra.readline()
    while line:
        [user_id, x, y, t] = [int(i) for i in line.strip().split()]
        # print('creating nn %s'%user_id)
        try:
            space_time[t][x][y].append(user_id)
        except:
            try:
                space_time[t][x][y] = []
                space_time[t][x][y].append(user_id)
            except:
                try:
                    space_time[t][x] = {}
                    space_time[t][x][y] = []
                    space_time[t][x][y].append(user_id)
                except:
                    space_time[t] = {}
                    space_time[t][x] = {}
                    space_time[t][x][y] = []
                    space_time[t][x][y].append(user_id)
        line = fp_tra.readline()
    fp_tra.close()

if __name__ == "__main__":
    max_step = int(sys.argv[1])
    num_user = int(sys.argv[2])
    max_x = int(sys.argv[3])
    max_y = int(sys.argv[4])
    start_time = time.time()
    create_tragectory_data(max_step, num_user, max_x, max_y)
    create_nn_gt(max_step, num_user, max_x, max_y)
    get_user_nn(max_step, num_user, max_x, max_y)
    print('Elaps time %f'%(time.time()-start_time))
