#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'wf'

import socket
import urllib2
import csv
import os
import zapretinfo_run as __edr


def __start():
    __edr.config()


def zabbix_check_status_write(status):
    """Пишем статус проверки в файл, для zabbix"""
    work_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
    if __edr.config('Dirs')['zb_check_file']:
        if __edr.config('Dirs')['zabbix_status_file'][0] == "/":
            zb_check_status_file = __edr.config('Dirs')['zb_check_file']
        else:
            zb_check_status_file = work_dir + __edr.config('Dirs')['zb_check_file']

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
    zabbix_check_status_write(0)
    __edr.LogWrite("Start check urls")
    f = urllib2.urlopen('http://api.antizapret.info/all.php?type=csv')
    reader = csv.reader(f, delimiter=';')
    result = []
    errors = []
    count = 0
    max_count = int(__edr.config('Main')['max_url_check'])
    for row in reader:
        if max_count <= count:
            break
        url = row[1] or row[2]
        if url:
            if url[:4] != "http":
                url = "http://%s" % url
            try:
                count += 1
                answer = urllib2.urlopen(url, timeout=int(__edr.config('Main')['check_timeout']))
                tmpanswer = answer.read(100)
                if max(word in tmpanswer for word in __edr.config('Main')['find_words']):
                    continue
                else:
                    __edr.printt("Url %(url)s not blocked: %(answer)s" % {"url": url, "answer": tmpanswer})
                    __edr.LogWrite("Url %(url)s not blocked: %(answer)s" % {"url": url, "answer": tmpanswer})
                    result.append(url)
            except urllib2.URLError as e:
                __edr.printt("There was an error: %r With: %s " % (e,url))
                errors.append(url)
            except socket.timeout as e:
                __edr.printt("There was an error: %r With: %s " % (e, url))
                errors.append(url)
    __edr.printt("result: %s" % result)
    __edr.LogWrite("result: %s" % result)
    __edr.printt("errors: %s" % errors)
    __edr.LogWrite("errors: %s" % errors)
    __edr.LogWrite("Stop check urls")
    zabbix_check_status_write(int(bool(result)))
    return int(bool(result))


def main():
    __start()
    checkblockedsites()


if __name__ == "__main__":
    main()
