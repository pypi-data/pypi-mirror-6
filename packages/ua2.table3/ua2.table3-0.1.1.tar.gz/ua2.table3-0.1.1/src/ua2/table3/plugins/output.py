from ua2.table3.plugin import BasePlugin
from django.template import loader, RequestContext


class DjangoTemplatePlugin(BasePlugin):
    """Django template pluging
    Support rendering output content via Django tempalte

    Lookup request vairables:
        template: name of template for render output

    """
    output = 'html'

    def __init__(self, template_path=None):
        self.template_path = template_path or 'ua2/table3/'

    def render(self, table_obj, table_cls):
        return loader.render_to_string(
            self.template_path + 'main.html',
            dictionary={'table': table_obj,
                        'header': self.header(table_obj, table_cls)},
            context_instance=RequestContext(table_obj.request))

    def header(self, table_obj, table_cls):
        for column_name in table_obj.columns:
            column = table_obj.base_columns[column_name]
            sort_mode = table_obj.features.get('sort',
                                               {}).get(column_name, None)
            yield loader.render_to_string(
                self.template_path + column.header_template,
                dictionary={
                    'table': table_obj,
                    'column_name': column_name,
                    'sort_mode': sort_mode,
                    'column': table_obj.base_columns[column_name]},
                context_instance=RequestContext(table_obj.request))
