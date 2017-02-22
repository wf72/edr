#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'wf'

import zapretinfo_run as __edr
import urllib2
import csv
import socket


def __start():
    __edr.config()


def checkblockedsites():
    f = urllib2.urlopen('http://api.antizapret.info/all.php?type=csv')
    reader = csv.reader(f, delimiter=';')
    result = []
    errors = []
    count = 0
    max_count = __edr.config('Main')['max_url_check']
    for row in reader:
        if max_count <= count:
            break
        url = row[1] or row[2]
        if url:
            if url[:4] != "http":
                url = "http://%s" % url
            try:
                count += 1
                answer = urllib2.urlopen(url, timeout=5)
                tmpanswer = answer.read(100)
                if max(word in tmpanswer for word in __edr.config('Main')['find_words']):
                    #print("Url %(url)s blocked: %(answer)s" % {"url": url, "answer": tmpanswer})
                    continue
                else:
                    print("Url %(url)s not blocked: %(answer)s" % {"url": url, "answer": tmpanswer})
                    result.append(url)
            except urllib2.URLError as e:
                print "There was an error: %r" % e
                errors.append(url)
            except socket.timeout as e:
                print "There was an error: %r" % e
                errors.append(url)


    print("result: %s" % result)
    print("errors: %s" % errors)



def main():
    checkblockedsites()



if __name__ == "__main__":
    main()
