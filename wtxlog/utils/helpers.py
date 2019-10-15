# -*- coding: utf-8 -*-

import xmlrpclib
from flask import current_app, request, url_for
from flask_themes import render_theme_template, get_theme
from ..models import Category


def get_current_theme():
    print("get_current_theme")
    cur_theme = get_theme(current_app.config.get('THEME', 'default'))
    print(dir(cur_theme))
    print(cur_theme.templates_path)
    print(cur_theme.path)
    print(cur_theme.name)
    return get_theme(current_app.config.get('THEME', 'default'))


def render_template(template, **context):
    print("render_template")
    print(template)
    return render_theme_template(get_current_theme(), template, **context)


def get_category_ids(longslug=''):
    """"返回指定longslug开头的所有栏目的ID列表"""
    print("---get_category_ids cates")
    cates = Category.query.filter(Category.longslug.startswith(longslug))
    print(cates)
    print("---get_category_ids cates2")
    cates2 = Category.query.filter(Category.longslug == longslug)
    print(cates2)
    if cates:
        return [cate.id for cate in cates.all()]
    else:
        return []


def page_url(page):
    """根据页码返回URL"""
    _kwargs = request.view_args
    if 'page' in _kwargs:
        _kwargs.pop('page')
    if page > 1:
        return url_for(request.endpoint, page=page, **_kwargs)
    return url_for(request.endpoint, **_kwargs)


def baidu_ping(url):
    """
    :ref: http://zhanzhang.baidu.com/tools/ping

    发送给百度Ping服务的XML-RPC客户请求需要包含如下元素：
    RPC端点： http://ping.baidu.com/ping/RPC2
    调用方法名： weblogUpdates.extendedPing
    参数： (应按照如下所列的相同顺序传送)
    博客名称
    博客首页地址
    新发文章地址
    博客rss地址
    """

    result = 1
    rpc_server = xmlrpclib.ServerProxy('http://ping.baidu.com/ping/RPC2')

    try:
        # 返回0表示提交成功
        current_app.logger.info('begin to ping baidu: <%s>' % url)
        result = rpc_server.weblogUpdates.extendedPing(
            current_app.config.get('SITE_NAME'),
            url_for('main.index', _external=True),
            url,
            url_for('main.feed', _external=True)
        )
    except:
        pass

    if result != 0:
        current_app.logger.warning('<%s> ping to baidu failed' % url)

    return result == 0
