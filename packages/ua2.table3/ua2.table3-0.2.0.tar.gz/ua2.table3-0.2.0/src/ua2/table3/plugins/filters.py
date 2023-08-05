from ua2.table3.plugin import BasePlugin


class CategoryFilter(BasePlugin):
    def __init__(self, categories):
        self.categories = categories


    def process_request(self, table, request):
        table.features['category'] = {'options': self.categories,
                                      'selected': None}

        category = request.REQUEST.get('category', None)
        categories = dict(self.categories)
        if category in categories:
            table.features['category']['selected'] = category
            cb = getattr(table, 'category_filter', None)
            if cb and callable(cb):
                cb(category)
