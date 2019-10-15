# -*- coding: utf-8 -*-
from ..models import *

def fanhao(f):
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

    article.title = u"[{0}]{1}".format(f['no'],f['name'])
    #article.longslug = f['no
    article.body = u'{0}{1}'.format(f['no'],f['desc'] if f['desc'] else '')
    article.thumbnail = f['imgpost']
    print("======f['no=========")
    print(f['no'])

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
