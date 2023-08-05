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

"""cubicweb-vcwiki wiki display related views"""

from logilab.mtconverter import xml_escape

from cubicweb.tags import a, div
from cubicweb.web import stdmsgs
from cubicweb.web.formfields import StringField
from cubicweb.web.formwidgets import Button, SubmitButton, HiddenInput
from cubicweb.web.views.forms import FieldsForm


from cubes.vcwiki.views import VCWikiView


class VCWikiViewPage(VCWikiView):
    __regid__ = 'vcwiki.view_page'
    consider_rev_parameter = True

    def page_title(self):
        if self.vcontent:
            name = self.vcwiki.display_name(self.vcontent.content_for[0])
        else:
            name = self._cw._('New wiki page')
        return u'%s - %s' % (self.vcwiki.dc_title(), name)

    def creation_link(self):
        url = self.vcwiki.page_url(self._cw.form['wikipath'],
                                   vid='vcwiki.edit_page')
        link = a(self._cw._('Create this wiki page?'), href=xml_escape(url))
        self.w(div(link, Class='section'))

    def entity_call(self, entity):
        self._cw.add_css('cubes.vcwiki.css')
        if not self.vcontent:
            self.w(div(self._cw._('This wiki page does not exist.'),
                       Class='stateMessage'))
            self.creation_link()
        else:
            self.w(self.vcontent.printable_value('data'))
