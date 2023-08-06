# -*- coding: utf-8 -*-
# Copyright 2012 Mark Hall (Mark.Hall@work.room3b.eu)
# 
# This file is part of the PyWebTools.
# 
# The PyWebTools is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# The PyWebTools are distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with PyWebTools. If not, see <http://www.gnu.org/licenses/>.

from genshi.builder import tag, Markup

def breadcrumbs(items):
    list_items = []
    for idx, item in enumerate(items):
        if idx == len(items) - 1:
            list_items.append(tag.li(tag.a(item[0], **item[1]), class_='current'))
        else:
            list_items.append(tag.li(tag.a(item[0], **item[1])))
    return tag.nav(tag.ol(list_items), class_='breadcrumbs')

def menu(items, current, **kwargs):
    menu_items = []
    for item in items:
        if item[0] == current:
            menu_items.append(tag.li(tag.a(item[1], **item[2]), class_='current'))
        else:
            menu_items.append(tag.li(tag.a(item[1], **item[2])))
    return tag.nav(tag.ul(menu_items), **kwargs)

def pager(base_url, page, pages, **kwargs):
    if '?' in base_url:
        if not base_url.endswith('?') and not base_url.endswith('&'):
            base_url = base_url + '&'
    else:
        base_url = base_url + '?'
    items = []
    if page > 1:
        items.append(tag.li(tag.a(Markup('&laquo;&nbsp;'), 'first', href='%spage=1' % base_url)))
        items.append(tag.li(tag.a(Markup('&lt;&nbsp;'), 'previous', href='%spage=%i' % (base_url, page - 1))))
    else:
        items.append(tag.li(Markup('&laquo;&nbsp;'), 'first'))
        items.append(tag.li(Markup('&lt;&nbsp;'), 'previous'))
    start_page = max(1, page - 2)
    end_page = min(pages + 1, start_page + 5)
    if end_page - start_page < 5:
        start_page = max(1, end_page - 5)
    for idx in range(start_page, end_page):
        if idx == page:
            items.append(tag.li(tag.a(idx, href='%spage=%i' % (base_url, idx)), class_='current'))
        else:
            items.append(tag.li(tag.a(idx, href='%spage=%i' % (base_url, idx))))
    if page < pages:
        items.append(tag.li(tag.a('next', Markup('&nbsp;&gt;'), href='%spage=%i' % (base_url, page + 1))))
        items.append(tag.li(tag.a('last', Markup('&nbsp;&raquo;'), href='%spage=%i' % (base_url, pages))))
    else:
        items.append(tag.li('next', Markup('&nbsp;&gt;')))
        items.append(tag.li('last', Markup('&nbsp;&raquo;')))
    if 'class_' in kwargs:
        if 'pager' not in kwargs['class_']:
            kwargs['class_'] = kwargs['class_'] + ' pager'
    else:
        kwargs['class_'] = 'pager'
    return tag.nav(tag.ol(items), **kwargs)
