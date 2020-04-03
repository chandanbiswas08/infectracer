#Add simulated user interactions... a simple simulation method...
#to make sure that we generate the ground truth for each user (we choose infected users at random)
#select a user one-by-one... for user with id 'u' and the maxuser id of this file (say m), 1<=u<=m,
#simulate a given number of ghost users with ids... m+u+1,m+u+2...m+u+k where k is the #ghost users 

if [ $# -lt 1 ]
then
        echo "Usage: $0 <data-file>"
        exit
fi

K=5
DATA=$1
EXTENDED_DATA=$DATA.ext
EPSILON=0.05


#edit the user ids in the original file
#only one user record... suffices for our simple simulation...
cat $DATA | sort -n -k1| awk 'BEGIN{prev=0; userid=1} {if ($1!=prev) {prev=$1; printf("%s %s %s %s\n", userid++, $2, $3, $4)}}' > tmp
mv tmp $DATA

maxuserid=`cat $DATA|awk '{print $1}'| tail -n1`
#echo "maxuserid = $maxuserid"

cat $DATA |awk -v K=$K -v EPSILON=$EPSILON -v MAXID=$maxuserid '{\
print $0; \
userid=$1; \
lat=$2; \
long=$3; \
time=$4; \
ghostuserid_start = MAXID + K*(userid-1); \
for (s=1; s<=K; s++) { \
    ghostuserid = ghostuserid_start + s; \
    del_lat = -EPSILON + rand()*2*EPSILON; \
    del_long = -EPSILON + rand()*2*EPSILON; \
    new_lat = lat + del_lat; \
    new_long = long + del_long; \
    printf ("%s %s %s %s\n", ghostuserid, new_lat, new_long, time); \
} \
}' > $EXTENDED_DATA

