#coding:utf-8

def disk_io():
    disk_file = open("/proc/diskstats", "rb")
    lines = disk_file.readlines()
    line = [i for i in lines if i.find(" sda ") >= 0][0]
    io_list = [int(i) for i in line.split()[3:]]
    disk_file.close()
    io = {}
    io['read_io'] = io_list[0]
    io['write_io'] = io_list[4]

    io['rrqm'] = io_list[1]
    io['wrqm'] = io_list[5]

    io['rkb'] = io_list[2] / 2.0
    io['wkb'] = io_list[6] / 2.0
    
    io['rtime'] = io_list[3]
    io['wtime'] = io_list[7]
    return io

def io_rate(start, end, t):
    io = {}
    io['rps'] = (end['read_io'] - start['read_io']) / float(t)
    io['wps'] = (end['write_io'] - start['write_io']) / float(t)
    io['rrqm'] = (end['rrqm'] - start['rrqm']) / float(t)
    io['wrqm'] = (end['wrqm'] - start['wrqm']) / float(t)
    io['rkb'] = (end['rkb'] - start['rkb']) / float(t)
    io['wkb'] = (end['wkb'] - start['wkb']) / float(t)
    io['rtime'] = (end['rtime'] - start['rtime']) / float(t)
    io['wtime'] = (end['wtime'] - start['wtime']) / float(t)
    return io


if __name__ == '__main__':
    import time
    start = disk_io()
    while True:
        time.sleep(1)
        end = disk_io()
        print io_rate(start, end, 1)
        start = end