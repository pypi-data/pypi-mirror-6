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

"""cubicweb-vcwiki test utilities"""

from os import path as osp
from shutil import rmtree

from logilab.common.shellutils import unzip

from cubes.vcsfile.testutils import VCSRepositoryTC

HERE = osp.dirname(__file__) or '.'

for repo in ('vcwiki',):
    repopath = osp.join(HERE, 'data', repo)
    if osp.exists(repopath):
        rmtree(repopath)
    unzip(osp.join(HERE, 'data', '%s.zip') % repo,  osp.join(HERE, 'data'))



class VCWikiTC(VCSRepositoryTC):
    _repo_path = u'vcwiki'

    def setup_database(self):
        # insert vcwiki
        self.vcwiki = self.execute(
            'INSERT VCWiki W: W name "vcwiki", W content_repo R, '
            'W content_file_extension "rst" '
            'WHERE R is Repository').get_entity(0, 0)
        # insert repository write permission for managers
        self.execute('INSERT CWPermission P: P name "write", P label "w p", '
                     'P require_group G, R require_permission P '
                     'WHERE R eid %(r)s, G name "managers"',
                     {'r': self.vcwiki.repository.eid})
        self.cleanup_repo()

    def cleanup_repo(self):
        if osp.exists(self.vcwiki.repository.path):
            rmtree(self.vcwiki.repository.path)
        unzip(self.datapath('vcwiki.zip'), self.datadir)
