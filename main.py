import socket
import requests
from icmplib import traceroute
import sqlalchemy as db
from sqlalchemy import *
import pandas as pd


def get_my_location():
    """
    return: MyIP, lon,lat,city
    """
    url = "https://ipapi.co/json/"
    response = requests.get(url)
    data = response.json()
    try:
        myIP = data["ip"]
        lon = data["longitude"]
        lat = data["latitude"]
        city = data["city"]
        return myIP, (lon, lat), city
    except KeyError as a:
        return f"Error: {a} Not Found"
    except:
        return "exception in get_my_location"


def get_ip_location(ip):
    """
    input: ip
    return: lon,lat,city
    """
    url = f"https://ipapi.co/{ip}/json/"
    response = requests.get(url)
    data = response.json()
    # try:
    if "error" in data:
        return data["reason"]
    lon = data["longitude"]
    lat = data["latitude"]
    return (data["longitude"], data["latitude"]), data["city"], data["asn"], data["org"]
    # except:
    #     return "exception in get_ip_location"


engine = create_engine('sqlite:///traceroute.db')
connection = engine.connect()
metadata = db.MetaData()

table = db.Table('traceroutes', metadata,
              db.Column('latency', db.Float()),
              db.Column('IP1', db.String(255)),
              db.Column('IP2', db.String(255))
              )


hostname = 'ya.ru'
#hostname = '1.1.1.1'


myLoc = get_my_location()

print(myLoc)


targetIP = socket.gethostbyname(hostname)

print(targetIP)



hops = traceroute(hostname, count=10)

print("Distance/TTL     Address     Min RTT     Geo")
last_distance = 0

for i in range(len(hops[:-1])):
    hop=hops[i]
    if last_distance + 1 != hop.distance:
        print("Some gateways are not responding")

    geo = get_ip_location(hop.address)

    # See the Hop class for details
    print(f"{hop.distance}      {hop.address}       {hop.min_rtt} ms        {geo}")

    last_distance = hop.distance


    query = db.insert(table).values(IP1=hop.address, IP2=hops[i+1].address, latency=hop.min_rtt) 
    ResultProxy = connection.execute(query)



output = connection.execute(table.select()).fetchall()
print(output)

df = pd.DataFrame(output)

df.head(4)

