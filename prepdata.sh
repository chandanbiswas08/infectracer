awk -F '\t' '\
    BEGIN { \
        mintime = 0; \
        m["Jan"]="01";m["Feb"]="02";m["Mar"]="03";m["Apr"]="04";m["May"]="05";m["Jun"]="06";m["Jul"]="07";m["Aug"]="08";m["Sep"]="09";m["Oct"]="10";m["Nov"]="11";m["Dec"]="12"; \
    } \
    FNR==NR { \
        loc[$1]=$2" "$3; next \
    } \
    { \
    split($3,t," "); date=t[6] " " m[t[2]] " "t[3]; split(t[4],ts,":"); time=ts[1]" "ts[2]" "ts[3]; dt=date " " time; epochs=mktime(dt); \
    if (mintime==0) { \
        mintime = epochs; \
        epochs = 0; \
    } else { \
        epochs = epochs - mintime; \
    } \
    printf("%s\t%s\t%s\n", $1, loc[$2], epochs); \
}' \
dataset_TIST2015_POIs.txt dataset_TIST2015_Checkins.txt > data.txt

