from brokerest.errors import *
from brokerest.base import BaseModel, BaseCriteria
import json
import requests
import re

class RestlessCriteria(BaseCriteria):
    
    def __init__(self, resource):
        self._results_per_page = None
        self._page = None
        self._offset = None
        self._limit = None
        self._filters = []
        self._order_by = []
        self._single = False
        super(RestlessCriteria, self).__init__(resource)

    def count(self, field='id'):
        if not 'functions' in self:
            self._functions = []
        self._functions.append({"name": "count", "field": field})
        return self
    
    def filter_by(self, attr, value):
        self._filters.append({'name' : attr, 'op' : 'eq', 'val' : value})
        return self

    def filter(self, attr, op, value):
        self._filters.append({'name' : attr, 'op' : op, 'val' : value})
        return self
        
    def order_by(self, attr, direction='asc'):
        self._order_by.append({"field": attr, "direction": direction})
        return self
    
    def offset(self, offset):
        self._offset = offset
        return self

    def limit(self, limit):
        self._limit = limit
        return self
        
    def scalar(self):
        resp = self.select()
        key, value = resp.popitem()
        return value

    def all(self):
        resp = self.request()
        return [self.resource.get_from(o) for o in resp]
    
    def one(self):
        self._single = True
        try:
            resp = self.request()
            if not resp:
                raise ObjectNotFound()
        except IntegrityError:
            raise ObjectNotFound()
        
        if 'headers' in resp:
            del resp["headers"]
        return self.resource.get_from(resp)
            

    def compute_params(self):
        params = {}
        for param in ['single', 'results_per_page', 'page', 'filters', 'order_by', 'limit', 'offset']:
            if getattr(self, "_"+param):
                params[param] = getattr(self, "_"+param)
        
        return {'q' : json.dumps(params)}
        
    

class RestlessModel(BaseModel):

    criteria_class = RestlessCriteria
    
    @classmethod
    def request(cls, method, url, params=None, headers=None, data=None):
        resp = BaseModel.request(method, url, params=params, headers=headers, data=data)
        if 'objects' in resp:
            return resp['objects']
        else:
            return resp
