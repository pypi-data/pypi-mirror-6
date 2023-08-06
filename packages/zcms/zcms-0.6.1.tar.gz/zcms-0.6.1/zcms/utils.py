# -*- encoding: utf-8 -*-

from datetime import datetime
from docutils.core import publish_parts
from docutils.writers.html4css1 import Writer
import urllib2
import os
import chardet
from string import Template
from pyramid.response import Response
from pyramid.threadlocal import get_current_registry
import rst2html5

_templates_cache = {}
EMPTY_THEME = u"""
     <html>
       <head>
          <title>$title - $site_title</title>
          <meta name="Description" content="$site_description"/>
       </head>
       <body>
          <ul>$nav</ul>
          <div>$upper</div>
          <table>
            <tr>
               <td>$left</td>
               <td>$content</td>
               <td>$right</td>
            </tr>
          </table>
       </body>
     </html>
"""

def getDisplayTime(input_time, show_mode='localdate'):
    """ 人性化的时间显示: (支持时区转换)

    time 是datetime类型，或者timestampe的服点数，
    最后的show_mode是如下:

    - localdate: 直接转换为本地时间显示，到天
    - localdatetime: 直接转换为本地时间显示，到 年月日时分
    - localtime: 直接转换为本地时间显示，到 时分
    - deadline: 期限，和当前时间的比较天数差别，这个时候返回2个值的 ('late', '12天前')
    - humandate: 人可阅读的天，今天、明天、后天、昨天、前天，或者具体年月日 ('today', '今天')
    """
    if not input_time:
        return ''

    today = datetime.now()
    time_date = datetime(input_time.year, input_time.month, input_time.day)
    year, month, day = today.year, today.month, today.day
    today_start = datetime(year, month, day)

    to_date = today_start - time_date

    # 期限任务的期限
    if show_mode == 'localdate':
        return input_time.strftime('%Y-%m-%d')
    elif show_mode == 'localdatetime':
        return input_time.strftime('%Y-%m-%d %H:%M')
    elif show_mode == 'localtime':
        return input_time.strftime('%H:%M')
    elif show_mode == 'deadline':
        if to_date == 0:
            return ('Today', '今天')
        elif to_date < 0:
            if to_date == -1:
                return (None, '明天')
            elif to_date == -2:
                return (None, '后天')
            else:
                return (None, str(int(-to_date))+'天')
        elif to_date > 0:
            if to_date == 1:
                return ('late', '昨天')
            elif to_date == 2:
                return ('late', '前天')
            else:
                return ('late', str(int(to_date))+'天前')
    elif show_mode == 'humandate':
        if to_date == 0:
            return ('Today', '今天')
        elif to_date < 0:
            if to_date == -1:
                return (None, '明天')
            elif to_date == -2:
                return (None, '后天')
            else:
                return (None, input_time.strftime('%Y-%m-%d'))
        elif to_date > 0:
            if to_date == 1:
                return ('late', '昨天')
            elif to_date == 2:
                return ('late', '前天')
            else:
                return ('late', input_time.strftime('%Y-%m-%d'))

def rst2html(rst, path, context, request):
    settings = {
        'halt_level':6,
        'input_encoding':'UTF-8',
        'output_encoding':'UTF-8',
        'initial_header_level':1,
        'file_insertion_enabled':1,
        'raw_enabled':1,
        'writer_name':'html',
        'language_code':'zh_cn',
        'context':context,
        'request':request
    }

    parts = publish_parts(
        rst,
        source_path = path,
        writer=rst2html5.HTML5Writer(),
        settings_overrides = settings
    )
    return parts['body']


def render_sections(site, context, request):
    if context.vpath == '/': return

    html_list = []
    for tab in site.values(True, True):
        class_str = ''
        if context.vpath.startswith(tab.vpath):
            class_str = "active"

        tab_url = tab.url(request)

        html_list.append(
            '<li class="%s"><a href="%s">%s</a></li>'
            % (class_str, tab_url, tab.title)
        )

    return ''.join(html_list)

def zcms_template(func):
    def _func(context, request):
        site = context.get_site()
        if 'X-ZCMS-VHM' in request.headers:
            # 线上运行，多站点支持, support ngix
            path_info = request.environ['PATH_INFO'].split('/', 2)
            if len(path_info) > 2:
                request.environ['HTTP_X_VHM_ROOT'] = '/' + site.__name__
                request.environ['PATH_INFO'] = '/%s' % path_info[2]

        content = func(context, request)
        if type(content) is tuple:  # index page may change context
            context, content = content
        if type(content) is not unicode:
            content = content.decode('utf-8')

        # 根据模版来渲染最终效果
        theme_base = site.metadata.get('theme_base', '')
        kw = {
        'site_title': site.title,
        'site_description': site.metadata.get('description', ''),
        'title': context.title,
        'description': context.metadata.get('description', ''),
        'nav': render_sections(site, context, request),
        'base': context.url(request),
        'content': content,
        'left': context.render_slots('left', request),
        'right': context.render_slots('right', request),
        'upper': context.render_slots('upper', request),
        'theme_base': theme_base,
        }

        theme_default = site.metadata.get('theme', 'default.html')
        theme = context.metadata.get('theme', theme_default)
        if theme_base.startswith('/'):
            theme_base = request.host_url + theme_base
        template = get_theme_template(theme_base + '/' + theme)
        output = template.substitute(kw).encode('utf8')
        return Response(output, headerlist=[
                ('Content-length', str(len(output))),
                ('Content-type', 'text/html; charset=UTF-8')
	    ])
    return _func

def get_theme_template(theme_url):
    # cache template, TODO refresh cache
    global _templates_cache
    is_debug = get_current_registry().settings.get('pyramid.debug_templates', False)

    if not is_debug and theme_url in _templates_cache:
        return _templates_cache[theme_url]

    if theme_url == '/default.html':
        theme = EMPTY_THEME
    else:
        theme = urllib2.urlopen(theme_url).read()
        text_encoding = chardet.detect(theme)['encoding']
        theme = theme.decode(text_encoding)
    template = Template(theme)
    _templates_cache[theme_url] = template
    return template
