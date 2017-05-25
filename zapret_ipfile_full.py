#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'wf'

from shutil import copyfile
from ast import literal_eval
from string import punctuation
from pid import PidFile


import zapretinfo_run as __edr
import dns.resolver


def __start():
    __edr.config()


def __check_domain(domain):
    try:
        nameservers = dns.resolver.query(domain, 'NS')
        if len(nameservers) > 0:
            return True
        else:
            return False
    except dns.exception.DNSException:
        return False

def __clean_domain_name(domain):
    while domain[0] in punctuation:
        domain = domain[1:]
    while domain[-1] in punctuation:
        domain = domain[:-1]
    return domain


def __gen_ipfile():
    ipfile = open(__edr.config('Dirs')['path_ip_file'] + "_full.tmp", 'w')
    if __edr.str2bool(__edr.config('Main')['export_ip_file']):
        con, cur = __edr.DBConnect()
        __edr.printt("Write ip's to file")
        __edr.LogWrite("Write ip's to file")
        cur.execute("SELECT ip FROM edrdata GROUP BY ip;")
        data = cur.fetchall()
        for ip in data:
            for i in literal_eval(ip[0]):
                ipfile.write("%s\n" % i)
    if __edr.str2bool(__edr.config('Main')['export_dns2ip_file']):
        __edr.printt("Write domain names to file")
        __edr.LogWrite("Write domain names to file")
        cur.execute("SELECT domain FROM edrdata GROUP BY domain;")
        data = cur.fetchall()
        domains = sorted(set([__edr.idnaconv(__clean_domain_name(domain[0])) for domain in data]))
        domains = sorted((domain for domain in domains if __check_domain(domain)))
        for domain in domains:
            ipfile.write("%s\n" % domain)
    ipfile.close()
    copyfile(__edr.config('Dirs')['path_ip_file'] + "_full.tmp", __edr.config('Dirs')['path_ip_file'] + "_full")


def main():
    if __edr.str2bool(__edr.config('Main')['nginx']):
        try:
            with PidFile("zapretinfo_run.py.pid"):
                __start()
                __gen_ipfile()
        except PidFileAlreadyLockedError:
            __edr.printt("Идёт обновление базы, выполненние невозможно.")
            __edr.LogWrite("Идёт обновление базы, выполненние невозможно.")

if __name__ == "__main__":
    main()
