#coding:utf-8
import time

def cpu_info():
    cpu_file = open("/proc/stat", "rb")
    line = cpu_file.readline()
    cpu_info_list = [int(i) for i in line.split()[1:]]
    cpu_file.close()
    return cpu_info_list

def cpu_rate(start, end):
    cpu_info_list_0 = start
    cpu_info_list_1 = end
    cpu_time_0 = sum(cpu_info_list_0)
    cpu_time_1 = sum(cpu_info_list_1)
    cpu_total_time = cpu_time_1 - cpu_time_0
    cpu_total_idle = cpu_info_list_1[3] - cpu_info_list_0[3]
    cpu_total_user = cpu_info_list_1[0] - cpu_info_list_0[0]
    cpu_total_iowait = cpu_info_list_1[4] - cpu_info_list_0[4]
    cpu_total_system = cpu_info_list_1[2] - cpu_info_list_0[2]

    cpu_total_rate = 100.0 * (cpu_total_time - cpu_total_idle) / cpu_total_time
    cpu_user_rate = 100.0 * cpu_total_user / cpu_total_time
    cpu_iowait_rate = 100.0 * cpu_total_iowait / cpu_total_time
    cpu_system_rate = 100.0 * cpu_total_system / cpu_total_time

    return {'total':cpu_total_rate, 'user':cpu_user_rate, 'system':cpu_system_rate, 'iowait':cpu_iowait_rate}

if __name__ == '__main__':
    def main(t):
        start = cpu_info()
        while True:        
            time.sleep(t)
            end = cpu_info()
            cpu_rate(start, end)
            start = end
    main(3)