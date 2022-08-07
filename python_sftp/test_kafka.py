from kafka import KafkaConsumer
import json
import csv
import configparser

conf = configparser.ConfigParser()
conf.read("config.ini", encoding="utf-8")
readnum = conf.getint('kafka','readnum')

consumer = KafkaConsumer('vpn',bootstrap_servers= ['120.79.169.123:9092'], consumer_timeout_ms=10000)
listmsg = []
for message in consumer:
    listmsg.append(message)
    if len(listmsg) >= readnum:
        break
dictcsv = {}
for message in listmsg:
    casdatas = json.loads(message.value)
    for casdata in casdatas:
        if casdata["vpnip"] != "":
            print("mac:",casdata["mac"]," vpnip:",casdata["vpnip"])
            dictcsv[casdata["mac"]] = casdata["vpnip"]   
listcsv = []
for mac,vpnip in dictcsv.items():
    listcsv.append((vpnip,mac))
with open('ip_sn.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(listcsv)
