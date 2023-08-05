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

from .resource import BaseResource

class Collection(BaseResource):
    def __getitem__(self, idx):
        return self._data[idx]

    def __setitem__(self, idx, value):
        pass

    def __delitem__(self, idx):
        self._cache.delete(self._data[idx].delete())
        del self._data[idx]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __nonzero__(self):
        return bool(self._data)

    def append(self, resource, post=True):
        if isinstance(resource, BaseResource):
            value = resource._data
        else:
            value = resource

        if post:
            obj = self._cache.post(self._uri, value)
            self._data.append(obj)
            return obj

        else:
            self._data.append(resource)

    def refresh(self):
        resource = self._cache.get(self._uri, cache=False)
        assert isinstance(resource, Collection)
        self._data = resource._data
        self._metadata = resource._metadata
