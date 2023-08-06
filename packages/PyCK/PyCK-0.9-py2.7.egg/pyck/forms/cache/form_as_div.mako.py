# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1397320996.678922
_enable_loop = True
_template_filename = '/MyWork/Projects/PyCK/pyck/forms/templates/form_as_div.mako'
_template_uri = 'form_as_div.mako'
_source_encoding = 'utf-8'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        form = context.get('form', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        if form._use_csrf_protection:
            # SOURCE LINE 3
            __M_writer(u'<input type="hidden" name="csrf_token" value="')
            __M_writer(unicode(form._csrf_token))
            __M_writer(u'" />\n')
        # SOURCE LINE 5
        if '_csrf' in form.errors:
            # SOURCE LINE 6
            __M_writer(u'<div class="danger">')
            __M_writer(unicode(form.errors['_csrf'][0]))
            __M_writer(u'</div><br />\n')
        # SOURCE LINE 8
        for field in form:
            # SOURCE LINE 9

            field_errors = ''
            if field.errors:
                field_errors = '<span class="danger">'
                for e in field.errors:
                    field_errors += e + ', '
                
                field_errors = field_errors[:-2] + '</span>'
            
            
            __M_locals_builtin_stored = __M_locals_builtin()
            __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['field_errors','e'] if __M_key in __M_locals_builtin_stored]))
            # SOURCE LINE 17
            __M_writer(u'\n\n<div class="form-group">\n    <div class="col-sm-3">\n    ')
            # SOURCE LINE 21
            __M_writer(unicode(field.label))
            __M_writer(u'    \n    </div>\n    \n    <div class="col-sm-9">\n      ')
            # SOURCE LINE 25
            __M_writer(unicode(field(class_="form-control")))
            __M_writer(u'\n    </div>\n</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


