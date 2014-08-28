#!/usr/bin/python
#coding=utf-8

import sys,os
from statsd import StatsClient
import re

'''
    version 1.0
    author Curosr
    Daemon方式采集nginx_access日志和fpm的slow,error日志
'''

BASEDIR = os.path.abspath(os.curdir)
PATH = lambda *p: os.path.join(BASEDIR, *p)
#BASEDIR = os.path.dirname("/usr/local/shell/pystatsd")
file_seek = {}

def seekfile(file_type, logfile, offset_values, file_size):
    cur_size = os.fstat(logfile.fileno()).st_size

    '''如果当前文件大小小于旧值, 说明文件已切割, 重置文件position位'''
    if cur_size >= file_size:
        logfile.seek(offset_values)
    else:
        logfile.seek(0)

    lines = logfile.readlines()
    position = logfile.tell()

    position_list = [0,0]
    position_list[0] = position
    position_list[1] = cur_size

    file_seek[file_type] = position_list

    return lines


def check_nginx_status(coll_type, file, server, port, local):
    nginx_type = "nginx_" + coll_type.split('.')[0].strip()

    if file_seek.has_key(nginx_type):
        offset_values = int(file_seek[nginx_type][0])
        file_size = int(file_seek[nginx_type][1])
    else:
        offset_values = 0
        file_size = 0

    logfile = open(file, 'r')

    '''seeklines信息是指从上次关闭文件的位置到此次打开文件的位置所包含的数据'''
    seeklines = seekfile(nginx_type, logfile, offset_values, file_size)
    logfile.close()

    nginx_status={'2XX':0,'3XX':0,'4XX':0,'5XX':0}

    if seeklines == "":
        nginx_status['2XX'] = 0
        nginx_status['3XX'] = 0
        nginx_status['4XX'] = 0
        nginx_status['5XX'] = 0
    else:
        for line in seeklines:
            status_tmp=line.strip().split('')[6]
            if int(status_tmp[:1]) in [2,3,4,5]:
                status = status_tmp[:1]+"XX"

            if nginx_status.has_key(status):
                nginx_status[status] += 1
            else:
                nginx_status[status] = 1

    #print nginx_status
    local_ip = local

    if local_ip:
        graphite_ip = local_ip.replace(".", "_")

    sc = StatsClient(server,port)
    for nginx_status, status_count in nginx_status.items():
        print nginx_status, status_count
        sc.gauge(graphite_ip+".nginx."+coll_type.split('.')[0].strip()+"."+nginx_status, int(status_count))

def check_fpm_error(coll_type, file, server, port, local):
    fpm_error_type = "fpm_err_" + coll_type.split('.')[0].strip()

    if file_seek.has_key(fpm_error_type):
        offset_values = int(file_seek[fpm_error_type][0])
        file_size = int(file_seek[fpm_error_type][1])
    else:
        offset_values = 0
        file_size = 0
    try:
        logfile = open(file, 'r')
        '''seeklines信息是指从上次关闭文件的位置到此次打开文件的位置所包含的数据'''
        seeklines = seekfile(fpm_error_type, logfile, offset_values, file_size)
        logfile.close()
    except IOError as ioerr:
        print ioerr

    fpm_error_status={'error_num' : 0}
    if seeklines == "":
        fpm_error_status['error_num'] = 0
    else:
        for line in seeklines:
            fpm_error_match = re.match(r'(^\[+\d+-\w+-\d+\s+\d+:\d+:\d+\s+\w+\])\s(.*)',line)
            if fpm_error_match != None:
                fpm_error_status['error_num'] += 1

    #print nginx_status
    local_ip = local

    if local_ip:
        graphite_ip = local_ip.replace(".", "_")

    sc = StatsClient(server,port)
    for fpm_status, fpm_count in fpm_error_status.items():
        print fpm_status, fpm_count
        sc.gauge(graphite_ip+".fpm_error."+coll_type.split('.')[0].strip()+"."+fpm_status, int(fpm_count))

def check_fpm_slow(coll_type, file, server, port, local):
    fpm_slow_type = "fpm_slow_" + coll_type.split('.')[0].strip()

    if file_seek.has_key(fpm_slow_type):
        offset_values = int(file_seek[fpm_slow_type][0])
        file_size = int(file_seek[fpm_slow_type][1])
    else:
        offset_values = 0
        file_size = 0
    try:
        logfile = open(file, 'r')
        '''seeklines信息是指从上次关闭文件的位置到此次打开文件的位置所包含的数据'''
        seeklines = seekfile(fpm_slow_type, logfile, offset_values, file_size)
        logfile.close()
    except IOError as ioerr:
        print ioerr

    fpm_slow_status = {'slow_num' : 0}

    if seeklines == "":
        fpm_slow_status['slow_num'] = 0
    else:
        for line in seeklines:
            fpm_slow_match = re.match(r'^\[\d+\-\w+\-\d+\s+\d+:\d+:\d+\].*$',line)
            if fpm_slow_match != None:
                fpm_slow_status['slow_num'] += 1

    #print nginx_status
    local_ip = local

    if local_ip:
        graphite_ip = local_ip.replace(".", "_")

    sc = StatsClient(server,port)
    for fpm_status, fpm_count in fpm_slow_status.items():
        print fpm_status, fpm_count
        sc.gauge(graphite_ip+".fpm_slow."+coll_type.split('.')[0].strip()+"."+fpm_status, int(fpm_count))

if __name__ == '__main__':
    import optparse
    import ConfigParser
    from time import sleep

    parser = optparse.OptionParser()
    parser.add_option("-c","--config", dest="config", default="/etc/pystatsd/pystatsd.conf", help="pytstatsd collect config")

    options, args = parser.parse_args()
    if options.config == "":
        print "run this script, example: python pystatsd.py -c /path/SelfDefine.conf Also the SelfDefine.conf default is /etc/pystatsd/pystatsd.conf"
        exit(0)

    cf = ConfigParser.ConfigParser()
    cf.read(options.config)

    # pystatsd config comm
    comm_server = cf.get('common', 'server')
    comm_port = int(cf.get('common', 'port'))
    comm_local = cf.get('common', 'local')
    comm_interval = float(cf.get('common', 'interval'))

    # pystatsd config nginx_access
    if int(cf.getboolean('nginx_access', 'enable')) == 1:
        nginx_access_dir = cf.get('nginx_access', 'log_base')

        '''nginx日志目录下存在多个项目的access日志, 用分号分割'''
        nginx_access_type = cf.get('nginx_access', 'log_type')

    # pystatsd config fpm_slow
    if int(cf.getboolean('fpm_slow', 'enable')) == 1:
        fpm_slow_dir = cf.get('fpm_slow', 'log_base')

        '''fpm日志目录下存在多个项目的slow日志, 用分号分割'''
        fpm_slow_type = cf.get('fpm_slow', 'log_type')

    # pystatsd config fpm_error
    if int(cf.getboolean('fpm_error', 'enable')) == 1:
        fpm_error_dir = cf.get('fpm_error', 'log_base')

        '''fpm日志目录下存在多个项目的error日志, 用分号分割'''
        fpm_error_type = cf.get('fpm_error', 'log_type')

    if not os.path.exists(BASEDIR):
        os.makedirs(BASEDIR)

    while True:
        if int(cf.getboolean('nginx_access', 'enable')) and nginx_access_dir != "":
            for access_type in nginx_access_type.split(';'):
                nginx_file = PATH(nginx_access_dir, access_type)
                check_nginx_status(access_type, nginx_file, comm_server, comm_port, comm_local)

        if cf.getboolean('fpm_error', 'enable') and fpm_error_dir != "":
            for error_type in fpm_error_type.split(';'):
                fpm_error_file = PATH(fpm_error_dir, error_type)
                check_fpm_error(error_type, fpm_error_file, comm_server, comm_port, comm_local)

        if cf.getboolean('fpm_slow', 'enable') and fpm_slow_dir != "":
            for slow_type in fpm_slow_type.split(';'):
                fpm_slow_file = PATH(fpm_slow_dir, slow_type)
                check_fpm_slow(slow_type, fpm_slow_file, comm_server, comm_port, comm_local)

        print "sleep %s" % comm_interval
        sleep(comm_interval)
