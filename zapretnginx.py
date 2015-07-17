#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'wf'

from urlparse import urlparse

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
        cur.execute("SELECT url FROM edrdata WHERE disabled=0 and  url like %s;", ('%://' + edr_domain + '/%',))
        edr_urls = cur.fetchall()
        # edr_ports = set(['443' if urlparse(i[0]).scheme == 'https' else '80' for i in edr_urls if i[0]])
        edr_ports = set([urlparse(i[0].strip()).scheme for i in edr_urls if i[0]])
        for edr_port in edr_ports:
            cur.execute("SELECT url FROM edrdata WHERE disabled=0 and url like %s;",
                        edr_port + '://' + edr_domain + '/%')
            edr_urls = cur.fetchall()
            conf_server = """server {
    server_name %(domain)s;
    listen %(port)s;
    resolver 8.8.8.8;
""" % {'domain': edr_domain, 'port': '443' if edr_port == 'https' else '80'}
            # Формирует location
            conf_location = ""
            domain_block = 0
            for edr_url_temp in edr_urls:
                edr_url = urlparse(edr_url_temp[0].strip())
                # domain_block = 0 if (edr_url.path and (not edr_url.path == '/')) else 1
                if (not edr_url.path) or (edr_url.path == '/'):
                    domain_block = 1
                if (edr_url.scheme+edr_url.netloc).__len__()+3 != edr_url_temp[0].strip().__len__():
                    url_string = edr_url_temp[0].strip()[(edr_url.scheme+edr_url.netloc).__len__()+3:]
                    # if edr_url_temp[0].strip().__contains__(" ") and re.search('[А-Я]+', edr_url_temp[0]):
                    #     url_string = quote(url_string).replace('%3D', '=') \
                    #         .replace('%26', '&').replace('%23', '#').replace('%3F', '?')
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

