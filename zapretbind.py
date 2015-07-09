#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'wf'

import zapretinfo_run as edr


def start():
    edr.config()
    global con
    global cur
    con, cur = edr.DBConnect()


def genereate():
    bind_file_path = edr.config('Dirs')['bind_file']
    bind_file = open(bind_file_path, 'w')
    cur.execute("SELECT domain from edrdata where disabled=0")
    data = cur.fetchall()
    for rec in data:
        edr_url = rec[0].strip()
        str = ('zone "%s" { type master; file "master/block-edr"; allow-query { any; }; };\n' % edr_url)
        bind_file.write(str)

    bind_file.close()


def main():
    start()
    genereate()


if __name__ == "__main__":
    main()
