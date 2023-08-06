# -*- coding: utf-8 -*-
# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from cubicweb.devtools.testlib import CubicWebTC

class CustomPermissionsTC(CubicWebTC):
    appid = 'data-perms'
    def test_collaborate_permissions(self):
        collaborates_on_rdef = self.schema['collaborates_on'].rdef('CWUser', 'CollaborativeEntityWithPermissions')

        self.assertEqual(frozenset(collaborates_on_rdef.permissions.items()),
                         frozenset({'read': ('foo_managers',),
                                    'add': ('foo_add_managers',),
                                    'delete': ('foo_del_managers',)}.items()))

    def test_container_rtype_permissions(self):
        crtype_rdef = self.schema['in_collaborativeentitywithpermissions'].rdef('ChildEnt', 'CollaborativeEntityWithPermissions')
        self.assertEqual(frozenset(crtype_rdef.permissions.items()),
                         frozenset({'read': ('bar_managers',),
                                    'add': ('bar_add_managers',),
                                    'delete': ('bar_del_managers',)}.items()))

    def test_container_etype_permissions(self):
        cetype = self.schema['CollaborativeEntityWithPermissions']
        self.assertEqual(frozenset(cetype.permissions.items()),
                         frozenset({'read': ('baz_managers',),
                                    'add': ('baz_add_managers',),
                                    'update': ('baz_update_managers',),
                                    'delete': ('baz_del_managers',)}.items()))

    def test_in_container_etype_permissions(self):
        in_cetypes = map(self.schema.get, ('ChildEnt', 'TranschildEnt'))
        for in_cetype in in_cetypes:
            self.assertEqual(frozenset(in_cetype.permissions.items()),
                             frozenset({'read': ('buzz_managers',),
                                        'add': ('buzz_add_managers',),
                                        'update': ('buzz_update_managers',),
                                        'delete': ('buzz_del_managers',)}.items()))

    def test_in_container_rdef_permissions(self):
        in_crdef = self.schema['transverse_ents'].rdef('ChildEnt', 'TranschildEnt')
        self.assertEqual(frozenset(in_crdef.permissions.items()),
                         frozenset({'read': ('fizz_managers',),
                                    'add': ('fizz_add_managers',),
                                    'delete': ('fizz_del_managers',)}.items()))

    def test_near_container_rdef_permissions(self):
        near_crdefs = (self.schema['children_ents'].rdef('CollaborativeEntityWithPermissions', 'ChildEnt'),
                       self.schema['transchildren_ents'].rdef('CollaborativeEntityWithPermissions', 'TranschildEnt'))
        for near_crdef in near_crdefs:
            self.assertEqual(frozenset(near_crdef.permissions.items()),
                             frozenset({'read': ('fooz_managers',),
                                        'add': ('fooz_add_managers',),
                                        'delete': ('fooz_del_managers',)}.items()))

    def test_ignored_rdefs_permissions(self):
        ignored_rdefs = (self.schema['custom_transchildren'].rdef('CollaborativeEntityWithPermissions', 'CustomTransChild'),
                         self.schema['custom_transents'].rdef('ChildEnt', 'CustomTransChild'),
                         self.schema['related_top_entity'].rdef('OtherEnt', 'CollaborativeEntityWithPermissions'))
        custom_perms = ({'read': ('custom_managers',),'add': ('custom_add_managers',),
                         'delete': ('custom_del_managers',)},
                        {'read': ('subcustom_managers',),
                         'add': ('subcustom_add_managers',),
                         'delete': ('subcustom_del_managers',)},
                        {'read': ('othercustom_managers',),
                         'add': ('othercustom_add_managers',),
                         'delete': ('othercustom_del_managers',)})
        for rdef, perms in zip(ignored_rdefs, custom_perms):
            self.assertEqual(frozenset(rdef.permissions.items()),
                             frozenset(perms.items()))

if __name__ == '__main__':
    unittest_main()
