from __future__ import unicode_literals

import json
import logging
import re
from copy import copy

import gevent
from gevent import monkey

from . import helpers
from . import relations as rel
from .managers import Manager
from .utils import DisabledStderr


monkey.patch_all(thread=False, select=False)

logging.basicConfig()
log = logging.getLogger(__name__)
# TODO use copy() instead of cls()
# TODO return self or copy(self)??

# TODO file resource, with download() and check_sha256() mayve overlay: {uri, sha256} ???

class Resource(object):
    """ schema-free resource representation (active record) """
    SERIALIZE_IGNORES = ['api', 'manager']
    
    def __repr__(self):
        module, name = type(self).__module__, type(self).__name__
        return "<%s.%s: %s>" % (module, name, self.uri or id(self))
    
    def __str__(self):
        return json.dumps(self.serialize(), indent=4)
    
    def __init__(self, *args, **kwargs):
        self._serialize_ignores = list(self.SERIALIZE_IGNORES)
        self.uri = None
        self.api = None
        self.manager = None
        self._headers = kwargs.get('_headers', None)
        if self._headers:
            self.process_links()
        self._has_retrieved = bool(self._headers)
        if args:
            self.api = args[0]
        # Build nested Resource structure
        for name, value in kwargs.iteritems():
            if not name.startswith('_'):
                if isinstance(value, dict):
                    value = Resource(*args, **value)
                if isinstance(value, list):
                    if value and isinstance(value[0], dict):
                        value = [ Resource(*args, **v) for v in value ]
                    value = RelatedCollection(value, api=self.api, parent=self, related_name=name)
            self.__dict__[name] = value
    
    def __getattr__(self, name):
        """ fetch and cache missing nested resources """
        if not name == 'uri' and not name.startswith('_') and self.api and self.uri:
            if not self._has_retrieved:
                self.retrieve()
                return getattr(self, name)
        msg = "'%s' object has no attribute '%s'"
        raise AttributeError(msg % (str(type(self)), name))
    
    def __eq__(self, other):
        if not isinstance(other, Resource):
            return False
        if self.uri and other.uri:
            return self.uri == other.uri
        if self.manager != other.manager:
            return False
        return self._data == other._data
    
    @classmethod
    def from_response(cls, api, response):
        """ constructor method accepting a response object """
        content = api.serialize_response(response.content)
        resource = cls(api, _headers=response.headers, **content)
        return resource
    
    @property
    def _data(self):
        """ hide internal methods and attributes """
        data = {}
        for name, value in self.__dict__.iteritems():
            if not name.startswith('_') and name not in self._serialize_ignores:
                data[name] = value
        return data
    
    def get_links(self):
        """ get link header urls mapped by relation """
        links = {}
        link_header = self._headers.get('link', False)
        if link_header:
            for line in link_header.split(','):
                link = re.findall(r'<(.*)>', line)[0]
                relation = re.findall(r'"(.*)"', line)[0]
                links[relation] = link
        return links
    
    def process_links(self):
        """ get extra managers from link relations """
        links = self.get_links()
        for relation, link in links.iteritems():
            try:
                __, name = rel.reverse(relation)
            except KeyError:
                log.warning("relation '%s' not found" % relation)
            else:
                if name not in self.__dict__:
                    setattr(self, name, Manager(link, relation, self.api))
                    self._serialize_ignores.append(name)
    
    def get_name(self):
        """ getting the resource name, suggestions are welcome :) """
        if self.uri:
            uri = self.uri
            if not uri.endswith('/'):
                uri += '/'
            return uri.split('/')[-3].replace('-', '_')[:-1]
        elif self.manager:
            type, name = rel.reverse(self.manager.relation)
            if name.endswith('s'):
                name = name[:-1]
            return name
        raise ValueError("don't know the name")
    
    def save(self):
        """ save object on remote and update field values from response """
        if self.uri:
            self.validate_binding()
            resource = self.api.update(self.uri, self.serialize())
        else:
            self.validate_binding()
            resource = self.manager.create(self.serialize())
        self.merge(resource)
    
    def merge(self, resource):
        """  merge input resource attributes to current resource """
        for key, value in resource._data.iteritems():
            setattr(self, key, value)
    
    def delete(self):
        """ delete remote object """
        self.validate_binding(uri=True)
        self.api.destroy(self.uri)
    
    def update(self, **kwargs):
        """ partial remote update of the object """
        self.validate_binding(uri=True)
        resource = self.api.partial_update(self.uri, kwargs)
        self.merge(resource)
    
    def retrieve(self):
        """ retrieve remote state of this object """
        resource = type(self).from_response(self.api, self.api.get(self.uri))
        self.merge(resource)
        self._headers = resource._headers
        self.process_links()
        self._has_retrieved = True
    
    def serialize(self, isnested=False):
        """ serialize object for storing in remote server """
        raw_data = self._data
        if isnested and raw_data['uri']:
            return { 'uri': raw_data['uri'] }
        data = {}
        for key, value in raw_data.iteritems():
            if isinstance(value, Resource):
                value = value.serialize(isnested=True)
            elif isinstance(value, RelatedCollection):
                value = value.serialize()
            # Don't include self.uri == None
            if key != 'uri' or value:
                data[key] = value
        return data
    
    def bind(self, manager):
        """ bind object to an api endpoint """
        self.api = manager.api
        self.manager = manager
    
    def validate_binding(self, manager=False, uri=False):
        """ checks if current object state satisfies bind requirements """
        if not self.api:
            raise TypeError('this resouce is not bound to an Api')
        if not self.uri and not self.manager:
            raise TypeError('this resource has no uri nor related Api endpoint')
        if manager and not self.manager:
            raise TypeError('this resource has no related Api endpoint')
        if uri and not self.uri:
            raise TypeError('this resource has no uri')


# TODO BaseCollection?
class Collection(object):
    """ represents a uniform collection of resources """
    # TODO this is a top-level collection, all methods have to be updated!
    REPR_OUTPUT_SIZE = 10
    
    def __repr__(self):
        return str(self.resources)
    
    def __str__(self):
        return str([str(resource) for resource in self.resources])
    
    def __init__(self, resources, api, uri):
        self.resources = resources
        self.api = api
        self.uri = uri
        self.manager = getattr(self.api, self.get_name())
    
    def __iter__(self):
        return iter(self.resources)
    
    def __getitem__(self, k):
        return self.resources[k]
    
    def __len__(self):
        return len(self.resources)
    
    def __getattr__(self, name):
        """ proxy methods of endpoint manager """
        try:
            return getattr(self.manager, name)
        except AttributeError:
            msg = "'%s' object has no attribute '%s'"
            raise AttributeError(msg % (str(type(self)), name))
    
    def get_name(self):
        uri = self.uri
        if not uri.endswith('/'):
            uri += uri + '/'
        return uri.split('/')[-2]
        
    def serialize(self):
        if self.resources and isinstance(self.resources[0], Resource):
            return [resource.serialize() for resource in self.resources]
        return [resource for resource in self.resources]
    
    def iterator(self, block=False):
        if not block:
            glets = [gevent.spawn(resource.api.retrieve, resource.uri) for resource in self.resources]
            for glet, resource in zip(glets, self.resources):
                with DisabledStderr():
                    glet.get()
                if glet._exception:
                    log.error(glet._exception)
                    yield resource
                else:
                    yield glet.value
        else:
            for resouce in self.resources:
                yield resource.api.retrieve(resource.uri)
    
    def filter(self, **kwargs):
        """ client-side filtering method """
        related = []
        for field in kwargs:
            relations = field.split('__')
            if relations[-1] in helpers.LOOKUPS:
                relations = relations[:-1]
            if len(relations) > 1:
                related.append('__'.join(relations))
        self.retrieve_related(*related)
        new = copy(self)
        new.resources = helpers.filter_collection(self, **kwargs)
        return new
    
    def get(self, **kwargs):
        resource = helpers.filter_collection(self, **kwargs)
        if len(resource) > 1:
            raise TypeError('more than one')
        elif len(resource) < 1:
            raise TypeError('not found')
        return resource[0]
    
    def exclude(self, **kwargs):
        kwargs['_exclude'] = True
        new = copy(self)
        new.resources = helpers.filter_collection(self, **kwargs)
        return new
    
    def group_by(self, field):
        pass
    
    def order_by(self, filed):
        pass
    
    def bulk(self, method, merge=True, **kwargs):
        glets = []
        for resource in self.resources:
            args = (resource.uri, kwargs) if kwargs else (resource.uri,)
            glets.append(gevent.spawn(getattr(resource.api, method), *args))
        total = len(glets)
        successes = []
        failures = []
        for glet, resource in zip(glets, self.resources):
            with DisabledStderr():
                glet.get()
            if glet._exception:
                log.error(glet._exception)
                failures.append(resource)
            else:
                if merge:
                    resource.merge(glet.value)
                successes.append(resource)
        return successes, failures
    
    def destroy(self):
        return self.bulk('destroy', merge=False)
    
    def update(self, **kwargs):
        """ remote update of all set elements """
        return self.bulk('partial_update', **kwargs)
    
    def retrieve(self):
        self.resources = [resource for resource in self.iterator(block=False)]
    
    def retrieve_related(self, *args):
        """ fetched related elements in batch """
        helpers.retrieve_related(self.resources, *args)
        return self
    
    def values_list(self, value):
        result = []
        for resource in self.resources:
            current = resource
            for attr in value.split('__'):
                current = getattr(current, attr)
            result.append(current)
        new = copy(self)
        new.resources = result
        return new
    
    def distinct(self):
        new = copy(self)
        new.resources = list(set(self.resources))
        return new
    
    def append(self, resource):
        self.resources.append(resource)
    
    def create(self, **kwargs):
        """ create can not be proxied """
        resource = self.manager.create(**kwargs)
        self.resources.append(resource)
        return resource

# TODO append + save() ? 
class RelatedCollection(Collection):
    """ represents a subcollection related to a parent object """
    def __init__(self, resources, api, parent, related_name):
        self.resources = resources
        self.api = api
        self.related_name = related_name
        self.parent = parent
        try:
            self.manager = getattr(self.api, self.related_name)
        except AttributeError:
            self.manager = None
    
    def get_name(self):
        return self.related_name
    
    def create(self, **kwargs):
        """ appending related object as attributes of new resource """
        kwargs[self.parent.get_name()] = self.parent
        resource = self.manager.create(**kwargs)
        self.resources.append(resource)
        return resource
    
    def retrieve(self):
        """ retrieve related collection taking care of the parent """
        self.parent.retrieve()
        collection = getattr(self.parent, self.related_name)
        super(RelatedCollection, collection).retrieve()
        return collection


# TODO inherit of list and set becuase COllection makes use of [] and list()
class ResourceSet(Collection):
    """
    represents a non-uniform set of resources that can be used for bulk operations
    maximizing concurrent throughput
    """
    def __init__(self, resources):
        self.resources = set(resources)
    
    def __getattr__(self, name):
        msg = "'%s' object has no attribute '%s'"
        raise AttributeError(msg % (str(type(self)), name))
    
    def create(self):
        return AttributeError('non-uniform resources can not be created')
