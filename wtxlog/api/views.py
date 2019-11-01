# -*- coding: utf-8 -*-

from flask import request
from ..models import db, Article, Cast
from . import api
import json
import codecs
import os
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash


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
    json_data = json.loads(data.decode("utf-8"))
    print(json_data)
    print('----------category-------------')
    print(json_data['category'])
    
    print('----------tags-------------')

    print(json_data['tags'])

    print('----------topics-------------')

    print(json_data['topics'])

    return json.dumps(json_data)
