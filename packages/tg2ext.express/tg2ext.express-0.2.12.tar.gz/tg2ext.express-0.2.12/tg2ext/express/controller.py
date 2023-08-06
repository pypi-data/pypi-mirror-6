# -*- coding: utf-8 -*-
import types
import logging
from sqlalchemy.orm.query import Query
from sqlalchemy import Column, Integer, SmallInteger, BigInteger
from sqlalchemy import String, Unicode
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.orm import joinedload, subqueryload
from sqlalchemy.sql import expression
from sqlalchemy import exc as sa_exc
import tg
from tg import RestController, expose, request, response
from tg.predicates import NotAuthorizedError, not_anonymous

from tg import predicates
from .exceptions import *

logger = logging.getLogger('tg2ext.express')


#######################################################################################################################
def revert_list_of_qs(qs):
    """revert_list_of_qs, process the result of escape.parse_qs_bytes which convert the item values if the type is list
    and has only one element to it's first element. Otherwize, keep the original value.
    """
    if not isinstance(qs, dict):
        return
    for k, v in qs.items():
        if isinstance(v, list) and len(v) == 1 and isinstance(v[0], (str, unicode)):
            qs[k] = v[0]


def make_pk_regex(pk_clmns):
    """make_pk_regex generate a tuple of (fieldname, regex_pattern) according to the giving primary key fields of table.
    Only the integer and string field are supported, return None if no primary key field of it's not type of integer or
    string. Function only takes the first pk if there're more than one primary key fields.
    """
    if isinstance(pk_clmns, Column):
        if isinstance(pk_clmns.type, (Integer, BigInteger, SmallInteger)):
            return pk_clmns.name, r'(?P<%s>[0-9]+)' % pk_clmns.name
        elif isinstance(pk_clmns.type, (String, Unicode)):
            return pk_clmns.name, r'(?P<%s>[0-9A-Za-z_-]+)' % pk_clmns.name
        else:
            return None  # , None
    elif isinstance(pk_clmns, (list, tuple)):
        return make_pk_regex(pk_clmns[0])
    else:
        return None  # , None


def str2list(s):
    if not s:
        return []
    if isinstance(s, (list, tuple)):
        ss = list()
        for x in s:
            r = str2list(x)
            if r:
                ss.extend(r)
        return ss
    elif isinstance(s, (str, unicode)):
        return s.split(',')


def str2int(s):
    if s is None:
        return None
    else:
        return int(s)


QUERY_LOOKUPS = ('not', 'contains', 'startswith', 'endswith', 'in', 'range', 'lt', 'lte', 'gt', 'gte',
                 'year', 'month', 'day', 'hour', 'minute', 'dow', )


def build_filter(model, key, value, joins=None):
    logger.debug('build_filter>>> %s | %s | %s | %s', model, key, value, joins)
    if not key:
        raise InvalidExpression(message='Invalid Expression!')  # return None, None

    def _encode_(k, v):
        f = model.__handler__._get_encoder(k) if hasattr(model, '__handler__') else None
        if f is None:
            return v
        else:
            return f(v)

    k1 = key.pop(0)  # Get the first part of key
    kk = k1.split('__')
    kk1 = kk.pop(0)
    if kk1 in model.__table__.c.keys():  # Check if this is a field
        field = getattr(model, kk1)
        if not kk:
            return field == _encode_(kk1, value), joins
        else:
            _not_ = False
            if 'not' in kk:
                _not_ = True
                kk.remove('not')
            if not kk:
                return (~(field == _encode_(kk1, value)) if _not_ else (field == _encode_(kk1, value))), joins
            op = kk.pop(0)
            if 'contains' == op and not kk:
                exp = field.like(u'%%%s%%' % _encode_(kk1, value))
            elif 'startswith' == op and not kk:
                exp = field.like(u'%s%%' % _encode_(kk1, value))
            elif 'endswith' == op and not kk:
                exp = field.like(u'%%%s' % _encode_(kk1, value))
            elif 'in' == op and not kk:
                exp = field.in_(map(lambda x: _encode_(kk1, x),
                                    value if isinstance(value, (list, tuple)) else str2list(value)))
            elif 'range' == op and not kk:
                value = map(lambda x: _encode_(kk1, x), value if isinstance(value, (list, tuple)) else str2list(value))
                if len(value) != 2:
                    raise InvalidExpression(message='Invalid Expression!')  # return None, None
                exp = and_(field >= _encode_(kk1, value[0]), field <= _encode_(kk1, value[1]))
            elif 'lt' == op and not kk:
                exp = field < _encode_(kk1, value)
            elif 'lte' == op and not kk:
                exp = field <= _encode_(kk1, value)
            elif 'gt' == op and not kk:
                exp = field > _encode_(kk1, value)
            elif 'gte' == op and not kk:
                exp = field >= _encode_(kk1, value)
            elif op in ('year', 'month', 'day', 'hour', 'minute', 'dow'):
                # This needs the RMDBs support the EXTRACT function for DATETIME field.
                if not kk:
                    exp = expression.extract(op.upper(), field) == int(value)
                elif len(kk) == 1:
                    exop = kk[0]
                    if exop == 'lt':
                        exp = expression.extract(op.upper(), field) < int(value)
                    elif exop == 'lte':
                        exp = expression.extract(op.upper(), field) <= int(value)
                    elif exop == 'gt':
                        exp = expression.extract(op.upper(), field) > int(value)
                    elif exop == 'gte':
                        exp = expression.extract(op.upper(), field) >= int(value)
                    elif exop == 'in':
                        exp = expression.extract(op.upper(), field).in_(map(lambda x: int(x),
                                                                            value if isinstance(value, (list, tuple))
                                                                            else str2list(value)))
                    elif exop == 'range':
                        value = map(lambda x: int(x), value if isinstance(value, (list, tuple)) else str2list(value))
                        if len(value) != 2:
                            raise InvalidExpression(message='Invalid Expression!')  # return None, None
                        exp = and_(expression.extract(op.upper(), field) >= int(value[0]),
                                   expression.extract(op.upper(), field) <= int(value[1]))
                    else:
                        raise InvalidExpression(message='Invalid Expression!')  # return None, None
                else:
                    raise InvalidExpression(message='Invalid Expression!')  # return None, None

            else:
                raise InvalidExpression(message='Invalid Expression!')  # return None, None
            return ~exp if _not_ else exp, joins
    elif k1 in model.__mapper__.relationships.keys() and key:  # Check if this is a relationship
        logger.debug('go relationships: %s, %s', k1, joins)
        relationship = getattr(model, k1)
        if joins:
            joins.append(relationship)
        else:
            joins = [relationship]
        return build_filter(model.__mapper__.relationships[k1].mapper.class_, key, value, joins=joins)
    else:  # Check of this is
        return None, None


def build_order_by(cls, order_by):
    """build_order_by: build order by criterias with the given list order_by in strings."""

    def _gen_order_by(c, by):
        is_desc = False
        if by and by.startswith('-'):
            by = by[1:]
            is_desc = True
        if by and by in c.__table__.c.keys():
            return None, desc(getattr(c, by)) if is_desc else asc(getattr(c, by))
        else:
            return None, None

    joins = list()
    order_bys = list()
    if not order_by:
        return joins, order_bys
    for x in order_by:
        j, o = _gen_order_by(cls, x)
        if o is None:
            continue
        order_bys.append(o)
        if j:
            joins.extend(j)
    return joins, order_bys


def find_join_loads(cls, extend_fields):
    """find_join_loads: find the relationships from extend_fields which we can call joinloads for EagerLoad..."""

    def _relations_(c, exts):
        if not exts:
            return None
        ret = []
        r = exts.pop(0)
        if r in c.__mapper__.relationships.keys():
            ret.append(r)
            r1 = _relations_(c.__mapper__.relationships[r].mapper.class_, exts)
            if r1:
                ret.extend(r1)
        return ret

    if not extend_fields:
        return None
    result = list()
    for x in extend_fields:
        y = _relations_(cls, x.split('.'))
        if y:
            result.append('.'.join(y))
    return result


def query_reparse(query, internal_filters=None):
    """query_reparse: reparse the query.
    Returns controls dictionary and re-constructed query dictionary.
    """
    if not query or not isinstance(query, dict):
        return {}, {}
    new_query = {'__default': {}}
    controls = {
        'include_fields': str2list(query.pop('__include_fields', None)),
        'exclude_fields': str2list(query.pop('__exclude_fields', None)),
        'extend_fields': str2list(query.pop('__extend_fields', None)),
        'begin': str2int(query.pop('__begin', 0)),
        'limit': str2int(query.pop('__limit', None)),
        'order_by': str2list(query.pop('__order_by', None))
    }
    for k, v in query.items():
        ks = k.split('|')
        if len(ks) == 1:
            new_query['__default'][k] = v
        else:
            new_query['_'.join(ks)] = dict(zip(ks, v.split('|')))
    if internal_filters:
        new_query['__default'].update(internal_filters)
    return controls, new_query


def restruct_ext_fields(cls, extend_fields):
    def _f_(s):
        ss = s.split('.', 1)
        logger.debug('_f_: %s', ss)
        return ss[0], ss[1] if len(ss) == 2 else None

    if not extend_fields:
        return {}
    result = {}
    for x, y in map(_f_, extend_fields):
        logger.debug('[1]restruct_ext_fields> %s: %s', x, y)
        if x not in cls.__mapper__.relationships.keys():
            continue
        if x not in result:
            result[x] = [y] if y else []
        elif y:
            result[x].append(y)
    logger.debug('[2]restruct_ext_fields> %s: %s', cls, result)
    return result


def serialize_object(cls, inst, include_fields=None, extend_fields=None):
    """serialize_object: serialize a single object from model instance into a dictionary.
    """
    logger.debug('Inst: %s | %s', inst, type(inst))
    if isinstance(inst, (list, tuple, types.GeneratorType)):
        return map(lambda x: serialize_object(cls, x, include_fields=include_fields, extend_fields=extend_fields),
                   inst)
    if not isinstance(inst, cls):
        return inst
    logger.debug('serialize_object> extend_fields: %s', extend_fields)
    include_fields = include_fields or cls.__table__.c.keys()
    include_fields = list(set(include_fields) | set(cls.__table__.primary_key.columns.keys()))
    #if not set(include_fields) <= set(cls.__mapper__.c.keys()):
    #    raise BadRequest(message='Column(s) "%s" does not exists!' % ','.join(list(
    #        set(include_fields) - set(cls.__mapper__.c.keys())
    #    )))
    result = dict((k, getattr(inst, k)) for k in include_fields)
    if extend_fields:
        logger.debug('serialize_object: extend_fields=%s', extend_fields)
        for relkey, relext in restruct_ext_fields(cls, extend_fields).items():
            rinst = cls.__mapper__.relationships[relkey]
            logger.debug('====> %s: %s', relkey, relext)
            #if rinst.direction.name in ('MANYTOONE', 'ONETOONE'):
            incs = filter(lambda x: x.find('.') < 0 and x in rinst.mapper.class_.__mapper__.c.keys(), relext)
            #[relext] if (relext and relext.find('.') < 0 and relext in rinst.mapper.class_.__mapper__.c.keys()) else None
            exts = filter(lambda x: x.find('.') > 0 or x in rinst.mapper.class_.__mapper__.relationships.keys(), relext)
            #[relext] if relext and incs is None else None
            logger.debug('inc=%s, ext=%s', incs, exts)
            result[relkey] = serialize_object(rinst.mapper.class_, getattr(inst, relkey),
                                              include_fields=incs,
                                              extend_fields=exts)
    return result


def serialize_query(cls, inst, include_fields=None, extend_fields=None):
    """serialize_query: serialize a query into a list of object dictionary."""
    if not isinstance(inst, Query):
        return None
    return serialize_object(cls, inst.all(), include_fields=include_fields, extend_fields=extend_fields)


def serialize(cls, inst, include_fields=None, extend_fields=None):
    """serialize: serialize model object(s) into dictionary(s)."""
    if isinstance(inst, Query):
        inst = inst.all()
    return serialize_object(cls, inst, include_fields=include_fields, extend_fields=extend_fields)


def exception_wapper(f):
    def wrapper_f(self, *args, **kwargs):
        try:
            result = f(self, *args, **kwargs)
        except sa_exc.IntegrityError, e:
            logger.exception(e)
            self._dbsession_.rollback()
            raise InvalidData(detail=str(e))
        except sa_exc.SQLAlchemyError, e:
            logger.exception(e)
            self._dbsession_.rollback()
            raise FatalError(detail=str(e))
        except ExpressError, e:
            logger.exception(e)
            self._dbsession_.rollback()
            raise e
        except Exception, e:
            logger.exception(e)
            self._dbsession_.rollback()
            raise FatalError(detail=str(e))
        else:
            return result

    return wrapper_f


class ExpressController(RestController):
    """
    ExpressController, a base controller class for expose models via RestController with minimum coding.

    args_params: params via Query in dict.
    """
    _model_ = None  # When define an ExpressController, a sqlalchemy model class should be given via _model_
    _readonly_fields_ = None
    _subcontrollers_ = None
    _internal_filters_ = None
    _permissions_ = None

    def __init__(self,
                 model=None,
                 dbsession=None,
                 allow_only=None,
                 permissions=None,
                 readonly=None,
                 subcontrollers=None,
                 extra_attrs=None,
                 **kwargs):
        if model is not None:
            self._model_ = model
        self._dbsession_ = dbsession
        if self._model_ is None:
            raise Exception('"_model_" can not be None, must be a valid model class of sqlalchemy!')
        self._columns_ = self._model_.__table__.c.keys()
        if extra_attrs is not None:
            extra_attrs = extra_attrs if isinstance(extra_attrs, (list, tuple)) else extra_attrs.split(',')
            self._columns_.extend(extra_attrs)
        if self._dbsession_ is None:
            raise Exception("A valid db session is required!")
        if allow_only is not None:
            self.allow_only = allow_only
        if isinstance(readonly, bool):
            self._table_readonly_ = readonly
            self._readonly_fields_ = None
        elif isinstance(readonly, (str, unicode, list, tuple)):
            readonly = readonly.split(',') if isinstance(readonly, (str, unicode)) else readonly
            if readonly is not None:
                self._readonly_fields_ = readonly
            self._table_readonly_ = False
        elif readonly is None:
            self._table_readonly_ = False
            self._readonly_fields_ = None
        else:
            raise Exception('Invalid value of readonly(%s)' % readonly)
        if permissions is not None:
            self._permissions_ = permissions
        if subcontrollers is not None:
            self._subcontrollers_ = subcontrollers
        if kwargs:
            self._internal_filters_ = kwargs

    def _lookup(self, pk=None, extra=None, *reminders):
        logger.debug('_lookup: pk=%s, extra=%s, reminders=%s', pk, extra, reminders)
        ## How to lookup ?
        ## ${pk}/${extra}
        ##
        if pk is None:
            pass
        elif extra is not None:
            pass
        else:
            pass

    def _before(self, *args, **kw):
        logger.debug('[%s]_before>>>>>: args=%s, %s', self.__class__.__name__, args, kw)
        #super(ExpressController, self)._before(*args, **kw)

    def _after(self, *args, **kw):
        logger.debug('[%s]_after>>>>>: args=%s, %s', self.__class__.__name__, args, kw)
        #super(ExpressController, self)._after(*args, **kw)

    ####################################################################################################################
    def _before_read(self, pk=None, query=None, **kwargs):
        logger.debug('[%s]_before_read> pk=%s, query=%s',
                     self.__class__.__name__, pk, query)

    def _before_update(self, inst, arguments, **kwargs):
        logger.debug('[%s]_before_update> inst=%s, arguments=%s',
                     self.__class__.__name__,
                     inst, arguments)

    def _before_create(self, objects, **kwargs):
        logger.debug('[%s]_before_create> objects=%s',
                     self.__class__.__name__,
                     objects)

    def _before_delete(self, inst, **kwargs):
        logger.debug('[%s]_before_delete> inst=%s',
                     self.__class__.__name__,
                     inst)

    def _after_read(self, inst, **kwargs):
        logger.debug('[%s]_after_read> inst=%s',
                     self.__class__.__name__, inst)

    def _after_update(self, inst, **kwargs):
        logger.debug('[%s]_after_update> inst=%s',
                     self.__class__.__name__, inst)

    def _after_create(self, objects, **kwargs):
        logger.debug('[%s]_after_create> objects=%s',
                     self.__class__.__name__,
                     objects)

    def _after_delete(self, deletes, **kwargs):
        logger.debug('[%s]_after_delete> deletes=%s',
                     self.__class__.__name__, deletes)

    ####################################################################################################################

    def _check_permission(self, seckey):
        permissions = getattr(self, '_permissions_', None)
        if permissions is None:
            return True
        predicate = permissions.get('seckey', None)
        if predicate is None:
            return True
        try:
            predicate.check_authorization(tg.request.environ)
        except NotAuthorizedError as e:
            reason = str(e)
            if hasattr(self, '_failed_authorization'):
                # Should shortcircuit the rest, but if not we will still
                # deny authorization
                self._failed_authorization(reason)
            if not_anonymous().is_met(tg.request.environ):
                # The user is authenticated but not allowed.
                raise Forbidden(detail=reason)
            else:
                # The user has not been not authenticated.
                raise Unauthorized(detail=reason)

    def _dump_object_(self, obj, **kwargs):
        """
        Dumps one or multiple object(s) into dict or list of dict.
        """
        if obj is None:
            return None
        if isinstance(obj, (list, tuple)):
            return map(lambda x: self._dump_object_(x, **kwargs), obj)
        elif isinstance(obj, self._model_):
            return dict([(k, getattr(obj, k)) for k in self._model_.__table__.c.keys()])
        else:
            raise FatalError("Invalid object to dump.")

    def table_schema(self, *args, **kwargs):
        """
        Generate the schema of table in to a dict.
        """
        table = self._model_
        fields = dict([(c.name, {'type': '%s' % c.type, 'default': '%s' % c.default if c.default else c.default,
                                 'nullable': c.nullable, 'unique': c.unique,
                                 'doc': c.doc, 'primary_key': c.primary_key})
                       for c in table.__table__.columns.values()])
        relationships = dict([(n, {'target': r.mapper.class_.__name__,
                                   'direction': r.direction.name,
                                   'field': ['%s.%s' % (c.table, c.name) for c in r._calculated_foreign_keys]})
                              for n, r in table.__mapper__.relationships.items()])
        return {
            'table': table.__name__,
            'fields': fields,
            'relationships': relationships,
        }

    def _serialize(self, inst,
                   include_fields=None,
                   exclude_fields=None,
                   extend_fields=None,
                   order_by=None,
                   begin=None,
                   limit=None):
        """_serialize generate a dictionary from a queryset instance `inst` according to the meta controled by handler
        and the following arguments:
        `include_fields`: a list of field names want to included in output;
        `exclude_fields`: a list of field names will not included in output;
        `extend_fields`: a list of foreignkey field names and m2m or related attributes with other relationships;
        `order_by`: a list of field names for ordering the output;
        `limit`: an integer to limit the number of records to output, 50 by default;
        Return dictionary will like:
        {
            '__ref': '$(HTTP_REQUEST_URI)',
            '__total': $(NUM_OF_MACHED_RECORDS),
            '__count': $(NUM_OF_RETURNED_RECORDS),
            '__limit': $(LIMIT_NUM),
            '__begin': $(OFFSET),
            '__model': '$(NAME_OF_MODEL)',
            '$(NAME_OF_MODEL)': [$(LIST_OF_RECORDS)], ## For multiple records mode
            '$(NAME_OF_MODEL)': {$(RECORD)}, ## For one record mode
        }
        """
        result = {
            '__ref': request.path,
            '__model': self._model_.__name__,
        }

        #if meta.invisible:
        #    exclude_fields = exclude_fields.extend(meta.invisible) if exclude_fields else meta.invisible
        include_fields = list((set(include_fields or self._columns_)
                               - set(exclude_fields or []))
                              | set(self._model_.__table__.primary_key.columns.keys()))
        if extend_fields:
            logger.debug('extend_fields: %s', extend_fields)
            pass
        if isinstance(inst, Query):
            begin = begin or 0
            limit = 50 if limit is None else limit
            result.update({
                '__total': inst.count(),
                '__count': inst.count(),
                '__limit': limit,
                '__begin': begin,
            })
            if order_by:
                joins, orderbys = build_order_by(self._model_, order_by)
                if orderbys:
                    inst = inst.order_by(*orderbys)
            if limit >= 0:
                inst = inst.slice(begin, begin + limit)  # inst[begin:begin+limit]
            result['__count'] = inst.count()
            result[self._model_.__name__] = serialize(self._model_,
                                                      inst,
                                                      include_fields=include_fields, extend_fields=extend_fields)
            # list(inst.values(*[getattr(self._model_, x) for x in include_fields]))
        else:
            logger.debug("Inst >>> %s", inst)
            logger.debug("Include Fields: %s", include_fields)
            objs = serialize(self._model_, inst, include_fields=include_fields, extend_fields=extend_fields)
            if isinstance(objs, (list, tuple)):
                result[self._model_.__name__] = objs
                result['__count'] = len(objs)
            else:
                result[self._model_.__name__] = objs
                # dict([(k, getattr(inst, k)) for k in include_fields])
        return result

    def _validate_object_data(self, object_data):
        assert isinstance(object_data, dict) and object_data
        validators = getattr(self, '_validators_', None)
        if validators:
            for key, vf in validators.items():
                if key in object_data:
                    vf(object_data[key])
        return object_data

    def _encode_object_data(self, object_data):
        assert isinstance(object_data, dict) and object_data
        encoders = getattr(self, '_encoders_', None)
        if encoders:
            for key, vf in encoders.items():
                if key in object_data:
                    object_data[key] = vf(object_data[key])
        return object_data

    def _update_object_data(self, object_data):
        assert isinstance(object_data, dict) and object_data
        generators = getattr(self, '_generators_', None)
        if generators:
            for key, vf in generators.items():
                object_data[key] = vf(object_data[key])
        return object_data

    def _build_filter(self, key, value):
        assert key
        flt, jns = build_filter(self._model_,
                                key.split('.') if isinstance(key, (str, unicode)) else key, value, joins=None)
        logger.debug('_build_filter >>> %s | %s', flt, jns)
        return flt, jns

    def _query(self, query=None):
        """_query: return a Query instance according to the giving query data.
        """
        inst = self._dbsession_.query(self._model_)
        if not query:
            return inst
        default_query = query.pop('__default', None)
        if default_query:
            filters = list()
            joins = list()
            for k, v in default_query.items():
                f, j = self._build_filter(k, v)
                if f is not None:
                    filters.append(f)
                    if j is not None:
                        joins.extend(j)
            logger.debug('[default] filters: %s', filters)
            logger.debug('[default] joins: %s', joins)
            for j in joins:
                inst = inst.join(j)
            if filters:
                inst = inst.filter(and_(*filters))
        for pair, conditions in query.items():
            filters, joins = list(), list()
            for k, v in conditions.items():
                f, j = self._build_filter(k, v)
                if f is not None:
                    filters.append(f)
                    if j is not None:
                        joins.extend(j)
            logger.debug('[%s] filters: %s', pair, filters)
            logger.debug('[%s] joins: %s', pair, joins)
            for j in joins:
                inst = inst.join(j)
            if filters:
                inst = inst.filter(or_(*filters))
        return inst

    @staticmethod
    def _retrieve_http_query(http_request):
        """
        Get the HTTP Query items from request object. we don't need the arg_params from request directly some time.
        """
        # logger.debug('Request.GET(%s):>> %s', type(http_request.GET), http_request.GET.items())
        result = dict()
        for k, v in http_request.GET.items():
            if k not in result:
                result[k] = v
            else:
                if isinstance(result[k], list):
                    result[k].append(v)
                else:
                    result[k] = [result[k], v]
        return result

    @staticmethod
    def _retrieve_http_post(http_request):
        """
        Get the HTTP Post content from request object. sometimes we don't want TG to do this.
        """
        logger.debug('Request.Content-Type:>> %s', http_request.content_type)
        #logger.debug('Request.params:>> %s', http_request.params.items())
        #debug_request(http_request)
        if http_request.content_type in ('application/json', ):
            if hasattr(http_request, 'json'):
                return http_request.json
            else:
                raise InvalidData(detail='Invalid JSON Data!')
        elif http_request.content_type in ('multipart/form-data', 'application/x-www-form-urlencoded'):
            result = dict()
            for k, v in http_request.POST.items():
                if k not in result:
                    result[k] = v
                else:
                    if isinstance(result[k], list):
                        result[k].append(v)
                    else:
                        result[k] = [result[k], v]
            return result
        else:
            raise BadRequest(detail="Not supported Content-Type(%s) yet!" % http_request.content_type)

    @exception_wapper
    def _read(self, pk=None, query=None,
              include_fields=None, exclude_fields=None, extend_fields=None, order_by=None, begin=None, limit=None):
        """_read: read record(s) from table."""
        logger.debug('%s:> _read', self.__class__.__name__)
        logger.debug('pk: %s', pk)
        logger.debug('query: %s', query)
        logger.debug('include_fields: %s', include_fields)
        logger.debug('exclude_fields: %s', exclude_fields)
        logger.debug('extend_fields: %s', extend_fields)
        logger.debug('order_by: %s', order_by)
        logger.debug('begin: %s', begin)
        logger.debug('limit: %s', limit)
        join_loads = find_join_loads(self._model_, extend_fields)
        join_loads = [joinedload(x) for x in join_loads] if join_loads else None
        logger.debug('join_loads: %s', join_loads)
        self._before_read(pk=pk, query=query)
        if pk is not None:
            inst = self._dbsession_.query(self._model_).options(*join_loads).get(pk) if join_loads \
                else self._dbsession_.query(self._model_).get(pk)
            if not inst:
                raise NotFound()
        else:
            inst = self._query(query)
            if join_loads:
                inst = inst.options(*join_loads)
        logger.debug('Inst: %s', type(inst))
        self._after_read(inst)
        return self._serialize(inst, include_fields=include_fields,
                               exclude_fields=exclude_fields,
                               extend_fields=extend_fields,
                               order_by=order_by,
                               begin=begin,
                               limit=limit)

    @exception_wapper
    def _create(self, arguments):
        """_create: Create record(s)."""
        logger.debug('%s:> _create', self.__class__.__name__)
        logger.debug('arguments: %s', arguments)
        ext_flds = list()

        def _do_create_obj(data):
            assert isinstance(data, dict)
            relatedobjs = {}
            objdata = {}

            for k, v in data.items():
                if k in self._model_.__table__.c.keys():
                    objdata[k] = v
                elif k in self._model_.__mapper__.relationships.keys():
                    relatedobjs[k] = v
                else:
                    pass
            if not objdata:
                raise InvalidData(detail='Invalid data! Empty object is not allowed!')
            objdata = self._update_object_data(self._encode_object_data(self._validate_object_data(objdata)))
            obj = self._model_(**objdata)
            for k, v in relatedobjs.items():
                related_instrument = self._model_.__mapper__.relationships[k]
                related_class = related_instrument.mapper.class_
                related_class_pk_name = related_class.__table__.primary_key.columns.keys()[0]
                exits_objs, new_objs, new_obj_datas = None, None, None
                logger.debug('%s: %s', k, v)
                if isinstance(v, (list, tuple)):
                    pks = map(lambda m: m[related_class_pk_name] if isinstance(m, dict) else m,
                              filter(lambda itm: True if (isinstance(itm, dict) and related_class_pk_name in itm)
                              or not isinstance(itm, dict) else False, v))
                    logger.debug('pks = %s', pks)
                    new_obj_datas = filter(lambda m: isinstance(m, dict) and related_class_pk_name not in m, v)
                    if pks:
                        exits_objs = self._dbsession_.query(related_class). \
                            filter(getattr(related_class, related_class_pk_name).in_(pks)).all()
                        logger.debug('exits_objs = %s', exits_objs)
                elif isinstance(v, dict):
                    if related_class_pk_name in v:
                        exits_objs = self._dbsession_.query(related_class).get(v[related_class_pk_name])
                        if not exits_objs:
                            raise NotFound(detail='%s with pk "%s" was not found!' % (k, v))
                    else:
                        new_obj_datas = v
                else:
                    exits_objs = self._dbsession_.query(related_class).get(v)
                    if not exits_objs:
                        raise NotFound(detail='%s with pk "%s" was not found!' % (k, v))
                if new_obj_datas:
                    new_objs = related_class(**new_obj_datas) if isinstance(new_obj_datas, dict) \
                        else [related_class(**xx) for xx in new_obj_datas]
                    ext_flds.append(k)
                else:
                    ext_flds.append(k)
                related_objs = None
                if exits_objs:
                    related_objs = exits_objs
                if new_objs:
                    related_objs = new_objs if not related_objs else related_objs + new_objs
                logger.debug('[%s]related_objs: %s', k, related_objs)
                setattr(obj, k, related_objs)
            self._before_create(obj, **data)
            return obj

        if isinstance(arguments, (list, tuple)):
            objects = map(_do_create_obj, arguments)
            self._dbsession_.add_all(objects)
        else:
            objects = _do_create_obj(arguments)
            self._before_create(objects, **arguments)
            self._dbsession_.add(objects)
        logger.debug('objects: %s', objects)
        self._dbsession_.flush()
        self._after_create(objects)
        return objects, list(set(ext_flds))

    @exception_wapper
    def _update(self, arguments, pk=None, query=None):
        """_update: Update record(s) according to query."""
        logger.debug('%s:> _update', self.__class__.__name__)
        logger.debug('pk: %s', pk)
        logger.debug('query: %s', query)
        logger.debug('arguments: %s', arguments)
        ext_flds = list()
        if pk is not None:
            inst = self._dbsession_.query(self._model_).get(pk)
            if not inst:
                raise NotFound()
            if not isinstance(arguments, dict) or not arguments:
                raise InvalidData()
            arguments = self._validate_object_data(self._encode_object_data(arguments))
            self._before_update(inst, arguments)
            for k, v in arguments.items():
                if self._readonly_fields_ and k in self._readonly_fields_:
                    raise InvalidData(detail='Column(%s) is read-only!' % k)
                setattr(inst, k, v)
            self._dbsession_.add(inst)
            result = inst
        else:
            inst = self._query(query)
            if not isinstance(arguments, dict) or not arguments:
                raise InvalidData()
            arguments = self._validate_object_data(self._encode_object_data(arguments))
            self._before_update(inst, arguments)
            for k, v in arguments.items():
                if self._readonly_fields_ and k in self._readonly_fields_:
                    raise InvalidData(detail='Column(%s) is read-only!' % k)
            inst.update(arguments)
            result = inst
        self._dbsession_.flush()
        self._after_update(inst)
        return result, ext_flds

    @exception_wapper
    def _delete(self, pk=None, query=None):
        """_delete: Delete records from table according to query or pk."""
        logger.debug('%s:> _delete', self.__class__.__name__)
        logger.debug('pk: %s', pk)
        logger.debug('query: %s', query)
        if pk is not None:
            inst = self._dbsession_.query(self._model_).get(pk)
            if not inst:
                raise NotFound()
            self._before_delete(inst)
            result = {'__count': 1,
                      'deleted': [{self._model_.__table__.primary_key.columns.keys()[0]: pk}],
                      '__model': self._model_.__name__}
            self._dbsession_.delete(inst)
        else:
            inst = self._query(query)
            self._before_delete(inst)
            result = map(lambda x: x._asdict(), inst.values(*self._model_.__table__.primary_key.columns.values()))
            #map(lambda x: {self._model_.__table__.primary_key.columns.keys()[0]: x},
            #         inst.values(self._model_.__table__.primary_key.columns.values()[0]))
            result = {'__count': len(result),
                      'deleted': result,
                      '__model': self._model_.__name__}
            inst.delete(synchronize_session='fetch')
        self._after_delete(result['deleted'])
        return result

    ###################################################################################################################
    # Below is following the RestController of tg to bring the interfaces

    @expose('json')
    def get_one(self, pk, **kwargs):
        """
        get_one         | Display one record.                                          | GET /movies/1
        """
        if pk is None:
            #abort(400, u"Invalid request!")
            raise BadRequest()
        try:
            controles, query = query_reparse(self._retrieve_http_query(request),
                                             internal_filters=self._internal_filters_)
            self._check_permission('read')
            result = self._read(pk=pk, **controles)
        except ExpressError, ne:
            logger.exception(u'>>> %s', ne)
            #abort(ne._code_, u"%s" % ne)
            raise ne
        except Exception, e:
            logger.exception(u'>>> %s', e)
            #abort(404, u"Object not found!", comment=u"%s" % e)
            raise FatalError(detail=str(e), title=u'Unknown error!')
        else:
            return result

    @expose('json')
    def get_all(self, **kwargs):
        """
        get_all         | Display all records in a resource.                           | GET /movies/
        """
        controles, query = query_reparse(self._retrieve_http_query(request),
                                         internal_filters=self._internal_filters_)
        try:
            self._check_permission('read')
            result = self._read(query=query, **controles)
        except ExpressError, ne:
            logger.exception(u'>>> %s', ne)
            raise ne
        except Exception, e:
            logger.exception(u'>>> %s', e)
            raise FatalError(detail=str(e))
        else:
            return result

    # @expose('json')
    # def get(self, *args, **kwargs):
    #     """
    #     get             | A combo of get_one and get_all.                              | GET /movies/  | GET /movies/1
    #     """
    #     debug_request(request)
    #     return {'args': args, 'kwargs': kwargs}

    # @expose('json')
    # def new(self, **kwargs):
    #     """
    #     new             | Display a page to prompt the User for resource creation.     | GET /movies/new
    #     """
    #     #controles, query = query_reparse(self._scratch_http_query(request),
    #                                          internal_filters=self._internal_filters_)
    #     postdata = self._retrieve_http_post(request)
    #     try:
    #         self._check_permission('create')
    #         result, ext_fields = self._create(postdata)
    #     except ExpressError, ne:
    #         logger.exception(u'>>> %s', ne)
    #         raise ne
    #     except Exception, e:
    #         logger.exception(u'>>> %s', e)
    #         raise ExpressError(detail=str(e))
    #     return self._serialize(result, extend_fields=ext_fields)
    #
    # @expose('json')
    # def edit(self, pk, **kwargs):
    #     """
    #     edit            | Display a page to prompt the User for resource modification. |  GET /movies/1/edit
    #     """
    #     #controles, query = query_reparse(self._scratch_http_query(request),
    #                                          internal_filters=self._internal_filters_)
    #     postdata = self._retrieve_http_post(request)
    #     try:
    #         self._check_permission('update')
    #         result, ext_fields = self._update(postdata, pk=pk)
    #     except ExpressError, ne:
    #         logger.exception(u'>>> %s', ne)
    #         raise ne
    #     except Exception, e:
    #         logger.exception(u'>>> %s', e)
    #         raise ExpressError(detail=str(e))
    #     else:
    #         return self._serialize(result, extend_fields=ext_fields)

    @expose('json')
    def post(self, pk=None, **kwargs):
        """
        post            | Create a new record.                                         | POST /movies/
        """
        if self._table_readonly_:
            raise Forbidden("Table is Read-Only!")
        postdata = self._retrieve_http_post(request)
        if not postdata:
            raise InvalidData()
        if pk is not None:
            try:
                self._check_permission('update')
                result, ext_fields = self._update(postdata, pk=pk)
            except ExpressError, ne:
                logger.exception(u'>>> %s', ne)
                raise ne
            except Exception, e:
                logger.exception(u'>>> %s', e)
                raise FatalError(detail=str(e))
        else:
            try:
                self._check_permission('create')
                result, ext_fields = self._create(postdata)
            except ExpressError, ne:
                logger.exception(u'>>> %s', ne)
                raise ne
            except Exception, e:
                logger.exception(u'>>> %s', e)
                raise FatalError(detail=str(e))
        return self._serialize(result, extend_fields=ext_fields)

    @expose('json')
    def put(self, pk=None, **kwargs):
        """
        put             | Update an existing record.                                   | POST /movies/1?_method=PUT
                                                                                       | PUT /movies/1
        """
        if self._table_readonly_:
            raise Forbidden("Table is Read-Only!")
        controles, query = query_reparse(self._retrieve_http_query(request),
                                         internal_filters=self._internal_filters_)
        postdata = self._retrieve_http_post(request)
        try:
            self._check_permission('update')
            result, ext_fields = self._update(postdata, pk=pk, query=query)
        except ExpressError, ne:
            logger.exception(u'>>> %s', ne)
            raise ne
        except Exception, e:
            logger.exception(u'>>> %s', e)
            raise FatalError(detail=str(e))
        else:
            return self._serialize(result, extend_fields=ext_fields)

    # @expose('json')
    # def post_delete(self, *args, **kwargs):
    #     """
    #     post_delete     | Delete an existing record.                                   | POST /movies/1?_method=DELETE
    #                                                                                    | DELETE /movies/1
    #     """
    #     debug_request(request)
    #     return {'args': args, 'kwargs': kwargs}
    #
    # @expose('json')
    # def get_delete(self, *args, **kwargs):
    #     """
    #     get_delete      | Display a delete Confirmation page.                          | GET /movies/1/delete
    #     """
    #     debug_request(request)
    #     return {'args': args, 'kwargs': kwargs}

    @expose('json')
    def delete(self, pk=None, **kwargs):
        """
        delete          | A combination of post_delete and get_delete.                 | GET /movies/delete
                                                                                        | DELETE /movies/1
                                                                                        | DELETE /movies/
                                                                                        | POST /movies/1/delete
                                                                                        | POST /movies/delete
        """
        if self._table_readonly_:
            raise Forbidden("Table is Read-Only!")
        controles, query = query_reparse(self._retrieve_http_query(request),
                                         internal_filters=self._internal_filters_)
        try:
            self._check_permission('delete')
            if pk is not None:
                result = self._delete(pk=pk)
            else:
                result = self._delete(query=query)
        except ExpressError, ne:
            logger.exception(u'>>> %s', ne)
            raise ne
        except Exception, e:
            logger.exception(u'>>> %s', e)
            raise FatalError(detail=str(e))
        else:
            return result