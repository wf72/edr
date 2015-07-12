#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'wf'

import zapretinfo_run as __edr
from urlparse import urlparse

def __start():
    __edr.config()
    global con
    global cur
    con, cur = __edr.DBConnect()


def __genereate():
    """
    Ну и ужас творится в списках, куча двойных записей, неправильных ссылок. И так как это всё потом
    передавать в настройки, нужно убрать все косяки из базы.
    :return:
    """
    cur.execute("SELECT url FROM edrdata WHERE disabled=0;")
    data = cur.fetchall()
    for rec in data:
        edr_url = rec[0].strip()
        if urlparse(edr_url).netloc[-1:] == ".":
            cur.execute("DELETE FROM edrdata WHERE url = %s;", edr_url)
            con.commit()
        edr_url2 = edr_url+"/"
        cur.execute("SELECT url FROM edrdata WHERE disabled=0 and url=%s", edr_url2)
        data2 = cur.fetchall()
        for rec2 in data2:
            __edr.printt("first : %s" % rec)
            __edr.printt("second: %s" % rec2)
            cur.execute("DELETE FROM edrdata WHERE url = %s;", edr_url)
            con.commit()
            __edr.printt("Deleted: %s" % edr_url)

    cur.execute("DELETE e1 FROM  edrdata e1, edrdata e2 WHERE e1.id > e2.id AND e1.url = e2.url;")
    con.commit()
    cur.execute('DELETE FROM  edrdata WHERE  url like "%?";')
    con.commit()
    cur.execute('DELETE FROM  edrdata WHERE  url like "%#";')
    con.commit()
    con.close()


def main():
    __start()
    __genereate()


if __name__ == "__main__":
    main()
