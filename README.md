% INFECTRACER: Approximate Nearest Neighbors Retrieval of GPS Location Traces to Report Candidate Infections
% Chandan Biswas, Indian Statistical Institute, Kolkata[^1]
  Debasis Ganguly, IBM Research Lab, Dublin, Ireland[^2]
[^1]: chandanbiswas08_r@isical.ac.in
[^2]: debasis.ganguly1@ie.ibm.com

In the present national emergency situation of coronavirus pandemic governments of all countries are trying to prevent massive propagation of that virus. To get a success in preventing propagation of the Covid-19 virus many governments have decided to keep the whole country locked down. According to experts, prevention of the spread of the disease can be achieved by quarantining all Covid-19 positive patients, and all those persons who came in contact or closer to these patients within last 15-20 days. Very often it happens that a person who came in close contact with an infected patient hides this information from local administration to avoid quarantine. In this situation, the key problem is finding out who those people are. This repository describes a  system that reports all possible cases of proximities of a person with another infected person. We believe that with the availabity of GPS location data of a large number of users, the system can very quickly help finding suspectible people in very quick time (which in the real-life could help in the initiative of imposing quarantine on them and prevent further spread of the disease).


## INFECTRACER

  

A tool to quickly locate a set of susceptible persons given a global database of user check-ins and a set of infected people.


### Extract the data

If you want to generate your own data (using a different simulation approach then read the Appendix section).  Else to conduct experiments on the provided dataset, simply execute

```bash
gunzip data/*
wc -l data/data.txt
wc -l data/data.txt.ext
```
For which you should see
```bash
266909 data/data.txt
1601454 data/data.txt.ext
```

### Approximate Retrieval Approach

The objective of the retrieval approach is then to find the set of ghost-users given a real user, because as per the ground-truth of the simulated data these (pseudo) users came in close contact with a known infected user. 

In a real life situation, one has a massive database of user checkins of a population out of which it is known that a number of persons are infected. The goal is to rapidly find the candidate set of people who came in close contact with the infected. However, a brute force search to locate the candidates would take a huge time (since it is a quadratic time complexity operation).

In our approach, we undertake an **approximate nearest neighbor** search approach to solve the problem. The two main research questions in this setup are:

1. How does **efficiency** (run-time) vary with the fraction of people infected, e.g., if `10% of a population gets infected, is this still a feasible solution`?
2. What is the **effectiveness** of the approximate nearest neighbor search? Since it is an approximate method, it can make mistakes. Is there a satisfactory bound on the error rate?

 
### Indexing the Data
  
The next step is to install the `nmslib` library. Simply execute `pip install nmslib`. Make sure you have `numpy` installed (if not execute `pip install numpy`).

You then need to execute
```bash
python index_checkins.py -d data/data.txt.ext -i simusers.idx
``` 
where you specify the data file (comprising the user-id, locations, time-offsets) and the index file to save the data. The indexing step enables a very fast retrieval of susceptible cases.
The geo-locations of users (which in real life can be obtained from GPS locations of smart phones) are then represented as `3` dimensional points (*2 space dimensions* corresponding to the location on the Earth's surface and *1 time dimension* measured in epoch seconds). The path traced in this 3 dimensional space-time corresponds to the activity phase of a single user. The idea is shown in the figure below, which shows a simple visualization of a 2d space-time world (the space-time in our case is 3d).

![Spacetime](spacetime.png)

Each person is shown as a path (curve) in this space-time, i.e. each person changing his position (x coordinate) with respect to time (which is ever increasing meaning that the curves monotonically increase with respect to the x coordinate, or in other words the curves never loop down). The figure shows two intersections in this graph one of which is an intersection of a healthy person with an infected one (leaving him at a high risk of infection). The job of the program is to **automatically find all such possible intersections** given a **huge** list of such person location traces (curves in the space-time) and a given list of infected people (query curves like the one shown with red in the figure). 

### Retrieval of Candidate Infected Persons

The next step is to retrieve the susceptible cases. The program simulates the case that a fraction of the population (whose data exists in the index already) has been infected. The `retrieval` program formulates and executes a query for each of these infected people and reports a list of 3 most susceptible persons that came in close contact (in terms of space and time) with an infected person.

You simply need to execute
```bash
python retrieve_susceptibles.py -d data/data.txt.ext -i simusers.idx -s 0.01 -n 266909
``` 
where you specify the data file (to simulate infected people), the index file (to retrieve susceptible people) and the fraction infected (in the example set to `0.01` or `1%`).
The last argument is the number of real users in the data (this is useful for the program to compute the ground-truth information and compute recall).

The program prints out output in the following format:
```bash
Reading data file...
Loading user ids...
Loading user data...
Number of users infected: 2669
Search time = 0.055400
Avg. Recall = 0.9332
```
 
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
sh addusers.sh data.txt
```



Again, we provide a zipped version of this file as `data/data.txt.ext.gz`. Unzipping this file you should see `1601454` lines (`wc -l`).


### Preliminary Results

To address the correctness of our algorithm we employ `Recall` as evaluation metric because the task of finding suspectible users is a recall-oriented task (false positives are acceptable but not the false negatvies). While the parameter `epsilon` controls the number of people to whom the disease spreads from a single person, the parameter `delta` controls the number of false positives (intentionally introduced to see if the algorithm can filter out the true positives from the false ones). In the following table we have present our initial experimental results.

| #Users | Infected (%) | #Infected | #Pseudo-users | `epsilon` | `delta` | #Retrieved | Search<br>time (s) | Recall |
|:------:|:--------------------:|:---------:|:------:|:----------:|:--------:|:----------:|:--------------:|:------:|
| 266909 | 1 | 2669 | 5 | 1 | 2 | 5 | 0.0774 | 0.9036 |
| 266909 | 2 | 5338 | 5 | 1 | 2 | 5 | 0.1569 | 0.9016 |
| 266909 | 3 | 8007 | 5 | 1 | 2 | 5 | 0.2559 | 0.9010 |
| 266909 | 4 | 10676 | 5 | 1 | 2 | 5 | 0.3087 | 0.9052 |
