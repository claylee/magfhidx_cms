# -*- coding: utf-8 -*-

import os
import re
import json
import urllib
import datetime

from flask import request, url_for, redirect, current_app, make_response, abort
from werkzeug.contrib.atom import AtomFeed
from werkzeug._compat import to_bytes
from webhelpers.paginate import Page, PageURL
from flask_mobility.decorators import mobile_template
from sqlalchemy import or_, and_, not_
from sqlalchemy.sql import func

from ..decorators import permission_required
from ..utils.helpers import render_template, get_category_ids, page_url
from ..utils.upload import SaveUploadFile
from ..utils.metaweblog import blog_dispatcher
from ..ext import cache
from ..models import db, Article, Category, Tag, Flatpage, Topic, \
    Role, Permission, Fanhao, Publisher_tag
from . import main

import requests

IMAGE_TYPES = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/gif': '.gif',
}


@main.route('/deploy/')
def deploy():
    db.create_all()
    Role.insert_roles()
    return 'deployed'


@main.route('/')
@main.route('/page/<int:page>/')
@mobile_template('{mobile/}%s')
@cache.cached()
def index(template, page=1):
    print('--------------------------------------')
    _template = template % 'index.html'
    print(_template)
    blog_mode = current_app.config.get("BLOG_MODE")
    print('--------------------------------------')
    if blog_mode:
        _url = page_url
        _query = Article.query.public()
        pagination = Page(_query, page=page, items_per_page=Article.PER_PAGE, url=_url)
        articles = pagination.items
        print('--------------------articles------------------')
        print(url_for('main.index'))

        return render_template(_template,
                               articles=articles,
                               pagination=pagination)
    else:
        print('--------------------render_template------------------')
        return render_template(_template)


#@main.route('/fhhash/<int:article_id>/')
#@main.route('/fhhash/<num>/')
@main.route('/article/<int:article_id>/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def article(template, article_id):
    article = Article.query.get_or_404(article_id)

    if not article.published:
        abort(403)

    _template = template % (article.category.article_template or
                            article.template or 'article.html')
    return render_template(_template, article=article)


@main.route('/category/<path:longslug>/')
@main.route('/category/<path:longslug>/page/<int:page>/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def category(template, longslug, page=1):
    category = Category.query.filter_by(longslug=longslug).first_or_404()
    print("-------category----------")
    print(category)
    cate_ids = get_category_ids(longslug)
    print("cate_ids")
    print(cate_ids)

    _url = page_url
    _query = Article.query.public().filter(Article.category_id.in_(cate_ids))
    pagination = Page(_query, page=page, items_per_page=Article.PER_PAGE, url=_url)

    articles = pagination.items
    print("articles:")
    print(articles)
    _template = template % (category.template or 'category.html')
    return render_template(_template,
                           category=category,
                           pagination=pagination,
                           articles=articles)


@main.route('/archives/<int:year>/<int:month>/')
@main.route('/archives/<int:year>/<int:month>/page/<int:page>/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def archives(template, year, month, page=1):
    _url = page_url
    _query = Article.query.archives(year, month)
    pagination = Page(_query, page=page, items_per_page=Article.PER_PAGE, url=_url)

    articles = pagination.items

    _template = template % 'archives.html'
    return render_template(_template,
                           pagination=pagination,
                           articles=articles,
                           year=year,
                           month=month)


@main.route('/tag/')
def tags_():
    return redirect(url_for('.tags'), code=301)


@main.route('/tags/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def tags(template):
    _template = template % 'tags.html'
    return render_template(_template)


@main.route('/tag/<name>/')
@main.route('/tag/<name>/page/<int:page>/')
@mobile_template('{mobile/}%s')
@cache.cached(0)
def tag(template, name, page=1):
    """
    :param template:
        模板文件，此参数自动传入
    :param name:
        Tag名称，若为非ASCII字符，一般是经过URL编码的
    """
    # 若name为非ASCII字符，传入时一般是经过URL编码的
    # 若name为URL编码，则需要解码为Unicode
    # URL编码判断方法：若已为URL编码, 再次编码会在每个码之前出现`%25`
    _name = to_bytes(name, 'utf-8')
    print("----------- tag ------------",_name)
    if urllib.quote(_name).count('%25') > 0:
        name = urllib.unquote(_name)

    print("----------- tag ------------")

    tag = Tag.query.filter_by(name=name).first_or_404()

    _url = page_url
    _query = Article.query.public().filter(Article.tags.any(id=tag.id))
    pagination = Page(_query, page=page, items_per_page=Article.PER_PAGE, url=_url)

    articles = pagination.items
    print("----------- tag ------------")
    print(articles)

    print("----------- tag ------------")
    _template = template % (tag.template or 'tag.html')
    print(_template)
    return render_template(_template,
                           tag=tag,
                           pagination=pagination,
                           articles=articles)


@main.route('/topic/')
def topics_():
    return redirect(url_for('.topics'), code=301)


@main.route('/topics/')
@main.route('/topics/page/<int:page>')
@main.route('/casts/')
@main.route('/casts/page/<int:page>')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def topics(template,page=1):
    _template = template % 'topics.html'
    _url = page_url
    _query = Topic.query.all()
    pagination = Page(_query, page=page, items_per_page=40, url=_url)

    topics = pagination.items
    return render_template(_template,_topics = topics, pages = len(pagination), curpage = page)


@main.route('/cast/<name>/')
@main.route('/topic/<slug>/')
@main.route('/topic/<slug>/page/<int:page>/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def topic(template, slug = "", name = '', page=1):
    topic = None
    if name:
        topic = Topic.query.filter_by(name=name).first_or_404()
    else:
        topic = Topic.query.filter_by(slug=slug).first_or_404()

    _url = page_url
    #_query = Article.query.public().filter(Article.topic_id == topic.id)
    _query = Article.query.public().filter(Article.topics.any(id=topic.id))
    pagination = Page(_query, page=page, items_per_page=Article.PER_PAGE, url=_url)

    articles = pagination.items
    print(articles)

    _template = template % (topic.template or 'topic.html')
    return render_template(_template,
                           topic=topic,
                           pagination=pagination,
                           articles=articles)


@main.route('/flatpage/<slug>/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def flatpage(template, slug):
    flatpage = Flatpage.query.filter_by(slug=slug).first_or_404()
    _template = template % (flatpage.template or 'flatpage.html')
    return render_template(_template, flatpage=flatpage)


@main.route('/search/')
@mobile_template('{mobile/}%s')
def search(template):
    page = int(request.args.get('page', 1))
    keyword = request.args.get('keyword', None)
    pagination = None
    articles = None
    if keyword:
        _url = PageURL(url_for('main.search'),
                       {"page": page, "keyword": keyword.encode('utf-8')})
        _query = Article.query.search(keyword)
        pagination = Page(_query, page=page, items_per_page=Article.PER_PAGE, url=_url)

        articles = pagination.items

    _template = template % 'search.html'
    return render_template(_template,
                           articles=articles,
                           keyword=keyword,
                           pagination=pagination)


@main.route('/sitemap.xsl')
def sitemap_xsl():
    response = make_response(render_template('sitemap.xsl'))
    response.mimetype = 'text/xsl'
    return response


@main.route('/sitemap.xml', methods=['GET'])
@cache.cached(86400)
def sitemap():
    """Generate sitemap.xml. Makes a list of urls and date modified."""
    urlset = []

    urlset.append(dict(
        loc=url_for('.index', _external=True),
        lastmod=datetime.date.today().isoformat(),
        changefreq='weekly',
        priority=1,
    ))

    # categories
    categories = Category.query.all()

    for category in categories:
        urlset.append(dict(
            loc=category.link,
            changefreq='weekly',
            priority=0.8,
        ))

    # tags
    tags = Tag.query.all()

    for tag in tags:
        urlset.append(dict(
            loc=tag.link,
            changefreq='weekly',
            priority=0.6,
        ))

    # articles model pages
    articles = Article.query.public().all()

    for article in articles:
        url = article.link
        modified_time = article.last_modified.date().isoformat()
        urlset.append(dict(
            loc=url,
            lastmod=modified_time,
            changefreq='monthly',
            priority=0.5,
        ))

    sitemap_xml = render_template('sitemap.xml', urlset=urlset)
    res = make_response(sitemap_xml)
    res.mimetype = 'application/xml'
    return res


@main.route('/feed/')
def feed():
    site_name = current_app.config.get('SITE_NAME')

    feed = AtomFeed(
        u"%s Recent Articles" % site_name,
        feed_url=request.url,
        url=request.url_root,
    )

    articles = Article.query.public().limit(10).all()

    for article in articles:
        feed.add(
            article.title,
            unicode(article.summary),
            content_type='html',
            author=article.author,
            url=article.link,
            updated=article.last_modified,
            published=article.created
        )

    res = make_response(feed.get_response())
    res.mimetype = 'application/xml'
    return res


@main.route('/upload/', methods=['POST', 'OPTIONS'])
@permission_required(Permission.UPLOAD_FILES)
def upload():
    ''' 文件上传函数 '''

    result = {"err": "", "msg": {"url": "", "localfile": ""}}
    fname = ''
    fext = ''
    data = None

    if request.method == 'POST' and 'filedata' in request.files:
        # 传统上传模式，IE浏览器使用这种模式
        fileobj = request.files['filedata']
        result["msg"]["localfile"] = fileobj.filename
        fname, fext = os.path.splitext(fileobj.filename)
        data = fileobj.read()
    elif 'CONTENT_DISPOSITION' in request.headers:
        # HTML5上传模式，FIREFOX等默认使用此模式
        pattern = re.compile(r"""\s.*?\s?filename\s*=\s*['|"]?([^\s'"]+).*?""", re.I)
        _d = request.headers.get('CONTENT_DISPOSITION').encode('utf-8')
        if urllib.quote(_d).count('%25') > 0:
            _d = urllib.unquote(_d)
        filenames = pattern.findall(_d)
        if len(filenames) == 1:
            result["msg"]["localfile"] = urllib.unquote(filenames[0])
            fname, fext = os.path.splitext(filenames[0])
        data = request.data

    ONLINE = False
    if ONLINE:
        obj = SaveUploadFile(fext, data)
        url = obj.save()
        result["msg"]["url"] = '!%s' % url
    else:
        obj = SaveUploadFile(fext, data)
        url = obj.save()
        result["msg"]["url"] = '!%s' % url
        pass

    return json.dumps(result)


@main.route('/uploadremote/', methods=['POST', 'OPTIONS'])
@permission_required(Permission.UPLOAD_FILES)
def uploadremote():
    """
    xheditor保存远程图片简单实现
    URL用"|"分隔，返回的字符串也是用"|"分隔
    返回格式是字符串，不是JSON格式
    """
    localdomain_re = re.compile("""https?:\/\/[^\/]*?(bcs\.duapp\.com)\/""", re.I)
    imageTypes = {'gif': '.gif', 'jpeg': '.jpg', 'jpg': '.jpg', 'png': '.png'}
    urlout = []
    result = ''
    srcUrl = request.form.get('urls', None)
    if srcUrl:
        urls = srcUrl.split('|')
        for url in urls:
            if not localdomain_re.search(url.strip()):
                downfile = urllib.urlopen(url)
                fext = imageTypes[downfile.headers.getsubtype().lower()]

                urlreturn = ''

                ONLINE = False
                if ONLINE:
                    obj = SaveUploadFile(fext, downfile.read())
                    urlreturn = obj.save()
                else:
                    obj = SaveUploadFile(fext, downfile.read())
                    urlreturn = obj.save()
                    pass

                urlout.append(urlreturn)
            else:
                urlout.append(url)
    result = '|'.join(urlout)
    return result


@main.route('/xmlrpc/', methods=['POST', 'OPTIONS'])
def xmlrpc():
    """
    author: digwtx <wtx358@qq.com>

    firefox-scribefire and Blogilo passed.

    Reference:

    * <http://codex.wordpress.org.cn/XML-RPC_MetaWeblog_API>
    * <http://blog.csdn.net/priderock/article/details/1754503>
    """

    # return blog_dispatcher._marshaled_dispatch(request.data)
    response_data = blog_dispatcher._marshaled_dispatch(request.data)
    return current_app.response_class(response_data, mimetype='text/xml')


@main.route('/ckupload/', methods=['POST', 'OPTIONS'])
@permission_required(Permission.UPLOAD_FILES)
def ckupload():
    """CKEditor file upload"""
    data = None
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")

    if request.method == 'POST' and 'upload' in request.files:
        # 传统上传模式，IE浏览器使用这种模式
        fileobj = request.files['upload']
        data = fileobj.read()
        fname, fext = os.path.splitext(fileobj.filename)
        if fext.lower() in ('.gif', '.jpg', '.jpeg', '.png'):
            _fext = fext
        else:
            _fext = fileobj.filename
        try:
            obj = SaveUploadFile(_fext, data)
            url = obj.save()
        except:
            error = 'upload error'
    else:
        error = 'post error'

    res = """<script type="text/javascript">
  window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
</script>""" % (callback, url, error)

    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response


@main.route("/fhs/",methods = ["Get","POST"])
@main.route("/fhs/<page>",methods = ["Get","POST"])
@main.route("/fhs_date",methods = ["Get","POST"])
@main.route("/fhs_date/<year>",methods = ["Get","POST"])
@main.route("/fhs_tag",methods = ["Get","POST"])
@main.route("/fhs_tag/<tag>",methods = ["Get","POST"])
@mobile_template('{mobile/}%s')
def fhs(template, page=1,year="",tag="",pagesize=20):
    _template = template % 'article_lists.html'
    perfile = 400
    page = int(page)

    fh_arr = []
    total = 0


    fh_query = None
    if year:
        #fh_arr, total = fh.load_fanhao_year(year,page,pagesize)
        fh_query = Article.query.filter(Article.issuedate.like('%'+year+'%'))
    elif tag:
        #fh_arr, total = fh.load_fanhao_tag(tag,page,pagesize)
        fh_query = Article.query.filter(Article._tags.like('%'+tag+'%'))
    else:
        #fh_arr, total = fh.load_fanhao_page(page,pagesize)
        fh_query = Article.query

    fh_pages = fh_query.order_by(Article.id.desc()).paginate(page,per_page=pagesize,error_out=False)
    fh_arr = fh_pages.items
    total = fh_pages.total

    return render_template(_template,pages= fh_pages.pages ,curpage = page, articles = fh_arr)


@main.route("/publishers/",methods = ["Get","POST"])
@mobile_template('{mobile/}%s')
def publishers(template):
    _template = template % 'categories.html'
    fh = Fanhao()
    publist = []

    results = db.session.query( Fanhao.publisher, func.count('*').label('cnt') ).filter(
        Fanhao.publisher != ''
    ).group_by( Fanhao.publisher)

    for c in results:
        if not c:
            continue
        publist.append({'pub':c.publisher,'count':c.cnt})
    return render_template(_template, publist = publist)

@main.route("/publishers/ordertag",methods = ["Get","POST"])
@mobile_template('{mobile/}%s')
def pus_order_tag(template):
    _template = template % 'categories_tag.html'
    fh = Fanhao()
    publist = {}
    pubgroup = {}
    limit = 5

    results = db.session.query( Fanhao.publisher, func.count('*').label('cnt') ).filter(
        Fanhao.publisher != ''
    ).group_by( Fanhao.publisher )

    tags = Publisher_tag()

    tag_query = Publisher_tag.query.all()

    for c in results:
        if not c:
            continue
        if not c.publisher:
            publist['None'] = c.cnt
        else:
            publist[c.publisher] = c.cnt

    pre_key = ''
    i = 0
    tot = 0
    for t in tag_query:
        group_key = t.tag
        pub_name = t.publisher

        if not group_key:
            group_key = 'None'

        tot+=1
        if pub_name != pre_key:
            pre_key = pub_name
            i = 0

        i +=1
        if i > limit:
            continue
        if not pub_name in publist:
            #print(pub_name)
            continue

        if group_key not in pubgroup:
            pubgroup[group_key] = []

        if not pub_name:
            pub_name = 'None'
        pubgroup[group_key].append([pub_name,publist[pub_name]])

    return render_template(_template, pubgroup = pubgroup)


@main.route("/publishers/ordernum",methods = ["Get","POST"])
@mobile_template('{mobile/}%s')
def pus_order_num(template):
    _template = template % 'categories_num.html'
    fh = Fanhao()
    publist = {}
    pubgroup = {}
    limit = 5

    results = db.session.query( Fanhao.publisher, func.count('*').label('cnt') ).filter(
        Fanhao.publisher != ''
    ).group_by( Fanhao.publisher )

    group_keys = ['收录量大于100+'.decode('utf-8'),'收录量50~100'.decode('utf-8')
        ,'收录量10~50'.decode('utf-8'),'收录量小于10-'.decode('utf-8')]
    pubgroup = {group_keys[0]:[],group_keys[1]:[],group_keys[2]:[],group_keys[3]:[]}

    for c in results:
        if not c:
            continue
        if not c.publisher:
            publist['None'] = c.cnt
        else:
            publist[c.publisher] = c.cnt

        if c.cnt > 100:
            pubgroup[group_keys[0]].append(c)
        elif c.cnt > 50:
            pubgroup[group_keys[1]].append(c)
        elif c.cnt > 10:
            pubgroup[group_keys[2]].append(c)
        elif c.cnt > 0:
            pubgroup[group_keys[3]].append(c)

    return render_template(_template, pubgroup = pubgroup)

@main.route("/publisher/<pub>",methods = ["Get","POST"])
@main.route("/publisher/<pub>/<page>",methods = ["Get","POST"])
@main.route("/publisher_date/<pub>/<year>",methods = ["Get","POST"])
@main.route("/publisher_date/<pub>/<year>/<page>",methods = ["Get","POST"])
@main.route("/publisher_tag/<pub>/<tag>/",methods = ["Get","POST"])
@main.route("/publisher_tag/<pub>/<tag>/<page>",methods = ["Get","POST"])
@mobile_template('{mobile/}%s')
def publisher(template, pub, year = "", page = 1 , tag = "", pagesize = 20, sensfilter = True):
    #file = codecs.open("data/publisher.json",'r',encoding='utf-8')
    pub = pub.replace("[_]","/")
    _template = template % 'category.html'
    page = int(page)
    year = str(year)
    fhlist = []
    fh_query = Fanhao.query.filter(Fanhao.publisher == pub)

    fh_tags = {}
    for fh in fh_query.all():
        if len(fh.tags) == 0:
            continue
        for t in fh.tags:
            if not t:
                continue
            if not t in fh_tags:
                fh_tags[t] = 1
            else:
                fh_tags[t] += 1
    fh_tags,tag_order = tag_nomalize(fh_tags)

    if year:
        fh_query = fh_query.filter(Fanhao.issuedate.like('%'+ year +'%'))
    if tag:
        fh_query = fh_query.filter(Fanhao._tags.like('%'+ tag +'%'))


    fhlist = fh_query.paginate(page, per_page = pagesize)
    #print(fh_tags)

    return render_template(_template, total = fhlist.total, articles = fhlist.items,
     year=year, tag=tag, publisher=pub, pages = fhlist.pages, curpage = page, tags = fh_tags,tag_order=tag_order)



def tag_nomalize(tags):
    min_ft = 12
    max_ft = 36
    max = 0
    min = 999999
    size_level = 6
    filter_word = [u'',u'\u5355\u4f53',u'\u5355\u4f53\u4f5c\u54c1']

    for tag in tags:
        if tag is None or tag in filter_word:
            continue
        if max < tags[tag]:
            max = tags[tag]
        if min > tags[tag]:
            min = tags[tag]

    rate_ft = (max_ft - min_ft + 0.01) / size_level
    rate = (max - min + 0.01) / size_level

    tag_order = []

    for tag in tags:
        if len(tag_order) == 0:
            tag_order.append([tag,tags[tag]])
            continue
        #print("|tags[tag]:",tags[tag])
        for i in range(0,len(tag_order)):
            v = tag_order[i][1]
            #print(i , v)
            if tags[tag] > v:
                tag_order.insert(i,[tag,tags[tag]])
                break
            if i == len(tag_order) - 1:
                #print("last",tag_order[i])
                tag_order.append([tag,tags[tag]])
            #print(tag_order)

    for tag in tags:
        if tags[tag] > max or tag is None or tag in filter_word:
            tags[tag] = [tags[tag], min_ft]
        else:
            tags[tag] = [tags[tag], float(tags[tag] - min) * rate_ft / rate + min_ft]

    return tags,tag_order


@main.route('/pulldata/<no>', methods=['GET','POST'])
@mobile_template('{mobile/}%s')
def pulldata(template,no):
    template = template % "admin/pull_data.html"
    api_url = "http://localhost:5001/api/get_fanhao/SDNM-116"
    r = requests.get(api_url)
    print(r.json())
    return render_template(template, data=r.json())


@main.route('/pullfh/', methods=['GET','POST'])
@mobile_template('{mobile/}%s')
def pullfh(template):
    template = template % "api/fhs.html"

    #page_url = url_for("main.pullfh", page=page)
    #pagination=Page(None,page=1,items_per_page=20,url=page_url)
    #pagination.page_count = 10
    return render_template(template)


@main.route('/pullcast/', methods=['GET','POST'])
@mobile_template('{mobile/}%s')
def pullcast(template):
    template = template % "api/casts.html"

    #page_url = url_for("main.pullfh", page=page)
    #pagination=Page(None,page=1,items_per_page=20,url=page_url)
    #pagination.page_count = 10
    return render_template(template)


from ..utils.fanhao import *
@main.route('/edit_fh/<no>', methods=['GET','POST'])
@mobile_template('{mobile/}%s')
def edit_fh(template,no):
    template = template % "api/fh_article.html"

    api_url = "http://localhost:5001/api/get_fanhao/"+no
    r = requests.get(api_url)

    fanhao(r.json())
    return "ok"

@main.route('/edit_cast/<name>', methods=['GET','POST'])
@mobile_template('{mobile/}%s')
def edit_cast(template,name):
    template = template % "api/fh_article.html"

    api_url = "http://localhost:5001/api/get_cast/"+name
    r = requests.get(api_url)
    print(r.json())
    cast(r.json())
    return "ok"
