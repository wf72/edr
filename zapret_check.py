#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'wf'

import socket
import urllib2
import csv
import zapretinfo_run as __edr
from datetime import datetime


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


def checkblockedsites():
    """Возвращает 1, если есть не заблокированные сайты. Используется для zabbix."""
    __edr.LogWrite("Start check urls", "zb_check")
    f = urllib2.urlopen('http://api.antizapret.info/all.php?type=csv')
    reader = csv.reader(f, delimiter=';')
    result = []
    errors = []
    blocked = []
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
            try:
                count += 1
                answer = urllib2.urlopen(url, timeout=int(__edr.config('Main')['check_timeout']))
                tmpanswer = answer.read()
                if max(word in tmpanswer for word in __edr.config('Main')['find_words'].split("|")):
                    blocked.append(url)
                    continue
                else:
                    __edr.printt("Url %(url)s not blocked: \n===start====\n%(answer)s\n===end===\n" %
                                 {"url": url, "answer": tmpanswer})
                    __edr.LogWrite("Url %(url)s not blocked: \n===start====\n%(answer)s\n===end===\n" %
                                   {"url": url, "answer": tmpanswer}, "zb_check")
                    result.append(url)
            except urllib2.URLError as e:
                __edr.printt("There was an error: %r With: %s " % (e, url))
                errors.append(url)
            except socket.timeout as e:
                __edr.printt("There was an error: %r With: %s " % (e, url))
                errors.append(url)
    __edr.printt("===\nBlocked result: %s\n" % blocked)
    __edr.printt("===\nNot blocked result: %s\n" % result)
    __edr.printt("===\nWith errors: %s\n" % errors)
    __edr.LogWrite("===\nBlocked result: %s\n" % blocked)
    __edr.LogWrite("===\nNot blocked result: %s\n" % result)
    __edr.LogWrite("===\nWith errors: %s\n" % errors)
    zabbix_check_status_write(int(bool(result)))
    return int(bool(result))


def main():
    __start()
    checkblockedsites()


if __name__ == "__main__":
    main()
