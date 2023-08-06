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

"""cubicweb-collaboration entity's classes"""

from cubicweb.view import EntityAdapter
from cubicweb.entities.adapters import ITreeAdapter
from cubicweb.web.views.ibreadcrumbs import IBreadCrumbsAdapter
from cubicweb.predicates import adaptable, relation_possible

from cubes.container.entities import Container, ContainerClone

COLLABORATIVE_SELECTOR = (relation_possible('frozen') &
                          relation_possible('collaborates_on', role='object'))


class ClonableAdapter(ContainerClone):
    """ The concrete adapter needs to define the selector according to the
    clone rdef.

    See CollaborationConfiguration.build_collaboration_entities.
    """
    __abstract__ = True

    def clone(self, original=None):
        super(ClonableAdapter, self).clone(original)
        self.set_meta_relations()

    def set_meta_relations(self):
        """Set meta relations for entities in the cloned container.

        `owned_by` and `created_by` relations are not handled by
        cubicweb-container (see http://www.cubicweb.org/ticket/3589525).
        """
        creator = self.entity.creator
        owners = self.entity.owned_by
        rtype = self.entity.container_config.rtype
        for row in self.entity.related(rtype, role='object').rows:
            eid = row[0]
            for rel in ('owned_by', 'created_by'):
                self._cw.execute(
                    'DELETE X %s U WHERE X eid %%(x)s' % rel, {'x': eid})
                self._cw.execute(
                    'SET X %s U WHERE X eid %%(x)s, U eid %%(u)s' % rel,
                    {'x': eid, 'u': owners[0].eid})


class CollaborativeAdapter(EntityAdapter):
    __regid__ = 'ICollaborative'
    __select__ = COLLABORATIVE_SELECTOR

    @property
    def frozen(self):
        return self.entity.frozen

    def set_frozen(self, value):
        self.entity.cw_set(frozen=value)

    @property
    def clones(self):
        rtype, role = self.entity.cw_adapt_to('Container.clone').clone_rtype_role
        role = {'subject': 'object', 'object': 'subject'}[role]
        return self.entity.related(rtype, role=role, entities=True)

    @property
    def collaborators(self):
        return self.entity.reverse_collaborates_on

    def set_collaborators(self, collab_list):
        self._cw.execute('DELETE X collaborates_on Y WHERE EXISTS(X collaborates_on Y, Y eid %(oeid)s)',
                         {'oeid': self.entity.eid})
        self.entity.cw_set(reverse_collaborates_on=collab_list)


class CollaborativeSecurityAdapter(EntityAdapter):
    __regid__ = 'ICollaborationSecurity'
    __select__ = (COLLABORATIVE_SELECTOR &
                  relation_possible('can_write', role='object'))

    def grant_permission(self, ueid, permission):
        """ Grants users can_read / can_write permissions on entities """
        assert permission in ('read', 'write')
        if permission == 'write':
            self._cw.execute('SET U can_write W WHERE '
                             'U eid %(u)s, W eid %(w)s, NOT U can_write W',
                             {'u': ueid, 'w': self.entity.eid})
        self._cw.execute('SET U can_read W WHERE '
                         'U eid %(u)s, W eid %(w)s, NOT U can_read W',
                         {'u': ueid, 'w': self.entity.eid})

    def revoke_permission(self, ueid, permission):
        """ Revokes users can_read / can_write permissions on entities """
        assert permission in ('read', 'write')
        self._cw.execute('DELETE U can_%s W WHERE U eid %%(u)s, W eid %%(w)s'
                         % permission, {'u': ueid, 'w': self.entity.eid})


class CollaborativeITreeAdapter(ITreeAdapter):
    """The concrete adapter needs to set the `tree_relation` attribute as well
    as the selector according to the clone relation.

    See CollaborationConfiguration.build_collaboration_entities.
    """
    __abstract__ = True
    parent_role = 'object'
    child_role = 'subject'


class CollaborativeIBreadCrumbsAdapter(IBreadCrumbsAdapter):
    """For collaborative entities, do not put all the path in the collaborative
    tree in the breadcrumbs. Thus, provide a ``parent_entity`` method which
    doesn't rely on the collaboration tree (``ITree``)'s parent method.

    """

    __select__ = IBreadCrumbsAdapter.__select__ & adaptable('ICollaborative')

    def parent_entity(self):
        """ Return nothing, so that in the breadcrumbs one only displays the
        link to the current entity and to the rset of entities of the same
        type.
        """
        return None
