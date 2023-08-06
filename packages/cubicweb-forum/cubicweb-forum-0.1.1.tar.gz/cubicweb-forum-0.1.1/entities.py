# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-forum entity's classes"""

from cubicweb.predicates import is_instance

from cubicweb.entities import AnyEntity
from cubicweb.entities.adapters import ITreeAdapter


class Forum(AnyEntity):
    __regid__ = 'Forum'

    @property
    def last_activity_date(self):
        return self._cw.execute(
            'Any MAX(MD) WHERE T modification_date MD, T? in_forum F, '
            'F eid %(eid)s', {'eid': self.eid})[0][0]


class ForumThread(AnyEntity):
    __regid__ = 'ForumThread'


class ForumITreeAdapter(ITreeAdapter):
    __select__ = is_instance('ForumThread')
    tree_relation = 'in_forum'

