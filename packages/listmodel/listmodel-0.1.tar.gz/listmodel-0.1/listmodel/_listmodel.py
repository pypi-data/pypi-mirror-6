import json
import types

from requests import Request, Session


class Role(object):
    def __init__(self, arg1=None, arg2=None):
        self._cache = {}

        if type(arg1) is types.FunctionType:
            self.path = None
            self.fget = arg1
        else:
            self.path = arg1
            self.fget = arg2

    def __get__(self, obj, objtype):
        id_ = id(obj)

        if id_ not in self._cache:
            self._cache[id_] = self._get_val(obj)

        return self._cache[id_]

    def __get__(self, obj, objtype):
        val = None

        if self.path is not None:
            val = self.query(obj, self.path)

        if self.fget is not None:
            val = self.fget(obj, val)

        return val

    def __call__(self, fget=None):
        self.fget = fget
        return self

    def query(self, obj, path):
        pass


class ContextMeta(type):
    def __new__(cls, name, bases, dct):
        roles = [name_ for name_, value in dct.iteritems()
                 if isinstance(value, Role)]
        dct['_roles'] = roles
        return type.__new__(cls, name, bases, dct)


class ContextHolder(object):
    __metaclass__ = ContextMeta

    def __init__(self, context):
        self.set_context(context)

    def set_context(self, content):
        self.context = content

    def __repr__(self):
        fields = ', '.join(self._get_rows_repr())
        return '<%s (%s)>' % (self.__class__.__name__, fields)

    def __str__(self):
        spacer = '\n' + ' ' * 4
        fields = (',' + spacer).join(self._get_rows_repr())
        return '<%s (%s%s)>' % (self.__class__.__name__, spacer, fields)

    def _get_rows_repr(self):
        return ['%s=%r' % (role, getattr(self, role))
                for role in self._roles]

    def dict(self):
        return {role: getattr(self, role) for role in self._roles}

    def json(self):
        return json.dumps(self.dict())


class ListModel(ContextHolder):
    def __init__(self, content, session=Session()):
        self._rows = []
        self._next_row = 0

        if isinstance(content, Request):
            content = self.get_http(content, session)

        self.set_context(content)

    def get_http(self, req, session):
        request = session.prepare_request(req)
        resp = session.send(request)
        resp.raise_for_status()

        return resp.content

    def __iter__(self):
        return self

    def next(self):
        try:
            row = self._rows[self._next_row]
        except IndexError:
            raise StopIteration
        else:
            self._next_row += 1
            return self.__rowcls__(context=row)

    def __len__(self):
        return len(self._rows)

    def __getitem__(self, i):
        return self.__rowcls__(context=self._rows[i])

    def saverows(self):
        for count, row in enumerate(self._rows, start=1):
            self.__rowcls__(context=row).save()
        return count


class Row(ContextHolder):
    pass
