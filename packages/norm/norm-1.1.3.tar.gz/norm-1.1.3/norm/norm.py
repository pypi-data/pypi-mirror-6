from __future__ import unicode_literals

QUERY_TYPE = b'qt'
COLUMN = b'c'
FROM = b'f'
WHERE = b'w'
HAVING = b'h'
GROUP_BY = b'gb'
ORDER_BY = b'ob'
LIMIT = b'l'
OFFSET = b'os'
EXTRA = b'ex'
TABLE = b't'
SET = b's'
RETURNING = b'r'

SELECT_QT = b's'
UPDATE_QT = b'u'
DELETE_QT = b'd'
INSERT_QT = b'i'

SEP = '\n       '
COLUMN_SEP = ',' + SEP
INSERT_COLUMNS_SEP = ',\n   '
INSERT_VALUES_SEP = ',\n          '


class BogusQuery(Exception):
    pass


def compile(chain, query_type):
    table = None
    columns = []
    from_ = []
    where = []
    having = None
    group_by = None
    order_by = None
    limit = None
    offset = None
    set_ = []
    extra = []
    returning = []

    for op, option in chain:
        if op == COLUMN:
            columns.append(option)
        elif op == WHERE:
            where.append(option)
        elif op == FROM:
            expr, join, op, criteria = option
            if not join:
                if from_:
                    from_[-1] += ','
                from_.append(expr)
            else:
                from_[-1] += '\n  ' + join + ' ' + expr
                if op is not None:
                    from_[-1] += '\n       ' + op + ' ' + criteria
        elif op == TABLE:
            table = option
        elif op == SET:
            set_.append(option)
        elif op == GROUP_BY:
            group_by = option
        elif op == ORDER_BY:
            order_by = option
        elif op == LIMIT:
            limit = option
        elif op == OFFSET:
            offset = option
        elif op == HAVING:
            having = option
        elif op == EXTRA:
            extra.append(option)
        elif op == RETURNING:
            returning.append(option)
        else:
            raise BogusQuery('There was a fatal error compiling query.')

    query = ''
    if query_type == SELECT_QT:
        query += 'SELECT ' + COLUMN_SEP.join(columns)
        if from_:
            query += '\n  FROM ' + SEP.join(from_)
        if where:
            query += '\n WHERE ' + (' AND' + SEP).join(where)
        if group_by is not None:
            query += '\nGROUP BY ' + group_by
        if having is not None:
            query += '\nHAVING ' + having
        if order_by is not None:
            query += '\nORDER BY ' + order_by
        if limit is not None:
            query += '\n LIMIT ' + limit
        if offset is not None:
            query += '\nOFFSET ' + offset
        if extra:
            query += '\n'.join(extra)
    elif query_type == UPDATE_QT:
        query += 'UPDATE ' + table
        if set_:
            query += '\n   SET ' + (',' + SEP).join(set_)
        if from_:
            query += '\n  FROM ' + SEP.join(from_)
        if where:
            query += '\n WHERE ' + (' AND' + SEP).join(where)
        if extra:
            query += '\n'.join(extra)
        if returning:
            query += '\nRETURNING ' + ', '.join(returning)
    elif query_type == DELETE_QT:
        query += 'DELETE FROM ' + table
        if from_:
            query += '\n  FROM ' + SEP.join(from_)
        if where:
            query += '\n WHERE ' + (' AND' + SEP).join(where)
        if returning:
            query += '\nRETURNING ' + ', '.join(returning)

    query += ';'
    return query


class Query(object):
    query_type = None
    bind_prefix = '%('
    bind_postfix = ')s'

    def __init__(self):
        self.parent = None
        self.chain = []
        self._binds = {}
        self._query = None

    @classmethod
    def bnd(cls, s):
        return "%s%s%s" % (cls.bind_prefix, s, cls.bind_postfix)

    @property
    def binds(self):
        binds = {}
        if self.parent is not None:
            binds.update(self.parent.binds)
        binds.update(self._binds)

        return binds

    def bind(self, **binds):
        s = self.child()
        s._binds.update(binds)
        return s

    def child(self):
        s = self.__class__()
        s.parent = self
        return s

    def build_chain(self):
        parent_chain = self.parent.build_chain() if self.parent else []
        return parent_chain + self.chain

    @property
    def query(self):
        if self._query is None:
            self._query = compile(self.build_chain(), self.query_type)
        return self._query


class _SELECT_UPDATE(Query):
    def WHERE(self, *args, **kw):
        # TODO: handle OR
        s = self.child()
        for stmt in args:
            s.chain.append((WHERE, stmt))
        for column_name, value in kw.iteritems():
            column_name = unicode(column_name)
            bind_val_name = '%s_bind_%s' % (column_name, len(self.binds))
            self._binds[bind_val_name] = value
            expr = column_name + ' = ' + self.bnd(bind_val_name)
            s.chain.append((WHERE, expr))
        return s

    def FROM(self, *args):
        s = self.child()
        for stmt in args:
            s.chain.append((FROM, (stmt, False, None, None)))
        return s

    def JOIN(self, stmt, ON=None, USING=None, outer=False):
        if outer:
            keyword = 'LEFT JOIN'
        else:
            keyword = 'JOIN'
        if ON is not None and USING is not None:
            raise BogusQuery("You can't specify both ON and USING.")
        elif ON is not None:
            op = 'ON'
            criteria = ON
        elif USING is not None:
            op = 'USING'
            criteria = USING
        else:
            raise BogusQuery('No join criteria specified.')

        s = self.child()
        s.chain.append((FROM, (stmt, keyword, op, criteria)))
        return s

    def LEFTJOIN(self, *args, **kw):
        return self.JOIN(*args, outer=True, **kw)

    def RETURNING(self, *args):
        s = self.child()
        for arg in args:
            self.chain.append((RETURNING, arg))
        return s


class SELECT(_SELECT_UPDATE):
    query_type = SELECT_QT

    def __init__(self, *args):
        _SELECT_UPDATE.__init__(self)

        for stmt in args:
            self.chain.append((COLUMN, stmt))

    def SELECT(self, *args):
        s = self.child()
        for stmt in args:
            s.chain.append((COLUMN, stmt))
        return s

    def HAVING(self, stmt):
        s = self.child()
        s.chain.append((HAVING, stmt))
        return s

    def ORDER_BY(self, stmt):
        s = self.child()
        s.chain.append((ORDER_BY, stmt))
        return s

    def GROUP_BY(self, stmt):
        s = self.child()
        s.chain.append((GROUP_BY, stmt))
        return s

    def LIMIT(self, stmt):
        if isinstance(stmt, (int, long)):
            stmt = unicode(stmt)
        s = self.child()
        s.chain.append((LIMIT, stmt))
        return s

    def OFFSET(self, stmt):
        if isinstance(stmt, (int, long)):
            stmt = unicode(stmt)
        s = self.child()
        s.chain.append((OFFSET, stmt))
        return s


class UPDATE(_SELECT_UPDATE):
    query_type = UPDATE_QT

    def __init__(self, table=None):
        super(UPDATE, self).__init__()

        if table is not None:
            self.chain.append((TABLE, table))

    def SET(self, *args, **kw):
        s = self.child()
        for stmt in args:
            self.chain.append((SET, stmt))

        for column_name, value in kw.iteritems():
            bind_name = column_name + '_bind'
            self._binds[bind_name] = value
            expr = unicode(column_name) + ' = ' + self.bnd(bind_name)
            s.chain.append((SET, expr))
        return s

    def EXTRA(self, *args):
        pass


class DELETE(_SELECT_UPDATE):
    query_type = DELETE_QT

    def __init__(self, table=None):
        super(DELETE, self).__init__()

        if table is not None:
            self.chain.append((TABLE, table))


class _default(object):
    pass


class INSERT(object):
    bind_prefix = '%('
    bind_postfix = ')s'
    defaultdefault = None

    def __init__(self,
                 table,
                 data=None,
                 columns=None,
                 default=_default,
                 returning=None):
        self.table = table
        self.data = data
        self._columns = columns
        if default is _default:
            self.default = self.defaultdefault
        else:
            self.default = default
        self.returning = returning

    @classmethod
    def bnd(cls, s):
        return "%s%s%s" % (cls.bind_prefix, s, cls.bind_postfix)

    @property
    def binds(self):
        binds = {}
        if self.data is None:
            return binds

        if self.multi_data:
            data = self.data
        else:
            data = [self.data]

        for index, d in enumerate(data):
            for col_name in self.columns:
                key = col_name + '_' + str(index)
                if col_name in d:
                    binds[key] = d[col_name]
                else:
                    binds[key] = self.default

        return binds

    @property
    def multi_data(self):
        if hasattr(self.data, 'iterkeys'):
            return False
        return True

    @property
    def columns(self):
        if self._columns is None:
            if self.data is None:
                return None
            if not self.multi_data:
                return sorted([key for key in self.data])
            else:
                columns = set()
                for d in self.data:
                    columns |= set(d)
                self._columns = sorted(columns)
        return self._columns

    @property
    def query(self):
        if self.multi_data:
            return self._query(self.data)
        else:
            return self._query([self.data])

    def _query(self, data):
        q = 'INSERT INTO %s ' % self.table

        if self.columns:
            q += '('
            q += ', '.join(col_name for col_name in self.columns)
            q += ') VALUES '

        if self.data is None:
            q += ' DEFAULT VALUES'
        else:
            for index, d in enumerate(data):
                if index > 0:
                    q += ',\n       '

                q += '('
                q += ', '.join(self.bnd(col_name + '_' + str(index))
                               for col_name in self.columns)
                q += ')'

        if self.returning:
            if isinstance(self.returning, basestring):
                returning = [self.returning]
            else:
                returning = self.returning
            q += '\nRETURNING ' + ', '.join(returning)
        q += ';'

        return q
