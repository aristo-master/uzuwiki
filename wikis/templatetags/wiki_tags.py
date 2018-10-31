from django import template
from django.urls import reverse
from django.template.loader import render_to_string
from commons.file import file_utils

register = template.Library()


@register.simple_tag
def wiki_url(page_type, wiki_id, page_dirs):
    argzz = [wiki_id]
    argzz.extend(page_dirs)

    if page_type == "show":
        return reverse('wikis.pages:show', args=argzz)

    if page_type == "edit":
        return reverse('wikis.pages:edit', args=argzz)

    if page_type == "attach":
        return reverse('wikis.attachments:attachment', args=argzz)

    if page_type == "copy":
        return reverse('wikis.pages:copy', args=argzz)

    if page_type == "comment":
        return reverse('wikis.comments:comment', args=argzz)

    if page_type == "history":
        return reverse('wikis.histories:history', args=argzz)

    if page_type == "diff":
        return reverse('wikis.histories:diff', args=argzz)

    if page_type == "src":
        return reverse('wikis.histories:src', args=argzz)

    if page_type == "maintenance":
        return reverse('wikis.maintenances:maintenance', args=argzz)

    return None


@register.simple_tag
def breadcrumb_list(wiki_id, page_dirs):
    breadcrumb_list = []
    argzz = [wiki_id]

    if len(page_dirs) == 1 and page_dirs[0] == "FrontPage":
        context = {"wiki_id": wiki_id}
        return render_to_string('wikis/page_name.html', context)

    if page_dirs[0] != "FrontPage":
        breadcrumb = {
            "name": "TOP",
            "url": reverse('wikis.pages:index', args=argzz)
        }

        breadcrumb_list.append(breadcrumb)

    for page_dir in page_dirs:
        argzz.append(page_dir)

        breadcrumb = {
            "name": page_dir,
            "url": reverse('wikis.pages:show', args=argzz)
        }

        breadcrumb_list.append(breadcrumb)

    context = {"wiki_id": wiki_id, "breadcrumb_list": breadcrumb_list}

    return render_to_string('wikis/page_name.html', context)


@register.simple_tag
def attachment_url(attachment_record):
    return file_utils.get_static_file_url(attachment_record)
