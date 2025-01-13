#!/bin/sh
n=$1
echo "var n=$n"
if [ "$n" -gt 3 ]; then
    echo "three"
fi

for a in $(seq 1 10); do
    echo "$a"
done
