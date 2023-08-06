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

import psycopg2

def connect(options):
    conn = psycopg2.connect(database=options.dbname,
                            user=options.username,
                            password=options.password,
                            host=options.host,
                            port=options.port)
    return conn

def num_tables(cursor, table_schema='public'):
    cursor.execute(
        """SELECT count(*) FROM information_schema.tables
           WHERE table_schema=%s""", (table_schema,))
    num_tbls = cursor.fetchone()
    return num_tbls[0]

def tables_name(cursor, table_schema='public'):
    cursor.execute(
        """SELECT table_name FROM information_schema.tables
           WHERE table_schema=%s
           ORDER BY table_name""", (table_schema,))
    res = cursor.fetchall()
    tbls_name = [d[0] for d in res]
    return tbls_name

def table_columns_name(cursor, table_name, table_schema='public'):
    cursor.execute(
        """SELECT column_name 
           FROM information_schema.columns
           WHERE table_schema=%s AND table_name=%s
           ORDER BY column_name""", (table_schema, table_name,))
    res = cursor.fetchall()
    tbl_cols_name = [d[0] for d in res]
    return tbl_cols_name

def table_columns(cursor, table_name, table_schema='public'):
    cursor.execute(
        """SELECT
             c.column_name, c.data_type, c.is_nullable, c.column_default,
             tc.constraint_name, 
             ccu.table_name AS foreign_table_name,
             ccu.column_name AS foreign_column_name,
             tc.constraint_type
           FROM information_schema.columns c
             LEFT OUTER JOIN information_schema.key_column_usage AS kcu
             ON c.column_name = kcu.column_name AND c.table_name = kcu.table_name AND c.table_schema = kcu.table_schema
             LEFT OUTER JOIN information_schema.table_constraints AS tc
             ON tc.constraint_name = kcu.constraint_name AND tc.constraint_type IN ('FOREIGN KEY', 'PRIMARY KEY')
             LEFT OUTER JOIN information_schema.constraint_column_usage AS ccu
             ON ccu.constraint_name = tc.constraint_name
           WHERE c.table_schema = %s AND c.table_name = %s
           ORDER BY tc.constraint_type DESC, c.column_name, c.is_nullable, c.column_default""", (table_schema, table_name,))
    res = cursor.fetchall()
    tbl_cols = []
    for d in res:
        tbl_cols.append({
                'name': d[0],
                'data_type': d[1],
                'is_nullable': d[2] == 'YES',
                'default': d[3] or None,
                'constraint': d[4] or None,
                'foreign_table': d[5],
                'foreign_column': d[6],
                'constraint_type': d[7] or None,  # 'PRIMARY KEY' or 'FOREIGN KEY'
            })
    return tbl_cols

def table_references(cursor, table_name, table_schema='public'):
    cursor.execute(
        """SELECT
             (SELECT nspname FROM pg_namespace WHERE oid=f.relnamespace) AS table_schema,
             f.relname AS foreign_table,
             (SELECT a.attname
                FROM pg_attribute a
                WHERE a.attrelid = f.oid AND a.attnum = o.confkey[1] AND a.attisdropped = false) AS foreign_colname,
             (SELECT nspname FROM pg_namespace
                WHERE oid=m.relnamespace) AS target_ns,
             m.relname AS target_table,
             (SELECT a.attname
                FROM pg_attribute a
                WHERE a.attrelid = m.oid AND a.attnum = o.conkey[1] AND a.attisdropped = false) AS target_colname,
             o.conname AS target_constraint_name
           FROM pg_constraint o LEFT JOIN pg_class c ON c.oid = o.conrelid
             LEFT JOIN pg_class f ON f.oid = o.confrelid LEFT JOIN pg_class m ON m.oid = o.conrelid, information_schema.tables t
           WHERE o.contype = 'f' AND o.conrelid IN (SELECT oid FROM pg_class c WHERE c.relkind = 'r')
             AND f.relname = t.table_name AND t.table_schema = %s AND f.relname = %s""", (table_schema, table_name,))
    res = cursor.fetchall()
    tbl_cols = []
    for d in res:
        tbl_cols.append({
                'table_schema': d[0],
                'foreign_table': d[1],
                'foreign_colname': d[2],
                'target_ns': d[3],
                'target_table': d[4],
                'target_colname': d[5],
                'target_constraint_name': d[6]
            })
    return tbl_cols

def count_references(cursor, table_name, table_schema='public', query=None):
    tbl_cols = table_references(cursor, table_name, table_schema)
    return count_columns_references(cursor, tbl_cols, table_schema, query)

def count_columns_references(cursor, tbl_cols, table_schema='public', query=None):
    count = ""
    for col in tbl_cols:
        q = "SELECT COUNT(*) FROM " + table_schema + "." + col["target_table"] + " WHERE " + col["target_colname"] + " = %s"
        cursor.execute(q, (query,))
        result = cursor.fetchone()[0]
        if result>0:
            count += "%s.%s: %s rows\n" % (col["target_table"], col["target_colname"], result)
    return count

def make_table_references_update(cursor, table_name, table_schema='public', query=None):
    tbl_cols = table_references(cursor, table_name, table_schema)
    return make_columns_references_update(cursor, tbl_cols, table_schema, query)

def table_references_update(cursor, table_name, table_schema='public', query=None):
    q = make_table_references_update(cursor, table_name, table_schema, query)
    cursor.execute(q)
    return True

def make_columns_references_update(cursor, tbl_cols, table_schema='public', query=None):
    old_value = None
    new_value = None
    if query:
        query = query.split(",")
        if len(query)==2:
            old_value = query[0]
            new_value = query[1]
    if not old_value or not new_value:
        old_value = "OLD_VALUE"
        new_value = "NEW_VALUE"
    update_query = ""
    for col in tbl_cols:
        q = \
"""UPDATE %(target_ns)s.%(target_table)s SET %(target_colname)s = %(new_value)s WHERE %(target_colname)s = %(old_value)s;
""" % {
        "target_ns": col["target_ns"],
        "target_table": col["target_table"],
        "target_colname": col["target_colname"],
        "old_value": old_value,
        "new_value": new_value,
      }
        update_query += q
    return update_query

def db_size(cursor, dbname):
    """
    Return size in megabytes
    """
    cursor.execute(
        """SELECT pg_size_pretty(pg_database_size(pg_database.datname))
           FROM pg_database where
           datname=%s
        """, (dbname,))
    dbsize = cursor.fetchone()
    return dbsize[0]
