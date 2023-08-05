import types

from django.db.models.manager import Manager
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.html import escape
from django.template import loader, RequestContext
from django.forms.util import flatatt

class Column(object):
    header_template = 'header_column.html'
    creation_counter = 0

    def __init__(self, label, refname=None, sortable=False, order_by=None,
                 header_style=None, cell_style=None, default_value='',
                 **attrs):
        self.name = None #fills by table metaclass
        self.label = label
        self.refname = refname
        self.sortable = sortable
        self.order_by = order_by
        self.header_style = header_style
        self.cell_style = cell_style
        self.attrs = attrs
        self.default_value = default_value

        self.creation_counter = Column.creation_counter
        Column.creation_counter += 1

    def __unicode__(self):
        return self.column.label

    def _recursive_value(self, row, keylist):
        value = None
        if hasattr(row, keylist[0]):
            value = getattr(row, keylist[0])
            if callable(value):
                value = value()
            if len(keylist) > 1:
                return self._recursive_value(value, keylist[1:])
        return value

    def get_value(self, table, row, refname=None, default=None, **kwargs):
        if refname is None and self.refname is None:
            return default

        value = self._recursive_value(
            row,
            (refname or self.refname).split('__'))

        if value is not None:
            if isinstance(value, Manager):
                return value.all()
            return value
        return default

    def as_html(self, table, row, **kwargs):
        value = self.get_value(table, row, **kwargs)
        if value is None:
            return self.default_value
        return value


class LabelColumn(Column):
    pass


class HrefColumn(Column):
    def __init__(self, *args, **attrs):
        self.reverse = attrs.pop('reverse', None)
        self.reverse_args = attrs.pop('reverse_args', [])
        self.get_args = attrs.pop('get', '')
        super(HrefColumn, self).__init__(*args, **attrs)

    def resolve(self, table, row):
        if not self.reverse:
            return ''

        reverse_args = self.reverse_args
        if callable(reverse_args):
            reverse_args = reverse_args(row)
        elif type(self.reverse_args) in (types.ListType, types.TupleType):
            reverse_args = [ self.get_value(table, row, refname=item) for item in reverse_args ]
        elif type(reverse_args) in types.StringTypes:
            reverse_args = [ self.get_value(table, row, refname=reverse_args)]

        try:
            href = reverse(self.reverse, args=reverse_args)
        except NoReverseMatch, e:
            href = "#NoReverseMatch"
        return href

    def as_html(self, table, row, **kwargs):
        html = u"<a href='{href}{get_args}' {attrs}>{content}</a>".format(
            href=self.resolve(table, row),
            attrs=flatatt(self.attrs),
            content=escape(self.get_value(table, row)),
            get_args=self.get_args
            )
        return mark_safe(html)


class TemplateColumn(Column):
    def __init__(self, *args, **attrs):
        self.template = attrs.pop('template', None)
        super(TemplateColumn, self).__init__(*args, **attrs)

    def as_html(self, table, row, **kwargs):
        if not self.template:
            return ''

        return loader.render_to_string(
            self.template,
            dictionary={'table': table,
                        'record': row, # for compatilibty with django_tables2 tempaltes
                        'row': row},
            context_instance=RequestContext(table.request))


class CheckboxColumn(Column):
    header_template = 'header_checkbox.html'

    def __init__(self, *args, **attrs):
        super(CheckboxColumn, self).__init__('', *args, **attrs)

    def as_html(self, table, row, **kwargs):
        attrs = self.attrs.copy()
        attrs['type'] = 'checkbox'
        attrs['autocomplete'] = 'off'
        attrs['name'] = self.name
        attrs['value'] = self.get_value(table, row, **kwargs)

        html = u"<input {attrs} />".format(attrs=flatatt(attrs))
        return mark_safe(html)
