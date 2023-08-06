from ua2.table3.plugin import BasePlugin
from django.db.models import Q



class QuickSearchORM(BasePlugin):
    def __init__(self, search_fields):
        self.search_fields = search_fields

    def build_filter(self, search_string, orm_qs):
        search_filter = []
        for orm_field_name in self.search_fields:
            filter_name = "%s__icontains" % orm_field_name
            search_filter.append(Q(**{filter_name: search_string}))

        result_q = Q()
        for item in search_filter:
            result_q.add(item, Q.OR)

        return orm_qs.filter(result_q)

    def clean(self, search_string):
        return search_string

    def process_request(self, table, request):
        table.features['quicksearch'] = {'active': False},

        if request.REQUEST.get('quicksearch', None):
            search_string = self.clean(request.REQUEST['quicksearch'])
            table.features['quicksearch'] = {'active': True,
                                             'search_string': search_string}

            table.data = self.build_filter(search_string,
                                           table.data)
