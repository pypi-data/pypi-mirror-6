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

"""cubicweb-collaboration specific hooks and operations"""

from yams.schema import role_name

from cubicweb import ValidationError, Unauthorized
from cubicweb.server.hook import Hook, Operation, DataOperationMixIn, match_rtype
from cubicweb.predicates import adaptable, yes


class CollaborativeEntityDontEditIfFrozen(Hook):
    # TODO : rearrange the cases in the `if`s
    """ Cannot edit if frozen """
    __regid__ = "collaborative-entity-dont-edit"
    __select__ = Hook.__select__ & adaptable('ICollaborative')
    events = ('before_update_entity',)

    def __call__(self):
        adapter = self.entity.cw_adapt_to('ICollaborative')
        if bool(adapter.clones):
            raise Unauthorized(self._cw._('Cannot modify the frozen and cloned entity'))
        if adapter.frozen and 'frozen' not in self.entity.cw_edited:
            raise Unauthorized(self._cw._('Cannot modify the frozen entity'))


class SetCreatorPermissions(Hook):
    """Set the read/write permissions for the creator of the collaborative
    entity."""
    __regid__ = 'collaboration.set_creator_permissions'
    __select__ = Hook.__select__ & adaptable('ICollaborative')
    events = ('after_add_entity', )

    def __call__(self):
        adapted = self.entity.cw_adapt_to('ICollaborationSecurity')
        if adapted:
            # Else the collaborative entity does not support security
            # relations.
            adapted.grant_permission(self._cw.user.eid, 'write')


class CanEditContainerHook(Hook):
    __regid__ = 'canedit-collaborative-container'
    __select__ = Hook.__select__ & adaptable('ICollaborative')
    events = ('before_update_entity',)

    def __call__(self):
        entity = self.entity
        # XXX To loop over the owners
        owner_eid = entity.owned_by[0].eid
        if 'frozen' in entity.cw_edited:
            if entity.frozen:
                CannotEditContainerOperation.get_instance(self._cw).add_data((owner_eid, entity.eid))
            else:
                CanEditContainerOperation.get_instance(self._cw).add_data((owner_eid, entity.eid))


class CanEditContainerOperation(DataOperationMixIn, Operation):

    def precommit_event(self):
        for ueid, ce_eid in self.get_data():
            if self.session.deleted_in_transaction(ueid) or self.session.deleted_in_transaction(ce_eid):
                continue
            adapted = self.session.entity_from_eid(ce_eid).cw_adapt_to('ICollaborationSecurity')
            adapted.grant_permission(ueid, 'write')


class CannotEditContainerOperation(DataOperationMixIn, Operation):

    def precommit_event(self):
        for ueid, ce_eid in self.get_data():
            if self.session.deleted_in_transaction(ueid) or self.session.deleted_in_transaction(ce_eid):
                continue
            adapted = self.session.entity_from_eid(ce_eid).cw_adapt_to('ICollaborationSecurity')
            if adapted:
                # Else the collaborative entity does not support security
                # relations.
                adapted.revoke_permission(ueid, 'write')


class GrantReadCollaboratorsHook(Hook):
    __regid__ = 'grant-read-collaborators'
    __select__ = Hook.__select__ & match_rtype('collaborates_on')
    events = ('before_add_relation',)

    def __call__(self):
        adapted = self._cw.entity_from_eid(self.eidto).cw_adapt_to('ICollaborationSecurity')
        adapted.grant_permission(self.eidfrom, 'read')


class RevokeReadCollaboratorsHook(Hook):
    __regid__ = 'revoke-read-collaborators'
    __select__ = Hook.__select__ & match_rtype('collaborates_on')
    events = ('after_delete_relation',)

    def __call__(self):
        adapted = self._cw.entity_from_eid(self.eidto).cw_adapt_to('ICollaborationSecurity')
        adapted.revoke_permission(self.eidfrom, 'read')


