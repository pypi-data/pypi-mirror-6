# -*- coding: utf-8 -*-`
from urlparse import urlparse

import psycopg2
from psycopg2.extensions import adapt

from pglogs.monkey import patch_psycopg


class PgConnection(object):

    def __init__(self, db_string, fields=[], table_name="pglogs"):
        patch_psycopg()
        self.conn = None
        parsed = urlparse(db_string)
        self.db_name = parsed.path.split('/')[1]
        self.db_user = parsed.netloc.split('@')[0].split(':')[0]
        self.db_host = parsed.netloc.split('@')[-1].split(':')[0]
        self.db_pwd = parsed.netloc.split('@')[0].split(':')[1]

        # TODO: parse port from db_string
        self.db_port = 5432
        self.table_name = table_name
        self.table_rows = fields

    def connect(self):
        self.conn = psycopg2.connect(
            "dbname=%s user=%s host=%s password=%s port=%s" %
            (self.db_name, self.db_user, self.db_host, self.db_pwd, self.db_port)
        )
        # create table if doesnt exists
        cur = self.conn.cursor()
        cur.execute(
            "select exists(select * from information_schema.tables where table_name=%s)",
            (self.table_name,)
        )
        if not cur.fetchone()[0]:
            sql = "CREATE TABLE %s (%sid SERIAL PRIMARY KEY);" % \
                (self.table_name,  "ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP, " + "".join(["%s TEXT, " % (row) for row in self.table_rows]))
            cur.execute(sql)
            self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()


class LogRecord(object):

    def __init__(self, pg):
        self.pg = pg
        self.cursor = pg.conn.cursor()
        self.conn = pg.conn
        self.fields = {}.fromkeys(self.pg.table_rows, "")
        sql = "INSERT INTO %s(%s) VALUES (%s) RETURNING id" %\
            (
                self.pg.table_name,
                ", ".join([k for k in self.fields.keys()]),
                ", ".join(["'%s'" % v for v in self.fields.values()])
            )
        self.cursor.execute(sql)
        self.id = self.cursor.fetchone()[0]
        self.conn.commit()

    def set_field(self, name, value):
        if name not in self.pg.table_rows:
            raise
        self.fields[name] = value

    def get_field(self, name):
        # Todo: load fields from table
        return self.fields.get(name, None)

    def commit(self):
        values_string = ", ".join(["%s=%s" % (k, adapt(v)) for k, v in self.fields.items()])
        sql = "UPDATE %s SET %s WHERE id=%s" % (self.pg.table_name, values_string, self.id)
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        except:
            return False


# if __name__ == "__main__":

#     fields = [
#         'state', 'proxy_request', 'proxy_response',
#         'chef_request', 'chef_response', 'error_msg'
#     ]
#     pg = PgConnection(
#         "postgresql://user:password@localhost/123",
#         fields=fields,
#         table_name='logs2'
#     )

#     pg.connect()
#     log = LogRecord(pg)
#     log.set_field('chef_request', """'{}[[[]dfdfd''']]--pdfdfdfdfd\\SOME HACKER BEEN HERE}'""")
#     log.set_field('proxy_response', """dfdg'gfgfd'g'dsgd\'gfsdfg\'gdf/dgfd/fdg/f/dgd'\"\\''''""")
#     log.set_field('proxy_request', "йохохо ")
#     log.commit()
#     log.set_field('state', "GOOD")
#     log.commit()
