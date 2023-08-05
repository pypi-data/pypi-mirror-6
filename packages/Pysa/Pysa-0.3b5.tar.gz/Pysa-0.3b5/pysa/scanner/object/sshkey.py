'''
Created on 2013-3-28

    pysa - reverse a complete computer setup
    Copyright (C) 2013  MadeiraCloud Ltd.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

@author: Ken
'''

from pysa.scanner.object.object_base import ObjectBase


class SSHKey(ObjectBase):
    
    def __init__(self, key, name, path, mode, _type=None, target=None, host_aliases=None, user=None):
        self.key = key
        self.name = name
        self.target = target
        self.host_aliases = host_aliases
        self.type = _type
        self.user = user
        self.path = path
        self.mode = mode

