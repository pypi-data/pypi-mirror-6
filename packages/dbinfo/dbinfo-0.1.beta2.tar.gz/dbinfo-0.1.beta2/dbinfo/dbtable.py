# -*- coding: utf-8 -*-
##############################################################################
#
#  DB Info, Database Information Tool
#  Copyright (C) 2013 MRDEV Software (<http://mrdev.com.ar>).
#
#  Author: Mariano Ruiz <mrsarm@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this programe.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from postgres import table_columns as table_columns_pg


class DbTable(object):

    def __init__(self, conn, table_name):
        self.conn = conn
        self.table_name = table_name
        self.columns = self._get_columns()
        self.col_nullable_insert, self.col_not_nullable_insert = self._get_cols_by_insert()

    def _get_columns(self):
        raise NotImplementedError()

    def _get_cols_by_insert(self):
        nullable_insert = []
        not_nullable_insert = []
        for col in self.columns:
            if col['is_nullable'] or col['default']:
                nullable_insert.append(col)
            else:
                not_nullable_insert.append(col)
        return nullable_insert, not_nullable_insert

    def _get_max_col_strlen(self):
        col_len = len("Column")
        for col in self.col_nullable_insert:
            if len(col['name']) > col_len:
                col_len = len(col['name'])
        for col in self.col_not_nullable_insert:
            if len(col['name']) > col_len:
                col_len = len(col['name'])
        return col_len + 1

    def _get_strhead(self, col_len):
        s = "Column".ljust(col_len) + "| Data Type                   | Default Value\n"
        s += "-" * (col_len + 45) + "\n"
        return s

    def __str__(self):
        col_len = self._get_max_col_strlen()
        tbl = """Table '%s'

> Mandatory fields
"""  % (self.table_name,)
        head = self._get_strhead(col_len)
        tbl += head
        for col in self.col_not_nullable_insert:
            tbl += col['name'].ljust(col_len) \
                + '| %-27s | %s\n' % (col['data_type'], 'YES' if col['default'] else 'NO')
        tbl += "\n> Optionals fields\n" + head
        for col in self.col_nullable_insert:
            tbl += col['name'].ljust(col_len) \
                + '| %-27s | %s\n' % (col['data_type'], 'YES' if col['default'] else 'NO')
        return tbl

class PgDbTable(DbTable):

    def __init__(self, conn, table_name, table_schema='public'):
        self.table_schema=table_schema
        super(PgDbTable, self).__init__(conn, table_name)

    def _get_columns(self):
        columns = table_columns_pg(self.conn.cursor(), self.table_name, self.table_schema)
        return columns
