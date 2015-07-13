#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'wf'

from urlparse import urlparse
from urllib import quote

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
    nginx_conf_file_path = __edr.config('Dirs')['nginx_conf_file']
    nginx_conf_file = open(nginx_conf_file_path, 'w')
    cur.execute("SELECT url FROM edrdata WHERE disabled=0 GROUP BY domain;")
    data = cur.fetchall()
    domains = sorted(set([urlparse(url[0]).netloc for url in data]))

    for edr_domain in domains:
        # Формируем секцию server
        cur.execute("SELECT url FROM edrdata WHERE disabled=0 and domain=%s;", (edr_domain,))
        edr_urls = cur.fetchall()
        # edr_ports = set(['443' if urlparse(i[0]).scheme == 'https' else '80' for i in edr_urls if i[0]])
        edr_ports = set([urlparse(i[0].strip()).scheme for i in edr_urls if i[0]])
        for edr_port in edr_ports:
            cur.execute("SELECT url FROM edrdata WHERE disabled=0 and domain=%(domain)s and url like %(scheme)s;",
                        {'domain': edr_domain, 'scheme': edr_port+':%'})
            edr_urls = cur.fetchall()
            conf_server = """server {
    server_name %(domain)s;
    listen %(port)s;
    resolver 8.8.8.8;
""" % {'domain': edr_domain, 'port': '443' if edr_port == 'https' else '80'}
            # Формирует location
            conf_location = ""
            domain_block = 0
            for edr_url in edr_urls:
                edr_url = urlparse(edr_url[0].strip())
                # domain_block = 0 if (edr_url.path and (not edr_url.path == '/')) else 1
                if (not edr_url.path) or (edr_url.path == '/'):
                    domain_block = 1
                url_string = ''
                if edr_url.path:
                    url_string += quote(edr_url.path)
                else:
                    url_string += "/"
                if edr_url.query:
                    url_string += "?" + edr_url.query
                if edr_url.fragment:
                    url_string += "#" + edr_url.fragment
                conf_location += """    location %s {
        proxy_pass http://1.1.254.93;
                }
""" % url_string
            if not domain_block:
                conf_location += """    location / {
        proxy_pass http://$host;
                }
"""
        # Закрываем настройки сервера
            conf_end = """}
"""
            __edr.printt(conf_server + conf_location + conf_end)

            nginx_conf_file.write(conf_server + conf_location + conf_end)

    nginx_conf_file.close()


def main():
    if __edr.str2bool(__edr.config('Main')['nginx']):
        __start()
        __genereate()


if __name__ == "__main__":
    main()
