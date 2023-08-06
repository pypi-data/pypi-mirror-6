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


from cubicweb import ValidationError, Unauthorized
from cubicweb.web import Redirect
from cubicweb.devtools.testlib import CubicWebTC

from cubes.container import ContainerConfiguration

from cubes.collaboration.views import CloneAction
from cubes.collaboration.testutils import CollaborationMixin


class CollaborationTC(CollaborationMixin, CubicWebTC):
    child_entities = True
    other_entities = True
    clone_rtype = 'clone_of_collaborative_entity'

    def setup_database(self):
        self.prepare_entities('CollaborativeEntity',
                              subetypes=('ChildEntity',),
                              otheretypes=('OtherEntity',))

class CollaborationSchemaTC(CollaborationTC):

    def test_collaborative_static_structure(self):
        collaborative_cfg = ContainerConfiguration('CollaborativeEntity',
                                                   'in_collaborative')
        self.assertEqual((frozenset(['child_entities', 'sub_children']),
                          frozenset(['ChildEntity', 'SubChildEntity'])),
                         collaborative_cfg.structure(self.vreg.schema))


class CollaborationEntityTC(CollaborationTC):

    def test_adapter_setters_act_on_the_adapted_entity(self):
        for value in (False, True):
            self.setup_ce(freeze=value)
            test_ent = self.request().entity_from_eid(self.ce_eid)
            self.assertEqual(test_ent.frozen, value)
        self.setup_ce(collaborators=self.users())
        test_ent = self.request().entity_from_eid(self.ce_eid)
        self.assertEqual(frozenset(user.eid for user in test_ent.reverse_collaborates_on),
                         frozenset(self.users()))

    def test_security_adapter_methods(self):
        admin_req = self.request()
        author = admin_req.execute('Any E LIMIT 1 WHERE X login "author", X eid E')[0][0]
        entity = admin_req.entity_from_eid(self.ce_eid)
        adapted = entity.cw_adapt_to('ICollaborationSecurity')
        # revoke read
        self.assertEqual(entity.reverse_can_read[0].eid, author)
        adapted.revoke_permission(author, 'read')
        entity.cw_clear_all_caches()
        self.assertEqual(len(entity.reverse_can_read), 0)
        # revoke write
        self.assertEqual(entity.reverse_can_write[0].eid, author)
        adapted.revoke_permission(author, 'write')
        entity.cw_clear_all_caches()
        self.assertEqual(len(entity.reverse_can_write), 0)
        # grant read
        self.assertEqual(len(entity.reverse_can_read), 0)
        adapted.grant_permission(author, 'read')
        entity.cw_clear_all_caches()
        self.assertEqual(entity.reverse_can_read[0].eid, author)
        # grant write; test write implies read (hence, revoke read first)
        adapted.revoke_permission(author, 'read')
        entity.cw_clear_all_caches()
        self.assertEqual(len(entity.reverse_can_read), 0)
        adapted.grant_permission(author, 'write')
        entity.cw_clear_all_caches()
        self.assertEqual(entity.reverse_can_write[0].eid, author)
        self.assertEqual(entity.reverse_can_read[0].eid, author)


class CollaborationCloneTC(CollaborationTC):

    def test_clone(self):
        self.setup_ce(freeze=True)
        with self.login('author'):
            req = self.request()
            entity = req.entity_from_eid(self.ce_eid)
            action = self.vreg['actions'].select('copy', req,
                                                 rset=entity.as_rset())
            self.assertIsInstance(action, CloneAction)
            clone_name = entity.name + ' (my clone)'
            req.form = {
                '__maineid' : 'X',
                'eid': 'X',
                '__cloned_eid:X': self.ce_eid,
                '__type:X': 'CollaborativeEntity',
                '_cw_entity_fields:X': ('name-subject,'
                                        'description-subject,'
                                        'clone_of_collaborative_entity-subject'),
                'name-subject:X': clone_name,
                'description-subject:X': entity.description,
                'clone_of_collaborative_entity-subject:X': self.ce_eid,
            }
            self.expect_redirect_handle_request(req, 'edit')
            # Ensure the clone now exists.
            clone = req.find_one_entity(
                'CollaborativeEntity', name=clone_name,
                clone_of_collaborative_entity=entity.eid)
        user_eid = self.users('author')[0]
        self.check_clone(clone.eid, user_eid,
                         clone_rtype = self.clone_rtype,
                         child_entities=self.child_entities,
                         other_entities=self.other_entities,
                         clone_name=clone_name)


class CollaborationPolicyTC(CollaborationTC):

    def test_author_can_clone_if_container_frozen(self):
        # XXX To put into container
        self.setup_ce(freeze=True)
        clone_eid = self.clone_ce('author', clone_rtype=self.clone_rtype)
        self.check_clone(clone_eid, self.users('author')[0],
                         clone_rtype=self.clone_rtype,
                         child_entities=self.child_entities,
                         other_entities=self.other_entities)

    def test_collaborators_can_clone_if_container_frozen(self):
        self.setup_ce(freeze=True, collaborators=self.users())
        for i, collaborator_eid in enumerate(self.users()):
            clone_eid = self.clone_ce(collaborator_eid, clone_rtype=self.clone_rtype,
                                      clone_name=u'My cloned entity_%s' % i)
            self.check_clone(clone_eid,
                             collaborator_eid,
                             clone_rtype=self.clone_rtype,
                             clone_name=u'My cloned entity_%s' % i,
                             child_entities=self.child_entities,
                             other_entities=self.other_entities)

    def test_cannot_clone_unless_collaborator_or_author(self):
        self.setup_ce(freeze=True, collaborators=self.users(u'0'))
        other_user_eids = self.users(u'[^0]')
        for i, user_eid in enumerate(other_user_eids):
            self.assert_clone_ce_raises(Unauthorized, user_eid, clone_rtype=self.clone_rtype,
                                        clone_name=u'My cloned entity_%s' % i)

    def test_cannot_unfreeze_after_clone(self):
        collaborator_eids = self.users('1')
        self.setup_ce(freeze=True, collaborators=collaborator_eids)
        self.clone_ce(collaborator_eids[0], clone_rtype=self.clone_rtype)
        self.assert_setup_ce_raises(Unauthorized, freeze=False)

    def test_cannot_clone_unless_frozen(self):
        test_ent = self.request().entity_from_eid(self.ce_eid)
        self.assertFalse(test_ent.cw_adapt_to('ICollaborative').frozen)
        self.assert_clone_ce_raises(ValidationError, self.users('author')[0], clone_rtype=self.clone_rtype)

    def test_cannot_edit_composite_rels_if_container_frozen(self):
        if self.child_entities:
            self.setup_ce(freeze=True)
            with self.do_as_user('author') as req:
                new_child = req.create_entity('ChildEntity',
                                              name=u'New child',
                                              description=u'new description')
                new_child_eid = new_child.eid # eid is context independent
            self.assert_setup_ce_raises(Unauthorized,
                                        child_entities=new_child_eid)

    def test_can_edit_composite_rels_if_container_not_frozen(self):
        if self.child_entities:
            self.setup_ce(freeze=False)
            with self.do_as_user('author') as req:
                new_child = req.create_entity('ChildEntity',
                                              name=u'New child',
                                              description=u'new description')
                new_child_eid = new_child.eid # eid is context independent
            self.setup_ce(child_entities=new_child_eid)

    def test_cannot_edit_sub_children_if_container_frozen(self):
        if self.child_entities:
            self.setup_ce(freeze=True)
            with self.userlogin('author') as cnx:
                req = cnx.request()
                one_child = req.entity_from_eid(self.ce_eid).child_entities[0]
                with self.assertRaises(Unauthorized):
                    req.create_entity('SubChildEntity',
                                      name=u'New sub-child',
                                      description=u'new sub-description',
                                      reverse_sub_children=one_child)
                    cnx.commit()

    def test_can_edit_sub_children_if_container_not_frozen(self):
        if self.child_entities:
            self.setup_ce(freeze=False)
            with self.do_as_user('author') as req:
                one_child = req.entity_from_eid(self.ce_eid).child_entities[0]
                req.create_entity('SubChildEntity',
                                  name=u'New sub-child',
                                  description=u'new sub-description',
                                  reverse_sub_children=one_child)

    def test_can_still_edit_non_composite_rels_if_container_frozen(self):
        # XXX Is this the right behavior?
        if self.other_entities:
            self.setup_ce(freeze=True)
            with self.do_as_user('author') as req:
                new_other = req.create_entity(
                    'OtherEntity',
                    name=u'New child',
                    other_description=u'new description'
                )
                new_other_eid = new_other.eid  # eid is context independent
            self.setup_ce(other_entities=new_other_eid)

    def test_cannot_edit_attributes_if_container_frozen(self):
        self.setup_ce(freeze=True)
        self.assert_setup_ce_raises(Unauthorized, name=u'Another, new name')

    def test_can_edit_attributes_if_container_not_frozen(self):
        self.setup_ce(freeze=False)
        self.setup_ce(name=u'Another, new name')

    def test_cannot_edit_sub_entities_if_container_frozen(self):
        if self.child_entities:
            self.setup_ce(freeze=True)
            with self.userlogin('author') as cnx:
                req = cnx.request()
                ent = req.entity_from_eid(self.ce_eid)
                children = ent.child_entities
                if children:
                    with self.assertRaises(Unauthorized):
                        children[0].cw_set(description=u'New child description')
                        cnx.commit()
                    cnx.rollback()

    def test_can_edit_collaborators_even_if_container_frozen(self):
        self.setup_ce(freeze=True, collaborators=self.users(u'1'))
        self.setup_ce(collaborators=self.users(u'2'))

    def test_cannot_read_unless_author_or_collaborator(self):
        self.setup_ce(collaborators=self.users(u'0'))
        other_user_eids = self.users(u'[^0]')
        for user_eid in other_user_eids:
            login = self.request().entity_from_eid(user_eid).login
            with self.userlogin(login) as cnx:
                req = cnx.request()
                with self.assertRaises(Unauthorized):
                    # req.entity_from_eid uses req.eid_rset that does not
                    # perform a real request and thus never raises Unauthorized
                    req.execute('Any X WHERE X eid %(eid)s',
                                {'eid': self.ce_eid})
                cnx.rollback()

    def test_author_can_edit_clone(self):
        self.setup_ce(freeze=True)
        author_eid = self.users('author')[0]
        clone_eid = self.clone_ce(author_eid, clone_rtype=self.clone_rtype)
        with self.do_as_user('author') as req:
            clone = req.entity_from_eid(clone_eid)
            clone.cw_set(name=u'New clone name')

    def test_collaborators_can_edit_clone(self):
        collaborator_eids = self.users()
        self.setup_ce(freeze=True, collaborators=collaborator_eids)
        for i, collaborator_eid in enumerate(collaborator_eids):
            clone_eid = self.clone_ce(collaborator_eid, clone_rtype=self.clone_rtype)
            with self.do_as_user(collaborator_eid) as req:
                clone = req.entity_from_eid(clone_eid)
                clone.cw_set(name=u'New clone name %s' % i)

    def test_collaborators_cannot_edit_container_even_if_not_frozen(self):
        collaborator_eids = self.users()
        self.setup_ce(collaborators=collaborator_eids, frozen=False)
        for i, collaborator_eid in enumerate(collaborator_eids):
            login = self.request().entity_from_eid(collaborator_eid).login
            with self.userlogin(login) as cnx:
                req = cnx.request()
                original_ent = req.entity_from_eid(self.ce_eid)
                with self.assertRaises(Unauthorized):
                    original_ent.cw_set(name=u'New name %s for the original' % i)
                    cnx.commit()
                cnx.rollback()


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
