import re

import gevent

from .utils import DisabledStderr


LOOKUPS = {
    'default': lambda a,b: a == b,
    'lt': lambda a,b: a < b,
    'lte': lambda a,b: a <= b,
    'gt': lambda a,b: a > b,
    'gte': lambda a,b: a >= b,
    'in': lambda a,b: a in b,
    'exact': lambda a,b: a == b,
    'iexact': lambda a,b: a.lower() == b.lower(),
    'startswith': lambda a,b: a.startswith(b),
    'istartswith': lambda a,b: a.lower().startswith(b.lower()),
    'contains': lambda a,b: b in a,
    'icontains': lambda a,b: b.lower() in a.lower(),
}


def filter_collection(collection, **kwargs):
    if not kwargs:
        return list(collection.resources)
    exclude = kwargs.pop('_exclude', False)
    result = []
    for resource in collection.resources:
        for key, value in kwargs.iteritems():
            include = False
            attrs = key.split('__')
            try:
                lookup = LOOKUPS[attrs[-1]]
            except KeyError:
                lookup = LOOKUPS.get('default')
            else:
                attrs = attrs[:-1]
            current = resource
            for attr in attrs:
                current = getattr(current, attr)
                if isinstance(current, type(collection)):
                    # "joining" with currenr Collection
                    attr = re.findall(r'%s__(.*)$' % attr, key)[0]
                    partial_kwargs = {
                        attr: value,
                        '_exclude': exclude
                    }
                    include = bool(filter_collection(current, **partial_kwargs))
                    break
            if not isinstance(current, type(collection)):
                if not exclude and lookup(current, value):
                    include = True
                elif exclude and not lookup(current, value):
                    include = True
            if not include:
                break
        if include:
            result.append(resource)
    return result


def retrieve_related(resources, *args):
    from .resources import Resource
    pool = {}
    MAX_RECURSION = 10
    args = list(args)
    for i in range(0, MAX_RECURSION):
        related = {}
        for resource in resources:
            for attr in args:
                try:
                    field = attr.split('__')[i]
                except IndexError:
                    args.remove(attr)
                else:
                    current = getattr(resource, field)
                    if isinstance(current, Resource):
                        related[current.uri] = current
                    else:
                        for nested in current:
                            if isinstance(current, Resource):
                                related[nested.uri] = nested
        if not related:
            return
        to_fetch = set(related.keys()) - set(pool.keys())
        glets = [gevent.spawn(related[url].api.retrieve, url) for url in to_fetch]
        for glet, url in zip(glets, to_fetch):
            with DisabledStderr():
                glet.get()
            if glet._exception:
                log.error(glet._exception)
                pool[url] = related[url]
            else:
                pool[glet.value.uri] = glet.value
        next = []
        for resource in resources:
            for related in args:
                field = related.split('__')[i]
                current = getattr(resource, field)
                if isinstance(current, Resource):
#                        current = Resource(current.api, **pool[current.uri]._data)
                    next.append(current)
                else:
#                        values = [
#                            Resource(nested._api, **pool[nested.uri]._data)
#                                for nested in current
#                        ]
#                        current = Collection(values, manager=current.manager)
                    next += values
                setattr(resource, field, current)
        resources = next
