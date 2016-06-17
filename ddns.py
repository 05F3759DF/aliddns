#!/usr/bin/env python
#-*- coding:utf-8 -*-
from __future__ import print_function
import httplib
import time
import re, json
import os, sys, argparse
from aliyunsdkcore import client
from aliyunsdkalidns.request.v20150109 import UpdateDomainRecordRequest, DescribeDomainRecordInfoRequest

import env
for k in dir(env):
    if not k.startswith('_'):
        globals()[k] = vars(env)[k]

clt = client.AcsClient(CLIENT_ID, SECRET_TOKEN, 'cn-hangzhou')

def printLog(*log):
    print('[%s] ' % time.ctime(), end='')
    for item in log[:-1]:
        print(item, end=', ')
    print(log[-1])

def getCurrentIP():
    request = DescribeDomainRecordInfoRequest.DescribeDomainRecordInfoRequest()
    request.set_RecordId(RECORD_ID)
    request.set_accept_format('json')
    response = clt.do_action(request)
    printLog(response)
    return json.loads(response)['Value']

def ddns(ip):
    request = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
    request.set_RecordId(RECORD_ID)
    request.set_RR(RR)
    request.set_Type('A')
    request.set_Value(ip)
    request.set_accept_format('json')
    response = clt.do_action(request)
    printLog(response)
    return response

def getIP():
    conn = httplib.HTTPConnection('ipwhois.cnnic.net.cn')
    conn.request('GET', '/')
    data = conn.getresponse().read().decode('utf8')
    conn.close()
    ip = re.search('欢迎来自([^ ]+)的用户'.decode('utf8'), data).group(1)
    return ip

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ali ddns')
    parser.add_argument('-d', '--daemon', action='store_true', help='set if works in background .')
    args = parser.parse_args()
    if args.daemon:
         sys.stderr = sys.stdout = open('ddns.log', 'a', 1)
         if os.fork():
             exit()

    current_ip = getCurrentIP()
    while True:
        try:
            ip = getIP()
            printLog(ip)
            if current_ip != ip:
                if ddns(ip):
                    current_ip = ip
        except Exception as e:
            printLog(e)
        time.sleep(30)
