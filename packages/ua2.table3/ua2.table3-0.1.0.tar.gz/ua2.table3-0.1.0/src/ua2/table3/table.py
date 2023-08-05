from ua2.table3.plugin import BasePlugin, StopProcessing
from ua2.table3.column import Column

from django.utils import six
from django.utils.datastructures import SortedDict
from django.utils.encoding import smart_text, force_text, python_2_unicode_compatible

from .render import LazyRender
from .settings import CFG_TABLE_PLUGINS
from .plugins.output import DjangoTemplatePlugin
from .plugin import BasePlugin
from .bound import BoundRow


def get_declared_columns(bases, attrs, with_base_columns=True):
    #inspired from django.forms.forms.get_declared_fields

    columns = [(column_name, attrs.pop(column_name))
               for column_name, obj in list(six.iteritems(attrs)) if isinstance(obj, Column)]
    columns.sort(key=lambda x: x[1].creation_counter)

    if with_base_columns:
        for base in bases[::-1]:
            if hasattr(base, 'base_columns'):
                columns = base.base_columns.items() + columns
    else:
        for base in bases[::-1]:
            if hasattr(base, 'declared_columns'):
                columns = base.declared_columns.items() + columns

    for name, column in columns:
        setattr(column, 'name', name)

    return SortedDict(columns)


class BaseTableMetaclass(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(BaseTableMetaclass, cls).__new__
        # six.with_metaclass() inserts an extra class called 'NewBase' in the
        # inheritance tree: Model -> NewBase -> object. But the initialization
        # should be executed only once for a given model class.

        # attrs will never be empty for classes declared in the standard way
        # (ie. with the `class` keyword). This is quite robust.
        if name == 'NewBase' and attrs == {}:
            return super_new(cls, name, bases, attrs)

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, BaseTableMetaclass) and
                not (b.__name__ == 'NewBase' and b.__mro__ == (b, object))]
        if not parents:
            return super_new(cls, name, bases, attrs)

        attr_meta = attrs.pop('Meta', None)
        if attr_meta:
            plugins = getattr(attr_meta, 'plugins', CFG_TABLE_PLUGINS)
        else:
            plugins = CFG_TABLE_PLUGINS

        attrs['base_columns'] = get_declared_columns(bases, attrs)

        new_class = super_new(cls, name, bases, attrs)

        cls.load_plugins(new_class, plugins)
        return new_class

    def load_plugins(new_class, plugins):
        rc = []
        render = LazyRender()

        for item in plugins:
            if isinstance(item, BasePlugin):
                plugin = item
            elif issubclass(item, BasePlugin):
                plugin = item()
            else:
                raise ValueError("Plugin shoud be subclass of BasePluging")

            if hasattr(item, 'render'):
                render.register(plugin.output,
                                plugin.render)
            rc.append(plugin)
        setattr(new_class, 'render', render)
        setattr(new_class, 'plugins', rc)


class Table(six.with_metaclass(BaseTableMetaclass)):
    def __init__(self, key_name, session_storage, data_source):
        self.id = key_name
        self.request_proxy = None # Class handler incoming request and convert it into internal Request class
        self.data_proxy = None # Class that retrieve data from extetnal storage
        self.plugins = []

        self.request = None
        self.data = data_source
        self.rows_iterator = None
        self.features = {}

    @property
    def columns(self):
        return self.base_columns.keys()

    def process_request(self, _request):
        self.request = _request

        self.rows_iterator = self.data.all()

        for plugin in self.__class__.plugins:
            if hasattr(plugin, 'process_request'):
                plugin.process_request(self, self.request)

        return

        self.request_proxy(_request)
        self.request['columns'] = self.base_columns.keys()

        for handler in self.plugins_request:
            try:
                handler(self.request)
            except StopProcessing, e:
                return self.request.response(e)

        output_handler = self.plugins_output[self.request.output]

        data = self.data_proxy(self, self.request)
        return self.request.build_response(self, output_handler, data)

    def rows(self):
        row_number = 1
        for row in self.rows_iterator():
            yield BoundRow(self, row_number, self.data, row)
            row_number += 1
