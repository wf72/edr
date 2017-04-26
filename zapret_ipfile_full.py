#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'wf'

from shutil import copyfile
from ast import literal_eval
from string import punctuation
import zapretinfo_run as __edr
import dns.resolver



def __start():
    __edr.config()

def __check_domain(domain):
    nameservers = dns.resolver.query(domain, 'NS')
    if len(nameservers) > 0:
        return True
    else False


def __clean_domain_name(domain):
    while domain[0] in punctuation:
        domain = domain[1:]
    while domain[-1] in punctuation:
        domain = domain[:-1]
    return domain

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
            for i in literal_eval(ip[0]):
                ipfile.write("%s\n" % i)
    if __edr.str2bool(__edr.config('Main')['export_dns2ip_file']):
        __edr.printt("Write domain names to file")
        __edr.LogWrite("Write domain names to file")
        cur.execute("SELECT domain FROM edrdata WHERE disabled=0 GROUP BY domain;")
        data = cur.fetchall()
        domains = sorted(set([__edr.idnaconv(__clean_domain_name(domain[0])) for domain in data]))
        domains = sorted((domain for domain in domains if __check_domain(domain)))
        for domain in domains:
            ipfile.write("%s\n" % i)
        ipfile.close()
        copyfile(__edr.config('Dirs')['path_ip_file'] + "_full.tmp", __edr.config('Dirs')['path_ip_file'] + "_full")


def main():
    if __edr.str2bool(__edr.config('Main')['nginx']):
        __start()
        __gen_ipfile()


if __name__ == "__main__":
    main()
