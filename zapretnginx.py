#!/usr/bin/env python
# -*- coding: utf-8 -*-
#__author__ = 'wf'

from urlparse import urlparse
from shutil import copyfile
import zapretinfo_run as __edr


def __start():
    __edr.config()
    global con
    global cur
    con, cur = __edr.DBConnect()


def __genereate():
    """
    Создаём файл настроек для nginx
    :return:
    """
    __edr.LogWrite("Genereate nginx file")
    nginx_conf_file_path = __edr.config('Dirs')['nginx_conf_file']
    nginx_conf_file = open(nginx_conf_file_path+".tmp", 'w')
    __edr.LogWrite("block long url")
    cur.execute("SELECT url FROM edrdata WHERE disabled=0 GROUP BY domain;")
    data = cur.fetchall()
    domains = sorted(set([urlparse(url[0]).netloc for url in data]))
    for edr_domain in domains:
        # Формируем секцию server
        cur.execute("SELECT url FROM edrdata WHERE disabled=0 and  url like %s;", ('%://' + edr_domain + '/%',))
        edr_urls = cur.fetchall()
        edr_ports = sorted(set([urlparse(i[0].strip()).scheme for i in edr_urls if i[0]]))
        for edr_port in edr_ports:
            if "all" in edr_ports and edr_port != "all":
                continue
            if edr_port == "https":
                port = '443'
            elif edr_port == "http":
                port = '80'
            else:
                port = "80;\nlisten 443"

            conf_server = """server {
    server_name %(domain)s;
    listen %(port)s;
""" % {'domain': __edr.idnaconv(edr_domain), 'port': port}
        # Формирует location
        conf_location = ""
        domain_block = 0
        url_string = "/"
        query = """SELECT url FROM edrdata WHERE disabled=0 and url like \'%s\' ORDER BY url;""" % \
                ('%://' + edr_domain + '/%')
        cur.execute(query)
        edr_urls = cur.fetchall()
        urls_to_write = set()
        for edr_url_temp in edr_urls:
            edr_url = urlparse(edr_url_temp[0].strip())
            # domain_block = 0 if (edr_url.path and (not edr_url.path == '/')) else 1
            if (not edr_url.path) or (edr_url.path == '/'):
                domain_block = 1
            if (edr_url.scheme+edr_url.netloc).__len__()+3 != edr_url_temp[0].strip().__len__():
                urls_to_write.add(edr_url_temp[0].strip()[(edr_url.scheme+edr_url.netloc).__len__()+3:])
        for url_string in urls_to_write:
            conf_location += """    location "%s" {
    proxy_pass %s;
            }
""" % (url_string, __edr.config('URLS')['nginx_stop_url'])
        if not domain_block:
            conf_location += """    location / {
    proxy_pass http://$host;
            }
"""
        # Закрываем настройки сервера
        conf_end = """    resolver %(dns_serv)s;
        }
""" % {'dns_serv':  __edr.config('Main')['dns_serv']}
        __edr.printt(conf_server + conf_location + conf_end)
        nginx_conf_file.write(conf_server + conf_location + conf_end)
    nginx_conf_file.close()
    copyfile(nginx_conf_file_path+".tmp", nginx_conf_file_path)


def main():
    if __edr.str2bool(__edr.config('Main')['nginx']):
        __start()
        __genereate()


if __name__ == "__main__":
    main()
