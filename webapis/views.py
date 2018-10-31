from django.http import HttpResponse
from commons.markdown import markdown_tools
from commons.file import file_utils
from django.template.loader import render_to_string
from django.urls import reverse
from commons import file_name_tools
import datetime
import json
from logging import getLogger

logger = getLogger(__name__)


# Create your views here.
def md_to_html(request):
    if request.method == 'POST':
        md_text = request.POST.get('contents')

        if not md_text:
            return HttpResponse("")

        html = markdown_tools.md_to_html(md_text)

        return HttpResponse(html)

    return HttpResponse("")


def get_latest_update(request):
    if request.method == 'GET':
        wiki_id = request.GET.get('wiki_id')

        page_file = json.loads(file_utils.get_file(wiki_id, "pages.json"))
        pages = page_file["data"]["pages"]
        pages = sorted(pages, key=lambda x: x['update'], reverse=True)

        for page in pages:
            file_name_slash = file_name_tools.file_name_to_page_name(page["file_name"])
            page["file_name"] = file_name_slash

            argzz = [wiki_id]
            argzz.extend(file_name_slash.split("/"))
            page["url"] = reverse('wikis.pages:show', args=argzz)

            tdatetime = datetime.datetime.strptime(page["update"], '%Y-%m-%dT%H:%M:%S.%f')
            tdate = datetime.date(tdatetime.year, tdatetime.month, tdatetime.day).strftime('%Y-%m-%d')
            page["update_day"] = tdate

        context = {"wiki_id": wiki_id, "pages": pages}

        html = render_to_string('webapis/latest_update.html', context)

        return HttpResponse(html)

    return HttpResponse("")


def get_side_bar(request):
    if request.method == 'GET':
        wiki_id = request.GET.get('wiki_id')

        if not wiki_id:
            return HttpResponse("")

        html = markdown_tools.get_contents(wiki_id, ["SideBar"])

        return HttpResponse(html)

    return HttpResponse("")
