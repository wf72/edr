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

def __write_to_file(data):
    conf_file_path = __edr.config('Dirs')['bind_file']
    conf_file = open(conf_file_path+".tmp", 'w')
    conf_file.write("%s\n" % data)
    conf_file.close()


def __domainparse(domain):
    skip_domain = ['youtube.com', 'www.youtube.com']
    __edr.printt(domain)

    if not domain.lower() in skip_domain:
        if domain[-1:].isalpha():
            write_data = ('zone "%s" { type master; file "%s"; allow-query { any; }; };\n' % (
                domain, __edr.config('Dirs')['bind_block_file']))
        else:
            continue
        __write_to_file(write_data)

def __genereate():
    """
    Создаём файл настроек для bind
    :return:
    """
    __edr.LogWrite("Genereate bind file")

    bind_file_path = __edr.config('Dirs')['bind_file']
    bind_file = open(bind_file_path+".tmp", 'w')
    cur.execute("SELECT domain FROM edrdata WHERE disabled=0 GROUP BY domain;")
    data = cur.fetchall()
    data2 = set([__edr.idnaconv(domain[0].strip()) for domain in data])

    bind_file.close()
    con.close()
    copyfile(bind_file_path+".tmp",bind_file_path)


def main():
    if __edr.str2bool(__edr.config('Main')['bind']):
        __start()
        __genereate()


if __name__ == "__main__":
    main()
