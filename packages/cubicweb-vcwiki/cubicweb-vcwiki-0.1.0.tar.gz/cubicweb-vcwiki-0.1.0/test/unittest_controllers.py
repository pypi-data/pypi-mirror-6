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

"""cubicweb-vcwiki controllers' tests"""

from os import path as osp

from cubicweb.web import Redirect

from utils import VCWikiTC


class VCWikiViewControllerTC(VCWikiTC):

    def publish_wiki_path(self, path, wikiid='vcwiki'):
        req = self.request()
        req.form = {'wikiid': wikiid, 'wikipath': path}
        return self.ctrl_publish(req, ctrl='wiki')

    def test_wiki_does_not_exist(self):
        self.assertTrue('no access to this view'
                        in self.publish_wiki_path('', wikiid='does_not_exist'))

    def test_wiki_page(self):
        self.assertTrue('content of subject2/content2'
                        in self.publish_wiki_path('subject2/content2'))

    def test_image(self):
        repo_path = self.vcwiki.repository.path
        fname = '120px-Crystal_Clear_app_kedit.png'
        image = self.publish_wiki_path(fname)
        with open(osp.join(repo_path, fname)) as image_file:
            self.assertEqual(image, image_file.read(),
                             'wrong image content delivery')


class VCWikiEditControllerTC(VCWikiTC):

    def setup_database(self):
        super(VCWikiEditControllerTC, self).setup_database()
        req = self.request()
        rql = 'Any X WHERE X is CWGroup, X name "managers"'
        managers = req.execute(rql).get_entity(0, 0)
        req.create_entity('CWPermission',
                          name=u'write',
                          label=u'vcwiki write',
                          require_group=managers,
                          reverse_require_permission=self.vcwiki.repository)
        self.commit()

    def vcwiki_edit(self, path, content=u'new content'):
        req = self.request()
        req.form = {'vcwiki_eid': self.vcwiki.eid,
                    'wikipath': path,
                    'content': content,
                    'message': u'my commit'}
        self.ctrl_publish(req, ctrl='vcwiki.edit_page')
        if content:
            vcontent = self.vcwiki.content(path)
            self.assertEqual(content,
                             vcontent.data.getvalue())

    def test_creation(self):
        self.vcwiki_edit(u'newsubject/dummy')

    def test_edition(self):
        self.vcwiki_edit(u'subject2/content2')

    def test_deletion(self):
        self.vcwiki_edit(u'subject2/content2', content=u'')
        vcontent = self.vcwiki.content(u'subject2/content2',
                                       allow_deleted=True)
        self.assertEqual(str(vcontent.e_schema), 'DeletedVersionContent')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
