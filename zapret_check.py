#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'wf'

#import zapretinfo_run as __edr
import urllib2
import csv

def checkblockedsites():
    f = urllib2.urlopen('http://api.antizapret.info/all.php?type=csv')
    reader = csv.reader(f, delimiter=';')
    result = []
    errors = []
    for row in reader:
        print row
        url = row[1] or row[2]
        if url:
            if url[:4] != "http":
                url = "http://%s" % url
            try:
                answer = urllib2.urlopen(url, timeout=2)
                if "Доступ закрыт" not in answer.read(100):
                    result.append(url)
            except urllib2.URLError as e:
                errors.append(url)
            except:
                errors.append(url)
    print result
    print errors



def main():
    checkblockedsites()



if __name__ == "__main__":
    main()
