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
    cur.execute("SELECT domain FROM edrdata WHERE disabled=0 GROUP BY domain;")
    data = cur.fetchall()
    for rec in data:
        # Формируем секцию server
        edr_domain = rec[0].strip()
        cur.execute("SELECT url FROM edrdata WHERE disabled=0 and domain=%s;", (edr_domain,))
        edr_urls = cur.fetchall()
        edr_ports = ' '.join(set(['443' if i == 'http' else '80' for i in edr_urls if i]))
        conf_server = """
        server {
            listen %(ports)s;
            server_name %(domain)s;
        """ % {'ports': edr_ports, 'domain': edr_domain}
        # Формирует location
        conf_location = ""
        for edr_url in edr_urls:
            edr_url = urlparse(edr_url[0])
            all_domain_block = 0 if edr_url.path else 1
            conf_location += """
                location /%(path)s {
                    proxy_pass http://127.0.0.1
                }
            """ % {'path': edr_url.path}

        if not all_domain_block:
            conf_location += """
                location / {
                    proxy_pass %s://$host
                }
            """ %
        # Закрываем настройки сервера
        conf_end = """
            }
        """
        if edr_urls.__len__() > 1:
            print edr_urls
            print(conf_server + conf_location + conf_end)
            break

            # nginx_conf_file.write(data)

    nginx_conf_file.close()


def main():
    if __edr.str2bool(__edr.config('Main')['bind']):
        __start()
        __genereate()


if __name__ == "__main__":
    main()
