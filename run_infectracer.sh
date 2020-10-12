#!/usr/bin/env bash
####**** Note: To generate dataset and reproduce results on large dataset like Traject-100K and Traject-1M please uncomment corresponding lines. ####

gunzip data/*
wc -l data/*

#HNSW
python build_index.py -d data/data.txt_5_1.ext --secure False
python retrieve_susceptibles.py -d data/data.txt_5_1.ext -s 0.04 -n 266909 -k 100 -g 5 -a hnsw -c True -l True --secure False



#PP-HNSW
python build_index.py -d data/data.txt_5_1.ext --secure True --depth_sb 2 --num_sb 8 --bins 1000000
python retrieve_susceptibles.py -d data/data.txt_5_1.ext -s 0.04 -n 266909 -k 100 -g 5 -a hnsw -c True -l True --secure True --depth_sb 2 --num_sb 8 --bins 1000000



#KD-tree
python build_tree.py -d data/data.txt_5_1.ext --secure False
python retrieve_susceptibles.py -d data/data.txt_5_1.ext -s 0.04 -n 266909 -k 100 -g 5 -a kd_tree -c True -l True --secure False




#PP-KD-tree
python build_tree.py -d data/data.txt_5_1.ext -l True --secure True --depth_sb 2 --num_sb 8 --bins 1000000
python retrieve_susceptibles.py -d data/data.txt_5_1.ext -s 0.04 -n 266909 -k 100 -g 5 -a kd_tree -c True -l True --secure True --depth_sb 2 --num_sb 8 --bins 1000000


######## Traject-10K #####################

#echo "Generating Trajectory dataset with 10K users..."
#python3 tragectory_data_gen.py 200 10000 50 50

data_path='data/trajectory_data_50_50_200_10000.txt'
idx_path='data/trajectory_data_50_50_200_10000.txt.idx'
gt_path='data/user_nn_50_50_200_10000.txt'
rm data/trajectory_data_50_50_200_10000.txt.out

### HNSW ###
python build_index.py -d $data_path --space l2 -m 4 -e 100 -t 1 -l True --secure False --depth_sb 2 --num_sb 8 --bins 128
python retrieve_susceptibles.py -d $data_path -s $FRACTION_INFECTED -n 10000 -k $nretrieve -g 30 -t $gt_path  -a hnsw -c False -l True  --secure False --depth_sb 2 --num_sb 8 --bins 128

### KD-tree ###
python build_tree.py -d $data_path --secure False
python retrieve_susceptibles.py -d $data_path -s $FRACTION_INFECTED -n 10000 -k $nretrieve -g 30 -t $gt_path  -a kd_tree -c False -l True  --secure False --depth_sb 2 --num_sb 8 --bins 128

### PP-HNSW ###
python build_index.py -d $data_path --space l2 -m 4 -e 100 -t 1 -l True --secure True --depth_sb 2 --num_sb 8 --bins 128
python retrieve_susceptibles.py -d $data_path -s $FRACTION_INFECTED -n 10000 -k $nretrieve -g 30 -t $gt_path  -a hnsw -c False -l True  --secure True --depth_sb 2 --num_sb 8 --bins 128

### PP-KD-tree ###
python build_tree.py -d $data_path -l True  --secure True --depth_sb 2 --num_sb 8 --bins 128
python retrieve_susceptibles.py -d $data_path -s $FRACTION_INFECTED -n 10000 -k $nretrieve -g 30 -t $gt_path  -a kd_tree -c False -l True  --secure True --depth_sb 2 --num_sb 8 --bins 128



######## Traject-100K #####################

#echo "Generating Trajectory dataset with 100K users..."
#python3 tragectory_data_gen.py 200 100000 500 500

#data_path='data/trajectory_data_500_500_2000_100000.txt'
#idx_path='data/trajectory_data_500_500_2000_100000.txt.idx'
#gt_path='data/user_nn_500_500_2000_100000.txt'
#rm data/trajectory_data_500_500_2000_100000.txt.out

### HNSW ###
#python build_index.py -d $data_path --space l2 -m 4 -e 100 -t 12 -l True --secure False --depth_sb 2 --num_sb 8 --bins 128
#python retrieve_susceptibles.py -d $data_path -s $FRACTION_INFECTED -n 100000 -k $nretrieve -g 30 -t $gt_path  -a hnsw -c False -l True --secure False --depth_sb 2 --num_sb 8 --bins 128

### KD-tree ###
#python build_tree.py -d $data_path --secure False
#python retrieve_susceptibles.py -d $data_path -s $FRACTION_INFECTED -n 100000 -k $nretrieve -g 30 -t $gt_path  -a kd_tree -c False -l True --secure False --depth_sb 2 --num_sb 8 --bins 128

### PP-HNSW ###
#python build_index.py -d $data_path --space l2 -m 4 -e 100 -t 12 --secure True --depth_sb 2 --num_sb 8 --bins 128
#python retrieve_susceptibles.py -d $data_path -s $FRACTION_INFECTED -n 100000 -k $nretrieve -g 30 -t $gt_path  -a hnsw -c False -l True --secure True --depth_sb 2 --num_sb 8 --bins 128

### PP-KD-tree ###
#python build_tree.py -d $data_path -l True --secure True --depth_sb 2 --num_sb 8 --bins 128
#python retrieve_susceptibles.py -d $data_path -s $FRACTION_INFECTED -n 100000 -k $nretrieve -g 30 -t $gt_path  -a kd_tree -c False -l True --secure True --depth_sb 2 --num_sb 8 --bins 128



######## Traject-1M #####################

#echo "Generating Trajectory dataset with 1M users..."
#python3 tragectory_data_gen.py 200 1000000 500 500


#data_path='data/trajectory_data_500_500_200_1000000.txt'
#idx_path='data/trajectory_data_500_500_200_1000000.txt.idx'
#gt_path='data/user_nn_500_500_200_1000000.txt'
#rm data/trajectory_data_500_500_200_1000000.txt.out

### HNSW ###
#python build_index.py -d $data_path --space l2 -m 4 -e 100 -t 200 -l True --secure False --depth_sb 2 --num_sb 8 --bins 1024
#python retrieve_susceptibles.py -d $data_path -s $FRACTION_INFECTED -n 1000000 -k $nretrieve -g 30 -t $gt_path  -a hnsw -c False -l True --secure False --depth_sb 2 --num_sb 8 --bins 1024

### KD-tree ###
#python build_tree.py -d $data_path --secure False
#python retrieve_susceptibles.py -d $data_path -s $FRACTION_INFECTED -n 1000000 -k $nretrieve -g 30 -t $gt_path  -a kd_tree -c False -l True --secure False --depth_sb 2 --num_sb 8 --bins 1024

### PP-HNSW ###
#python build_index.py -d $data_path --space l2 -m 4 -e 100 -t 200 --secure True --depth_sb 2 --num_sb 8 --bins 1024
#python retrieve_susceptibles.py -d $data_path -s $FRACTION_INFECTED -n 1000000 -k $nretrieve -g 30 -t $gt_path  -a hnsw -c False -l True --secure True --depth_sb 2 --num_sb 8 --bins 1024

### PP-KD-tree ###
#python build_tree.py -d $data_path -l True --secure True --depth_sb 2 --num_sb 8 --bins 1024
#python retrieve_susceptibles.py -d $data_path -s $FRACTION_INFECTED -n 1000000 -k $nretrieve -g 30 -t $gt_path  -a kd_tree -c False -l True --secure True --depth_sb 2 --num_sb 8 --bins 1024








