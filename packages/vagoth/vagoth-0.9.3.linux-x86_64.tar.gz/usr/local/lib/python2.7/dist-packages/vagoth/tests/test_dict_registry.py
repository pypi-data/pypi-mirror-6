#
# Vagoth Cluster Management Framework
# Copyright (C) 2013  Robert Thomson
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#

"""
Test vagoth.registry.couch_registry.CouchRegistry
"""

import unittest
from ..registry.dict_registry import DictRegistry
import uuid
import couchdb
from .. import exceptions
from registry_mixin import RegistryMixin

NO_DEFAULT=uuid.uuid4()

class testDictRegistry(unittest.TestCase, RegistryMixin):
    def setUp(self):
        self.registry = DictRegistry(None, {})
        self.mixin_setUp()

    def test_dict_initial_object(self):
        self.assertEqual(len(self.registry.nodes), 1)
        self.assertTrue("0xdeadbeef" in self.registry.nodes)
        self.assertEqual(len(self.registry.unique), 2)
        self.assertIn("VAGOTH_NAME_node001.example.com", self.registry.unique)
        self.assertIn("node001_uniquekey", self.registry.unique)
