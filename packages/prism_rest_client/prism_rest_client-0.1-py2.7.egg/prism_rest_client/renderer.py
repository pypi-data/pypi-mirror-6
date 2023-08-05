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

from .lib.util import AttrDict
from .resource import Resource
from .collection import Collection

class JSONRenderer(object):
    def __init__(self, cache):
        self.cache = cache

    def __call__(self, pairs):
        uri = pairs.get('id')
        md = pairs.get('metadata')
        pairs = AttrDict(pairs)

        if not uri:
            return pairs

        data = pairs.get('data')
        if data is not None:
            resource = Collection(uri, self.cache, data=data, metadata=md)

        else:
            resource = Resource(uri, self.cache, data=pairs, metadata=md)

        return resource
