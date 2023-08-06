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

"""cubicweb-forum views/forms/actions/components for web ui"""

from cubicweb.predicates import is_instance

from cubicweb import view
from cubicweb.web.views import primary, baseviews


class ForumSameETypeListView(baseviews.SameETypeListView):
    __select__ = baseviews.SameETypeListView.__select__ & is_instance('Forum')

    def call(self, **kwargs):
        _ = self._cw._
        showtitle = kwargs.pop('showtitle', not 'vtitle' in self._cw.form)
        if showtitle:
            self.w(u'<h1>%s</h1>' % self.title)
        rset = self._cw.execute(
            'Any F,D,COUNT(T),F GROUPBY F,D WHERE F eid in (%s),'
            '   F description D, T? in_forum F'
            % ','.join(str(row[0]) for row in self.cw_rset))
        self.wview('table', rset=rset,
                   cellvids={3: 'forum_last_activity'},
                   headers=[_('Topic'), _('Description'),
                            _('Number of threads'), _('Last activity')])


class ForumLastActivity(view.EntityView):
    __regid__ = 'forum_last_activity'
    __select__ = view.EntityView.__select__ & is_instance('Forum')

    def entity_call(self, forum, **kwargs):
        date = forum.last_activity_date
        if date:
            self.w(self._cw.format_date(date, time=True))


class ForumPrimaryView(primary.PrimaryView):
    __select__ = primary.PrimaryView.__select__ & is_instance('Forum')

    def render_entity_attributes(self, entity):
        _ = self._cw._
        self.w(u'<div class="section">%s</div>' %
               entity.printable_value('description'))
        rset = self._cw.execute(
            "Any T,CD,COUNT(C),MD GROUPBY T,CD,MD ORDERBY MD DESC "
            "WHERE T in_forum F, F eid %(eid)s, T title D, C? comments T, "
            "      T modification_date MD, T creation_date CD",
            {"eid": entity.eid})
        if rset:
            self.w(u'<div class="section">')
            self.wview('table', rset=rset,
                       headers=[_('Subject'), _('Created'), _('Answers'),
                                _('Last answered')])
            self.w(u'</div>')
        else:
            self.w(u'<div class="searchMessage"><strong>%s</strong></div>\n'
                   % _('This forum does not have any thread yet.'))


class ForumThreadPrimaryView(primary.PrimaryView):
    __select__ = primary.PrimaryView.__select__ & is_instance('ForumThread')

    def render_entity_attributes(self, entity):
        self.w(u'<div class="section">%s</div>' %
               entity.printable_value('content'))
