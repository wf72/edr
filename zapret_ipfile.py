#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'wf'

from shutil import copyfile
from ast import literal_eval
import zapretinfo_run as __edr


def __start():
    __edr.config()


def blacklist():
    f = open(__edr.config('Dirs')['path_blacklist_ips'],'r')
    return set(line for line in f)


def __gen_ipfile():
    if __edr.str2bool(__edr.config('Main')['export_ip_file']):
        con, cur = __edr.DBConnect()
        ipfile = open(__edr.config('Dirs')['path_ip_file']+".tmp", 'w')
        __edr.printt("Write ip's to file")
        __edr.LogWrite("Write ip's to file")
        if __edr.str2bool(__edr.config('Main')['export_clear_ip']):
            cur.execute("SELECT ip FROM edrdata WHERE disabled=0 and domain='ip' GROUP BY ip;")
            data = cur.fetchall()
            cur.execute('SELECT ip FROM edrdata WHERE disabled=0 and domain rlike "^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$" GROUP BY ip;')
            data += cur.fetchall()
        else:
            cur.execute("SELECT ip FROM edrdata WHERE disabled=0 GROUP BY ip;")
            data = cur.fetchall()
        cur.close()
        con.close()
        __edr.printt(data)
        for ip in data:
            for i in literal_eval(ip[0]):
                ipfile.write("%s\n" % i)
        for ip in blacklist():
            ipfile.write("%s\n" % ip)
        ipfile.close()
        copyfile(__edr.config('Dirs')['path_ip_file'] + ".tmp", __edr.config('Dirs')['path_ip_file'])
        __edr.LogWrite("Write ip's to file done")


def main():
    __start()
    __gen_ipfile()


if __name__ == "__main__":
    main()
