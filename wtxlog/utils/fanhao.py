# -*- coding: utf-8 -*-
from ..models import *
from flask_themes import render_theme_template, get_theme
from ..utils.helpers import render_template

def fanhao(f):
    #theme_name = get_theme(current_app.config.get('THEME', 'default'))
    article = Article()

    cate = Category.query.filter(Category.name == u"番号").first()
    if cate:
        article.category_id = cate.id
    else:
        raise Exception("Category not exists")

    topics = Topic.query.filter(Topic.name.in_(f['cast'])).all()
    for topic in topics:
        article.topics.append(topic)

    tags = Tag.query.filter(Tag.name.in_(f['tags'])).all()
    for tag in tags:
        article.tags.append(tag)

    article.title = u"[{0}]{1}".format(f['no'],f['name'][0:f['name'].find(u'番号:')])
    #article.longslug = f['no
    #article.body = u'{0}{1}'.format(f['no'],f['desc'] if f['desc'] else '')
    print("======f['no=========")
    print(f['no'])

    article_temp = "/body_templates/fh.html"
    print(f)
    print(type(f))
    article.body = render_template(article_temp,fh = f)
    article.thumbnail = f['img'] if f['imgpost'] is None else f['imgpost']

    article.seokey = u'番号[{0}],{1},{2},{3}'.format(
        f['no'],f['name'],f['name_jp'],u','.join(f['cast']),f['publisher'])

    article.seotitle = u"{0}{1}-{2}-{3}".format(
        f['no'], f['name_jp'], f['cast'][0], f['publisher']
    )

    article.seodesc = u"[{0}]{1}，由演员{2}出演, 影片标记为{3}。{4}由{5}\
    发行于{6},提供磁力链接下载地址".format(
        f['no'], f['name_jp'] if f['name_jp'] else f['name'] if f['name'] else ''
        , u'、'.join(f['cast'])
        , u'、'.join(f['tags'])
        , f['desc'] if f['desc'] else '',
        f['publisher'], f['issuedate']
    )

    article.hit = f['hot']
    article.created = datetime.today()
    article.last_modified = datetime.today()

    db.session.add(article)
    db.session.commit()


def cast(f):
    article = Article()

    cate = Category.query.filter(Category.name == u"女优介绍").first()
    if cate:
        article.category_id = cate.id
    else:
        raise Exception("Category not exists")

    topics = Topic.query.filter(Topic.name.in_(f['name'])).all()
    for topic in topics:
        article.topics.append(topic)

    tags = Tag.query.filter(Tag.name.in_(f['tags'])).all()
    for tag in tags:
        article.tags.append(tag)

    article.title = u"{0}".format(f['name'])
    #article.longslug = f['no
    #article.body = u'{0}{1}'.format(f['no'],f['desc'] if f['desc'] else '')
    print("======f['no=========")
    print(f['name'])

    cast_temp = "/body_templates/cast.html"
    print(f)
    print(type(f))
    article.body = render_template(cast_temp,cast = f, articles = f['fhs'])
    article.thumbnail = f['img'] if f['imgpost'] is None else f['imgpost']

    article.seokey = u'番号[{0}],{1},{2},{3}'.format(
        f['castdate'],f['name'],f['alias'],u','.join(f['castdate']),f['castdate'])

    article.seotitle = u"{0}{1}-{2}-{3}".format(
        f['castdate'], f['name'], f['tags'][0], f['castdate']
    )

    article.seodesc = u"f['desc']"

    article.hit = f['hot']
    article.created = datetime.today()
    article.last_modified = datetime.today()

    db.session.add(article)
    db.session.commit()
