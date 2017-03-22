#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'wf'

from urlparse import urlparse
from urllib import quote
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
    domains = sorted(set([__edr.idnaconv(urlparse(url[0]).netloc) for url in data]))
    for edr_domain in domains:
        # Формируем секцию server
        cur.execute("SELECT url FROM edrdata WHERE disabled=0 and url like %s;", ('%://' + edr_domain + u'/%',))
        edr_urls = cur.fetchall()
        cur.execute("SELECT url FROM edrdata WHERE disabled=0 and url like %s;", ('%://' + edr_domain,))
        edr_urls += cur.fetchall()
        # try:
        #     cur.execute("SELECT url FROM edrdata WHERE disabled=0 and url like %s;",
        #                 ('%://' + __edr.idnaconv(edr_domain, True) + '/%',))
        #     edr_urls += cur.fetchall()
        #     cur.execute("SELECT url FROM edrdata WHERE disabled=0 and url like %s;",
        #                 ('%://' + __edr.idnaconv(edr_domain, True),))
        #     edr_urls += cur.fetchall()
        # except UnicodeDecodeError as e:
        #     print("Cannot parse %s with error %s" % (edr_domain, e))
        # except UnicodeEncodeError as e:
        #     print("Cannot parse %s with error %s" % (edr_domain, e))

        edr_ports = sorted(set([urlparse(i[0].strip()).scheme for i in edr_urls if i[0]]))
        conf_ports = ''
        for edr_port in edr_ports:
            if "all" in edr_ports and edr_port != "all":
                continue
            if edr_port == "https":
                port = '443'
            elif edr_port == "http":
                port = '80'
            else:
                port = "80;\n\tlisten 443"
            conf_ports += "\tlisten %(port)s;\n" % {'port': port}
        conf_server = """server {
    server_name %(domain)s;
""" % {'domain': __edr.idnaconv(edr_domain)}
        conf_server += conf_ports
        # Формирует location
        conf_location = u""
        domain_block = 0
        query = """SELECT url FROM edrdata WHERE disabled=0 and url like \'%s\';""" % \
                ('%://' + edr_domain + u'/%')
        cur.execute(query)
        edr_urls = cur.fetchall()
        query = """SELECT url FROM edrdata WHERE disabled=0 and url like \'%s\';""" % \
                ('%://' + edr_domain)
        cur.execute(query)
        edr_urls += cur.fetchall()
        urls_to_write = set()

        for edr_url_temp in sorted(edr_urls):
            edr_url = urlparse(edr_url_temp[0].strip())

            if (not edr_url.path.strip()) or (edr_url.path == '/'):
                urls_to_write.add('/')
                domain_block = 1
                break
            try:
                path = edr_url.path.strip().encode('ascii')
            except UnicodeEncodeError:
                path = quote(edr_url.path.strip())
            urls_to_write.add(path)


        for url_string in sorted(urls_to_write):
            conf_location += """    location "%s" {
    proxy_pass %s;
            }
""" % (url_string.strip(), __edr.config('URLS')['nginx_stop_url'])

        if not domain_block:
            conf_location += """    location / {
        proxy_pass http://$host;
            }
"""
        # Закрываем настройки сервера
        conf_end = """    resolver %(dns_serv)s;
        }
""" % {'dns_serv':  __edr.config('Main')['dns_serv']}
        try:
            __edr.printt("%s\n%s\n%s" % (conf_server, conf_location, conf_end))
        except UnicodeEncodeError as e:
            __edr.printt(e)
        try:
            nginx_conf_file.write("%s\n%s\n%s" % (conf_server, conf_location, conf_end))
        except UnicodeEncodeError as e:
            __edr.printt(e)
            raise
    nginx_conf_file.close()
    copyfile(nginx_conf_file_path+".tmp", nginx_conf_file_path)
    con.close()


def main():
    if __edr.str2bool(__edr.config('Main')['nginx']):
        __start()
        __genereate()


if __name__ == "__main__":
    main()
