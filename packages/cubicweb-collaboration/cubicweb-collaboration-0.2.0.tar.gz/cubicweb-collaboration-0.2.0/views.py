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

"""cubicweb-collaboration views/forms/actions/components for web ui"""
import json

from logilab.mtconverter import xml_escape

from cubicweb.predicates import is_instance
from cubicweb.web.views.treeview import TreeViewItemView
from cubicweb.web.views.baseviews import OneLineView
from cubicweb.web.views.actions import CopyAction


from cubicweb.predicates import (adaptable, one_line_rset, has_permission,
                                 score_entity, rql_condition, match_user_groups)
from cubicweb.web import action, Redirect, component
from cubicweb.view import EntityView
from cubicweb.web.views import primary, uicfg, editcontroller

_pvs = uicfg.primaryview_section

_pvs.tag_object_of(('CWUser', 'collaborates_on', '*'), 'attributes')


def is_frozen(entity):
    adapted = entity.cw_adapt_to('ICollaborative')
    if adapted is not None:
        return int(adapted.frozen)
    return 0


def is_unfrozen(entity):
    adapted = entity.cw_adapt_to('ICollaborative')
    if adapted is not None:
        return int(not adapted.frozen)
    return 0


def cloned(entity):
    adapted = entity.cw_adapt_to('ICollaborative')
    if adapted is not None:
        return 1 if adapted.clones else 0
    return 0


def not_cloned(entity):
    adapted = entity.cw_adapt_to('ICollaborative')
    if adapted is not None:
        return 0 if adapted.clones else 1
    return 0


class FreezeAction(action.Action):
    __regid__ = 'collaboration.freeze'
    __select__ = (action.Action.__select__ & score_entity(is_unfrozen)
                  & has_permission('update'))
    title = _('freeze')
    category = 'moreactions'
    order = 28

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return entity.absolute_url(vid='collaboration.freeze-unfreeze')


class UnfreezeAction(action.Action):
    __regid__ = 'collaboration.unfreeze'
    # match_user_groups('owners') in the selector because the CanEditContainerHook
    # revokes the write permission once the entity is frozen, and it suffices
    # to be an owner of a not cloned frozen entity, to be able to unfreeze it
    __select__ = (action.Action.__select__ & score_entity(is_frozen) &
                  score_entity(not_cloned) & match_user_groups('owners'))
    title = _('unfreeze')
    category = 'moreactions'
    order = 29

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return entity.absolute_url(vid='collaboration.freeze-unfreeze', value='false')


class FreezeUnfreezeView(EntityView):
    __regid__ = 'collaboration.freeze-unfreeze'
    __select__ = (EntityView.__select__ &
                  adaptable('ICollaborative'))

    def entity_call(self, entity, **kwargs):
        frozen = json.loads(self._cw.form.get('value', 'true'))
        entity.cw_adapt_to('ICollaborative').set_frozen(frozen)
        if frozen:
            msg = self._cw._('%s is now frozen') % entity.dc_title()
        else:
            msg = self._cw._('%s is now unfrozen') % entity.dc_title()
        raise Redirect(entity.absolute_url(__message=msg))


class CloneAction(CopyAction):
    """Just a copy action (copy is handled by edit controller below) named 'clone'."""
    __select__ = (CopyAction.__select__ & one_line_rset() &
                  adaptable('ICollaborative') &
                  score_entity(is_frozen) & has_permission('add'))
    title = _('clone')

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        rtype, role = entity.cw_adapt_to('Container.clone').clone_rtype_role
        linkto = '%s:%s:%s' % (rtype, entity.eid, role)
        return entity.absolute_url(vid='copy', __linkto=linkto)


CopyAction.__select__ &= ~adaptable('ICollaborative')


class CollaborativeCloneTreeView(component.EntityCtxComponent):
    context = 'left'
    __regid__ = 'collaboration.treeview-ctx'
    order = 31
    title = _('collaborative tree')
    __select__ = (component.EntityCtxComponent.__select__ &
                  adaptable('ICollaborative'))

    def render_body(self, w):
        root = self.entity.cw_adapt_to('ITree').root()
        root.view('treeview', w=w, subvid='collaboration.current-entity',
                  current_entity=self.entity.eid)


class CurrentCollaborativeEntityView(EntityView):
    __regid__ = 'collaboration.current-entity'
    __select__ = (EntityView.__select__ &
                  adaptable('ICollaborative'))

    def cell_call(self, row, col, **morekwargs):
        entity = self.cw_rset.get_entity(row, col)
        current_entity = morekwargs.get('current_entity')
        self.w(self.html(entity, current_entity))

    def creator_html(self, entity):
        creator = entity.created_by[0]
        if creator.eid == self._cw.user.eid:
            return u''
        else:
            return u'<span class="creator">%s</span>' % creator.view('oneline')

    def entity_html(self, entity, current_entity):
        if entity.eid == current_entity:
            return xml_escape(entity.dc_title())
        else:
            return entity.view('oneline')

    def html(self, entity, current_entity):
        html = self.entity_html(entity, current_entity)
        creator_html = self.creator_html(entity)
        if creator_html:
            html += u' (%s)' % creator_html
        return html


class CollaborativeTreeItemView(TreeViewItemView):
    __select__ = (TreeViewItemView.__select__ &
                  adaptable('ICollaborative'))
    default_branch_state_is_open = True
