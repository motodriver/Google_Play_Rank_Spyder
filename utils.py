#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
import subprocess
import uuid
import datetime
import pytz
import config
# import MySQLdb
import base64
import logging


def mysql_gen_insert_sql(table_name, model, field_list, default_value):
    column_list = []
    value_list = []
    for fff in field_list:
        val = model.get(fff)
        if not val:
            if fff in default_value:
                val = default_value.get(fff)
            else:
                val = ""
        column_list.append("`{fff}`".format(fff=fff))
        value_list.append("'{val}'".format(val=val))
    column = ",".join(column_list)
    value = ",".join(value_list)
    sql = "INSERT INTO {table_name}({column})VALUES({value});".format(table_name=table_name, column=column, value=value)
    return sql


def mysql_get_latest_2(table_name, country, lang, type, search_hash):
    rest = None
    try:
        db_config = config.mysql_config
        conn = MySQLdb.connect(host=db_config['host'], user=db_config['user'], passwd=db_config['passwd'],
                               db=db_config['dbname'])
        cur = conn.cursor()
        SELECT_SQL = " SELECT `date`,`value` FROM `{table_name}` " \
                     " WHERE `country`='{country}' AND `lang`='{lang}' " \
                     "  AND `type`='{type}' AND `search_hash`='{search_hash}' " \
                     " ORDER BY `date` DESC " \
                     " LIMIT 2;".format(table_name=table_name, country=country,
                                        lang=lang, type=type, search_hash=search_hash)
        logging.info("SELECT_SQL:%s" % SELECT_SQL)
        cur.execute(SELECT_SQL)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        res_list = []
        for r in rows:
            d, js = r
            m = {
                "date": d,
                "value": js
            }
            res_list.append(m)
        rest = res_list
    except MySQLdb.Error, e:
        logging.info(("Mysql Error %d: %s" % (e.args[0], e.args[1])))
    except Exception as e:
        logging.info("mysql_get_latest_2:%s" % e)
    finally:
        return rest


def init_log(log_file, debug=False):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=log_file,
                        filemode='a')
    if debug:
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)


def gen_sql_file_name():
    return "/tmp/%s.sql" % str(uuid.uuid4()).replace("-", "")


def run_command(command):
    try:
        p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             stdin=subprocess.PIPE,
                             shell=True, env=os.environ)
        (output, err) = p.communicate()
        logging.info('run_command:(%s) output:\n%s\n' % (command, output))
        logging.info('run_command:(%s) error :\n%s\n' % (command, err))
        print(output)
        print(err)
        return (output, err)
    except Exception, e:
        logging.info('run_command exception: %s' % e)
        return False


def execute_mysql_sql(host, user, passwd, dbname, sql_file):
    cmd = "mysql --force --host=%s --user=%s --password=%s %s < %s " % (host, user, passwd, dbname, sql_file)
    logging.info("execute_mysql_sql:CMD:%s" % cmd)
    run_command(cmd)


def exec_sql(sql):
    db_config = config.mysql_config
    cmd = 'mysql -u%s -p%s -h%s -D%s -e"%s"' % (
        db_config['user'],
        db_config['passwd'],
        db_config['host'],
        db_config['dbname'],
        sql)
    logging.info("query_sql:CMD:%s" % cmd)
    run_command(cmd)


def query_sql(sql):
    db_config = config.mysql_config
    conn = MySQLdb.connect(
        host=db_config['host'],
        port=3306,
        user=db_config['user'],
        passwd=db_config['passwd'],
        db=db_config['dbname'],
        charset='utf8',
        use_unicode=True
    )
    cur = conn.cursor()
    res = cur.execute(sql)
    logging.info("query_sql:CMD:%s" % sql)
    return cur.fetchmany(res)


def get_pst_now():
    return get_time_now("US/Pacific")


def get_beijing_now():
    return get_time_now("Asia/Shanghai")


def get_time_now(tzname="UTC"):
    tz = pytz.timezone(tzname)
    dt = datetime.datetime.now(tz=tz)
    return dt.strftime("%Y-%m-%dT%H:%M:%S %Z")


def report_diff(model, what="", rank_from=0, rank_to=0):
    '''
    :param model:
        {
            "country": "us",
            "lang": "en_US",
            "type": "search",
            "search": "keyword",
            "pst_time": "2016-12-24T03:03:03 PST",
            "beijing_time": "2016-12-24T03:03:03 beijing",
            "appname": "appname",
            "package": "package",
            "developer": "developer",
        }
    :param what:消息类型
    :return:
    '''

    info_list = []
    info_list.append("=" * 20)
    if what == "New":
        info_list.append("新增应用")
    elif what == "Del":
        info_list.append("删除应用")
    elif what == "InRank":
        info_list.append("进榜")
        info_list.append("[??? -> %s ]" % rank_to)
    elif what == "OutRank":
        info_list.append("落榜")
        info_list.append("[%s -> ??? ]" % rank_from)
    elif what == "RankUp":
        info_list.append("排名上升")
        info_list.append("[%s -> %s]" % (rank_from, rank_to))
    elif what == "RankDown":
        info_list.append("排名下降")
        info_list.append("[%s -> %s]" % (rank_from, rank_to))
    if model["type"] == "search":
        info_list.append(
            "@Search@:[{keyword}]".format(keyword=model["search"].encode('utf-8')))
    else:
        info_list.append("@Developer@:[{keyword}]".format(keyword=model["search"].encode('utf-8')))
    info_list.append("Check Time(太平洋时间):{pst_time}".format(pst_time=model["pst_time"]))
    info_list.append("Check Time(  北京时间):{beijing_time}".format(beijing_time=model["beijing_time"]))
    info_list.append("Country:{country}".format(country=model["country"]))
    info_list.append("lang:{lang}".format(lang=model["lang"]))

    appname = base64.b64decode(model.get("appname", "")).encode('utf-8')
    package = base64.b64decode(model.get("package", "")).encode('utf-8')
    developer = base64.b64decode(model.get("developer", "")).encode('utf-8')
    info_list.append("AppName:{appname}".format(appname=appname))
    info_list.append("Package:{package}".format(package=package))
    info_list.append("Developer:{developer}".format(developer=developer))
    return "\n".join(info_list)
