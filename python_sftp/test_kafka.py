from kafka import KafkaConsumer
import json
import csv

consumer = KafkaConsumer('vpn',bootstrap_servers= ['120.79.169.123:9092'], consumer_timeout_ms=10000)
listmsg = []
for message in consumer:
    listmsg.append(message)
    if len(listmsg) >= 10:
        break
listcsv = []
for message in listmsg:
    casdatas = json.loads(message.value)
    for casdata in casdatas:
        if casdata["vpnip"] != "":
            print("mac:",casdata["mac"]," vpnip:",casdata["vpnip"])
            listcsv.append((casdata["vpnip"],casdata["mac"]))
with open('newData.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(listcsv)