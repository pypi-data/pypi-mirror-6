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

import MySQLdb

def connect(options):
    conn = MySQLdb.connect(db=options.dbname,
                           user=options.username,
                           passwd=options.password,
                           host=options.host,
                           port=int(options.port))
    return conn

def num_tables(cursor):
    cursor.execute("SHOW TABLES")
    res = cursor.fetchall()
    return len(res)

def tables_name(cursor, table_schema='public'):
    cursor.execute("SHOW TABLES")
    res = cursor.fetchall()
    tbls_name = [d[0] for d in res]
    return tbls_name

def table_columns_name(cursor, table_name):
    cursor.execute("SHOW COLUMNS FROM %s" % table_name)
    res = cursor.fetchall()
    tbl_cols_name = [d[0] for d in res]
    return tbl_cols_name

def db_size(cursor, dbname):
    """
    Return size in megabytes
    """
    cursor.execute(
        """SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 1)
           FROM information_schema.tables
           WHERE table_schema=%s
        """, (dbname,))
    dbsize = cursor.fetchone()
    return "%s %s" % (dbsize[0], "MB")
