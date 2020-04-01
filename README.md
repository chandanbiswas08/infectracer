# INFECTRACER

  

A tool to quickly locate a set of susceptible persons given a global database of user check-ins and a set of infected people.

  

## Create the data

  

Download the Foursquare global [check-in data]([https://drive.google.com/file/d/0BwrgZ-IdrTotZ0U0ZER2ejI3VVk/view](https://drive.google.com/file/d/0BwrgZ-IdrTotZ0U0ZER2ejI3VVk/view)) in the project folder. Execute the script `prepdata.sh`
```
sh prepdata.sh
```
to create the data file (named `data.txt`). The script converts the date-time formatted data into epochs and creates a file in the following format.
```
<userid> <check-in lattitude> <check-in longitude> <offset (in epochs)>
50756  55.696132 37.557842  0
190571  41.029717 28.974420  1
221021  40.748939 -73.992280  2
66981  30.270753 -97.752936  2
21010  59.941041 30.308104  3
```

The next step is to install the `nmslib` library. Simply execute `pip install nmslib`. Make sure you have `numpy` installed.

You then need to execute
```
python index_checkins.py -d foursquare/data.txt -i 1m.idx
``` 
where you specify the data file (comprising the user-id, locations, time-offsets) and the index file to save the data. The indexing step enables a very fast retrieval of susceptible cases.

The next step is to retrieve the susceptible cases. The program simulates the case that a fraction of the population (whose data exists in the index already) has been infected. The `retrieval` program formulates and executes a query for each of these infected people and reports a list of 3 most susceptible persons that came in close contact (in terms of space and time) with an infected person.

You simply need to execute
```
python retrieve_susceptibles.py -d foursquare/data.1m.txt -i 1m.idx -s 0.00
``` 
where you specify the data file (to simulate infected people), the index file (to retrieve susceptible people) and the fraction infected (in the example set to `0.01` or `1%`).
The program prints out output in the following format:
```
Your CPU supports instructions that this binary was not compiled to use: AVX2
For maximum performance, you can install NMSLIB from sources
pip install --no-binary :all: nmslib
Reading data file...
Loading user ids...
Loading user data...

Number of users infected: 102
Infected user: 122449.0
Query location: [4198.565659367674, 2331.5955328793125, 4186.328901918209, 346462.0]
Suspectible User = 122449, distance from infected = 0.0
Suspectible User = 91054, distance from infected = 1.0602682828903198
Suspectible User = 215088, distance from infected = 13.606935501098633

Query location: [4214.166399962419, 2316.47542230921, 4179.0410588154255, 559599.0]
Suspectible User = 24151, distance from infected = 439.2506103515625
Suspectible User = 11306, distance from infected = 638.5771484375
Suspectible User = 76382, distance from infected = 1088.8251953125
...
...
```
 
 The main usefulness of the program is the `lightning fast search` through billions of check-in locations identifying the susceptible people in quick time. Exact brute force distance computation involves scanning through billions of check-in locations for each infected person (a new query), which is not scalable. Pandemics can be better fought if susceptible people to catch an infection are quickly identified and quarantined. We believe that this tool can contribute to such a cause.
  

