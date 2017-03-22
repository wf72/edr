#!/usr/bin/env python
# -*- coding: utf-8 -*-
#__author__ = 'wf'
import ConfigParser
import base64
import getopt
import getpass
import os
import sys
import time
import xml.etree.ElementTree as etree
import zipfile
import MySQLdb as db
import suds
import zapretbind
import zapretdelete_duple
import zapretnginx
import zapret_ipfile
from time import strftime
from pid.decorator import pidfile


def del_front_punctuation(params):
    if params[0] in ".":
        params = "*%s" % params
    return params


def idnaconv(url, reverse=False):
    tmp_url = del_front_punctuation(url)
    if tmp_url:
        printt("Converting: %s, type %s" % (tmp_url, type(tmp_url)))
        if reverse:
            try:
                printt("Result: %s" % tmp_url.strip().decode('idna'))
                return tmp_url.strip().decode('idna')
            except UnicodeEncodeError:
                return tmp_url.strip()

        else:
            if type(url) == unicode:
                printt("Result: %s" % tmp_url.strip().encode('idna'))
                return tmp_url.strip().encode('idna')
            else:
                printt("Result: %s" % tmp_url.strip().decode('utf-8').encode('idna'))
                return tmp_url.strip().decode('utf-8').encode('idna')
    else:
        printt("Result: %s" % tmp_url)
        return tmp_url.strip()


def str2bool(value):
    if isinstance(value, bool):
        return value
    return True if value.lower() in ('true', 'yes', '1') else False


def config(section=''):
    """ConfigParser"""
    global work_dir
    work_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
    DefaultConfig = {'API_URL': "http://vigruzki.rkn.gov.ru/services/OperatorRequest/?wsdl",
                     'XML_FILE_NAME': "zapros.xml",
                     'SIG_FILE_NAME': "zapros.xml.sign",
                     'STOP_URL': "302:http://zapret.vh-group.net\n",
                     'dumpFormatVersion': "2.0",
                     'path_IP_file': "edr_ipfile.txt",
                     'filelog': "edr.log",
                     'zabbix_status_file': "zb_status",
                     'host': '',
                     'user': '',
                     'passwd': '',
                     'db': '',
                     'dns_serv': '80.78.96.1',
                     'Verbose': False}

    Config = ConfigParser.SafeConfigParser(DefaultConfig)
    Config.read(work_dir+"/settings.cfg")

    global Verbose
    Verbose = Config.get('Main', 'Verbose')
    if not section:
        global API_URL, XML_FILE_NAME, SIG_FILE_NAME, path_IP_file, filelog, zabbix_status_file, STOP_URL, \
            dumpFormatVersion

        API_URL = Config.get('URLS', 'API_URL')
        STOP_URL = Config.get('URLS', 'STOP_URL')

        if Config.get('Dirs', 'XML_FILE_NAME')[0] == "/":
            XML_FILE_NAME = Config.get('Dirs', 'XML_FILE_NAME')
        else:
            XML_FILE_NAME = work_dir + Config.get('Dirs', 'XML_FILE_NAME')
        if Config.get('Dirs', 'SIG_FILE_NAME')[0] == "/":
            SIG_FILE_NAME = Config.get('Dirs', 'SIG_FILE_NAME')
        else:
            SIG_FILE_NAME = work_dir + Config.get('Dirs', 'SIG_FILE_NAME')
        dumpFormatVersion = Config.get('Dirs', 'dumpFormatVersion')
        if Config.get('Dirs', 'path_IP_file')[0] == "/":
            path_IP_file = Config.get('Dirs', 'path_IP_file')
        else:
            path_IP_file = work_dir + Config.get('Dirs', 'path_IP_file')
        if Config.get('Dirs', 'filelog')[0] == "/":
            filelog = Config.get('Dirs', 'filelog')
        else:
            filelog = work_dir + Config.get('Dirs', 'filelog')
        if Config.get('Dirs', 'zabbix_status_file')[0] == "/":
            zabbix_status_file = Config.get('Dirs', 'zabbix_status_file')
        else:
            zabbix_status_file = work_dir + Config.get('Dirs', 'zabbix_status_file')
        return

    elif section == 'DBConfig':
        return {'host': Config.get('DBConfig', 'dbHost'),
                'user': Config.get('DBConfig', 'dbUser'),
                'passwd': Config.get('DBConfig', 'dbPassword'),
                'db': Config.get('DBConfig', 'dbName'),
                'charset': 'utf8mb4',
                'use_unicode': 'True',
                }
    else:
        dict1 = {}
        options = Config.options(section)
        for option in options:
            try:
                dict1[option] = Config.get(section, option)
                if section == 'Dirs' and Config.get(section, option):
                    if Config.get(section, option)[0] == "/":
                        dict1[option] = Config.get(section, option)
                    else:
                        dict1[option] = work_dir + Config.get(section, option)
                if dict1[option] == -1:
                    printt("skip: %s" % option)
            except SystemError as e:
                printt("exception on %s!" % option)
                dict1[option] = None

        return dict1


def printt(message):
    """print messages"""
    if str2bool(Verbose):
        print(message)


def LogWrite(message,type = ""):
    """Write logs"""
    if type == "zb_check":
        filelog_local = config('Dirs')['filelog_check']
    else:
        filelog_local = filelog
    if str2bool(config('Main')['log_write']):
        log = open(filelog_local, 'a')
        log.write(" %s : %s \n" % (strftime("%Y-%m-%d %H:%M:%S"), message))
        log.close()


def DBConnect():
    global cur, con
    try:
        printt("Start connecting to DB")
        con = db.connect(**config('DBConfig'))
        con.set_character_set('utf8mb4')
        cur = con.cursor()
        printt("Connecting done")
        # cur.execute('SET NAMES `utf8`')
        cur.execute("SET NAMES utf8mb4;")
        cur.execute("SET CHARACTER SET utf8mb4;")
        cur.execute("SET character_set_connection=utf8mb4;")
        return con, cur
    except db.Error as e:
        printt(e)


def CreateDB():
    dbRootUser = raw_input("Enter mysql superuser name [%s]: " % 'root')
    if not dbRootUser:
        dbRootUser = 'root'

    dbRootPass = getpass.getpass("Enter mysql superuser password: ")

    try:
        printt("Create DB on host: %s User: %s, Pass: %s" % (config('DBConfig')['host'], dbRootUser, dbRootPass))
        concreate = db.connect(host=config('DBConfig')['host'], user=dbRootUser, passwd=dbRootPass, db='mysql')
        curcreate = concreate.cursor()
        printt("SET NAMES `utf8`;")
        curcreate.execute("SET NAMES `utf8`;")
        sqltext = "CREATE DATABASE IF NOT EXISTS %(db)s;" % {'db': config('DBConfig')['db']}
        curcreate.execute(sqltext)
        sqltext= "USE %(db)s;" % {'db': config('DBConfig')['db']}
        curcreate.execute(sqltext)
        sqltext = """CREATE TABLE IF NOT EXISTS edrdata (
        `id` INT NOT NULL,
        `includeTime` DATETIME,
        `decDate` DATE,
        `decNum` TEXT,
        `decOrg` VARCHAR(30),
        `url` TEXT,
        `domain` VARCHAR(255),
        `ip` TEXT,
        `disabled` TINYINT,
         PRIMARY KEY (`id`),
         INDEX (url(255), domain(50))
        ) ENGINE = InnoDB DEFAULT CHARACTER SET=utf8;"""
        printt(sqltext)
        curcreate.execute(sqltext)
        sqltext = """CREATE TABLE IF NOT EXISTS version (
        version VARCHAR(4)
        ) ENGINE = InnoDB DEFAULT CHARACTER SET=utf8;"""
        printt(sqltext)
        curcreate.execute(sqltext)
        sqltext = """CREATE USER '%(user)s'@'localhost' IDENTIFIED BY '%(password)s';
        GRANT ALL PRIVILEGES ON %(db)s.* to '%(user)s'@'%%';
        FLUSH PRIVILEGES;""" % {'user': config('DBConfig')['user'],
                                'password': config('DBConfig')['passwd'],
                                'db': config('DBConfig')['db']}
        curcreate.execute(sqltext)
        concreate.commit()
        curcreate.execute("INSERT INTO version SET `version`=%s", (0.3,))
        #curcreate.execute("ALTER TABLE edrdata ADD INDEX (url(20), id, domain);")
        concreate.commit()
        curcreate.close()
    except db.Error, e:
        try:
            print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
        except IndexError:
            print "MySQL Error: %s" % str(e)


def UpdateTable():
    printt("Data prepare dump file")
    LogWrite("Data prepare dump file")
    try:
        zf = zipfile.ZipFile(work_dir + 'result' + '.zip', 'r')
        zf.extractall(work_dir)
        printt("Zip extract")
        LogWrite("Zip extract")
    except zipfile.BadZipfile as E:
        printt("Bad Zip File %s" % E )
        start()
    else:
        zf.close()
    printt("Обновляем базу")
    LogWrite("Обновляем базу")
    cur.execute("UPDATE edrdata SET disabled=1")
    con.commit()
    printt("XML parse")
    LogWrite("XML parse")
    try:
        xmlfile = etree.parse(work_dir + 'dump.xml')
        xmlroot = xmlfile.getroot()
    except etree.ElementTree.ParseError as E:
        printt(E)
        LogWrite(E)
        start()
    printt("XML parse loop")
    LogWrite("XML parse loop")
    for child in xmlroot:
        if child.tag == 'content':
            decDate = ""
            decNumber = ""
            decOrg = ""
            url = ""
            domain = ""
            ip = set()
            idd = child.attrib['id'].encode('utf8').strip()
            includeTime = child.attrib['includeTime'].replace('T', ' ').strip()
            for child2 in child:
                if child2.tag == 'decision':
                    decDate = child2.attrib['date'].encode('utf8').strip()
                    decNumber = child2.attrib['number'].encode('utf8').strip()
                    decOrg = child2.attrib['org'].encode('utf8').strip()
                elif child2.tag == 'url':
                    url = child2.text.strip().encode('utf8').strip()
                    url = "all://%s/" % domain if not url else url
                elif child2.tag == 'domain':
                    domain = child2.text.strip().encode('utf8').strip()
                    url = "all://%s/" % domain if not url else url
                elif child2.tag == 'ip':
                    ip.add(child2.text.strip().encode('utf8').strip())
                    if not domain:
                        domain = 'ip'
            if url and ip and domain and decDate and decNumber and decOrg:
                cur.execute("""INSERT edrdata SET includeTime=%(includeTime)s, decDate=%(decDate)s, decNum=%(decNumber)s,
            decOrg=%(decOrg)s, url=%(url)s, domain=%(domain)s, ip=%(ip)s, id=%(idd)s, disabled=0 ON DUPLICATE KEY UPDATE
            includeTime=%(includeTime)s, decDate=%(decDate)s, decNum=%(decNumber)s,
            decOrg=%(decOrg)s, url=%(url)s, domain=%(domain)s, ip=%(ip)s, id=%(idd)s, disabled=0; \n
            """, {'includeTime': includeTime, 'decDate': decDate, 'decNumber': decNumber,
                   'decOrg': decOrg, 'url':url, 'domain': domain, 'ip': str(list(ip)), 'idd': idd})

                printt("""INSERT edrdata SET includeTime=%(includeTime)s, decDate=%(decDate)s, decNum=%(decNumber)s,
            decOrg=%(decOrg)s, url=%(url)s, domain=%(domain)s, ip=%(ip)s, id=%(idd)s, disabled=0 ON DUPLICATE KEY UPDATE
            includeTime=%(includeTime)s, decDate=%(decDate)s, decNum=%(decNumber)s,
            decOrg=%(decOrg)s, url=%(url)s, domain=%(domain)s, ip=%(ip)s, id=%(idd)s, disabled=0; \n
            """ % {'includeTime': includeTime, 'decDate': decDate, 'decNumber': decNumber,
                   'decOrg': decOrg, 'url':url, 'domain': domain, 'ip': str(list(ip)), 'idd': idd})
            con.commit()

    con.commit()
    zabbix_status_write(1)
    printt("DB update done")
    LogWrite("DB update done")


def DeleteTrash():
    printt("Удаляем мусор")
    try:
        os.remove(work_dir + 'result.zip') if os.path.exists(work_dir + 'result.zip') else None
    except OSError:
        pass

    try:
        os.remove(work_dir + 'dump.xml') if os.path.exists(work_dir + 'dump.xml') else None
    except OSError:
        pass

    try:
        os.remove(work_dir + 'dump.xml.sig') if os.path.exists(work_dir + 'dump.xml.sig') else None
    except OSError:
        pass


def zabbix_status_write(status):
    """Пишем статус проверки в файл, для zabbix"""
    if config('Main')['zb_file']:
        zb_file = open(zabbix_status_file, "w")
        if status:
            zb_file.write("1\n")
            printt("Writing to zb_status 1")
            LogWrite("Writing to zb_status 1")
        else:
            zb_file.write("0\n")
            printt("Writing to zb_status 0")
            LogWrite("Writing to zb_status 0")
        zb_file.close()


def getLastDumpDate():
    """Проверка последнего изменения файла на серве"""
    printt("Проверка последнего изменения файла на серве")
    client = suds.client.Client(API_URL)
    result = client.service.getLastDumpDate()
    printt("Результат:")
    LogWrite("Результат:")
    printt(unicode(result))
    LogWrite(unicode(result))
    return result


def sendRequest(requestFile, signatureFile, dumpformatversion):
    """Формируем и отправляем запрос на файл, в ответе код"""
    req_file = open(requestFile, "rb")  # входные параметры фаил xml и подпись файла
    data = req_file.read()
    req_file.close()
    xml = base64.b64encode(data)
    req_file = open(signatureFile, "rb")
    data = req_file.read()
    req_file.close()
    printt("Отправляем запрос с данными:")
    LogWrite("Отправляем запрос с данными:")
    # printt(data)

    sign = base64.b64encode(data)

    client = suds.client.Client(API_URL)
    result = client.service.sendRequest(xml, sign, dumpformatversion)

    return dict(((k, v.encode('utf-8')) if isinstance(v, suds.sax.text.Text) else (k, v)) for (k, v) in result)


def getResult(code):
    """скачиваем фаил"""
    printt("скачиваем файл ")
    LogWrite("скачиваем файл ")
    client = suds.client.Client(API_URL)
    result = client.service.getResult(code)
    printt("получен результат")
    LogWrite("получен результат")
    #printt(unicode((dict(((k, v.encode('utf-8')) if isinstance(v, suds.sax.text.Text) else (k, v)) for (k, v) in result))))
    return dict(((k, v.encode('utf-8')) if isinstance(v, suds.sax.text.Text) else (k, v)) for (k, v) in result)


def start():
    DeleteTrash()
    DBConnect()

    date_file = getLastDumpDate()
    zabbix_status_write(0)
    request = sendRequest(XML_FILE_NAME, SIG_FILE_NAME, dumpFormatVersion)

    # Проверяем, принят ли запрос к обработке
    if request['result']:
        # Запрос не принят, получен код
        code = request['code']
        printt('Got code %s' % code)
        printt('LastDumpDate %s' % date_file)
        printt('Trying to get result...')
        printt('sleep 60 sec')
        LogWrite('Got code %s' % code)
        LogWrite('LastDumpDate %s' % date_file)
        LogWrite('Trying to get result...')
        LogWrite('sleep 60 sec')
        time.sleep(60)
        while 1:
            request = getResult(code)  # Пытаемся получить архив по коду
            if request['result']:
                # Архив получен, скачиваем его и распаковываем
                printt('Got it!')
                LogWrite('Got it!')
                file = open(work_dir + 'result' + '.zip', "wb")
                file.write(base64.b64decode(request['registerZipArchive']))
                file.close()
                #exportIp(work_dir + 'result' + '.zip')
                UpdateTable()
                con.close()
                zapret_ipfile.main()
                zapretdelete_duple.main()
                zapretbind.main()
                zapretnginx.main()
                LogWrite('It is Done!')
                printt('It is Done!')
                break
            else:
                # Архив не получен, проверяем причину.
                if request['resultComment'] == 'запрос обрабатывается':
                    # Если это сообщение об обработке запроса, то просто ждем минутку.
                    printt('Not ready yet.')
                    printt('sleep 180 sec')
                    LogWrite('Not ready yet.')
                    LogWrite('sleep 180 sec')
                    time.sleep(180)
                else:
                    # Если это любая другая ошибка, выводим ее и прекращаем работу
                    printt('Error: %s' % request['resultComment'])
                    LogWrite("%s: Update error %s\n" % (strftime("%Y-%m-%d %H:%M:%S"), request['resultComment']))
                    zabbix_status_write(0)
                    con.close()
                    break
    else:
        # Запрос не принят, возвращаем ошибку
        printt('Error: %s' % request['resultComment'])
        LogWrite("%s: Update error %s\n" % (strftime("%Y-%m-%d %H:%M:%S"), request['resultComment']))
        zabbix_status_write(0)
        con.close()

@pidfile()
def main(argv):
    config()
    try:
        opts, args = getopt.getopt(argv, "hcuv", ["createdb", "update", "verbose"])
    except getopt.GetoptError:
        print '-h for help'
        sys.exit(2)
    startupdate = False
    createdb = False
    for opt, arg in opts:
        if opt == '-h':
            print """--createdb or -c to create database
--update or -u to update dump
-h to see that message
                """
            sys.exit()
        elif opt in ("-v", "--verbose"):
            global Verbose
            Verbose = True
            printt("Verbose mode on")
        elif opt in ("-u", "--update"):
            printt("Запускаем обмен")
            startupdate = True
        elif opt in ("-c", "--createdb"):
            createdb = True

    if createdb:
        CreateDB()
    elif startupdate:
        start()


if __name__ == "__main__":
    main(sys.argv[1:])
