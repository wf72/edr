#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'wf'
import os
import zapretinfo_run as __edr
from datetime import datetime, timedelta


def __start():
    __edr.config()


def diff_request():
    con, cur = __edr.DBConnect()
    cur.execute("SELECT max(time) FROM requests;")
    data = cur.fetchall()
    if data:
        request_date = data[0]
    else:
        request_date = "2012-01-01T01:01:01.000+06:00"
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
    request_path = __edr.config('Dirs')['XML_FILE_NAME']
    request_sig_path = __edr.config('Dirs')['SIG_FILE_NAME']
    pem_file = __edr.config('Dirs')['PEM_FILE_NAME']
    request_file = open(request_path, 'w')
    request_file.write(request_text)
    request_file.close()
    os.system("openssl smime -sign -in %(zapros)s -out %(zapros_sig)s -binary -signer %(pem)s -outform DER -nodetach" %
              {"zapros": request_file, "zapros_sig": request_sig_path, "pem": pem_file})


def full_request():
    request_text = """<?xml version="1.0" encoding="windows-1251"?>
    <request>
            <requestTime>2012-01-01T01:01:01.000+06:00</requestTime>
            <operatorName>Общество с ограниченной ответственностью «ВиЭйчДжи»</operatorName>
            <inn>7202217753</inn>
            <ogrn>1117232016076</ogrn>
    <email>vh-group@vh-group.net</email>
    </request>
    """
    request_path = __edr.config('Dirs')['XML_FILE_NAME']
    request_sig_path = __edr.config('Dirs')['SIG_FILE_NAME']
    pem_file = __edr.config('Dirs')['PEM_FILE_NAME']
    request_file = open(request_path, 'w')
    request_file.write(request_text)
    request_file.close()
    os.system("openssl smime -sign -in %(zapros)s -out %(zapros_sig)s -binary -signer %(pem)s -outform DER -nodetach" %
              {"zapros": request_file, "zapros_sig": request_sig_path, "pem": pem_file})


def request2db(data, **kwargs):
    con, cur = __edr.DBConnect()
    cur.execute("INSERT requests SET time=%(time)s data=%(data)s diff=%(diff)s code=%(code)s;",
                {'time': datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S%z"), 'data': data,
                 'diff': 1 if kwargs.get('diff', False) else 0, 'code': kwargs.get('code', "")})
    cur.close()
    con.close()


def main():
    __edr.config()


if __name__ == "__main__":
    main()
