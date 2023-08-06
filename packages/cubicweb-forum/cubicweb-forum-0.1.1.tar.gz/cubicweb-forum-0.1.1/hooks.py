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

"""cubicweb-forum specific hooks and operations"""

from datetime import datetime

from cubicweb.server import hook
from cubes.nosylist import hooks as nosylisthooks


class SetModificationDateAfterAddComment(hook.Hook):
    """update all parent entities modification date after adding a comment"""
    __regid__ = 'forum.set_modification_date_after_comment'
    events = ('after_add_relation',)
    __select__ = (hook.Hook.__select__ &
                  hook.match_rtype('comments',
                                   toetypes=['ForumThread', 'Comment']))

    def __call__(self):
        entity = self._cw.entity_from_eid(self.eidto)
        while entity.e_schema == 'Comment':
            entity = entity.cw_adapt_to('ITree').root()
        entity.cw_set(modification_date=datetime.now())


# nosylist configuration

nosylisthooks.S_RELS |= set(('in_forum',))
nosylisthooks.O_RELS |= set(('comments',))


class SetNosyListBeforeAddComment(hook.Hook):
    """automatically add user who adds a comment to the nosy list"""
    __regid__ = 'forum.set_nosylist_after_add_comment'
    events = ('after_add_relation',)
    __select__ = hook.Hook.__select__ & hook.match_rtype('comments',)

    def __call__(self):
        if self._cw.is_internal_session:
            return
        comment = self._cw.entity_from_eid(self.eidfrom)
        entity = comment.cw_adapt_to('ITree').root()
        if str(entity.e_schema) == 'ForumThread':
            self._cw.execute('SET X nosy_list U WHERE X eid %(x)s, U eid %(u)s,'
                             'NOT X nosy_list U',
                             {'x': entity.eid, 'u': self._cw.user.eid})
