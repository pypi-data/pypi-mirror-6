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

"""cubicweb-vcwiki restructured text rendering tests"""


from utils import VCWikiTC


class VCWikiViewTC(VCWikiTC):

    base_url = u'http://testing.fr/cubicweb/wiki/vcwiki'

    def wiki_view(self, path, **form):
        req = self.request()
        req.form = {'wikipath': path}
        req.form.update(form)
        vcwiki = req.entity_from_eid(self.vcwiki.eid)
        return self.view('vcwiki.view_page', vcwiki.as_rset(), req=req)

    def assertEntitled(self, expected_title, html):
        self.assertEqual([u'vcwiki - %s' % expected_title],
                         html.find_tag('title'))

    def assertHasLink(self, text, html, url_path, klass):
        attrs = {'class': klass, 'href': self.base_url + url_path}
        links = tuple(html.matching_nodes('a', **attrs))
        self.assertTrue(1, len(links))
        self.assertTrue(text, links[0].text)

    def test_existing_wiki_page(self):
        html = self.wiki_view('subject2/content2')
        self.assertEntitled('content2', html)
        self.assertTrue('content of subject2/content2.rst' in html)

    def test_existing_wiki_page_with_revision(self):
        req = self.request()
        # Check test prerequisite
        vc0 = self.vcwiki.content('hello.rst', revision=0)
        vc1 = self.vcwiki.content('hello.rst') # last revision
        new_words = 'modified since its creation'
        self.assertFalse(new_words in vc0.data.getvalue())
        self.assertTrue(new_words in vc1.data.getvalue())
        # Check new added content is not present in the view of the old revision
        html = self.wiki_view('hello.rst', rev='0')
        self.assertFalse(new_words in html)

    def test_non_existing_wiki_page(self):
        html = self.wiki_view('does_not_exist')
        self.assertEntitled('New wiki page', html)
        self.assertTrue('This wiki page does not exist.' in html)
        self.assertTrue(html.has_link('Create this wiki page?'))

    def test_link_to_existing_page(self):
        html = self.wiki_view('with_links.rst')
        self.assertHasLink('link to content1', html,
                           u'/subject1/content1.rst', u'reference')

    def test_link_to_non_existing_page(self):
        html = self.wiki_view('with_links.rst')
        self.assertHasLink('link to non-existing page', html,
                           u'/does_not_exist', u'doesnotexist reference')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
