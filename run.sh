#!/bin/bash
python3 progress_bar.py &
for ((i = 1; i <= 15; i++ ))
do
python3 fetch.py &
done
wait