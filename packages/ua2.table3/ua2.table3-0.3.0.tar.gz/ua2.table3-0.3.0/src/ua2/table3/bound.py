class BoundCell(object):
    def __init__(self, column_name, table, row_number, data, row):
        self.column_name = column_name
        self.table = table
        self.column = table.base_columns[column_name]
        self.row_number = row_number
        self.data = data
        self.row = row
        self._cell_atts = None
        self._value = None

    def __unicode__(self):
        return unicode(self.value)

    @property
    def value(self):
        if self._value is None:
            self._value = self.column.get_value(self.table, self.row, row_number=self.row_number)
        return self._value

    def as_html(self):
        return self.column.as_html(self.table, self.row, row_number=self.row_number)

    @property
    def html_attrs(self):
        if self._cell_atts is None:
            self._cell_atts = self.column.cell_html_attrs(
                self.table,
                self.row,
                self.value,
                row_number=self.row_number)
        return self._cell_atts


class BoundRow(object):
    def __init__(self, table, row_number, data, row):
        self.table = table
        self.number = row_number
        self.data = data
        self.row = row
        self.row_number = row_number

    def cells(self):
        for column_name in self.table.columns:
            yield BoundCell(column_name,
                            self.table,
                            self.row_number,
                            self.data,
                            self.row)
