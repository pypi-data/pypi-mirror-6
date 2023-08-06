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

from contextlib import contextmanager


class CollaborationMixin(object):

    @contextmanager
    def userlogin(self, *args):
        cnx = self.login(*args)
        yield cnx
        self.restore_connection()

    @contextmanager
    def do_as_user(self, *args):
        '''
        Context manager that connects as user - given in positional
        arguments (see ``CubicWebTC.login``). The request object is
        returned. A commit is performed at exit.

        :Note: for convenience, if ``*args`` is a unique eid, the
               login is automatically retrieved.
        '''
        if len(args) == 1 and isinstance(args[0], int):
            login = self.request().entity_from_eid(args[0]).login
            args = (login,)

        cnx = self.login(*args)
        yield cnx.request()
        cnx.commit()
        self.restore_connection()

    def prepare_entities(self, etype, subetypes=(), otheretypes=()):
        req = self.request()
        self.create_user(req, 'author', groups=('users',), commit=True)
        for i in xrange(3):
            self.create_user(req, 'my_uname_%s' % i, groups=('users',), commit=True)
        with self.do_as_user('author') as req:
            self.ce_eid = req.create_entity(etype, name=u'My test entity',
                                            description=u'My description').eid
            for i in xrange(3):
                for subetype in subetypes:
                    child = req.create_entity(
                        subetype,
                        name=u'child %s %s' % (subetype, i),
                        description=u'Some description %s' % i,
                        reverse_child_entities=self.ce_eid
                    )
                    child_eid = child.eid
                    self.commit()
                    for j in xrange(3):
                        req.create_entity(
                            'Sub' + subetype,
                            name=u'sub-child %s %s of %s' % (subetype, j, i),
                            description=u'description %s of %s' % (j, i),
                            reverse_sub_children=child_eid
                        )
                for otheretype in otheretypes:
                    req.create_entity(
                        otheretype,
                        name=u'other %s %s' % (otheretype, i),
                        other_description=u'other description %s' % i,
                        reverse_other_entities=self.ce_eid
                    )
                    for j in xrange(3):
                        req.create_entity(
                            otheretype,
                            name=u'sub-other %s %s of %s' % (otheretype, j, i),
                            other_description=u'description %s of %s' % (j, i),
                            reverse_others=child_eid
                        )

    def users(self, rex=None):
        if rex is None:
            pattern = 'LIKE "my_uname_%"'
        elif rex == 'author':
            pattern = '"author"'
        else:
            pattern = 'REGEXP "my_uname_%s"' % rex
        rql = ('Any X WHERE X is CWUser, X login %(pattern)s' %
               {'pattern': pattern})
        return [row[0] for row in self.request().execute(rql)]

    def _setup_ce(self, req, collaborators=None, freeze=None,
                  **extra_attributes):
        entity = req.entity_from_eid(self.ce_eid)
        if extra_attributes:
            for attr in extra_attributes.iteritems():
                entity.cw_set(**dict([attr]))
        adapted = entity.cw_adapt_to('ICollaborative')
        if collaborators is not None:
            adapted.set_collaborators(collaborators)
        if freeze is not None:
            adapted.set_frozen(freeze)

    def setup_ce(self, as_user='author', freeze=None, collaborators=None, **extra_attributes):
        with self.do_as_user(as_user) as req:
            self._setup_ce(req,
                           freeze=freeze,
                           collaborators=collaborators,
                           **extra_attributes)

    def assert_setup_ce_raises(self, exception, as_user=None, freeze=None, collaborators=None,
                               **extra_attributes):
        if as_user is not None:
            login = self.request().entity_from_eid(as_user).login
        else:
            login = 'author'
        with self.userlogin(login) as cnx:
            req = cnx.request()
            with self.assertRaises(exception):
                self._setup_ce(req,
                               freeze=freeze,
                               collaborators=collaborators,
                               **extra_attributes)
                cnx.commit()
            cnx.rollback()

    def _clone_ce(self, req, clone_rtype='clone_of',
                  clone_name=u'My cloned entity'):
        entity = req.entity_from_eid(self.ce_eid)
        clone = req.create_entity(entity.cw_etype, name=clone_name,
                                  description=entity.description,
                                  **{clone_rtype: entity})
        return clone.eid

    def clone_ce(self, user_eid, clone_rtype, clone_name=u'My cloned entity'):
        with self.do_as_user(user_eid) as req:
            clone_eid = self._clone_ce(req, clone_rtype, clone_name=clone_name)
        return clone_eid

    def assert_clone_ce_raises(self, exception, user_eid, clone_rtype,
                               clone_name=u'My cloned entity'):
        login = self.request().entity_from_eid(user_eid).login
        with self.userlogin(login) as cnx:
            with self.assertRaises(exception):
                self._clone_ce(cnx.request(), clone_rtype, clone_name=clone_name)
                cnx.commit()
            cnx.rollback()

    def check_clone(self, clone_eid, creator_eid, clone_rtype='clone_of',
                    clone_name=u'My cloned entity',
                    child_entities=False, other_entities=False):
        test_ent = self.request().entity_from_eid(self.ce_eid)
        cloned_ent = self.request().entity_from_eid(clone_eid)
        self.assertEqual(cloned_ent.owned_by[0].eid, creator_eid)
        for entity in cloned_ent.reverse_in_collaborativeentity:
            self.assertEqual(entity.created_by[0].eid, creator_eid)
            self.assertEqual(entity.owned_by[0].eid, creator_eid)
        self.assertEqual(cloned_ent.owned_by[0].eid, creator_eid)
        self.assertTrue(test_ent.cw_adapt_to('ICollaborative').clones)
        self.assertEqual(test_ent.name, u'My test entity')
        self.assertEqual(cloned_ent.name, clone_name)
        self.assertEqual(getattr(cloned_ent, clone_rtype)[0].eid, test_ent.eid)
        self.assertNotEqual(cloned_ent.eid, test_ent.eid)
        self.assertEqual(cloned_ent.description, test_ent.description)

        getattr_entities = lambda entities, name: frozenset(getattr(_e, name)
                                                            for _e in entities)
        if child_entities:
            self.assertEqual(len(test_ent.child_entities),
                             len(cloned_ent.child_entities))
            self.assertFalse(
                getattr_entities(test_ent.child_entities, 'eid') &
                getattr_entities(cloned_ent.child_entities, 'eid')
            )
            self.assertEqual(
                getattr_entities(test_ent.child_entities, 'name'),
                getattr_entities(cloned_ent.child_entities, 'name')
            )
            self.assertEqual(
                getattr_entities(test_ent.child_entities, 'description'),
                getattr_entities(cloned_ent.child_entities, 'description')
            )

            test_sub_entities = [ent
                                 for ent in test_ent.child_entities
                                 for scent in ent.sub_children]
            cloned_sub_entities = [ent
                                   for ent in cloned_ent.child_entities
                                   for scent in ent.sub_children]
            self.assertFalse(
                getattr_entities(test_sub_entities, 'eid') &
                getattr_entities(cloned_sub_entities, 'eid')
            )
            self.assertEqual(
                getattr_entities(test_sub_entities, 'name'),
                getattr_entities(cloned_sub_entities, 'name')
            )
            self.assertEqual(
                getattr_entities(test_sub_entities, 'description'),
                getattr_entities(cloned_sub_entities, 'description')
            )
        if other_entities:
            self.assertEqual(len(test_ent.other_entities),
                             len(cloned_ent.other_entities))
            # links to the same entities for non-composite
            self.assertEqual(getattr_entities(test_ent.other_entities, 'eid'),
                             getattr_entities(cloned_ent.other_entities, 'eid'))
            if child_entities:

                test_other_entities = [scent
                                       for ent in test_ent.child_entities
                                       for scent in ent.others]
                cloned_other_entities = [scent
                                         for ent in cloned_ent.child_entities
                                         for scent in ent.others]
                # links to the same entities for non-composite
                self.assertEqual(
                    getattr_entities(test_other_entities, 'eid'),
                    getattr_entities(cloned_other_entities, 'eid')
                )
                self.assertEqual(
                    getattr_entities(test_other_entities, 'name'),
                    getattr_entities(cloned_other_entities, 'name')
                )
                self.assertEqual(
                    getattr_entities(test_other_entities, 'other_description'),
                    getattr_entities(cloned_other_entities, 'other_description')
                )

    def setup_ce_owners(self, owners):
        """Setup owners on the collaborative entity. """

        req = self.request()
        entity = req.entity_from_eid(self.ce_eid)
        entity.cw_set(owned_by=owners)
        self.commit()

