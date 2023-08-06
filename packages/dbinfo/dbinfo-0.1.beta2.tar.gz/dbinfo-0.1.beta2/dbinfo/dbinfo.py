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

import optparse
import sys
from os import path

__version__ = '0.1.beta2'
__license__ = 'LGPL-3'

def error_db_not_implemented():
    sys.stderr.write("Database connector not implemented!")
    exit(-1)

def main(db='pg'):
    parser = optparse.OptionParser(version='%prog v' + __version__)
    if db=='pg':
        from postgres import connect, num_tables, tables_name, \
             table_columns_name, table_columns, db_size, \
             table_references, make_table_references_update, \
             table_references_update, count_references
        from dbtable import PgDbTable as Table
        from dbtableref import PgDbTableReferences as DbTableReferences
        username_default = 'postgres'
        password_default = 'postgres'
        port_default = '5432'
    elif db=='my':
        from mysql import connect, num_tables, tables_name, table_columns_name, db_size
        username_default = 'root'
        password_default = 'admin'
        port_default = '3306'
    else:
        error_db_not_implemented()
    parser.add_option("-U", "--username", dest="username", help='database user name (default: "%s")' % (username_default,), default=username_default)
    parser.add_option("-W", "--password", dest="password", help='database password (default: "%s")' % (password_default,), default=password_default)
    parser.add_option("-d", "--dbname", dest="dbname", help='database name to connect', default=None)
    parser.add_option("-H", "--host", dest="host", help='database server host or socket directory (default: "localhost")', default="localhost")
    parser.add_option("-p", "--port", dest="port", help='database server port (default: "%s")' % (port_default,), default=port_default)
    parser.add_option("-t", "--table", dest="table", help='describe table', default=None)
    parser.add_option("-r", "--references", dest="references", metavar="TABLE", help='all foreign keys references for the given table', default=None)
    parser.add_option("-s", "--size", dest="size", action="store_true", help='database size', default=False)
    parser.add_option("-l", "--list", dest="list", action="store_true", help='table list', default=False)
    parser.add_option("-q", "--query", dest="query", metavar="OLD KEY,NEW KEY", help='use with -r. Parse query to update table references to TABLE with OLD KEY to NEW KEY', default=None)
    parser.add_option("-x", "--query-exec", dest="query_exec", metavar="OLD KEY,NEW KEY", help='use with -r. Execute query to update table references to TABLE with OLD KEY to NEW KEY', default=None)
    parser.add_option("-c", "--count", dest="count", metavar="KEY", help='use with -r. Count all rows in table with references to TABLE with KEY id', default=None)
    (options, args) = parser.parse_args()

    if options.table or options.size or options.list or options.references:
        try:
            conn = connect(options)
        except Exception, e:
            sys.stderr.write("Connection Error: " + e.message)
            exit(-2)
        try:
            cur = conn.cursor()
        except Exception, e:
            conn.close()
            sys.stderr.write("Cursor Error: " + e.message)
            exit(-3)
    else:
        cmd = path.split(sys.argv[0])[1]
        sys.stderr.write("No command specified!\nTry `%s -h' or '%s --help' for more information.\n" % (cmd, cmd))
        exit(-1)
    try:
        if options.table:
            if db=='my':
                print "Tables columns name:", table_columns_name(cur, options.table)
            else:
                tbl_path = options.table.split('.')
                if len(tbl_path)==1:
                    print Table(conn, options.table)
                else:
                    print Table(conn, tbl_path[1], tbl_path[0])
        elif options.size:
            print "Database size:", db_size(cur, options.dbname)
        elif options.list:
            print "Number of tables:", num_tables(cur)
            print "Tables names:", str(tables_name(cur))[1:-1]
        elif options.references:
            tbl_path = options.references.split(".")
            if len(tbl_path)==1:
                if options.query:
                    print make_table_references_update(cur, table_name=options.references, query=options.query)
                elif options.query_exec:
                    table_references_update(cur, table_name=options.references, query=options.query_exec)
                elif options.count:
                    print count_references(cur, table_name=options.references, query=options.count)
                else:
                    print DbTableReferences(conn, options.references)
            else:
                if options.query:
                    print make_table_references_update(cur, tbl_path[1], tbl_path[0], options.query)
                elif options.query_exec:
                    table_references_update(cur, tbl_path[1], tbl_path[0], options.query_exec)
                elif options.count:
                    print count_references(cur, tbl_path[1], tbl_path[0], options.count)
                else:
                    print DbTableReferences(conn, tbl_path[1], tbl_path[0])
        conn.commit()
    except Exception, e:
        conn.rollback()
        conn.close()
        sys.stderr.write("Error: " + e.message)
        exit(-1)

    conn.close()
    exit(0)

def main_pg():
    main('pg')

def main_my():
    main('my')


if __name__=="__main__":
    main()
