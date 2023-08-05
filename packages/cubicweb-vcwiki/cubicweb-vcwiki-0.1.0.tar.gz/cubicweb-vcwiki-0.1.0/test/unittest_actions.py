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

"""cubicweb-vcwiki actions' tests"""

from utils import VCWikiTC


class VCWikiActionsTC(VCWikiTC):

    def wiki_actions(self, **form):
        req = self.request()
        req.form = form
        rset = req.execute('VCWiki X')
        return [a.__regid__
                for a in rset.possible_actions()
                if tuple(a.actual_actions())]

    def simple_user_wiki_actions(self, **form):
        self.create_user('toto')
        with self.login('toto'):
            return self.wiki_actions(**form)

    def test_wiki_actions(self):
        actions = self.simple_user_wiki_actions()
        self.assertTrue('vcwiki.view_home' in actions)

    def test_wiki_page_simple_user_actions(self):
        actions = self.simple_user_wiki_actions(wikipath=u'subject1/content1')
        self.assertFalse('edit' in actions)
        self.assertFalse('delete' in actions)
        self.assertFalse('vcwiki.view_history' in actions)

    def test_wiki_existing_page_authorized_user_actions(self):
        actions = self.wiki_actions(wikipath=u'subject1/content1')
        self.assertTrue('edit' in actions)
        self.assertTrue('delete' in actions)
        self.assertTrue('vcwiki.view_history' in actions)

    def test_wiki_non_existing_page_authorized_user_actions(self):
        actions = self.wiki_actions(wikipath=u'does_not_exist')
        self.assertFalse('edit' in actions)
        self.assertFalse('delete' in actions)
        self.assertFalse('vcwiki.view_history' in actions)


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
