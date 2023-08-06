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

"""cubicweb-collaboration schema"""

from yams.buildobjs import RelationType


class can_read(RelationType):
    subject = 'CWUser'


class can_write(RelationType):
    subject = 'CWUser'


class frozen(RelationType):
    """Determine whether the collaborative entity can be updated or not."""
    object = 'Boolean'
    default = False


class collaborates_on(RelationType):
    subject = 'CWUser'
    cardinality = '**'


class clone_of(RelationType):
    cardinality = '?*'
    inlined = True
