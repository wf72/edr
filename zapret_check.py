#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'wf'

import socket
import urllib2
import csv
import zapretinfo_run as __edr
from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool


def __start():
    __edr.config()


def zabbix_check_status_write(status):
    """Пишем статус проверки в файл, для zabbix"""
    if __edr.config('Dirs')['zb_check_file']:
        zb_check_status_file = __edr.config('Dirs')['zb_check_file']
        zb_file = open(zb_check_status_file, "w")
        if status:
            zb_file.write("1\n")
            __edr.printt("Writing to zb_check_file 1")
            __edr.LogWrite("Writing to zb_check_file 1")
        else:
            zb_file.write("0\n")
            __edr.printt("Writing to zb_check_file 0")
            __edr.LogWrite("Writing to zb_check_file 0")
        zb_file.close()


def checksite(url):
    result = {'notblocked': [], 'errors': [], 'blocked': []}
    if url:
        if url[:4] != "http":
            url = "http://%s" % url
        try:
            answer = urllib2.urlopen(url, timeout=int(__edr.config('Main')['check_timeout']))
            tmpanswer = answer.read()
            if max(word in tmpanswer for word in __edr.config('Main')['find_words'].split("|")):
                result['blocked'] = url
            else:
                result['notblocked'] = url
        except urllib2.URLError:
            result['errors'] = url
        except socket.timeout:
            result['errors'] = url
    __edr.LogWrite("""===Blocked result: %(blocked)s
!!!Not blocked: %(notblocked)s
...With errors: %(errors)s\n""" % result)
    return result


def checkblockedsites():
    """Возвращает 1, если есть не заблокированные сайты. Используется для zabbix."""
    __edr.LogWrite("Start check urls", "zb_check")
    f = urllib2.urlopen('http://api.antizapret.info/all.php?type=csv')
    reader = csv.reader(f, delimiter=';')
    pool = ThreadPool(4)
    result = {'notblocked': [], 'errors': [], 'blocked': []}
    urls = []
    count = 0
    max_count = int(__edr.config('Main')['max_url_check'])
    for row in reader:
        if row[0] == datetime.now().strftime("%Y-%m-%d"):
            continue
        if max_count <= count:
            break
        url = row[1] or row[2]
        if url:
            if url[:4] != "http":
                url = "http://%s" % url
            urls.append(url)
            count += 1
    results = pool.map(checksite, urls)
    for i in results:
        for key in result.keys():
            if i[key]:
                result[key].append(i[key])
    __edr.printt("===\nBlocked result: %s\n" % result['blocked'])
    __edr.printt("===\nNot blocked result: %s\n" % result['notblocked'])
    __edr.printt("===\nWith errors: %s\n" % result['errors'])
    __edr.LogWrite("===\nBlocked result: %s\n" % result['blocked'])
    __edr.LogWrite("===\nNot blocked result: %s\n" % result['notblocked'])
    __edr.LogWrite("===\nWith errors: %s\n" % result['errors'])
    pool.close()
    pool.join()
    zabbix_check_status_write(int(bool(result)))
    return int(bool(result))


def main():
    __start()
    checkblockedsites()


if __name__ == "__main__":
    main()
