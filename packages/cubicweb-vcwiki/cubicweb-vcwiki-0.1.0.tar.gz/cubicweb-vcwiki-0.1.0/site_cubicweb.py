from docutils import nodes, utils
from docutils.parsers.rst.roles import register_canonical_role, set_classes


def wiki_page_reference_role(role, rawtext, text, lineno, inliner,
                             options={}, content=[]):
    text = text.strip()
    try:
        wikipath, rest = text.split(u':', 1)
    except:
        wikipath, rest = text, text
    context = inliner.document.settings.context # VersionContent instance
    if not (hasattr(context, 'repository')
            and context.repository.reverse_content_repo):
        return [nodes.Text(rest)], []
    vcwiki = context.repository.reverse_content_repo[0]
    ref = vcwiki.page_url(wikipath)
    set_classes(options)
    if not vcwiki.content(wikipath):
        options['classes'] = ['doesnotexist']
    else:
        options.pop('classes', None)
    return [nodes.reference(rawtext, utils.unescape(rest), refuri=ref,
                            **options)], []


register_canonical_role('wiki', wiki_page_reference_role)
