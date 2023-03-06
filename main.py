import socket
import requests
from icmplib import traceroute
import sqlalchemy as db
from sqlalchemy import *
import pandas as pd


engine = create_engine('sqlite:///traceroute.db')
connection = engine.connect()
metadata = db.MetaData()

table = db.Table('traceroutes', metadata,
              db.Column('latency', db.Float()),
              db.Column('IP1', db.String(255)),
              db.Column('IP2', db.String(255))
              )


file_db = open('traceroute.txt', 'a')

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


def save_all_hops_with_rtt(hostname):
    targetIP = socket.gethostbyname(hostname)
    print(f'targetIP is {targetIP}')
    hops = traceroute(targetIP, count=20)
    last_distance = 1
    first_ip = hops[0].address
    for i in range(1,len(hops)):
        hop=hops[i]
        if last_distance + 1 != hop.distance:
            print("Some gateways are not responding")
        else:
            print(f'inserting {first_ip}-{hop.address} with {hop.min_rtt} ms')
            # query = db.insert(table).values(IP1=hops[i-1].address, IP2=hop.address, latency=hop.min_rtt) 
            # query = db.insert(table).values(IP1=first_ip, IP2=hop.address, latency=hop.min_rtt) 
            # ResultProxy = connection.execute(query)
            query = table.insert().values(IP1=first_ip, IP2=hop.address, latency=hop.min_rtt)
            connection.execute(query)
            file_db.write(f'{first_ip};{hop.address};{hop.min_rtt}\n')

        # geo = get_ip_location(hop.address)
        geo = ''

        # See the Hop class for details
        # print(f"{hop.distance}      {hop.address}       {hop.min_rtt} ms        {geo}")

        last_distance = hop.distance
        first_ip = hop.address




hostname = 'ya.ru'
#hostname = '1.1.1.1'

# myLoc = get_my_location()

# print(myLoc)

# targetIP = socket.gethostbyname(hostname)

# print(targetIP)

# hops = traceroute(hostname, count=20)

# print("Distance/TTL     Address     Min RTT     Geo")
# last_distance = 1

# first_ip = hops[0].address

# for i in range(1,len(hops)):
#     hop=hops[i]
#     # if last_distance + 1 != hop.distance:
#     #     print("Some gateways are not responding")
#     # else:
#     #     print(f'inserting {first_ip}-{hop.address} with {hop.min_rtt} ms')

#     # geo = get_ip_location(hop.address)
#     geo = ''

#     # See the Hop class for details
#     print(f"{hop.distance}      {hop.address}       {hop.min_rtt} ms        {geo}")

#     last_distance = hop.distance
#     first_ip = hop.address


#     query = db.insert(table).values(IP1=hops[i-1].address, IP2=hop.address, latency=hop.min_rtt) 
#     ResultProxy = connection.execute(query)

# save_all_hops_with_rtt('ya.ru')


# output = connection.execute(table.select()).fetchall()
# print(output)

# df = pd.DataFrame(output)

# df.head(10)



hosts_file = open('hosts_for_tracerouting.txt').readlines()

for host in hosts_file:
    # print(host.strip())
    save_all_hops_with_rtt(host.strip())

connection.commit()
connection.close()


