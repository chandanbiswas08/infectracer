# INFECTRACER: Approximate Nearest Neighbors Retrieval of GPS Location Traces to Report Candidate Infections

In the present national emergency situation of coronavirus pandemic governments of all countries are trying to prevent massive propagation of that virus. To get a success in preventing propagation of the Covid-19 virus many governments have decided to keep the whole country locked down. According to experts, prevention of the spread of the disease can be achieved by quarantining all Covid-19 positive patients, and all those persons who came in contact or closer to these patients within last 15-20 days. Very often it happens that a person who came in close contact with an infected patient hides this information from local administration to avoid quarantine. In this situation, the key problem is finding out who those people are. This repository describes a  system that reports all possible cases of proximities of a person with another infected person. We believe that with the availabity of GPS location data of a large number of users, the system can very quickly help finding suspectible people in very quick time (which in the real-life could help in the initiative of imposing quarantine on them and prevent further spread of the disease).


## INFECTRACER

  

A tool to quickly locate a set of susceptible persons given a global database of user check-ins and a set of infected people.


### Extract the data

If you want to generate your own data (using a different simulation approach then read the Appendix section).  Else to conduct experiments on the provided dataset, simply execute

```bash
gunzip data/*
wc -l data/*
```
For which you should see
```bash
   266909 data/data.txt
  4270544 data/data.txt_5_1.ext
  1499439 data/trajectory_data_50_50_200_10000.txt
    10000 data/user_nn_50_50_200_10000.txt
  6046892 total
```

### Approximate Retrieval Approach

The objective of the retrieval approach is then to find the set of ghost-users given a real user, because as per the ground-truth of the simulated data these (pseudo) users came in close contact with a known infected user. 

In a real life situation, one has a massive database of user checkins of a population out of which it is known that a number of persons are infected. The goal is to rapidly find the candidate set of people who came in close contact with the infected. However, a brute force search to locate the candidates would take a huge time (since it is a quadratic time complexity operation).

In our approach, we undertake an **approximate nearest neighbor** search approach to solve the problem. The two main research questions in this setup are:

1. How does **efficiency** (run-time) vary with the fraction of people infected, e.g., if `10% of a population gets infected, is this still a feasible solution`?
2. What is the **effectiveness** of the approximate nearest neighbor search? Since it is an approximate method, it can make mistakes. Is there a satisfactory bound on the error rate?

 
### Indexing the Data
  
The next step is to install the `nmslib` library. Simply execute `pip install nmslib`. Make sure you have `numpy` installed (if not execute `pip install numpy`).

The indexing step enables a very fast retrieval of susceptible cases. To perform the indexing step using different algorithms we need to execute following commands:

### HNSW
```bash
python build_index.py -d data/data.txt_5_1.ext --secure False
``` 

### PP-HNSW
```bash
python build_index.py -d data/data.txt_5_1.ext --secure True --depth_sb 2 --num_sb 8 --bins 1000000
```  

### KD-tree
```bash
python build_tree.py -d data/data.txt_5_1.ext --secure False
``` 

### PP-KD-tree
```bash
python build_tree.py -d data/data.txt_5_1.ext -l True --secure True --depth_sb 2 --num_sb 8 --bins 1000000
```
For **HNSW** and **KD-tree** we specify the data file (comprising the user-id, locations, time-offsets) and secure=False and for **PP-HNSW** and **PP-KD-tree** we specify  the data file, to preserve privacy we write secure=True, number of projection axis of the setsof hyperplanes, number of sets of hyperplanes and the number of bins in which we quantize the project data to preserve the privacy.

The geo-locations of users (which in real life can be obtained from GPS locations of smart phones) are then represented as `3` dimensional points (*2 space dimensions* corresponding to the location on the Earth's surface and *1 time dimension* measured in epoch seconds). The path traced in this 3 dimensional space-time corresponds to the activity phase of a single user. The idea is shown in the figure below, which shows a simple visualization of a 2d space-time world (the space-time in our case is 3d).

![Spacetime](spacetime.png)

Each person is shown as a path (curve) in this space-time, i.e. each person changing his position (x coordinate) with respect to time (which is ever increasing meaning that the curves monotonically increase with respect to the x coordinate, or in other words the curves never loop down). The figure shows two intersections in this graph one of which is an intersection of a healthy person with an infected one (leaving him at a high risk of infection). The job of the program is to **automatically find all such possible intersections** given a **huge** list of such person location traces (curves in the space-time) and a given list of infected people (query curves like the one shown with red in the figure). 

### Retrieval of Candidate Infected Persons

The next step is to retrieve the susceptible cases. The program simulates the case that a fraction of the population (whose data exists in the index already) has been infected. The `retrieval` program formulates and executes a query for each of these infected people and reports a list of **K** most susceptible persons that came in close contact (in terms of space and time) with an infected person.

The commands for retrieval step and corresponding outputs for different algorithms are following:
### HNSW
```bash
python retrieve_susceptibles.py -d data/data.txt_5_1.ext -s 0.04 -n 266909 -k 100 -g 5 -a hnsw -c True -l True --secure False
``` 
## Output:
```bash
Algorithm name HNSW
Data file name data/data.txt_5_1.ext
Loading user ids from pkl...
Loading data matrix from pkl...
Loading userinfomap from pkl...
Retrieval started ...
Number of users infected: 10676 
K = 100 
Search time = 0.036500 millisec/query 
Avg. Recall = 0.998700
Total retrieval time = 2.38 sec
```

### PP-HNSW
```bash
python retrieve_susceptibles.py -d data/data.txt_5_1.ext -s 0.04 -n 266909 -k 100 -g 5 -a hnsw -c True -l True --secure True --depth_sb 2 --num_sb 8 --bins 1000000
``` 
## Output:
```bash
Algorithm name PP-HNSW
Data file name data/data.txt_5_1.ext
Loading user ids from pkl...
Loading data matrix from pkl...
Loading userinfomap from pkl...
Quantized data shape (4270544, 16) Number of bins 1000000

Retrieval started ...
Number of users infected: 10676 
K = 100 
Search time = 0.047200 millisec/query 
Avg. Recall = 0.769800
Total retrieval time = 3.18 sec
``` 

### KD-tree
```bash
python retrieve_susceptibles.py -d data/data.txt_5_1.ext -s 0.04 -n 266909 -k 100 -g 5 -a kd_tree -c True -l True --secure False
``` 
## Output:
```bash
Algorithm name KD-tree
Data file name data/data.txt_5_1.ext
Loading user ids from pkl...
Loading data matrix from pkl...
Loading userinfomap from pkl...
Loading nbrs from pkl...
Retrieval started ...
Number of users infected: 10676 
K = 100 
Search time = 2.945400 millisec/query 
Avg. Recall = 1.000000
Total retrieval time = 33.94 sec
```

### PP-KD-tree
```bash
python retrieve_susceptibles.py -d data/data.txt_5_1.ext -s 0.04 -n 266909 -k 100 -g 5 -a kd_tree -c True -l True --secure True --depth_sb 2 --num_sb 8 --bins 1000000
``` 
## Output:
```bash
Algorithm name PP-KD-tree
Data file name data/data.txt_5_1.ext
Loading user ids from pkl...
Loading data matrix from pkl...
Loading userinfomap from pkl...
Quantized data shape (4270544, 16) Number of bins 1000000

Loading nbrs from pkl...
Retrieval started ...
Number of users infected: 10676 
K = 100 
Search time = 9.137400 millisec/query 
Avg. Recall = 0.807800
Total retrieval time = 100.38 sec
```
In each algorithm we specify the data file (to simulate infected people),  the fraction infected (in the example set to `0.04` or `4%`), the number of real users in the data (this is useful for the program to compute the ground-truth information and compute recall),  tne number of most susceptible persons that came in close contact (in terms of space and time) with an infected person, whether it is Check-In data, whether load data from pkl and for **PP-HNSW** and **PP-KD-tree** we specify privacy preservation by secure=True, and we mension number of projection axis of the setsof hyperplanes, number of sets of hyperplanes and the number of bins in which we quantize the project data to preserve the privacy
 
 The main usefulness of the program is the `lightning fast search` through millions of check-in locations identifying the susceptible people in real quick time. Exact brute force distance computation involves scanning through billions of check-in locations for each infected person (a new query), which is not scalable. Pandemics can be better fought if susceptible people to catch an infection are quickly identified and quarantined. We believe that this tool can contribute to such a cause. We also observe that the recall achieved is satisfactory.

Play around with the parameters, i.e., `s (fraction infected)` to see what effects does it have on the recall and search times.


### Appendix: To generate data from FourSquare Check-ins

#### Get the FourSquare Check-in data

Download the Foursquare global check-in data (https://drive.google.com/file/d/0BwrgZ-IdrTotZ0U0ZER2ejI3VVk/view) in the project folder. After the files are downloaded execute the script `prepdata.sh`
```bash
sh prepdata.sh
```
to create the data file (named `data.txt`). The script converts the date-time formatted data into epochs and creates a file in the following format.
```bash
<userid> <check-in lattitude> <check-in longitude> <offset (in epochs)>
50756  55.696132 37.557842  0
190571  41.029717 28.974420  1
221021  40.748939 -73.992280  2
66981  30.270753 -97.752936  2
21010  59.941041 30.308104  3
```

As a part of the repository, we provide a zipped version of this file `data/data.txt.gz`. Check that after unzipping it, and executing `wc -l`, you should see `266909` lines.


#### Generating Simulated User Overlap Data 

The real FourSquare check-in data is not directly applicable for our study because it is much less likely that two Foursquare users would check-in to the same location (a point-of-interest, e.g. a museum/restaurant) at near about the same time. However, to model an infectious disease spread, we need to have users that came in close contact with each other (in terms of both space and time).

We undertake a simple simulation model to generate pseudo-user interactions (likely contacts). First, we filter the `data.txt` file to retain only one check-in per user. This makes the simulation algorithm easier to manage.

Next, for each user `U` (having a unique id),  we generate a set of mutually exclusive `pseudo-users` or `ghost-users`, which comprises the ground-truth information for each user. Note that since all the original/real user-checkins were sufficiently apart in space-time coordinates, it is likely that the neighbourhood of a user comprised of the ghost-user check-ins are also far apart  (in which case one can rely with sufficient confidence on the simulated ground-truth data).
For each user `U` we generate `p+n` number of `ghost-user` in `delta` neighbourhood, out of them `p` number of `ghost-users` are belong to `epsilon` neighbourhood, if user `U` is positively infected person then these `p` `ghost-users` will be considered as  vulnerable person, whom we need to identify, and remaining `n` people will be considered as non-suspicious persons as they are in safe distance from the infected person `U`.  In the following figure we have shown a visualization of simulated `ghost-users` corresponding to a real infected user (red person in the figure).
![Infected noninfected](Infected_noninfected.png)

To generate simulated data, simply execute
```bash
sh addusers.sh data.txt 5 1
```
where second argument is number of `ghost-users` `p`, we consider value of `n` as `2*p` and the last argument is value of `epsilon` and we consider `delta=2*epsilon`. 



Again, we provide a zipped version of this file as `data/data.txt_5_1.ext.gz`. Unzipping this file you should see `4270544` lines (`wc -l`).


### Preliminary Results

To address the correctness of our algorithm we employ `Recall` as evaluation metric because the task of finding suspectible users is a recall-oriented task (false positives are acceptable but not the false negatvies). While the parameter `epsilon` controls the number of people to whom the disease spreads from a single person, the parameter `delta` controls the number of false positives (intentionally introduced to see if the algorithm can filter out the true positives from the false ones). In the following table we have present our initial experimental results.

|Algorithm| #Users | Infected (%) | #Infected | #Pseudo-users | `epsilon` | `delta` | #Retrieved | Search<br>time (ms) | Recall |
|:------:|:------:|:--------------------:|:---------:|:------:|:----------:|:--------:|:----------:|:--------------:|:------:|
|HNSW| 266909 | 4 | 10676 | 5 | 1 | 2 | 100 | 0.0365 | 0.9987 |
|PP-HNSW| 266909 | 4 | 10676 | 5 | 1 | 2 | 100 | 0.0472 | 0.7698 |
|KD-tree| 266909 | 4 | 10676 | 5 | 1 | 2 | 100 | 2.9454 | 1.0000 |
|PP-KD-tree| 266909 | 4 | 10676 | 5 | 1 | 2 | 100 | 9.1374 | 0.8078 |
