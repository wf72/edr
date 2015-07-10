#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'wf'

import sys
from urlparse import urlparse

import zapretinfo_run as __edr


def start():
    __edr.config()
    global con
    global cur
    con, cur = __edr.DBConnect()


def ValidateUrl(line):
    """
    Проверяем URL по базе
    :param line: Строка, переданная squidoм, первый параметр URL, второй - адрес клиента
    :return:
    """
    ban = 0
    if not line:
        return
    __edr.LogWrite('Reques: %s' % line)
    llist = line.split(' ')
    URL = urlparse(llist[0].strip())
    cur.execute('SELECT url from __edrdata where domain=%s and disabled=0',
                (URL.netloc,))
    data = cur.fetchall()
    for rec in data:
        __edr_url = urlparse(rec[0].strip())
        if (not __edr_url.path) and (__edr_url.netloc == URL.netloc):
            ban = 1
        elif (__edr_url.netloc == URL.netloc) and (__edr_url.path == URL.path):
            ban = 1

    if not ban:
        __edr.LogWrite("Url passed: %s ip: %s" % (tuple(llist[:2]), ''))
        return llist[0].strip() + "\n"
    else:
        __edr.LogWrite("Url blocked: %s ip: %s" % (tuple(llist[:2]), ''))
        return __edr.STOP_URL + "\n"


def main():
    start()
    while True:
        llist = sys.stdin.readline().strip()
        sys.stdout.write(ValidateUrl(llist))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
