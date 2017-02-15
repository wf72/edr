#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'wf'

import zapretinfo_run as __edr
from shutil import copyfile


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
    __edr.LogWrite("Genereate bind file")
    skip_domain = ['youtube.com', 'www.youtube.com']
    bind_file_path = __edr.config('Dirs')['bind_file']
    bind_file = open(bind_file_path+".tmp", 'w')
    cur.execute("SELECT domain FROM edrdata WHERE disabled=0 GROUP BY domain;")
    data = cur.fetchall()
    for rec in data:
        edr_url = rec[0].strip()
        if (not edr_url.lower() in skip_domain):
            if (edr_url[-1:].isalpha()):
                write_data = ('zone "%s" { type master; file "%s"; allow-query { any; }; };\n' % (\
                edr_url.encode('idna'), __edr.config('Dirs')['bind_block_file']))
            #elif edr_url[-1:] == ".":
            #    write_data = ('zone "%s" { type master; file "%s"; allow-query { any; }; };\n' % ( \
            #    edr_url[:-1], __edr.config('Dirs')['bind_block_file']))
            else:
                continue
            bind_file.write(write_data)
    bind_file.close()
    con.close()
    copyfile(bind_file_path+".tmp",bind_file_path)


def main():
    if __edr.str2bool(__edr.config('Main')['bind']):
        __start()
        __genereate()


if __name__ == "__main__":
    main()
