#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'wf'

from shutil import copyfile
import zapretinfo_run as __edr


def __start():
    __edr.config()


def __gen_ipfile():
    if __edr.str2bool(__edr.config('Main')['export_ip_file']):
        con, cur = __edr.DBConnect()
        ipfile = open(__edr.config('Dirs')['path_ip_file']+"_full.tmp", 'w')
        __edr.printt("Write ip's to file")
        __edr.LogWrite("Write ip's to file")
        cur.execute("SELECT ip FROM edrdata WHERE disabled=0 GROUP BY ip;")
        data = cur.fetchall()
        __edr.printt(data)
        for ip in data:
            __edr.printt(ip[0])
            ipfile.write(ip[0] + "\n")
        ipfile.close()
        copyfile(__edr.config('Dirs')['path_ip_file'] + "_full.tmp", __edr.config('Dirs')['path_ip_file'] + "_full")


def main():
    if __edr.str2bool(__edr.config('Main')['nginx']):
        __start()
        __gen_ipfile()


if __name__ == "__main__":
    main()
