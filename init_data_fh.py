#coding:utf-8
import os
import sys
import re
import json
import urllib
import datetime, calendar

from os import path

deps_paths = [
    path.join(path.split(path.realpath(__file__))[0], 'deps'),
    path.join(path.split(path.realpath(__file__))[0], 'mydeps'),
]

for deps_path in deps_paths:
    if deps_path not in sys.path:
        sys.path.insert(0, deps_path)

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='wtxlog/*')
    COV.start()

from wtxlog import create_app, db, get_appconfig
from flask import Flask, send_from_directory
from flask.ext.script import Manager
from config import config
from sqlalchemy import func
from flask.ext.migrate import Migrate, MigrateCommand

from wtxlog.models import *


class InitData():

    connectstring = "../data_dev_sqlite.db"

    def createApp(self,config_name):
        app = Flask(__name__)
        app.config.from_object(config[config_name])

        db.init_app(app)
        db.app = app

    def __init__(self):
        self.createApp("default")


    def new_article(self):
        tags = {}
        fhs = Fanhao.query.all()
        db.session
        i = 0
        cate_default = Category.query.filter(Category.slug=='null').first()
        #cate_default.slug="null"
        #cate_default.longslug="null"
        #cate_default.name = 'no publisher'
        for f in fhs:
            i+=1
            print("------{0}------".format(i))
            article = Article()
            cate = Category.query.filter(Category.name == f.publisher).first()
            article.title = f.no + f.name if f.name else ''
            article.slug = f.no
            article.longslug = f.no
            article.body = u'{0}{1}'.format(f.no,f.desc if f.desc else '')
            article.thumbnail = f.imgpost
            print("======f.no=========")
            print(f.no)

            article.seokey = u'番号[{0}],{1},{2},{3}'.format(
                f.no,f.name,f.name_jp,u','.join(f.cast),f.publisher)

            article.seotitle = u"{0}{1}-{2}-{3}".format(
                f.no, f.name_jp, f.cast[0], f.publisher
            )

            article.seodesc = u"[{0}]{1}，由演员{2}出演, 影片标记为{3}。{4}由{5}\
发行于{6},提供磁力链接下载地址".format(
                f.no, f.name_jp if f.name_jp else f.name if f.name else ''
                , u'、'.join(f.cast)
                , u'、'.join(f.tags)
                , f.desc if f.desc else '',
                f.publisher, f.issuedate
            )

            if cate:
                article.category_id = cate.id
            else:
                print("-- default cate_default")
                article.category = cate_default

            topics = Topic.query.filter(Topic.name.in_(f.cast)).all()
            for topic in topics:
                article.topics.append(topic)


            tags = Tag.query.filter(Tag.name.in_(f.tags)).all()
            for tag in tags:
                article.tags.append(tag)

            article.hit = f.hot
            article.created = datetime.today()
            article.last_modified = datetime.today()

            db.session.add(article)
            if i % 2000 ==0:
                print(i)
                db.session.commit()

        db.session.commit()




    def new_tags(self):
        tags = {}
        fhs = Fanhao.query.all()
        db.session
        i = 0
        for f in fhs:
            for t in f.tags:
                if t not in tags:
                    i = i + 1
                    tags[t] = t
                    tag = Tag()
                    tag.name = t
                    tag.seotitle = t
                    tag.seodesc = t
                    db.session.add(tag)
                    if i % 500 ==0:
                        print(i)
                        db.session.commit()
        print(i)
        db.session.commit()


    def new_cate(self):
        pubs = Publisher.query.all()
        i = 0
        for p in pubs:
            i += 1
            cate = Category()
            cate.slug = p.publisher + '_'+str(i)
            cate.longslug = p.publisher + '_'+str(i)
            print(str(i))
            cate.name = p.publisher
            cate.thumbnail = p.imgpost
            cate.seotitle = u'{0}系列番号{1}部'.format(
                p.publisher, p.cnt
            )
            cate.seokey = u'{0}系列番号{1}部,{2}'.format(
                p.publisher, p.cnt, p.tags
            )
            cate.seodesc = u'{0}系列番号{1}部'.format(
                p.publisher, p.cnt
            )
            cate.body = u'{0}系列番号{1}部,{2}'.format(
                p.publisher, p.cnt, p.tags
            )

            db.session.add(cate)
        db.session.commit()


    def new_topic(self):
        tags = {}
        casts = Cast.query.all()
        db.session
        i = 0
        for c in casts:
            cnt = db.session.query(func.count(Fanhao.id)).filter(
                Fanhao._cast.like('%' + c.name + '%')).scalar()
            fhs = Fanhao.query.filter(
                Fanhao._cast.like('%' + c.name + '%')).all()
            if c.name not in tags:
                i = i+1
                tags[c.name] = c.name
                topic = Topic()
                topic.slug = c.name
                topic.longslug = c.name
                topic.name = c.name

                topic.seotitle = u'{0}合集{1}部番号'.format(
                    c.name,cnt
                )

                topic.seokey = u'{0}番号合集,{1}'.format(
                    c.name,u",".join(c.tags)
                )

                names = ''
                for fh in fhs:
                    names += fh.name_jp + u',' if fh.name_jp else ''
                topic.seodesc = u'{0},别名{1}, {2}{3}{4}'.format(
                    c.name,
                    #c.alias[0:20] + u'...' if len(c.alias) > 20 else c.alias,
                    c.alias,
                    c.castdate + u'出道番号' if c.castdate else u'',
                    u'{0}部：'.format(cnt) if cnt else u':',
                    names
                )

                topic.thumbnail = c.imgpost
                topic.body = c.desc
                db.session.add(topic)
                if i % 2000 ==0:
                    print(i)
                    db.session.commit()
        print(i)
        db.session.commit()


    def conn(self):
        return sqlite3.connect(connectstring)


    def db_all(self, tablename):
        con = sqlite3.connect(self.connectstring)
        cur = con.execute("select * from "+tablename)

        for row in cur:
            yield row


if __name__ == "__main__":
    ini = InitData()
    ini.new_article()
    #ini.new_cate()
