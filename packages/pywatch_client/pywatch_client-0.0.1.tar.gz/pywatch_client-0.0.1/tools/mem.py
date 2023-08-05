#coding:utf-8

def mem_info():
    mem_file = open("/proc/meminfo", "rb")
    lines = mem_file.readlines()
    mem_file.close()
    data = [int(i.split()[1]) for i in lines if i]
    mem_dict = {}
    mem_dict['total'] = data[0]
    mem_dict['free'] = data[1]
    mem_dict['os_used'] = data[0] - data[1]
    mem_dict['app_used'] = data[0] - data[1] - data[2] - data[3]
    mem_dict['available'] = data[1] + data[2] +data[3]
    mem_dict['buffers'] = data[2]
    mem_dict['cached'] = data[3]
    mem_dict['swap_total'] = data[13]
    mem_dict['swap_free'] = data[14]
    mem_dict['swap_used'] = data[13] - data[14]
    return mem_dict

if __name__ == '__main__':
    print mem_info()