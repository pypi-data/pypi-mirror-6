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

"""cubicweb-vcwiki web UI actions"""

from cubicweb.predicates import (is_instance, one_line_rset, match_form_params,
                                 score_entity, objectify_predicate)
from cubicweb.web.action import Action

from cubes.vcsfile.views.actions import VFAction

from cubes.vcwiki.views import is_vcwiki_page


class VCWikiAction(Action):
    __select__ = Action.__select__ & is_instance('VCWiki') & one_line_rset()

    @property
    def vcwiki(self):
        return self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)


class VCWikiViewAction(VCWikiAction):
    __regid__ = 'vcwiki.view_home'
    title = _('wiki homepage')
    category = 'moreactions'

    def url(self):
        return self.vcwiki.url


@objectify_predicate
def has_write_perm_on_repo(cls, req, rset=None, entity=None, col=0, **kwargs):
    """ Predicate to be complemented by is_instance('VCWiki'), that will return
    1 in the case the given VCWiki has a content repository on which current
    user as the update permission.
    """
    entity = entity or (rset and rset.get_entity(0, col))
    repo = entity.content_repo[0] or None
    rset = req.user.has_permission('write', contexteid=repo.eid)
    if rset:
        return 1
    return 0


class VCWikiEditAction(VCWikiAction):
    __regid__ = 'edit' # override default edit action
    __select__ = (VCWikiAction.__select__
                  & match_form_params('wikipath')
                  & has_write_perm_on_repo())
    title = _('edit this page')
    category = 'mainactions'
    page_vid = 'vcwiki.edit_page'

    def actual_actions(self):
        """ Override default edit action for VCWiki instances, unless an
        existing wiki page is selected.
        """
        if is_vcwiki_page(self.vcwiki):
            yield self

    def url(self):
        path = self._cw.form['wikipath']
        if not path.endswith(self.vcwiki.content_file_extension):
            path += self.vcwiki.content_file_extension
        return self.vcwiki.page_url(self._cw.form['wikipath'], vid=self.page_vid)


class VCWikiDeleteAction(VCWikiEditAction):
    __regid__ = 'delete' # override default delete action
    title = _('delete this page')
    category = 'mainactions'
    page_vid = 'vcwiki.delete_page'


class VCWikiViewHistoryAction(VCWikiEditAction):
    __regid__ = 'vcwiki.view_history'
    title = _('history of this page')
    category = 'mainactions'
    page_vid = 'vcwiki.page_history'
    order = 1000


def is_vfile_of_wiki(entity):
    return bool(entity._cw.execute('Any W WHERE W content_repo R, X eid %(x)s, '
                                   'X from_repository R', {'x': entity.eid}))


class VersionedFileSeeInWikiAction(VFAction):
    __regid__ = 'vcwiki.see_versioned_file'
    __select__ = VFAction.__select__ & score_entity(is_vfile_of_wiki)

    title = _('see in wiki')
    order = 95

    def url(self):
        vfile = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        vcwiki = vfile.repository.reverse_content_repo[0]
        path = vcwiki.display_name(vfile)
        if vfile.directory:
            path = vfile.directory + '/' + path
        if path == 'index':
            path = ''
        return vcwiki.page_url(path)
