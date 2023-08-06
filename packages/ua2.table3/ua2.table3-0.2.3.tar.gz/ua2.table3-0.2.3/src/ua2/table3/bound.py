class BoundCell(object):
    def __init__(self, column_name, table, row_number, data, row):
        self.column_name = column_name
        self.table = table
        self.column = table.base_columns[column_name]
        self.row_number = row_number
        self.data = data
        self.row = row
        self._style = None

    def __unicode__(self):
        return unicode(self.value)

    @property
    def value(self):
        return self.column.get_value(self.table, self.row, row_number=self.row_number)

    def as_html(self):
        return self.column.as_html(self.table, self.row, row_number=self.row_number)

    @property
    def style(self):
        if self._style is None:
            if self.column.cell_style and callable(self.column.cell_style):
                self._style = self.column.cell_style(self.table, self.row, self.value)
            else:
                self._style = self.column.cell_style
        return self._style

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
