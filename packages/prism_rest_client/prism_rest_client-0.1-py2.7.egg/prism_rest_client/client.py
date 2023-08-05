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

import requests

class Client(object):
    def __init__(self, headers=None):
        self.headers = headers

    def get(self, uri, params=None):
        return requests.get(uri, headers=self.headers,
                params=params and params or {})

    def post(self, uri, data):
        return requests.post(uri, data, headers=self.headers)

    def delete(self, uri):
        return requests.delete(uri, headers=self.headers)

    def put(self, uri, data):
        return requests.put(uri, data, headers=self.headers)
