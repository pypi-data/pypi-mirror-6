from errors import *
import json
import requests
import re

class BaseCriteria(object):
    
    def __init__(self, resource):
        self.resource = resource

    def __iter__(self):
        return self.all()
        
    def all(self):
        resp = self.request()
        return [self.resource.get_from(o) for o in resp]
    
    def one(self):
        resp = self.request()
        return self.resource.get_from(resp[0])
    
    def compute_params(self):
        return None
        
    def request(self):
        params=self.compute_params()
        return self.resource.request('get', self.resource.url(), params=params)
    
    

class BaseObject(dict):
    
    _pk = 'id'
    
    def __init__(self, id=None):
    
        self._unsaved_values = set()
        self._transient_values = set()

        self[self._pk] = id
    
    def __setattr__(self, k, v):
        if k[0] == '_' or k in self.__dict__:
            return super(BaseObject, self).__setattr__(k, v)
        else:
            self[k] = v

    def __getattr__(self, k):
        if k[0] == '_':
            raise AttributeError(k)

        try:
            return self[k]
        except KeyError, err:
            raise AttributeError(*err.args)

    def __setitem__(self, k, v):
        if v == "":
            raise ValueError(
                "You cannot set %s to an empty string. Set %s.%s = None to delete the property." % 
                ( k, str(self), k))

        super(BaseObject, self).__setitem__(k, v)
        self._unsaved_values.add(k)

    def __getitem__(self, k):
        try:
            return super(BaseObject, self).__getitem__(k)
        except KeyError, err:
            if k in self._transient_values:
                raise KeyError(
                    "%r attribute not set, available values on this object are: %s" %
                    (k, ', '.join(self.keys())))
            else:
                raise err

    def __delitem__(self, k):
        raise TypeError(
            "You cannot delete attributes, to unset a property, set it to None.")
    
class classproperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

class BaseModel(BaseObject):

    criteria_class = BaseCriteria
    
    ObjectNotFound = ObjectNotFound
    RequestError = RequestError
    AccessError = AccessError
    
    inline_models = dict()

    def __str__(self):
        return "%s #%s" % (self.__class__.__name__, self.obj_id())
    
    def __getitem__(self, k):
        try:
            return super(BaseModel, self).__getitem__(k)
        except KeyError:
            try:
                resp = self.__class__.request('get', self.instance_url()+'/'+k)
                self.load_attr(k, resp)
                return self[k]
                
            except self.RequestError:
                raise KeyError(
                    "%r attribute or method not found, available values on this object are: %s" %
                    (k, ', '.join(self.keys())))
    
    def obj_id(self):
        return self[self._pk]
    
    def instance_url(self):
        return "%s/%s" % (self.__class__.url(), self.obj_id())

    @classmethod
    def url(cls):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        return "/%s" % (name)
        
    @classmethod
    def get(cls, id):
        obj = cls(id)
        obj.reload()
        return obj

    @classmethod
    def get_from(cls, values):
        instance = cls(values.get(cls._pk, None))
        instance.reload_from(values)
        return instance

    def reload(self):
        self.reload_from(self.request('get', self.instance_url()))
        return self
    
    def reload_from(self, values):
        
        removed = set(self.keys()) - set(values)
        self._transient_values = self._transient_values | removed
        self._unsaved_values = set()

        self.clear()
        self._transient_values = self._transient_values - set(values)
        
        for k, v in values.iteritems():
            self.load_attr(k, v)
            
    def load_attr(self, k, v):
        if isinstance(v, dict):
            type = self.inline_models.get(k, BaseModel)
            value = type.get_from(v)
        elif isinstance(v, list):
            type = self.inline_models.get(k, BaseModel)
            value = []
            for o in v:
                value.append(type.get_from(o))
        else:
            value = v
        super(BaseObject, self).__setitem__(k, value)
    
    
    def save(self):
        if self.obj_id():
            self.reload_from(self.request('put', self.instance_url(), data=self.serialize()))
        else:
            self.reload_from(self.request('post', self.__class__.url(), data=self.serialize()))
            
    def serialize(self):
        params = {}
        if self._unsaved_values:
            for k in self._unsaved_values:
                if k == self._pk:
                    continue
                v = getattr(self, k)
                params[k] = v# if v is not None else ""
        return params
            
    @classproperty
    @classmethod
    def find(cls):
        return cls.criteria_class(cls)
        
    @classmethod
    def request(cls, method, url, params=None, headers={'Content-Type': 'application/json'}, data=None):
        
        resp = requests.request(method, url, headers=headers, data=json.dumps(data), params=params, timeout=80)
        if 200 <= resp.status_code < 399:
            return resp.json()
        elif resp.status_code in [400, 405]:
            raise RequestError(url)
        elif resp.status_code == 401:
            raise AccessError(url)
        elif 402 <= resp.status_code < 500:
            raise ObjectNotFound(url)
        else:
            raise Exception('API query error (%s - %s): %s %s' % (url, resp.status_code, resp.text, params) )
            
