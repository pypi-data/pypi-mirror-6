# -*- coding: utf-8 -*-
# The HTMLFormFiller is taken from Genshi and has been extended to
# handle HTML 5 form elements. It is distributed under the following
# license:
#
#Copyright (C) 2006-2010 Edgewall Software
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions
#are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 3. The name of the author may not be used to endorse or promote
#    products derived from this software without specific prior
#    written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS
#OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
#DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
#GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
#IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
#IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from genshi import filters

class HTMLFormFiller(object):
    """A stream filter that can populate HTML forms from a dictionary of values.
    Adds support for HTML5 form elements and multi-selection of checkboxes.
    
    >>> from genshi.input import HTML
    >>> html = HTML('''<form>
    ...   <p><input type="text" name="foo" /></p>
    ... </form>''')
    >>> filler = HTMLFormFiller(data={'foo': 'bar'})
    >>> print(html | filler)
    <form>
      <p><input type="text" name="foo" value="bar"/></p>
    </form>
    """
    # TODO: only select the first radio button, and the first select option
    #       (if not in a multiple-select)
    # TODO: only apply to elements in the XHTML namespace (or no namespace)?

    def __init__(self, name=None, id=None, data=None, passwords=False):
        """Create the filter.
        
        :param name: The name of the form that should be populated. If this
                     parameter is given, only forms where the ``name`` attribute
                     value matches the parameter are processed.
        :param id: The ID of the form that should be populated. If this
                   parameter is given, only forms where the ``id`` attribute
                   value matches the parameter are processed.
        :param data: The dictionary of form values, where the keys are the names
                     of the form fields, and the values are the values to fill
                     in.
        :param passwords: Whether password input fields should be populated.
                          This is off by default for security reasons (for
                          example, a password may end up in the browser cache)
        :note: Changed in 0.5.2: added the `passwords` option
        """
        self.name = name
        self.id = id
        if data is None:
            data = {}
        self.data = data
        self.passwords = passwords

    def __call__(self, stream):
        """Apply the filter to the given stream.
        
        :param stream: the markup event stream to filter
        """
        in_form = in_select = in_option = in_textarea = False
        select_value = option_value = textarea_value = None
        option_start = None
        option_text = []
        no_option_value = False

        for kind, data, pos in stream:

            if kind is filters.html.START:
                tag, attrs = data
                tagname = tag.localname

                if tagname == 'form' and (
                        self.name and attrs.get('name') == self.name or
                        self.id and attrs.get('id') == self.id or
                        not (self.id or self.name)):
                    in_form = True

                elif in_form:
                    if tagname == 'input':
                        type = attrs.get('type', '').lower()
                        if type in ('checkbox', 'radio'):
                            name = attrs.get('name')
                            if name and name in self.data:
                                try:
                                    value = self.data.getall(name)
                                except AttributeError:
                                    value = self.data[name]
                                declval = attrs.get('value')
                                checked = False
                                if isinstance(value, (list, tuple)):
                                    if declval:
                                        checked = declval in [unicode(v) for v
                                                              in value]
                                    else:
                                        checked = any(value)
                                else:
                                    if declval:
                                        checked = declval == unicode(value)
                                    elif type == 'checkbox':
                                        checked = bool(value)
                                if checked:
                                    attrs |= [(filters.html.QName('checked'), 'checked')]
                                elif 'checked' in attrs:
                                    attrs -= 'checked'
                        elif type in ('', 'hidden', 'text', 'number', 'email', 'url', 'date', 'time', 'datetime', 'month') \
                                or type == 'password' and self.passwords:
                            name = attrs.get('name')
                            if name and name in self.data:
                                value = self.data[name]
                                if isinstance(value, (list, tuple)):
                                    value = value[0]
                                if value is not None:
                                    attrs |= [
                                        (filters.html.QName('value'), unicode(value))
                                    ]
                    elif tagname == 'select':
                        name = attrs.get('name')
                        if name in self.data:
                            select_value = self.data[name]
                            in_select = True
                    elif tagname == 'textarea':
                        name = attrs.get('name')
                        if name in self.data:
                            textarea_value = self.data.get(name)
                            if isinstance(textarea_value, (list, tuple)):
                                textarea_value = textarea_value[0]
                            in_textarea = True
                    elif in_select and tagname == 'option':
                        option_start = kind, data, pos
                        option_value = attrs.get('value')
                        if option_value is None:
                            no_option_value = True
                            option_value = ''
                        in_option = True
                        continue
                yield kind, (tag, attrs), pos

            elif in_form and kind is filters.html.TEXT:
                if in_select and in_option:
                    if no_option_value:
                        option_value += data
                    option_text.append((kind, data, pos))
                    continue
                elif in_textarea:
                    continue
                yield kind, data, pos

            elif in_form and kind is filters.html.END:
                tagname = data.localname
                if tagname == 'form':
                    in_form = False
                elif tagname == 'select':
                    in_select = False
                    select_value = None
                elif in_select and tagname == 'option':
                    if isinstance(select_value, (tuple, list)):
                        selected = option_value in [unicode(v) for v
                                                    in select_value]
                    else:
                        selected = option_value == unicode(select_value)
                    okind, (tag, attrs), opos = option_start
                    if selected:
                        attrs |= [(filters.html.QName('selected'), 'selected')]
                    elif 'selected' in attrs:
                        attrs -= 'selected'
                    yield okind, (tag, attrs), opos
                    if option_text:
                        for event in option_text:
                            yield event
                    in_option = False
                    no_option_value = False
                    option_start = option_value = None
                    option_text = []
                elif tagname == 'textarea':
                    if textarea_value:
                        yield filters.html.TEXT, unicode(textarea_value), pos
                    in_textarea = False
                yield kind, data, pos

            else:
                yield kind, data, pos
