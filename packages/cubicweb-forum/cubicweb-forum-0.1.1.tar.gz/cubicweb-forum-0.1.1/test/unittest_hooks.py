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

"""unittests for hooks of cubicweb-forum"""

from cubicweb.devtools.testlib import CubicWebTC


class SetModificationDateTC(CubicWebTC):

    def setup_database(self):
        forum = self.request().create_entity(
            'Forum', topic=u'Meteo', description=u'La pluie et le beau temps')
        self.thread = self.request().create_entity(
            'ForumThread', title=u"quel temps ce week-end?",
            content=u"en Bretagne", in_forum=forum)

    def test_depth1(self):
        req = self.request()
        md = self.thread.modification_date
        c = req.create_entity('Comment', content=u"Yo",
                              comments=self.thread.eid)
        self.commit()
        self.thread.cw_clear_all_caches()
        self.assertGreater(self.thread.modification_date, md)

    def test_depth2(self):
        """Check subcomments
        Also check that intermediate comments are not modified"""
        req = self.request()
        c1 = req.create_entity('Comment', content=u"Moche",
                               comments=self.thread.eid)
        self.commit()
        bmd = self.thread.modification_date
        cmd = c1.modification_date
        c2 = req.create_entity('Comment', content=u"Pluie bien sûr",
                               comments=c1.eid)
        self.commit()
        self.thread.cw_clear_all_caches()
        c1.cw_clear_all_caches()
        self.assertGreater(self.thread.modification_date, bmd)
        self.assertEqual(c1.modification_date, cmd)


class NosylistTC(CubicWebTC):

    def setup_database(self):
        req = self.request()
        self.forum_eid = req.create_entity('Forum', topic=u'Wine').eid
        self.create_user(req, u'fcayre')

    def nosy_logins(self, entity):
        return [u.login for u in entity.nosy_list]

    def test_create(self):
        self.commit()
        forum = self.request().entity_from_eid(self.forum_eid)
        self.assertTrue('admin' in self.nosy_logins(forum))

    def test_add_thread(self):
        with self.login(u'fcayre'):
            req = self.request()
            thread = req.create_entity('ForumThread', title=u'Bourgogne',
                                       content=u'...', in_forum=self.forum_eid)
            self.commit()
            self.assertTrue('fcayre' in self.nosy_logins(thread))

    def test_add_comment(self):
        req = self.request()
        thread = req.create_entity('ForumThread', title=u'Bourgogne',
                                   content=u'...', in_forum=self.forum_eid)
        self.commit()
        self.assertFalse('fcayre' in self.nosy_logins(thread))
        with self.login(u'fcayre'):
            req = self.request()
            c = req.create_entity('Comment', content=u'miam',
                                  comments=thread.eid)
            self.commit()
            thread = c.comments[0]
            self.assertTrue('fcayre' in self.nosy_logins(thread))

    def test_reply_to_comment(self):
        req = self.request()
        thread = req.create_entity('ForumThread', title=u'Bourgogne',
                                   content=u'...', in_forum=self.forum_eid)
        c1 = req.create_entity('Comment', content=u'miam',
                               comments=thread.eid)
        self.commit()
        self.assertFalse('fcayre' in self.nosy_logins(thread))
        with self.login(u'fcayre'):
            req = self.request()
            c2 = req.create_entity('Comment', content=u'miam',
                                   comments=c1.eid)
            self.commit()
            thread = c2.comments[0].comments[0]
            self.assertTrue('fcayre' in self.nosy_logins(thread))


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
