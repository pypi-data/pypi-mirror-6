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


class GrantOwnersPermissions(Hook):
    """Grant read/write permissions to the owners of the collaborative
    entity."""
    __regid__ = 'collaboration.set_owners_permissions'
    __select__ = Hook.__select__ &  match_rtype('owned_by')
    events = ('after_add_relation',)

    def __call__(self):
        adapted = self._cw.entity_from_eid(self.eidfrom).cw_adapt_to('ICollaborationSecurity')
        if adapted:
            # Else the collaborative entity does not support security
            # relations.
            adapted.grant_permission(self.eidto, 'write')


class RevokeOwnersPermissions(Hook):
    """Revoke read and write permissions for users who do not own the collaborative
    entity anymore."""
    __regid__ = 'collaboration.revoke_owners_permissions'
    __select__ = Hook.__select__ &  match_rtype('owned_by')
    events = ('after_delete_relation',)

    def __call__(self):
        entity = self._cw.entity_from_eid(self.eidfrom)
        adapted = entity.cw_adapt_to('ICollaborationSecurity')
        if adapted:
            # Else the collaborative entity does not support security
            # relations.
            adapted.revoke_permission(self.eidto, 'write')
            c_adapted = entity.cw_adapt_to('ICollaborative')
            if self.eidto not in (user.eid for user in c_adapted.collaborators):
                adapted.revoke_permission(self.eidto, 'read')


class CanEditContainerHook(Hook):
    __regid__ = 'canedit-collaborative-container'
    __select__ = Hook.__select__ & adaptable('ICollaborative')
    events = ('before_update_entity',)

    def __call__(self):
        entity = self.entity
        if 'frozen' in entity.cw_edited:
            for owner in entity.owned_by:
                SetContainerWritePermOperation.get_instance(self._cw).add_data(
                    (owner.eid, entity.frozen, entity.eid))


class SetContainerWritePermOperation(DataOperationMixIn, Operation):

    def precommit_event(self):
        for ueid, frozen, ce_eid in self.get_data():
            if (self.session.deleted_in_transaction(ueid)
                or self.session.deleted_in_transaction(ce_eid)):
                continue
            c_ent = self.session.entity_from_eid(ce_eid)
            adapted = c_ent.cw_adapt_to('ICollaborationSecurity')
            if adapted:
                if frozen:
                    adapted.revoke_permission(ueid, 'write')
                else:
                    adapted.grant_permission(ueid, 'write')


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
        entity = self._cw.entity_from_eid(self.eidto)
        adapted = entity.cw_adapt_to('ICollaborationSecurity')
        if self.eidfrom not in (u.eid for u in entity.owned_by):
            adapted.revoke_permission(self.eidfrom, 'read')


