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


from cubicweb import ValidationError, Unauthorized, NoSelectableObject
from cubicweb.web import Redirect
from cubicweb.devtools.testlib import CubicWebTC

from cubes.container import ContainerConfiguration

from cubes.collaboration.views import CloneAction, FreezeAction, UnfreezeAction
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

    def test_collaborative_breadcrumbs_for_collaborative_entities(self):
        req = self.request()
        entity = req.entity_from_eid(self.ce_eid)
        ibread_entity = entity.cw_adapt_to('IBreadCrumbs')
        self.assertEqual([entity], ibread_entity.breadcrumbs())
        one_child = entity.child_entities[0]
        ibread_child = one_child.cw_adapt_to('IBreadCrumbs')
        self.assertEqual([one_child], ibread_child.breadcrumbs())


class CollaborationActionsTC(CollaborationTC):

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

    def test_freeze_unfreeze(self):
        actions = self.vreg['actions']
        with self.do_as_user('author') as req:
            entity = req.entity_from_eid(self.ce_eid)
            freeze_action = actions.select('collaboration.freeze', req,
                                           rset=entity.as_rset())
            self.assertIsInstance(freeze_action, FreezeAction)
            with self.assertRaises(NoSelectableObject):
                unfreeze_action = actions.select('collaboration.unfreeze', req,
                                                 rset=entity.as_rset())
        self.setup_ce(freeze=True)
        with self.do_as_user('author') as req:
            entity = req.entity_from_eid(self.ce_eid)
            entity.cw_clear_all_caches()
            unfreeze_action = actions.select('collaboration.unfreeze', req,
                                             rset=entity.as_rset())
            self.assertIsInstance(unfreeze_action, UnfreezeAction)
            with self.assertRaises(NoSelectableObject):
                freeze_action = actions.select('collaboration.freeze', req,
                                               rset=entity.as_rset())


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
        req = self.request()
        user_1 = self.users(u'1')
        # Add a collaborator
        self.setup_ce(freeze=True, collaborators=user_1)
        entity = req.entity_from_eid(self.ce_eid)
        adapter = entity.cw_adapt_to('ICollaborative')
        # Check the collaborator is the only collaborator
        self.assertEqual([adapter.collaborators[0].eid], user_1)
        user_2 = self.users(u'2')
        # Add another collaborator
        self.setup_ce(collaborators=user_2)
        entity.cw_clear_all_caches()
        # Check this other collaborator is now the only collaborator
        self.assertEqual([adapter.collaborators[0].eid], user_2)
        entity.cw_clear_all_caches()
        # Pick up two collaborators
        users_1_2 = self.users(u'[12]')
        # Check that we really have two collaborators
        self.assertEqual([user for user in users_1_2],
                         [user_1[0], user_2[0]])
        # Add these two collaborators
        self.setup_ce(collaborators=users_1_2)
        # Check that these two collaborators are now the only collaborators
        self.assertEqual(frozenset(col.eid for col in adapter.collaborators),
                         frozenset(users_1_2))

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

    def test_owners_can_freeze_unfreeze_container(self):
        owners = self.users(u'[0-2]')
        self.setup_ce_owners(owners)
        # Check each owner can freeze and unfreeze the entity,
        # can edit the entity while unfrozen and cannot edit it while frozen,
        # except for unfreezeing it;
        for owner_eid in owners:
            self.setup_ce(as_user=owner_eid, name=u'my own name')
            self.setup_ce(as_user=owner_eid, freeze=True)
            self.assert_setup_ce_raises(Unauthorized, as_user=owner_eid,
                                        name=u'my own new name')
            self.setup_ce(as_user=owner_eid, freeze=False)
            self.setup_ce(as_user=owner_eid, name=u'my own new name')

    def test_owners_can_clone_and_cannot_unfreeze_if_clones(self):
        owners = self.users(u'[0-2]')
        self.setup_ce_owners(owners)
        admin_req = self.request()
        for nb_clones, owner_eid in enumerate(owners):
            # Check if not already frozen
            entity = admin_req.entity_from_eid(self.ce_eid)
            # clear cache to update frozen
            entity.cw_clear_all_caches()
            if entity.frozen != True:
                self.setup_ce(as_user=owner_eid, freeze=True)
            clone_eid = self.clone_ce(owner_eid, clone_rtype=self.clone_rtype,
                                      clone_name=u'%s\'s new name' % owner_eid)
            collab_ent = admin_req.entity_from_eid(self.ce_eid)
            adapted_ent = collab_ent.cw_adapt_to('ICollaborative')
            self.assertEqual(len(adapted_ent.clones), 1 + nb_clones)
            clone_ent = admin_req.entity_from_eid(clone_eid)
            original = getattr(clone_ent, self.clone_rtype)
            self.assertEqual(len(original), 1)
            self.assertEqual(original[0].eid, self.ce_eid)
            self.assert_setup_ce_raises(Unauthorized, as_user=owner_eid, freeze=False)

    def test_owners_can_delete_own_clone(self):
        owners = self.users(u'[0-2]')
        self.setup_ce_owners(owners)
        admin_req = self.request()
        entity = admin_req.entity_from_eid(self.ce_eid)
        for owner_eid in owners:
            # Check if not already frozen
            # clear cache to update frozen
            entity.cw_clear_all_caches()
            if entity.frozen != True:
                self.setup_ce(as_user=owner_eid, freeze=True)
            clone_eid = self.clone_ce(owner_eid, clone_rtype=self.clone_rtype,
                                      clone_name=u'%s\'s new name' % owner_eid)
            with self.userlogin(admin_req.entity_from_eid(owner_eid).login) as cnx:
                req = cnx.request()
                clone_etype = req.entity_from_eid(clone_eid).cw_etype
                req.execute('DELETE %(cetype)s X WHERE X eid %%(ceid)s'
                            % {'cetype': clone_etype},
                            {'ceid': clone_eid})
                cnx.commit()

    def test_owners_cannot_delete_others_clones(self):
        owners = self.users(u'[0-2]')
        self.setup_ce_owners(owners)
        admin_req = self.request()
        entity = admin_req.entity_from_eid(self.ce_eid)
        for owner_eid in owners:
            # Check if not already frozen
            # clear cache to update frozen
            entity.cw_clear_all_caches()
            if entity.frozen != True:
                self.setup_ce(as_user=owner_eid, freeze=True)
            clone_eid = self.clone_ce(owner_eid, clone_rtype=self.clone_rtype,
                                      clone_name=u'%s\'s new name' % owner_eid)
            with self.userlogin(admin_req.entity_from_eid(owner_eid).login) as cnx:
                req = cnx.request()
                clone_etype = req.entity_from_eid(clone_eid).cw_etype
                # get clones not owned by current owner
                rql = ('Any E WHERE X is %(cetype)s, X eid E, '
                       'EXISTS(X %(clone_rtype)s Y), '
                       'NOT X owned_by U, U eid %%(ueid)s'
                       % {'cetype': clone_etype,
                          'clone_rtype': self.clone_rtype})
                other_clones = admin_req.execute(rql, {'ueid': owner_eid}).rows
                for other_clone in (oc[0] for oc in other_clones):
                    with self.assertRaises(Unauthorized):
                        req.execute('DELETE %(cetype)s X WHERE X eid %%(ceid)s'
                                    % {'cetype': clone_etype},
                                    {'ceid': other_clone})
                        cnx.commit()
                    cnx.rollback()

    def test_former_owners_cannot_read_unless_collaborators(self):
        owners = self.users(u'[0-2]')
        self.setup_ce_owners(owners)
        admin_req = self.request()
        entity = admin_req.entity_from_eid(self.ce_eid)
        self.setup_ce(collaborators=owners[0])
        for owner_eid in owners:
            admin_req.execute('DELETE X owned_by U WHERE X eid %(eeid)s, U eid %(ueid)s',
                              {'eeid': self.ce_eid, 'ueid': owner_eid})
            self.commit()
            self.assert_setup_ce_raises(Unauthorized, as_user=owner_eid, name=u'my other_name')
            with self.userlogin(admin_req.entity_from_eid(owner_eid).login) as cnx:
                req = cnx.request()
                if owner_eid == owners[0]:
                    my_entity = req.execute('Any X WHERE X eid %(eeid)s',
                                            {'eeid': self.ce_eid}).get_entity(0, 0)
                    self.assertEqual(my_entity.cw_etype, entity.cw_etype)
                    self.assertEqual(frozenset(ch.eid for ch in my_entity.child_entities),
                                     frozenset(ch.eid for ch in  entity.child_entities))
                else:
                    with self.assertRaises(Unauthorized):
                        req.execute('Any X WHERE X eid %(eeid)s', {'eeid': self.ce_eid})

    def test_owners_can_edit_collaborators(self):
        owners = self.users(u'[0-2]')
        self.setup_ce_owners(owners)
        entity = self.request().entity_from_eid(self.ce_eid)
        adapted = entity.cw_adapt_to('ICollaborative')
        for owner_eid in owners:
            self.setup_ce(as_user=owner_eid, collaborators=())
            entity.cw_clear_all_caches()
            self.assertEqual(len(adapted.collaborators), 0)
            self.setup_ce(as_user=owner_eid, collaborators=owners[:2])
            entity.cw_clear_all_caches()
            self.assertEqual(frozenset(c.eid for c in adapted.collaborators),
                             frozenset(owners[:2]))




if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
