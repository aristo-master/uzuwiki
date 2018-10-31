import markdown
from commons import file_name_tools
from commons.file import file_utils
import bleach
from commons.errors import PageNotFoundError
from logging import getLogger

logger = getLogger(__name__)


def md_to_html(md_text):
    logger.debug("md_to_html:start")

    main_contents = markdown.markdown(md_text, extensions=[
        'markdown.extensions.abbr',
        'markdown.extensions.admonition',
        'markdown.extensions.attr_list',
        'markdown.extensions.codehilite',
        'markdown.extensions.def_list',
        'markdown.extensions.extra',
        'markdown.extensions.fenced_code',
        'markdown.extensions.footnotes',
        'markdown.extensions.headerid',
        'markdown.extensions.meta',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
        'markdown.extensions.smart_strong',
        'markdown.extensions.smarty',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        # 'markdown.extensions.wikilinks',
        'MarkdownHighlight.highlight',
        'commons.markdown.extensions.mdx_del_ins',
        'commons.markdown.extensions.mdx_superscript',
        'commons.markdown.extensions.mdx_semanticwikilinks',
        'commons.markdown.extensions.mdx_semanticdata',
        'subscript',
    ])

    ALLOWED_TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'b',
                    'i', 'strong', 'a', 'abbr', 'acronym', 'table', 'thead', 'tbody',
                    'th', 'tr', 'td', 'ul', 'li', 'br', 'pre', 'code',
                    'blockquote', 'cite', 'hr', 'em', 'del', 'sup', 'sub',
                    'mark', 'ins', 'span', 'img', 'ol', 'strong']

    ALLOWED_ATTRIBUTES = ['content', 'property', 'href', 'target', 'alt', 'src', 'title']

    html = bleach.clean(markdown.markdown(main_contents), tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)

    logger.debug("md_to_html:end")

    return html


def get_contents(wiki_id, page_dirs):
    logger.debug("get_contents:start")

    try:
        page_name = file_name_tools.page_dirs_to_file_name(page_dirs)

        get_page_file_data = file_utils.get_file(wiki_id, page_name + ".md")
        main_contents = md_to_html(get_page_file_data)
    except FileNotFoundError:

        raise PageNotFoundError("ページが存在しません。")

    logger.debug("get_contents:end")

    return main_contents


def get_edit_contents(wiki_id, page_dirs):
    logger.debug("get_edit_contents:start")

    try:
        page_name = file_name_tools.page_dirs_to_file_name(page_dirs)

        get_page_file_data = file_utils.get_file(wiki_id, page_name + ".md")
    except FileNotFoundError:

        raise PageNotFoundError("ページが存在しません。")

    logger.debug("get_edit_contents:end")

    return get_page_file_data
