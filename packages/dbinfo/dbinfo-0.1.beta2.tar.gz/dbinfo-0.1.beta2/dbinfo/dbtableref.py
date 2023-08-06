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


from postgres import table_references as table_references_fks_pg


class DbTableReferences(object):

    def __init__(self, conn, table_name):
        self.conn = conn
        self.table_name = table_name
        self.columns = self._get_columns()

    def _get_columns(self):
        raise NotImplementedError()

    def _get_max_col_strlen(self):
        table_schema = len("Table Schema")
        foreign_table = len("Table")
        foreign_colname = len("Foreign Column")
        target_ns = len("Target Schema")
        target_table = len("Target Table")
        target_colname = len("Target Column")
        target_constraint_name = len("Target Name")
        for col in self.columns:
            if len(col['table_schema']) > table_schema:
                table_schema = len(col['table_schema'])
            if len(col['foreign_table']) > foreign_table:
                foreign_table = len(col['foreign_table'])
            if len(col['foreign_colname']) > foreign_colname:
                foreign_colname = len(col['foreign_colname'])
            if len(col['target_ns']) > target_ns:
                target_ns = len(col['target_ns'])
            if len(col['target_table']) > target_table:
                target_table = len(col['target_table'])
            if len(col['target_colname']) > target_colname:
                target_colname = len(col['target_colname'])
            if len(col['target_constraint_name']) > target_constraint_name:
                target_constraint_name = len(col['target_constraint_name'])
        col_len = {
                'table_schema': table_schema + 1,
                'foreign_table': foreign_table + 1,
                'foreign_colname': foreign_colname + 1,
                'target_ns': target_ns + 1,
                'target_table': target_table + 1,
                'target_colname': target_colname + 1,
                'target_constraint_name': target_constraint_name + 1, 
            }
        total = 0
        for k in col_len.keys():
            total += col_len[k]
        col_len['total'] = total
        return col_len

    def _get_strhead(self, col_len):
        s = "Table Schema".ljust(col_len['table_schema']) + "| " \
          + "Table".ljust(col_len['foreign_table']) + "| " \
          + "Foreign Column".ljust(col_len['foreign_colname']) + "| " \
          + "Target Schema".ljust(col_len['target_ns']) + "| " \
          + "Target Table".ljust(col_len['target_table']) + "| " \
          + "Target Column".ljust(col_len['target_colname']) + "| " \
          + "Target Name".ljust(col_len['target_constraint_name']) + "\n"
        s += "-" * (col_len['total'] + 11) + "\n"
        return s

    def __str__(self):
        col_len = self._get_max_col_strlen()
        tbl = "Foreign keys references to '%s'\n\n"  % self.table_name
        head = self._get_strhead(col_len)
        tbl += head
        for col in self.columns:
            tbl += col['table_schema'].ljust(col_len['table_schema']) + "| " \
                 + col['foreign_table'].ljust(col_len['foreign_table']) + "| " \
                 + col['foreign_colname'].ljust(col_len['foreign_colname']) + "| " \
                 + col['target_ns'].ljust(col_len['target_ns']) + "| " \
                 + col['target_table'].ljust(col_len['target_table']) + "| " \
                 + col['target_colname'].ljust(col_len['target_colname']) + "| " \
                 + col['target_constraint_name'].ljust(col_len['target_constraint_name']) + "\n"
        return tbl

class PgDbTableReferences(DbTableReferences):

    def __init__(self, conn, table_name, table_schema='public'):
        self.table_schema=table_schema
        super(PgDbTableReferences, self).__init__(conn, table_name)

    def _get_columns(self):
        columns = table_references_fks_pg(self.conn.cursor(), self.table_name, self.table_schema)
        return columns
