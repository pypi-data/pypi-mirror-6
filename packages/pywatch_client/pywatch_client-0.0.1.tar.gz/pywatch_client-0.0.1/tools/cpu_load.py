#coding:utf-8

def cpu_load():
    cpu_file = open("/proc/loadavg", "rb")
    line = cpu_file.readline()
    cpu_file.close()
    load_list = line.split()
    process_count = int(load_list[3].split('/')[-1])
    return {'1m':float(load_list[0]), '5m':float(load_list[1]), '15m':float(load_list[2]), 'process_count':process_count}

if __name__ == '__main__':
    print cpu_load()