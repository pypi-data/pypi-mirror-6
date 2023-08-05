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

"""cubicweb-vcwiki schema"""


from yams.buildobjs import EntityType, SubjectRelation, String


class VCWiki(EntityType):
    name = String(required=True, unique=True)
    content_repo = SubjectRelation('Repository', cardinality='1?', inlined=True)
    content_file_extension = String(required=True, maxsize=16,
                                    description=_(
            'extension of the names of the files in the vcwiki repository.'
            ' Examples: "rst", "html"'))
