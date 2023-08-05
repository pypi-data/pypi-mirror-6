from mercurial import cmdutil, patch, scmutil, ui as uimod
from mercurial.error import RepoError

from cubicweb import Binary
from cubicweb.server import Service

from cubes.vcsfile import bridge


class RevisionDiffService(Service):
    """ Return the diff between two revisions.
    """

    __regid__ = 'vcwiki.export-rev-diff'

    def call(self, repo_eid, path, rev1, rev2):
        repo = self._cw.entity_from_eid(repo_eid)
        ui = uimod.ui()
        diffopts = patch.diffopts(ui, {'git': True, 'unified': 5})
        hdrepo = bridge.repository_handler(repo)
        try:
            hgrepo = hdrepo.hgrepo()
        except RepoError:
            return None
        output = Binary()
        node1, node2 = scmutil.revpair(hgrepo, (rev1, rev2))
        m = scmutil.matchfiles(hgrepo, (path.encode(repo.encoding),))
        cmdutil.diffordiffstat(ui, hgrepo, diffopts, node1, node2, m, fp=output)
        return output.getvalue()
