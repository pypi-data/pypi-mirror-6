#coding:utf-8
import time
import json
import zmq
import re

from tools import cpu_load
from tools import cpu_rate
from tools import mem
from tools import disk_used
from tools import disk_io
from tools import net_io

version = "0.0.2"

def get_hostname():
    eth_info = open("/etc/sysconfig/network-scripts/ifcfg-eth1", "rb")
    lines = eth_info.readlines()
    eth_info.close()
    for line in lines:
        if line.startswith("IPADDR"):
            host = "s" + re.search(r"(?<=168\.1\.)\d+", line).group()
            return host

TIME_INTERVAL = 60
MASTER_IP = "192.168.1.227:3721"
CLIENT_INFO = get_hostname()

context = zmq.Context()
sender = context.socket(zmq.PUSH)
sender.connect("tcp://%s"%MASTER_IP)

def get_info():
    info_dict = {}
    info_dict['cpu_load'] = cpu_load.cpu_load()
    info_dict['mem'] = mem.mem_info()
    info_dict['root_used'] = disk_used.disk_info("/")
    info_dict['data_used'] = disk_used.disk_info("/data")
    info_dict['cpu_rate'] = cpu_rate.cpu_info()
    info_dict['disk_io'] = disk_io.disk_io()
    info_dict['net_io0'] = net_io.net_info("eth0")
    info_dict['net_io1'] = net_io.net_info("eth1")
    return info_dict

def get_result(start, end):
    result = {}
    result['cpu_load'] = end['cpu_load']
    result['mem'] = end['mem']
    result['root_used'] = end['root_used']
    result['data_used'] = end['data_used']
    result['cpu_rate'] = cpu_rate.cpu_rate(start['cpu_rate'], end['cpu_rate'])
    result['disk_io'] = disk_io.io_rate(start['disk_io'], end['disk_io'], TIME_INTERVAL)
    result['net_io0'] = net_io.net_rate(start['net_io0'], end['net_io0'], TIME_INTERVAL)
    result['net_io1'] = net_io.net_rate(start['net_io1'], end['net_io1'], TIME_INTERVAL)
    return result

def main():
    start = get_info()
    global TIME_INTERVAL
    time_start = int(time.time())
    while True:
        time.sleep(TIME_INTERVAL)
        end = get_info()
        time_end = int(time.time())
        if (time_end - time_start) != 60:
            TIME_INTERVAL = 60 - int(time_end) + int(time_start) + 60
            ts = time_end - int(time_end) + int(time_start) + 60
            print TIME_INTERVAL
        else:
            TIME_INTERVAL = 60
            ts = time_end
        time_start = ts
        send_dict = get_result(start, end)
        send_dict['timestamp'] = int(ts)
        print ts
        send_dict['host'] = CLIENT_INFO
        sender.send(json.dumps(send_dict))
        start = end


if __name__ == '__main__':
    main()