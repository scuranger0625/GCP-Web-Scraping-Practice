#!/bin/bash

# 確認執行進度

# VM1: instance-20241215-071520 (northamerica-northeast1-c)
echo "==== VM1: northamerica-northeast1-c ===="
gcloud compute ssh instance-20241215-071520 --zone=northamerica-northeast1-c --command="tail -n 20 /tmp/crawler_log.txt"

# VM2: instance-20241215-071631 (europe-west1-d)
echo "==== VM2: europe-west1-d ===="
gcloud compute ssh instance-20241215-071631 --zone=europe-west1-d --command="tail -n 20 /tmp/crawler_log.txt"

# VM3: instance-20241215-214321 (northamerica-northeast2-c)
echo "==== VM3: northamerica-northeast2-c ===="
gcloud compute ssh instance-20241215-214321 --zone=northamerica-northeast2-c --command="tail -n 20 /tmp/crawler_log.txt"

# VM4: instance-20241215-214421 (us-west1-a)
echo "==== VM4: us-west1-a ===="
gcloud compute ssh instance-20241215-214421 --zone=us-west1-a --command="tail -n 20 /tmp/crawler_log.txt"

# VM5: instance-20241215-214438 (europe-west3-c)
echo "==== VM5: europe-west3-c ===="
gcloud compute ssh instance-20241215-214438 --zone=europe-west3-c --command="tail -n 20 /tmp/crawler_log.txt"

# VM6: instance-20241215-214502 (europe-west9-c)
echo "==== VM6: europe-west9-c ===="
gcloud compute ssh instance-20241215-214502 --zone=europe-west9-c --command="tail -n 20 /tmp/crawler_log.txt"
