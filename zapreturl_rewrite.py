#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'wf'

import sys
from urlparse import urlparse

import zapretinfo_run as edr


def start():
    edr.config()
    global con
    global cur
    con, cur = edr.DBConnect()


def ValidateUrl(line):
    """
    Проверяем URL по базе
    :param line: Строка, переданная squidoм, первый параметр URL, второй - адрес клиента
    :return:
    """
    ban = 0
    if not line:
        return
    edr.LogWrite('Reques: %s' % line)
    llist = line.split(' ')
    URL = urlparse(llist[0].strip())
    cur.execute('SELECT url from edrdata where domain=%s and disabled=0',
                (URL.netloc,))
    data = cur.fetchall()
    for rec in data:
        edr_url = urlparse(rec[0].strip())
        if (not edr_url.path) and (edr_url.netloc == URL.netloc):
            ban = 1
        elif (edr_url.netloc == URL.netloc) and (edr_url.path == URL.path):
            ban = 1

    if not ban:
        edr.LogWrite("Url passed: %s ip: %s" % (tuple(llist[:2]), ''))
        return llist[0].strip() + "\n"
    else:
        edr.LogWrite("Url blocked: %s ip: %s" % (tuple(llist[:2]), ''))
        return edr.STOP_URL + "\n"


def main():
    start()
    while True:
        llist = sys.stdin.readline().strip()
        sys.stdout.write(ValidateUrl(llist))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
