#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'wf'

import socket
import urllib2
import csv
from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool


def checksite(url):
    find_words = ['<title> Доступ Закрыт! - VHG! </title>', '<title>Доступ закрыт</title>', '<title>Доступ ограничен</title>']
    result = {'notblocked': [], 'errors': [], 'blocked': []}
    if url:
        if url[:4] != "http":
            url = "http://%s" % url
        try:
            answer = urllib2.urlopen(url, timeout=10)
            tmpanswer = answer.read()
            if max(word in tmpanswer for word in find_words):
                result['blocked'] = url
            else:
                result['notblocked'] = url
        except urllib2.URLError:
            result['errors'] = url
        except socket.timeout:
            result['errors'] = url

    print("url: %s\nresult: %s\n" % (url, result))
    return result


def checkblockedsites():
    """Возвращает результаты ввиде спиской сайтов. Можно скомпилировать для запуска в консоли
    под windows."""
    print("Start check urls")
    f = urllib2.urlopen('http://api.antizapret.info/all.php?type=csv')
    reader = csv.reader(f, delimiter=';')
    result = {'notblocked': [], 'errors': [], 'blocked': []}
    pool = ThreadPool(4)
    urls = []
    count = 0
    max_count = 10
    for row in reader:
        if row[0] == datetime.now().strftime("%Y-%m-%d"):
            continue
        if max_count <= count:
            break
        url = row[1] or row[2]
        if url:
            if url[:4] != "http":
                url = "http://%s" % url
            urls.append(url)
            count += 1
    results = pool.map(checksite, urls)
    print(results)
    for i in results:
        for key in result.keys():
            if i[key]:
                result[key].append(i[key])
    print("===\nBlocked result: %s\n" % result['blocked'])
    print("===\nNot blocked result: %s\n" % result['notblocked'])
    print("===\nWith errors: %s\n" % result['errors'])
    pool.close()
    pool.join()


def main():
    checkblockedsites()


if __name__ == "__main__":
    main()
