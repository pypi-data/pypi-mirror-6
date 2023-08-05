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

"""cubicweb-vcwiki controllers"""

import json

from logilab.common.decorators import cachedproperty

from cubicweb import Binary
from cubicweb.predicates import is_instance, match_form_params
from cubicweb.web import Redirect, ValidationError
from cubicweb.web.views.basecontrollers import ViewController
from cubicweb.web.views.editcontroller import EditController

from cubes.preview.views.controllers import PreviewControllerMixin

from cubes.vcwiki.entities import split_path

class VCWikiViewController(ViewController):
    __regid__ = 'wiki'
    __select__ = ViewController.__select__ & match_form_params('wikiid', 'wikipath')

    def publish(self, rset=None):
        if self.vcwiki is None:
            self._cw.form['vid'] = 'noresult'
            return super(VCWikiViewController, self).publish()

        self.normalize_path()
        is_binary_content, vcontent = self.get_downloadable_content()
        if is_binary_content:
            self._cw.form.setdefault('vid', 'download')
            rset = vcontent.as_rset()
        else:
            self._cw.form.setdefault('vid', 'vcwiki.view_page')
            rset = self.vcwiki.as_rset()
        return super(VCWikiViewController, self).publish(rset)

    @cachedproperty
    def vcwiki(self):
        """ Return VCWiki instance designated by the URL or None."""
        rset = self._cw.execute('VCWiki W WHERE W name %(n)s',
                                {'n': self._cw.form.pop('wikiid')})
        if rset:
            return rset.get_entity(0, 0)

    def normalize_path(self):
        """ Normalize the web form's `path` parameter, handling the None case
        (== root path), and removing leading and trailing slashes, if any.
        """
        form = self._cw.form
        form['wikipath'] = (form['wikipath'] or u'').lstrip('/').rstrip('/')

    def get_downloadable_content(self):
        """ Return a boolean telling if the wiki content (if any) that matches
        the web form's path is downloadable or not, and the corresponding
        VersionContent instance (or None if none match the given path).
        """
        vcontent = self.vcwiki.content(self._cw.form['wikipath'])
        is_binary_content = False
        if vcontent is not None:
            is_binary_content = not vcontent.cw_adapt_to(
                'IDownloadable').download_content_type().startswith('text/')
        return is_binary_content, vcontent


class VCWikiEditController(PreviewControllerMixin, EditController):
    __regid__ = 'vcwiki.edit_page'
    __select__ = match_form_params('vcwiki_eid', 'wikipath', 'content', 'message')

    def create_new_revision(self, path, content, msg):
        """ Create a new revision of the vcwiki with commit msg `msg`.
        If content is None, the versioned file with path `path` (if any) is
        deleted, otherwise its content is updated with `content`.
        When `content` if empty and the path points to a non yet existing file,
        an error is raised.
        """
        vfile = self.vcwiki.vcfile(path)
        # handle the above-described error case
        if not content and vfile is None:
            raise ValidationError(self.vcwiki.eid, {'content': self._cw._(
                'can not set an empty content to a new wiki page')})
        # create the new revision
        author = self._cw.user.dc_title()
        if self._cw.user.primary_email:
            author += u' <%s>' % self._cw.user.primary_email[0].address
        new_rev = self.vcwiki.repository.make_revision(msg=msg, author=author)
        # handle the wiki page creation page
        vfile = vfile or self.create_new_versioned_file(path)
        if content:
            self.create_new_version_content(vfile, new_rev, content)
        else:
            self.create_new_deleted_version_content(vfile, new_rev)

    def create_new_versioned_file(self, path):
        filedir, filename = split_path(path)
        return self._cw.create_entity('VersionedFile',
                                      directory=filedir,
                                      name=filename,
                                      from_repository=self.vcwiki.repository)

    def create_new_version_content(self, vfile, revision, content):
        encoding = self._cw.encoding
        ctype = self.vcwiki.content_mimetype
        self._cw.create_entity('VersionContent',
                               content_for=vfile,
                               from_revision=revision,
                               data=Binary(content.encode(encoding)),
                               data_format=unicode(ctype),
                               data_encoding=unicode(encoding))

    def create_new_deleted_version_content(self, vfile, revision):
        self._cw.create_entity('DeletedVersionContent',
                               content_for=vfile,
                               from_revision=revision)

    @cachedproperty
    def vcwiki(self):
        return self._cw.entity_from_eid(int(self._cw.form['vcwiki_eid']))

    def _default_publish(self):
        form = self._cw.form
        msg = form.get('message') or u'no commit message'
        if form['wikipath'] == u'':
            form['wikipath'] = u'index'
        self.create_new_revision(form['wikipath'], form['content'], msg)

    def publish(self, rset=None):
        """ Use all EditController machinery but the HTTP Redirect response, to
        be transformed into a javascript redirect. """
        try:
            return super(VCWikiEditController, self).publish(rset)
        except Redirect as exc:
            return self._javascript_redirect(exc.location)
        except ValidationError as ex:
            return self._javascript_error(ex)

    def _javascript_redirect(self, url):
        """ Javascript redirect response from a child iframe. """
        return ('<script type="text/javascript">'
                'window.parent.location.replace(%s);'
                '</script>' % json.dumps(url))

    def _javascript_error(self, exception):
        self._cw.set_content_type('text/html')
        return """<script type="text/javascript">
 window.parent.handleFormValidationResponse('form', null, null, %s, null);
</script>""" % (json.dumps((False, (None, exception.errors), None)))

    def _action_preview(self):
        """ Preview machinery: publish as normal, but rollback and respond with
        the new, formatted, wiki page content. """
        self._default_publish()
        self._cw.cnx.rollback()
        form = self._cw.form
        # The new VersionContent is not available yet as the `at_revision`
        # relation to its revision is created in an Operation (after a commit).
        # We use the old one here to use its `printable_value` method with the
        # new content as a value.
        old_vcontent = self.vcwiki.content(form['wikipath'])
        new_html_content = old_vcontent.printable_value(
            'data', value=Binary(form['content'].encode(self._cw.encoding)))
        domid = form.get('__domid', 'form')
        return self._preview_trampoline(domid, new_html_content, 'inline')
