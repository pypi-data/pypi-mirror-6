from __future__ import unicode_literals

import json
import logging
import requests

from . import status
from .resources import Resource, Collection


logging.basicConfig()
log = logging.getLogger(__name__)

# TODO jumping api boundaries

class Api(Resource):
    """
    Represents a REST API encapsulating some assumptions about its behaviour
    
     - application/json is the default content-type
     - tokens is the default authentication mechanism
    
    However this tries to be a generic implementation, support for other methods
    and types can be achieved by means of subclassing and method overiding
    """
    CONTENT_TYPE = 'application/json'
    SERIALIZE_IGNORES = Resource.SERIALIZE_IGNORES + ['username', 'password', 'token']
    DEFAULT_HEADERS = {
        'accept': CONTENT_TYPE,
        'content-type': CONTENT_TYPE,
    }
    
    def __init__(self, uri, username='', password=''):
        super(Api, self).__init__(self, uri=uri)
        self.username = username
        self.password = password
    
    def serialize_response(self, content):
        # TODO accept response object, and lookup for response.content-type?
        """ hook for other content-type response serialization """
        if self.CONTENT_TYPE == 'application/json':
            return json.loads(content)
        else:
            msg = "serialization for '%s' response not implemented"
            raise NotImplementedError(msg % self.CONTENT_TYPE)
        
    def serialize_request(self, content):
        """ hook for other content-type request serialization """
        if self.CONTENT_TYPE == 'application/json':
            return json.dumps(content)
        else:
            msg = "serialization for '%s' request not implemented"
            raise NotImplementedError(msg % self.CONTENT_TYPE)
    
    def request(self, method, *args, **kwargs):
        """ wrapper function for DRYing boilerplate """
        headers = kwargs.get('headers', self.DEFAULT_HEADERS)
        headers.update(kwargs.pop('extra_headers', {}))
        kwargs['headers'] = headers
        log.info(' ' + method.__name__.upper() + str(args))
        log.debug('\n\t' + str(kwargs))
        return method(*args, **kwargs)
    
    def get(self, url, **kwargs):
        """ low level get method """
        return self.request(requests.get, url, **kwargs)
    
    def post(self, url, *args, **kwargs):
        """ low level post method """
        if args:
            if isinstance(args[0], file):
                kwargs['files'] = {'file': args[0]}
                kwargs['extra_headers'] = {
                    'content-type': None
                }
                args = args[1:]
            else:
                args = (self.serialize_request(args[0]),) + args[1:]
        return self.request(requests.post, url, *args, **kwargs)
    
    def put(self, url, data, **kwargs):
        """ low level put method """
        if args:
            args = (self.serialize_request(args[0]),) + args[1:]
        return self.request(requests.put, url, *args, **kwargs)
    
    def patch(self, url, data, **kwargs):
        """ low level patch method """
        if args:
            args = (self.serialize_request(args[0]),) + args[1:]
        return self.request(requests.patch, url, *args, **kwargs)
    
    def delete(self, url, **kwargs):
        """ low level delete method """
        return self.request(requests.delete, url, **kwargs)
    
    def head(self, url, **kwargs):
        """ low level delete method """
        return self.request(requests.head, url, **kwargs)
    
    def create(self, url, data=None, extra_headers={}, headers=None, **kwargs):
        """ high level api method for creating objects """
        if data is None:
            obj = Resource(self, **kwargs)
            data = obj.serialize()
        kwargs = {
            'extra_headers': extra_headers
        }
        if headers is not None:
            kwargs['headers'] = headers
        response = self.post(url, data, **kwargs)
        self.validate_response(response, status.HTTP_201_CREATED)
        return Resource.from_response(self, response)
    
    def self_retrieve(self):
        """ retrieve self """
        base = Resource.from_response(self, self.get(self.uri))
        self.merge(base)
        self._headers = base._headers
        self.process_links()
        self._has_retrieved = True
    
    def retrieve(self, *args, **kwargs):
        """ high level api method for retrieving objects """
        if not args:
            self.self_retrieve()
        elif len(args) != 1:
            raise ValueError('Too many positional arguments')
        else:
            url = args[0]
            save_to = kwargs.pop('save_to', '')
            if save_to:
                response = self.get(url, stream=True, **kwargs)
                self.validate_response(response, status.HTTP_200_OK)
                with open(save_to, 'wb') as f:
                    for chunk in response.iter_content():
                        f.write(chunk)
            else:
                response = self.get(url, **kwargs)
                self.validate_response(response, status.HTTP_200_OK)
                content = self.serialize_response(response.content)
                if isinstance(content, list):
                    resources = [Resource(self, **obj) for obj in content]
                    return Collection(resources, api=self, uri=response.url)
                return Resource(self, _headers=response.headers, **content)
    
    def update(self, url, data, **kwargs):
        """ high level api method for updating objects """
        response = self.put(url, data, **kwargs)
        self.validate_response(response, status.HTTP_200_OK)
        content = self.serialize_response(response.content)
        return Resource(self, **content)
        
    def partial_update(self, url, data, **kwargs):
        """ high level api method for partially updating objects """
        response = self.patch(url, data, **kwargs)
        self.validate_response(response, status.HTTP_200_OK)
        content = self.serialize_response(response.content)
        return Resource(self, **content)
    
    def destroy(self, url, **kwargs):
        """ high level api method for deleting objects """
        response = self.delete(url, **kwargs)
        self.validate_response(response, status.HTTP_204_NO_CONTENT)
    
    def validate_response(self, response, codes):
        """ validate response status code """
        if not hasattr(codes, '__iter__'):
            codes = [codes]
        if response.status_code not in codes:
            try:
                content = self.serialize_response(response.content)
            except ValueError:
                # Internal server error with a bunch of html most probably
                content = {'detail': response.content[:200]}
            context = {
                'url': response.url,
                'code': response.status_code,
                'reason': response.reason,
                'expected': str(codes)[1:-1],
                'detail': content.get('detail', content)
            }
            # TODO include method
            msg = "[%(url)s]: %(code)d %(reason)s (!= %(expected)s) %(detail)s"
            raise self.ResponseStatusError(msg % context)
    
    def login(self, username=None, password=None):
        """ further requests will use authentication """
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password
        response = self.get_auth_token(username=self.username, password=self.password)
        token = 'Token %s' % self.serialize_response(response.content)['token']
        self.DEFAULT_HEADERS['authorization'] = token
    
    def logout(self):
        """ further requests will not use authentication """
        self.DEFAULT_HEADERS.pop('authorization')
    
    @classmethod
    def enable_logging(cls):
        cls.logger = logging.getLogger(__name__)
        cls.logger.setLevel(logging.INFO)
    
    @classmethod
    def disable_logging(cls):
        cls.logger.setLevel(logging.ERROR)
    
    class ResponseStatusError(Exception):
        pass
