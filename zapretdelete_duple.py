#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'wf'

import zapretinfo_run as __edr


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
    __edr.LogWrite('Remove duplicates')
    cur.execute("SELECT url FROM edrdata WHERE disabled=0;")
    data = cur.fetchall()
    __edr.LogWrite('Remove duplicates. Loop.')
    for rec in data:
        edr_url = rec[0].strip()
        edr_url2 = edr_url+"/"
        cur.execute("SELECT url FROM edrdata WHERE disabled=0 and url=%s", edr_url2)
        data2 = cur.fetchall()
        for rec2 in data2:
            __edr.printt("first : %s" % rec)
            __edr.printt("second: %s" % rec2)
            cur.execute("DELETE FROM edrdata WHERE url = %s;\n", edr_url)
    con.commit()
    __edr.LogWrite('Remove duplicates: End Loop. Start simple delete.')
    cur.execute("DELETE e1 FROM  edrdata e1, edrdata e2 WHERE e1.id > e2.id AND e1.url = e2.url AND disabled=0;")
    con.commit()
    __edr.LogWrite('Remove duplicates: Delete strange url.')
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
