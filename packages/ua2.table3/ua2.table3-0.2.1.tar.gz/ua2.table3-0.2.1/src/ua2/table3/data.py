from django.db.models.manager import Manager

class DjnagoORM(object):
    def __init__(self, qs=None):
        self.table = None
        self.request = None
        self.qs = qs

    def __call__(self, table, request):
        self.table = table
        self.request = request
        return self

    def __iter__(self):
        for item in self.qs:
            yield item


    def _recursive_value(self, row, keylist):
        value = None
        if hasattr(row, keylist[0]):
            value = getattr(row, keylist[0])
            if callable(value):
                value = value()
            if len(keylist) > 1:
                return self._recursive_value(value, keylist[1:])

        return value

    def resolve(self, row, id, column):
        refname = column.refname or id

        value = self._recursive_value(row, refname.split('__'))
        if value is not None:
            if isinstance(value, Manager):
                return value.all()
            return value
