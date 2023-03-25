import socket
import requests
from icmplib import traceroute
import sqlalchemy as db
from sqlalchemy import *
import pandas as pd
from datetime import datetime
import ipaddress
import time

# engine = create_engine("sqlite:///traceroute.db")
# connection = engine.connect()
# metadata = db.MetaData()

# table = db.Table(
#     "traceroutes",
#     metadata,
#     db.Column("datetime", db.String(255)),
#     db.Column("latency", db.Float()),
#     db.Column("IP1", db.String(255)),
#     db.Column("IP2", db.String(255)),
# )
# metadata.create_all(engine)

file_db_string = open("traceroutes-string.txt", "a")
file_db_unixtimestamp = open("traceroutes-unixtimestamp.txt", "a")


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
    try:
        if "/" in hostname:
            targetips = [str(ip) for ip in ipaddress.IPv4Network(hostname)]
        else:
            print(hostname)
            targetips = [socket.gethostbyname(hostname)]
            print(targetips)

        # print(f"targetips is {targetips}")
        for targetIP in targetips:
            hops = traceroute(targetIP, count=20)
            if hops:
                last_distance = 1
                first_ip = hops[0].address
                for i in range(1, len(hops)):
                    hop = hops[i]
                    print(hop)
                    if last_distance + 1 != hop.distance:
                        print("Some gateways are not responding")
                    else:
                        print(f"inserting {first_ip}-{hop.address} with {hop.min_rtt} ms")

                        file_db_string.write(
                            f"{datetime.now()};{first_ip};{hop.address};{hop.min_rtt}\n"
                        )
                        file_db_unixtimestamp.write(
                            f"{time.time()};{first_ip};{hop.address};{hop.min_rtt}\n"
                        )

                    # geo = get_ip_location(hop.address)
                    geo = ""
                    # See the Hop class for details
                    # print(f"{hop.distance}      {hop.address}       {hop.min_rtt} ms        {geo}")

                    last_distance = hop.distance
                    first_ip = hop.address
    except:
        print(f'problem w/ {hostname}')


hostname = "ya.ru"
# hostname = '1.1.1.1'

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


hosts_file = open("hosts_for_tracerouting.txt").readlines()

for host in hosts_file:
    # print(host.strip())
    save_all_hops_with_rtt(host.strip())

# connection.commit()
# connection.close()
