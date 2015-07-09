#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'wf'

import zapretinfo_run as __edr


def __start():
    __edr.config()
    global con
    global cur
    con, cur = __edr.DBConnect()


def __genereate():
    """
    Создаём файл настроек для bind
    :return:
    """
    bind_file_path = __edr.config('Dirs')['bind_file']
    bind_file = open(bind_file_path, 'w')
    cur.execute("SELECT domain from edrdata where disabled=0")
    data = cur.fetchall()
    for rec in data:
        edr_url = rec[0].strip()
        data = ('zone "%s" { type master; file "master/block-edr"; allow-query { any; }; };\n' % edr_url)
        bind_file.write(data)

    bind_file.close()


def main():
    if __edr.config('Main')['bind']:
        __start()
        __genereate()


if __name__ == "__main__":
    main()
