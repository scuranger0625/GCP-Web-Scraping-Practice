#!/bin/bash

# VM1: instance-20241215-071520 (northamerica-northeast1-c)
gcloud compute ssh instance-20241215-071520 --zone=northamerica-northeast1-c --command="/tmp/venv/bin/python /tmp/crawler.py 4900 6249 > /tmp/crawler_log.txt 2>&1" &

# VM2: instance-20241215-071631 (europe-west1-d)
gcloud compute ssh instance-20241215-071631 --zone=europe-west1-d --command="/tmp/venv/bin/python /tmp/crawler.py 6250 7599 > /tmp/crawler_log.txt 2>&1" &

# VM3: instance-20241215-214321 (northamerica-northeast2-c)
gcloud compute ssh instance-20241215-214321 --zone=northamerica-northeast2-c --command="/tmp/venv/bin/python /tmp/crawler.py 7600 8949 > /tmp/crawler_log.txt 2>&1" &

# VM4: instance-20241215-214421 (us-west1-a)
gcloud compute ssh instance-20241215-214421 --zone=us-west1-a --command="/tmp/venv/bin/python /tmp/crawler.py 8950 10299 > /tmp/crawler_log.txt 2>&1" &

# VM5: instance-20241215-214438 (europe-west3-c)
gcloud compute ssh instance-20241215-214438 --zone=europe-west3-c --command="/tmp/venv/bin/python /tmp/crawler.py 10300 10800 > /tmp/crawler_log.txt 2>&1" &

# VM6: instance-20241215-214502 (europe-west9-c)
gcloud compute ssh instance-20241215-214502 --zone=europe-west9-c --command="/tmp/venv/bin/python /tmp/crawler.py 10801 11290 > /tmp/crawler_log.txt 2>&1" &

# 等待所有背景任務完成
wait

echo "所有爬蟲任務已完成！"
