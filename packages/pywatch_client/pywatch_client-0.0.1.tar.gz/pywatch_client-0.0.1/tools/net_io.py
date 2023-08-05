#coding:utf-8
import time

def net_info(card):
    net_file = open("/proc/net/dev", "rb")
    lines = net_file.readlines()
    net_file.close()
    in_byte_list = []
    in_packets_list = []
    out_byte_list = []
    out_packets_list = []
    for line in lines:
        if line.find(card) >= 0:
            data = line.split()
            in_byte_list.append(int(data[1]))
            in_packets_list.append(int(data[2]))
            out_byte_list.append(int(data[9]))
            out_packets_list.append(int(data[10]))
    net_dict = {}
    net_dict['in_byte'] = sum(in_byte_list)
    net_dict['in_packets'] = sum(in_packets_list)
    net_dict['out_byte'] = sum(out_byte_list)
    net_dict['out_packets'] = sum(out_packets_list)
    return net_dict

def net_rate(start, end, t):
    net_rate_dict = {}
    net_rate_dict['in_byte_rate'] = (end['in_byte'] - start['in_byte']) / float(t)
    net_rate_dict['out_byte_rate'] = (end['out_byte'] - start['out_byte']) / float(t)
    net_rate_dict['in_packets_rate'] = (end['in_packets'] - start['in_packets']) / float(t)
    net_rate_dict['out_packets_rate'] = (end['out_packets'] - start['out_packets']) / float(t)
    return net_rate_dict

if __name__ == '__main__':
    while True:
        start0 = net_info("eth0")
        start1 = net_info("eth1")
        time.sleep(1)
        end0 = net_info("eth0")
        end1 = net_info("eth1")
        result0 = net_rate(start0, end0, 1)
        result1 = net_rate(start1, end1, 1)
        print "eth0:\n{0}".format(result0)
        print "eth1:\n{0}".format(result1)