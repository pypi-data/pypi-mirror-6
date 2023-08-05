# -*- coding: utf-8 -*-

from marcellus.dataset import DataSet
from marcellus.util import strtotime
from sqlalchemy import Table, MetaData, select, exists
from sqlalchemy.sql.expression import and_, Select, or_, alias
from sqlalchemy.types import DATE, TIME, DATETIME, INTEGER, NUMERIC, BOOLEAN, BIGINT
import re
import datetime as dt

_CONSTANT_DATE_TODAY       = 'today'
_CONSTANT_DATE_START_WEEK  = 'start_week'
_CONSTANT_DATE_END_WEEK    = 'end_week'
_CONSTANT_DATE_START_MONTH = 'start_month'
_CONSTANT_DATE_END_MONTH   = 'end_month'
_CONSTANT_DATE_START_YEAR  = 'start_year'
_CONSTANT_DATE_END_YEAR    = 'end_year'
_CONSTANT_DAY              = 'd'
_CONSTANT_WEEK             = 'w'
_CONSTANT_MONTH            = 'm'
_CONSTANT_YEAR             = 'y'


class Busqueda(object):

    def __init__(self, tabla, columnas_trans=None, strtodatef=None):
        self.tabla = tabla
        self.cols = []
        self.types = []
        for col in self.tabla.columns:
            self.cols.append(col.name)
            self.types.append(col.type)

        self.cache_campo = {}

        # string to date conversion function
        self.strtodatef = strtodatef

        if not columnas_trans:
            self.cols_trans = [re.sub(r'[^a-z0-9]*', '', self.remove_accents(col))
                               for col in self.cols]
        else:
            self.cols_trans = columnas_trans

    def no_accents(self, texto):

        resultado = texto
        resultado = re.sub(r'(a|á|à|ä)', '(a|á|à|ä)', resultado)
        resultado = re.sub(r'(e|é|è|ë)', '(e|é|è|ë)', resultado)
        resultado = re.sub(r'(i|í|ì|ï)', '(i|í|ì|ï)', resultado)
        resultado = re.sub(r'(o|ó|ò|ö)', '(o|ó|ò|ö)', resultado)
        resultado = re.sub(r'(u|ú|ù|ü)', '(u|ú|ù|ü)', resultado)

        return resultado

    def remove_accents(self, texto):
        texto = texto.encode('utf-8')

        return texto.lower(). \
            replace('á', 'a'). \
            replace('é', 'e'). \
            replace('í', 'i'). \
            replace('ó', 'o'). \
            replace('ú', 'u'). \
            replace('ü', 'u')

    def get_col(self, campo):

        if campo.lower() in self.cache_campo:
            return self.cache_campo[campo.lower()]

        else:
            col = None
            for ct, c in zip(self.cols_trans, self.cols):

                if ct.startswith(campo.lower()):
                    if not col or col['length'] > len(ct):
                        col = dict(name=c, length=len(ct))

            if col:
                self.cache_campo[campo.lower()] = col['name']
                return col['name']

            else:
                return None

    def process_date_constants(self, termino):

        def _sub(m):
            cons = m.group(1)
            s = m.group(3)
            q = int(m.group(4) or 0)
            t = m.group(5) or _CONSTANT_DAY

            r = None
            if cons == _CONSTANT_DATE_TODAY:
                r = dt.date.today()

            elif cons == _CONSTANT_DATE_START_WEEK:
                wd = dt.date.today().weekday()
                r = dt.date.today() - dt.timedelta(days=wd)

            elif cons == _CONSTANT_DATE_END_WEEK:
                wd = 6 - dt.date.today().weekday()
                r = dt.date.today() + dt.timedelta(days=wd)

            elif cons == _CONSTANT_DATE_START_MONTH:
                today = dt.date.today()
                r = dt.date(today.year, today.month, 1)

            elif cons == _CONSTANT_DATE_END_MONTH:
                today = dt.date.today()
                next_month = today + dt.timedelta(days=30)
                r = dt.date(next_month.year, next_month.month, 1) - dt.timedelta(days=1)

            elif cons == _CONSTANT_DATE_START_YEAR:
                today = dt.date.today()
                r = dt.date(today.year, 1, 1)

            elif cons == _CONSTANT_DATE_END_YEAR:
                today = dt.date.today()
                r = dt.date(today.year, 12, 31)

            if r:
                if s and q:
                    if t == _CONSTANT_DAY:
                        if s == '-':
                            n = -q
                        else:
                            n = q

                        r = r + dt.timedelta(days=n)

                    elif t == _CONSTANT_WEEK:
                        if s == '-':
                            n = -q * 7
                        else:
                            n = q * 7

                        r = r + dt.timedelta(days=n)

                    elif t == _CONSTANT_MONTH:

                        r_ = r

                        if s == '-':
                            n = -1
                        else:
                            n = +1

                        def _next_month(d, inc):
                            year = d.year
                            month = 1
                            if inc > 0:
                                if d.month < 12:
                                    month = d.month + inc

                                elif d.month == 12:
                                    month = 1
                                    year += 1
                            else:
                                if d.month > 1:
                                    month = d.month + inc

                                else:
                                    month = 12
                                    year -= 1

                            return dt.date(year, month, 1)

                        i = 0
                        while abs(i) != q:
                            next_month = _next_month(r_, n)

                            if cons == _CONSTANT_DATE_END_MONTH:
                                day = (_next_month(next_month, 1) - dt.timedelta(days=1)).day

                            else:
                                day = r.day

                            r_ = dt.date(next_month.year, next_month.month, day)

                            i += n

                        r = r_

                    elif t == _CONSTANT_YEAR:
                        if s == '-':
                            n = -q

                        else:
                            n = +q

                        r = dt.date(r.year + n, r.month, r.day)

                return r.strftime('%Y-%m-%d')

            else:
                return m.group(0)

        return re.sub(r'\{\s*(\w+)(\s+([\+\-])\s*(\d+)\s*(\w?))?\s*}', _sub, termino)

    def _get_date(self, s):
        if self.strtodatef:
            try:
                return self.strtodatef(s).strftime('%Y-%m-%d')
            except:
                s_ = self.process_date_constants(s)
                if s != s_:
                    return s_

                return None
        else:
            try:
                return dt.datetime.strptime(s, '%d/%m/%Y').strftime('%Y-%m-%d')
            except ValueError:
                s_ = self.process_date_constants(s)
                if s != s_:
                    return s_

                return None

    def _get_time(self, s):
        m_time = re.search(r'^\d{1,2}:\d{1,2}(:\d{1,2})?$', s)
        if m_time:
            return s

    def _get_datetime(self, s):
        m_datetime = re.search(r'^\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{1,2}(:\d{1,2})?$', s)
        if m_datetime:
            fmt = '%d/%m/%Y %H:%M'
            if m_datetime.group(1):
                fmt += ':%S'

            try:
                return dt.datetime.strptime(s, fmt).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None

    def _get_number(self, s):
        m_number = re.search(r'^\d+(\.\d+)?$', s)
        if m_number:
            return s

    def process(self, s):

        filters = []
        order_by = []
        terminos = re.findall(r'(!|#|\+|\-)?(\w[\w\s]+\w?|\w)\s*(<>|<=|>=|==|!=|=|<|>)?\s*("[^"]+"|\d+\.\d+|\d+|\w[\w\s]+\w?)?,?', s)
        for termino in terminos:
            operator0 = termino[0]
            field     = termino[1].strip()
            operator  = termino[2].strip()

            # remove " at the begining and the end
            operand = termino[3]
            m_operand = re.search(r'^"([^"]+)"$', operand)
            if m_operand:
                operand = m_operand.group(1)

            c = None
            if operator == '' and operator0 == '':
                for operand in field.split():
                    # buscar en cada columna por el término correspondiente
                    filters_ = []
                    for col in self.tabla.columns:
                        col_name = col.name.encode('utf-8')

                        if col_name == 'id' or col_name.startswith('id_'):
                            continue

                        filter_ = []
                        if isinstance(col.type, DATE) or isinstance(col.type, TIME) or isinstance(col.type, DATETIME):
                            filter_.append('"{0}" IS NOT NULL'.format(col_name))

                        elif isinstance(col.type, INTEGER) or isinstance(col.type, NUMERIC) or isinstance(col.type, BIGINT):
                            filter_.append('"{0}" IS NOT NULL'.format(col_name))

                        else:
                            filter_.append('COALESCE(CAST("{0}" as Text), \'\') != \'\''.format(col_name))

                        args_ = (col_name, self.no_accents(operand))
                        filter_.append("UPPER(CAST(\"{0}\" as Text)) SIMILAR TO UPPER('%{1}%')".format(*args_))

                        filters_.append('({0})'.format(' AND '.join(filter_)))

                    filters.append('({0})'.format('\nOR '.join(filters_)))

            else:
                c = self.get_col(field)

            if not c:
                continue

            col = self.tabla.columns[c]

            if operator0 == '#':
                # DATE, TIME, DATETIME
                if isinstance(col.type, DATE) or isinstance(col.type, TIME) or isinstance(col.type, DATETIME):
                    filters.append('"{0}" IS NOT NULL'.format(c.encode('utf-8')))

                # INTEGER, NUMERIC, BIGINT
                elif isinstance(col.type, INTEGER) or isinstance(col.type, NUMERIC) or isinstance(col.type, BIGINT):
                    filters.append('"{0}" IS NOT NULL'.format(c.encode('utf-8')))

                # BOOLEAN
                elif isinstance(col.type, BOOLEAN):
                    filters.append('"{0}" = TRUE'.format(c.encode('utf-8')))

                else:
                    filters.append('TRIM(COALESCE(CAST("{0}" as Text), \'\')) != \'\''.format(c.encode('utf-8')))

            elif operator0 == '!':
                # DATE, TIME, DATETIME
                if isinstance(col.type, DATE) or isinstance(col.type, TIME) or isinstance(col.type, DATETIME):
                    filters.append('"{0}" IS NULL'.format(c.encode('utf-8')))

                # INTEGER, NUMERIC, BIGINT
                elif isinstance(col.type, INTEGER) or isinstance(col.type, NUMERIC) or isinstance(col.type, BIGINT):
                    filters.append('"{0}" IS NULL'.format(c.encode('utf-8')))

                # BOOLEAN
                elif isinstance(col.type, BOOLEAN):
                    filters.append('"{0}" = FALSE'.format(c.encode('utf-8')))

                else:
                    filters.append('TRIM(COALESCE(CAST("{0}" as Text), \'\')) = \'\''.format(c.encode('utf-8')))

            # ORDER BY: ASC
            elif operator0 == '+':
                order_by.append('"{0}" ASC'.format(c.encode('utf-8')))

            # ORDER BY: DESC
            elif operator0 == '-':
                order_by.append('"{0}" DESC'.format(c.encode('utf-8')))

            elif operator != '':
                # operator = <, >, <=, >=, =, <>, ==, !=

                # CONTAIN (=)
                if operator == '=':
                    # DATE
                    if isinstance(col.type, DATE):
                        operand_ = self._get_date(operand)
                        if operand_:
                            filters.append('"{0}" = \'{1}\''.format(c.encode('utf-8'), operand_))

                    # TIME
                    elif isinstance(col.type, TIME):
                        operand_ = self._get_time(operand)
                        if operand_:
                            filters.append('"{0}" = \'{1}\''.format(c.encode('utf-8'), operand_))

                    # DATETIME
                    elif isinstance(col.type, DATETIME):
                        operand_ = self._get_datetime(operand)
                        if operand_:
                            filters.append('"{0}" = \'{1}\''.format(c.encode('utf-8'), operand_))

                    # INTEGER, NUMERIC, BIGINT
                    elif isinstance(col.type, INTEGER) or isinstance(col.type, NUMERIC) or isinstance(col.type, BIGINT):
                        operand_ = self._get_number(operand)
                        if operand_:
                            filters.append('"{0}" = {1}'.format(c.encode('utf-8'), operand))

                    else:
                        args_ = (c.encode('utf-8'), self.no_accents(operand))
                        filters.append("UPPER(CAST(\"{0}\" as Text)) SIMILAR TO UPPER('%{1}%')".format(*args_))

                # NOT CONTAIN (<>)
                elif operator == '<>':
                    # DATE
                    if isinstance(col.type, DATE):
                        operand_ = self._get_date(operand)
                        if operand_:
                            filters.append('"{0}" != \'{1}\''.format(c.encode('utf-8'), operand_))

                    # TIME
                    elif isinstance(col.type, TIME):
                        operand_ = self._get_time(operand)
                        if operand_:
                            filters.append('"{0}" != \'{1}\''.format(c.encode('utf-8'), operand_))

                    # DATETIME
                    elif isinstance(col.type, DATETIME):
                        operand_ = self._get_datetime(operand)
                        if operand_:
                            filters.append('"{0}" != \'{1}\''.format(c.encode('utf-8'), operand_))

                    # INTEGER, NUMERIC, BIGINT
                    elif isinstance(col.type, INTEGER) or isinstance(col.type, NUMERIC) or isinstance(col.type, BIGINT):
                        operand_ = self._get_number(operand)
                        if operand_:
                            filters.append('"{0}" != {1}'.format(c.encode('utf-8'), operand))

                    else:
                        args_ = (c.encode('utf-8'), self.no_accents(operand))
                        filters.append("UPPER(CAST(\"{0}\" as Text)) NOT SIMILAR TO UPPER('%{1}%')".format(*args_))

                # EQUAL TO (==)
                elif operator == '==':
                    # DATE
                    if isinstance(col.type, DATE):
                        operand_ = self._get_date(operand)
                        if operand_:
                            filters.append('"{0}" = \'{1}\''.format(c.encode('utf-8'), operand_))

                    # TIME
                    elif isinstance(col.type, TIME):
                        operand_ = self._get_time(operand)
                        if operand_:
                            filters.append('"{0}" = \'{1}\''.format(c.encode('utf-8'), operand_))

                    # DATETIME
                    elif isinstance(col.type, DATETIME):
                        operand_ = self._get_datetime(operand)
                        if operand_:
                            filters.append('"{0}" = \'{1}\''.format(c.encode('utf-8'), operand_))

                    # INTEGER, NUMERIC, BIGINT
                    elif isinstance(col.type, INTEGER) or isinstance(col.type, NUMERIC) or isinstance(col.type, BIGINT):
                        operand_ = self._get_number(operand)
                        if operand_:
                            filters.append('"{0}" = {1}'.format(c.encode('utf-8'), operand))

                    else:
                        args_ = (c.encode('utf-8'), operand)
                        filters.append('UPPER(TRIM(COALESCE(CAST("{0}" as Text), \'\'))) = UPPER(\'{1}\')'.format(*args_))

                # NOT EQUAL TO (!=)
                elif operator == '!=':
                    # DATE
                    if isinstance(col.type, DATE):
                        operand_ = self._get_date(operand)
                        if operand_:
                            filters.append('"{0}" != \'{1}\''.format(c.encode('utf-8'), operand_))

                    # TIME
                    elif isinstance(col.type, TIME):
                        operand_ = self._get_time(operand)
                        if operand_:
                            filters.append('"{0}" != \'{1}\''.format(c.encode('utf-8'), operand_))

                    # DATETIME
                    elif isinstance(col.type, DATETIME):
                        operand_ = self._get_datetime(operand)
                        if operand_:
                            filters.append('"{0}" != \'{1}\''.format(c.encode('utf-8'), operand_))

                    # INTEGER, NUMERIC, BIGINT
                    elif isinstance(col.type, INTEGER) or isinstance(col.type, NUMERIC) or isinstance(col.type, BIGINT):
                        operand_ = self._get_number(operand)
                        if operand_:
                            filters.append('"{0}" != {1}'.format(c.encode('utf-8'), operand))

                    else:
                        args_ = (c.encode('utf-8'), operand)
                        filters.append('UPPER(TRIM(COALESCE(CAST("{0}" as Text), \'\'))) != UPPER(\'{1}\')'.format(*args_))

                # LESS THAN (<), LESS THAN OR EQUAL TO (<=), GREATER THAN (>), GREATER THAN OR EQUAL TO (>=)
                elif operator in ['<', '<=', '>', '>=']:
                    # DATE
                    if isinstance(col.type, DATE):
                        operand_ = self._get_date(operand)
                        if operand_:
                            filters.append('"{0}" {1} \'{2}\''.format(c.encode('utf-8'), operator, operand_))

                    # TIME
                    elif isinstance(col.type, TIME):
                        operand_ = self._get_time(operand)
                        if operand_:
                            filters.append('"{0}" {1} \'{2}\''.format(c.encode('utf-8'), operator, operand_))

                    # DATETIME
                    elif isinstance(col.type, DATETIME):
                        operand_ = self._get_datetime(operand)
                        if operand_:
                            filters.append('"{0}" {1} \'{2}\''.format(c.encode('utf-8'), operator, operand_))

                    elif isinstance(col.type, INTEGER) or isinstance(col.type, NUMERIC) or isinstance(col.type, BIGINT):
                        operand_ = self._get_number(operand)
                        if operand_:
                            filters.append('"{0}" {1} \'{2}\''.format(c.encode('utf-8'), operator, operand))

        filters_sql = None
        if len(filters) > 0:
            filters_sql = ('\nAND '.join(filters)).decode('utf-8')

        order_by_sql = None
        if len(order_by) > 0:
            order_by_sql = (', '.join(order_by)).decode('utf-8')

        return filters_sql, order_by_sql


class Search(object):

    def __init__(self, session, table_name, strtodatef=None):
        self.session = session
        self.table_name = table_name

        self.meta = MetaData(bind=self.session.bind)
        self.strtodatef = strtodatef
        self.sql = None
        self.order = ''

        if isinstance(self.table_name, Select):
            self.tbl = self.table_name

        else:
            self.tbl = Table(self.table_name, self.meta, autoload=True)

        self.from_ = self.tbl

    def apply_qry(self, q):

        if q:
            if isinstance(q, unicode):
                q = q.encode('utf-8')

            # process "q"
            qres = Busqueda(self.tbl, strtodatef=self.strtodatef)
            filters_sql, order_sql = qres.process(q)

            # apply search conditions
            self.sql = and_(filters_sql, self.sql)

            # apply order
            if order_sql:
                self.order = order_sql

    def and_(self, *cond):
        self.sql = and_(self.sql, *cond)

    def or_(self, cond):
        self.sql = or_(self.sql, cond)

    def join(self, *args, **kwargs):
        self.from_ = self.from_.join(*args, **kwargs)

    def outerjoin(self, *args, **kwargs):
        self.from_ = self.from_.outerjoin(*args, **kwargs)

    def apply_filters(self, filters):

        tbl = self.tbl

        # apply filters
        if filters:
            filters_tuple = (self.sql,)
            for f in filters:
                if len(f) > 2:
                    # (<field name>, <field value>, <operator>,)
                    # different
                    if f[2] == '!=':
                        filters_tuple += (tbl.c[f[0]] != f[1],)

                    # greater
                    elif f[2] == '>':
                        filters_tuple += (tbl.c[f[0]] > f[1],)

                    # greater or equal
                    elif f[2] == '>=':
                        filters_tuple += (tbl.c[f[0]] >= f[1],)

                    # less
                    elif f[2] == '<':
                        filters_tuple += (tbl.c[f[0]] < f[1],)

                    # less or equal
                    elif f[2] == '<=':
                        filters_tuple += (tbl.c[f[0]] <= f[1],)

                    # equal (and anything else...)
                    else:
                        filters_tuple += (tbl.c[f[0]] == f[1],)

                elif len(f) == 2:
                    # (<field name>, <field value>,)
                    # equal (by default)
                    filters_tuple += (tbl.c[f[0]] == f[1],)

                elif len(f) == 1:
                    filters_tuple += (f[0],)

            self.sql = and_(*filters_tuple)

    def __call__(self, rp=100, offset=0, collection=None, no_count=False, show_ids=False):
        """
        IN
          rp          <int>
          offset      <int>
          filters     [<tuple>, ...]
          collecion   <tuple> (<str>, <str>, <int>,)
          no_count    <bool> => False
          show_ids    <bool> => False

        OUT
          <DataSet>
        """

        sql = self.sql
        if collection:

            child_table_name = collection[0]
            child_attr = collection[1]
            parent_id = collection[2]

            child_attr_alias = '{0}$'.format(child_attr)
            if child_attr_alias in self.tbl.c:
                sql = and_(sql, self.tbl.c[child_attr_alias] == parent_id)

            else:
                child_table = alias(Table(child_table_name, self.meta, autoload=True))

                self.from_ = self.from_.\
                    join(child_table,
                         and_(child_table.c.id == self.tbl.c.id,
                              child_table.c[child_attr] == parent_id))

        # where
        if isinstance(self.tbl, Select):
            qry = self.tbl.where(sql)

        else:
            qry = select([self.tbl], from_obj=self.from_, whereclause=sql)

        # order by
        if self.order:
            qry = qry.order_by(self.order)

        return DataSet.procesar_resultado(self.session, qry, rp, offset, no_count=no_count, show_ids=show_ids)
