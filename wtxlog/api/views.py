# -*- coding: utf-8 -*-

from flask import request
from ..models import db, Article, Cast, Category, Tag, Topic
from . import api
import json
import codecs
import os
from datetime import datetime
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base,DeclarativeMeta
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric


@api.route('/gethits/')
def gethits():
    id = int(request.args.get('id', 0))
    article = Article.query.get(id)
    print("----get hits-----")
    print(id)
    if article:
        article.hits += 1
        db.session.add(article)
        db.session.commit()
        return str(article.hits)
    return 'err'

@api.route('/ini_recom_fhs', methods=['GET','POST'])
def ini_recom_fhs():
    print(os.path.abspath("wtxlog/templates/fh/recomm/recom_fh.txt"))
    fhs = read_ini_list("wtxlog/templates/fh/recomm/recom_fh.txt")
    per_page = 12
    fh_page = Article.query.filter(Article.slug.in_((fhs))).paginate(1,per_page=per_page)
    fanhaoitems = fh_page.items
    template_name = "/fh/recomm/recom_fhs_temp.html"
    for i in range(1, fh_page.pages+1):
        f = codecs.open("wtxlog/templates/fh/recomm/fhs/fh_" + str(i) + ".html","w", encoding="utf-8")

        s = render_template(template_name, fanhaolist = fanhaoitems)
        #print(s)
        f.write(s)
        f.flush()
        f.close()
        if not fh_page.has_next:
            break
        fanhaoitems = fh_page.next().items

    return "OK"


@api.route('/ini_recom_cast', methods=['GET','POST'])
def ini_recom_cast():
    f = codecs.open("wtxlog/templates/fh/recomm/recom_cast.txt",'r','utf-8')
    cast_names = list()
    for line in f.readlines():
        line = line.strip('\r\n')
        if line.strip() == '':
            continue
        print(line)
        cast_names.append(line)

    print(cast_names)
    per_page = 12
    cast_page = Cast.query.filter(Cast.name.in_((cast_names))).paginate(1,per_page=per_page)
    print("--- cast_page.pages")
    print(cast_page.pages)
    print(cast_page.total)
    castlist = cast_page.items
    cast_all = Cast.query.filter(Cast.name.in_((cast_names)))
    for c in cast_all:
        print(c.name)

    for i in range(1, cast_page.pages + 1):
        f = codecs.open("wtxlog/templates/fh/recomm/cast/cast_" + str(i) + ".html","w", encoding="utf-8")

        s = render_template("/fh/recomm/recom_cast_right_temp.html", casts = castlist)
        #print(s)
        f.write(s)
        f.flush()
        f.close()
        if not cast_page.has_next:
            break

        castlist = cast_page.next().items

    return 'tuple(())'


def read_ini_list(ini_file):
    f = codecs.open(ini_file,'r','utf-8')
    cast_names = list()
    for line in f.readlines():
        line = line.strip('\r\n')
        print(line)
        if line.strip() == '':
            continue
        cast_names.append(line)
    f.close()
    return cast_names


@api.route('/push_article/<no>', methods=['GET','POST'])
def push_article(no):
    print(no)
    data = request.get_data()
    print("------data---------")
    print(data)
    json_data = json.loads(data.decode("utf-8"))

    article = Article()
    article.slug = json_data['slug']
    filter_fields = ['category','tags','topics']

    print("push_article---------")
    print(json_data['category'])
    fill_by_json(article, json_data)

    db.session.add(article)
    db.session.commit()

    return json.dumps(json_data)

def fill_by_json(article, json_data, deep = 1, filter_fields = []):
    deep +=1

    if deep > 2:
        return

    cols = article.__table__.columns
    for k in json_data:

        if k in filter_fields:
            continue

        if not k in article.__table__.columns:
            continue

        if not hasattr(article,k) or k in filter_fields:
            continue

        col = cols[k]
        if type(col.type) == DateTime:
            #data=data.strftime('%Y-%m-%d %H:%M:%S')
            print('sqltypes.DateTime')
            setattr(article,k,datetime.strptime(json_data[k],'%Y-%m-%d %H:%M:%S'))
        else:
            setattr(article,k,json_data[k])

        print(k,getattr(article,k),isinstance(getattr(article,k), datetime))

    print(json_data)
    print(json_data['category'])
    get_cate(article, json_data['category'])
    get_tag(article, json_data['tags'])
    get_topic(article, json_data['topics'])



def get_cate(article, json_data):
    cate = Category.query.filter(Category.name == json_data['name']).first()
    if not cate:
        cate = Category()
        db.session.add(cate)
        db.session.commit()
    article.category_id = cate.id


def get_topic(article, json_data):
    topics = Topic.query.all()
    db_topics =  {x.name:x for x in topics}

    for tp in json_data:
        topic = None
        if not tp['name'] in db_topics:
            topic = Topic()
            topic.name = tp['name']
            topic.slug = tp['name']
            db.session.add(topic)
            db.session.commit()
        else:
            topic = db_topics[tp['name']]

        article.topics.append(topic)


def get_tag(article, json_data):
    tags = Tag.query.all()
    db_tags =  {x.name:x for x in tags}
    print(db_tags)
    for tp in json_data:
        tag = None
        print("tag.['name']")
        print(tp['name'])
        print(db_tags[tp['name']])
        if not tp['name'] in db_tags:
            tag = Tag()
            tag.name = tp['name']
            db.session.add(tag)
            db.session.commit()
        else:
            tag = db_tags[tp['name']]

        article.tags.append(tag)
