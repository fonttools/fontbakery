num_checks () {
    i=$1
    numchecks=$(git grep "/check/" | grep " id" | grep "=" | cut -d= -f2 | cut -d, -f1 | sort | uniq | wc -l)
    echo "$i: $numchecks"

    #rm -rf checks.txt
    #for cmd in $(fontbakery --list-subcommands | tr " " "\n" | grep check- | grep -v "\-profile"| grep -v "\-specification"); do
    #    fontbakery $cmd -L | grep /check/ >> checks.txt;
    #done;
    #cat checks.txt | sort | uniq > sorted-checks.txt
    #numchecks=$(cat sorted-checks.txt | wc -l)

    date=$(git log | grep "Date:" | head -n1 | cut -d: -f2,3,4)
    output="$numchecks,$date"
    echo "$output" >> /tmp/num-checks.csv
    echo "$i | $output"
}

echo "Checks,Date" > /tmp/num-checks.csv
git checkout main
for i in $(seq 1 300); do
    num_checks $i;
    git checkout HEAD~1 2>&1 | grep "is now" | cut -d\  -f1,4,5
done;
git checkout main

