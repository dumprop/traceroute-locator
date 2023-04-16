import dublintraceroute, pprint, json,time
from datetime import datetime

# print(json.dumps(flows))

def calculate_dublin_traceroute(ip):
    dublin = dublintraceroute.DublinTraceroute(ip, npaths=10)
    results = dublin.traceroute()
    flows = results['flows']
    # print(dublin)
    # pprint.pprint(results)
    # results.pretty_print()
    for flow in flows:
        
        # print(flow)
        for cur_flow in flows[flow]:
            result_str = ''
            flow_val=cur_flow
            # print(flows[flow])
            # print(flow_val['flowhash'])
            # print(json.dumps(flows[flow]))
            result_str+=f"{flow};{flow_val['flowhash']};{flow_val['is_last']};{flow_val['name']};"
            if 'nat_id' in flow_val:
                result_str+=f"{flow_val['nat_id']};"
            else:
                result_str+=f";"
            if not flow_val['received']:
                result_str+=f";;;;;;;;;;"
            else:
                flow_val_recv = flow_val['received']
                result_str+=f"{flow_val_recv['icmp']['code']};{flow_val_recv['icmp']['description']};{flow_val_recv['icmp']['extensions']};{flow_val_recv['icmp']['mpls_labels']};{flow_val_recv['icmp']['type']};{flow_val_recv['ip']['dst']};{flow_val_recv['ip']['id']};{flow_val_recv['ip']['src']};{flow_val_recv['ip']['ttl']};{flow_val_recv['timestamp']};"
            result_str+=f"{flow_val['rtt_usec']};"
            if not flow_val['sent']:
                result_str+=f";;;;;;;"
            else:
                flow_val_sent = flow_val['sent']
                result_str+=f"{flow_val_sent['ip']['dst']};{flow_val_sent['ip']['src']};{flow_val_sent['ip']['ttl']};{flow_val_sent['timestamp']};{flow_val_sent['udp']['dport']};{flow_val_sent['udp']['sport']};"
            if 'zerottl_forwarding_bug' in flow_val:
                result_str+=f'{flow_val["zerottl_forwarding_bug"]}'
            # print(result_str)
            file_db_string = open("dublin-traceroutes-string.txt", "a")
            file_db_unixtimestamp = open("dublin-traceroutes-unixtimestamp.txt", "a")
            file_db_string.write(
                f"{datetime.now()};{result_str}\n"
            )
            file_db_unixtimestamp.write(
                f"{time.time()};{result_str}\n"
            )
            file_db_string.close()
            file_db_unixtimestamp.close()
    #     

# calculate_dublin_traceroute('8.8.8.8')
calculate_dublin_traceroute('1.1.1.1')
