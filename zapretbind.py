#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'wf'

from shutil import copyfile
from multiprocessing.dummy import Pool as ThreadPool
from pid import PidFile
from pid import PidFileError
import zapretinfo_run as __edr


def __start():
    __edr.config()
    global con
    global cur
    con, cur = __edr.DBConnect()


def __write_to_file(data):
    if data:
        conf_file_path = __edr.config('Dirs')['bind_file']
        conf_file = open(conf_file_path+".tmp", 'w')
        conf_file.write("%s\n" % data)
        conf_file.close()


def __domainparse(domain):
    #skip_domain = ['youtube.com', 'www.youtube.com']
    white_list = __edr.config('Main')['white_list'].split(';')
    #__edr.printt(domain.strip())
    if not domain.lower() in white_list:
        if domain[-1:].isalpha():
            write_data = 'zone "%s" { type master; file "%s"; allow-query { any; }; };' % (
                domain, __edr.config('Dirs')['bind_block_file'])
            return write_data
    return ""


def __genereate():
    """
    Создаём файл настроек для bind
    :return:
    """
    __edr.LogWrite("Genereate bind file")
    cur.execute("SELECT domain FROM edrdata WHERE disabled=0 GROUP BY domain;")
    data = cur.fetchall()
    data2 = sorted(set([__edr.idnaconv(domain[0].strip()) for domain in data]))
    cur.close()
    con.close()
    pool = ThreadPool(int(__edr.config('Main')['threads']))
    result = set(pool.map(__domainparse, data2))
    __write_to_file("\n".join(result))
    bind_file_path = __edr.config('Dirs')['bind_file']
    copyfile(bind_file_path+".tmp", bind_file_path)
    __edr.LogWrite("Genereate bind file done")


def main():
    try:
        with PidFile("zapretbind.py.pid"):
            if __edr.str2bool(__edr.config('Main')['bind']):
                __start()
                __genereate()
    except PidFileError:
        __edr.printt("Уже запущено обновление.")

if __name__ == "__main__":
    main()
