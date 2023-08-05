#
# Copyright (c) Elliot Peele <elliot@bentlogic.net>
#
# This program is distributed under the terms of the MIT License as found
# in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/mit-license.php.
#
# This program is distributed in the hope that it will be useful, but
# without any warrenty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the MIT License for full details.
#

import json

from .renderer import JSONRenderer

class Default(object): pass

class InstanceCache(dict):
    __slots__ = ('client', 'resp_cache', )

    def __init__(self, client):
        self.client = client
        self.resp_cache = ResponseCache()

    def __getitem__(self, uri, force=False, cache=True, params=None):
        if uri in self and not force and cache:
            return dict.__getitem__(self, uri)
        else:
            resp = self.client.get(uri, params=params)
            return self.get_by_response(resp, cache=cache)

    def get(self, uri, default=Default, force=False, cache=True, params=None):
        if uri not in self and not force and default is not Default:
            return default
        else:
            return self.__getitem__(uri, force=force, cache=cache,
                    params=params)

    def get_by_response(self, resp, cache=True):
        resp.close()
        if resp.status_code >= 400:
            import epdb; epdb.st()
        resource = resp.json(object_hook=JSONRenderer(self))
#        self.resp_cache[resource._uri] = resp

        if cache:
            self[resource._uri] = resource
        return resource

    def delete(self, uri):
        del self[uri]
#        del self.resp_cache[uri]
        self.client.delete(uri).close()

    def post(self, uri, data):
        resp = self.client.post(uri, json.dumps(data))
        return self.get_by_response(resp, cache=True)

    def put(self, uri, data):
        resp = self.client.put(uri, json.dumps(data))
        resource = self.get_by_response(resp, cache=False)
        self[resource._uri]._data = resource._data


class ResponseCache(dict):
    __slots__ = ()
