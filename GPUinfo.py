# sudo docker ps --no-trunc --format "table {{.ID}}|{{.Names}}"                                                                                                                   

import csv
from pprint import pprint
from subprocess import Popen, PIPE
from lxml import etree
import psutil
import json
import time

htmldir = "/home/"
dockerdir = "/home/"
timeStr = "%Y-%m-%d %H:%M:%S"

def getDockerData():
    datas = csv.DictReader(open(dockerdir + "dockerData"), delimiter='|')
    dic = {}
    for i in datas:
        dic[i['CONTAINER ID']] = i['NAMES']
    return dic

def getNvidiaData():
    datas = {}
    with Popen(["nvidia-smi", '-q', '-x'], stdout=PIPE) as proc:
        xml = etree.fromstring(proc.stdout.read().decode())

        datas['last_sync_time'] = time.strftime(timeStr)
        datas['driver_version'] = xml.find('driver_version').text
        datas['gpus'] = []

        for gpu in xml.findall('gpu'):
            gdata = {
                'minor_number': gpu.find('minor_number').text,
                'product_name': gpu.find('product_name').text,
                'memory_total': gpu.find('fb_memory_usage/total').text,
                'memory_used': gpu.find('fb_memory_usage/used').text,
                'memory_free': gpu.find('fb_memory_usage/free').text,
                'memory_usage': gpu.find('utilization/memory_util').text,
                'gpu_usage': gpu.find('utilization/gpu_util').text,
                'gpu_usage': gpu.find('utilization/gpu_util').text,
                'process': []
            }
            for pro in gpu.findall('processes/process_info'):
                gdata['process'].append({
                    'used_memory': pro.find('used_memory').text,
                    'pid'        : pro.find('pid').text})
            datas['gpus'].append(gdata)
    return datas

def getContainer(p):
    while p.name() != 'docker-containerd-shim':
        p = p.parent()
    h = ""
    for l in p.cmdline():
        if 'moby' in l:
            h = l[l.rfind('/') + 1:]
    assert(h)
    return h

dockers = getDockerData()
while True:
    nvidias = getNvidiaData()
    for nv in nvidias['gpus']:
        for pr in nv['process']:
            pid = psutil.Process(int(pr['pid']))
            pr['user'] = dockers[getContainer(pid)]
            pr['create_time'] = time.strftime(timeStr, time.localtime(pid.create_time()))
            del pr['pid']
    json.dump(nvidias, open(htmldir + "GPUinfo.json", 'w'))
    time.sleep(9.5)