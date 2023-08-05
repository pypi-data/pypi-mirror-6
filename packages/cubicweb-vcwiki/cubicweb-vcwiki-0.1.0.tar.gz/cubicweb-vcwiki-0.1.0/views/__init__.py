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

"""cubicweb-vcwiki views"""


from logilab.common.decorators import cachedproperty

from cubicweb.predicates import is_instance, match_form_params
from cubicweb.view import EntityView


def is_vcwiki_page(vcwiki):
    form = vcwiki._cw.form
    if 'wikipath' in form and vcwiki.content(form['wikipath']):
        return 1


class VCWikiView(EntityView):
    __abstract__ = True
    __select__ = (EntityView.__select__
                  & is_instance('VCWiki')
                  & match_form_params('wikipath'))
    consider_rev_parameter = False

    @property
    def vcontent(self):
        """ Return the VersionContent instance of current path in current
        vcwiki. This will consider the `rev` url parameter (which must contain a
        revision number) if the attribute `consider_rev_parameter` is set (which
        is not the default).
        """
        form = self._cw.form
        revnum = None
        if self.consider_rev_parameter:
            revnum = form.get('rev')
        return self.vcwiki.content(form['wikipath'], revision=revnum)

    @cachedproperty
    def vcwiki(self):
        return self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
