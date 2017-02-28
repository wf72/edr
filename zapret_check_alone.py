#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'wf'

import socket
import urllib2
import csv


def checkblockedsites():
    """Возвращает результаты ввиде спиской сайтов. Можно скомпилировать для запуска в консоли
    под windows."""
    print("Start check urls")
    find_words = ['<title> Доступ Закрыт! - VHG! </title>','<title>Доступ закрыт</title>']
    print("Tryiing to find: %s" % ";".join(find_words)  )
    f = urllib2.urlopen('http://api.antizapret.info/all.php?type=csv')
    reader = csv.reader(f, delimiter=';')
    result = []
    errors = []
    blocked = []
    count = 0
    max_count = 1000
    for row in reader:
        if row[0] == datetime.now().strftime("%Y-%m-%d"):
            continue
        if max_count <= count:
            break
        url = row[1] or row[2]
        if url:
            if url[:4] != "http":
                url = "http://%s" % url
            try:
                count += 1
                answer = urllib2.urlopen(url, timeout=5)
                tmpanswer = answer.read()
                if max(word in tmpanswer for word in find_words):
                    blocked.append(url)
                    continue
                else:
                    print("Url %(url)s not blocked: \n===start====\n%(answer)s\n===end===\n" % {"url": url, "answer": tmpanswer})
                    result.append(url)
            except urllib2.URLError as e:
                print("There was an error: %r With: %s " % (e, url))
                errors.append(url)
            except socket.timeout as e:
                print("There was an error: %r With: %s " % (e, url))
                errors.append(url)
    print("===\nBlocked result: %s\n" % blocked)
    print("===\nNot blocked result: %s\n" % result)
    print("===\nWith errors: %s\n" % errors)
    return int(bool(result))


def main():
    checkblockedsites()


if __name__ == "__main__":
    main()
