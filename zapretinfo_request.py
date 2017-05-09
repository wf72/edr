#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'wf'
import os
import zapretinfo_run as __edr
from datetime import datetime, timedelta


def __start():
    __edr.config()


def gen_request(**kwargs):
    __start()
    con, cur = __edr.DBConnect()
    request_date = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S%z")
    # else:
    #     request_date = "2012-01-01T01:01:01.000+06:00"
    cur.close()
    con.close()
    request_text = """<?xml version="1.0" encoding="windows-1251"?>
<request>
        <requestTime>%s</requestTime>
        <operatorName>Общество с ограниченной ответственностью «ВиЭйчДжи»</operatorName>
        <inn>7202217753</inn>
        <ogrn>1117232016076</ogrn>
<email>vh-group@vh-group.net</email>
</request>
""" % request_date
    # datetime.strftime(datetime.now() - timedelta(days=7), "%Y-%m-%dT%H:%M:%S%z")
    request_path = __edr.config('Dirs')['xml_file_name']
    request_sig_path = __edr.config('Dirs')['sig_file_name']
    pem_file = __edr.config('Dirs')['pem_file_name']
    openssl = __edr.config('Dirs')['openssl_path']
    request_file = open(request_path, 'w')
    request_file.write(request_text)
    request_file.close()
    os.system("%(openssl)s smime -sign -in %(zapros)s -out %(zapros_sig)s -binary -signer %(pem)s -outform DER -nodetach" %
              {"zapros": request_path, "zapros_sig": request_sig_path, "pem": pem_file, 'openssl': openssl})


def request2db(data, **kwargs):
    __start()
    con, cur = __edr.DBConnect()
    __edr.printt("INSERT requests SET time=%(time)s, data=%(data)s, code=%(code)s;" %
                {'time': datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S%z"),
                 'data': data, 'code': kwargs.get('code', "")})
    cur.execute("INSERT requests SET time=%(time)s, data=%(data)s, code=%(code)s;",
                {'time': datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S%z"),
                 'data': data, 'code': kwargs.get('code', "")})
    con.commit()
    cur.close()
    con.close()


def get_last_dump_date():
    __start()
    con, cur = __edr.DBConnect()
    cur.execute('SELECT max(time) FROM requests;')
    data = cur.fetchall()
    if data[0][0]:
        last_dump_date_epoch = int(data[0][0].strftime('%s'))*1000
    else:
        last_dump_date_epoch = 0
    return last_dump_date_epoch


def main():
    __start()


if __name__ == "__main__":
    main()
