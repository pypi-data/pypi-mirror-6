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

import logging

log = logging.getLogger('prism_rest_client.util')

class AttrDict(dict):
    """
    Dictionary implementation that lets you refer to dictionary keys as
    normal attributes.
    """

    __slots__ = ()

    def __getattr__(self, attr):
        if attr.startswith('_'):
            return dict.__getattribute__(self, attr)
        else:
            return self.__getitem__(attr)

    def __setattr__(self, attr, value):
        if attr.startswith('_'):
            return dict.__setattr__(self, attr, value)
        else:
            return self.__setitem__(attr, value)
