from django.views.generic import *
from wikis.mixins import *
from django.http import HttpResponse
from commons.markdown import markdown_tools
from commons import file_name_tools
from .forms import CommentForm
from django.urls import reverse
from wikis.comments import comment_tool
from django.shortcuts import render


# Create your views here.


class CommentView(PageMixin, CommentFlgMixin, FormView):
    """
    ページのコメントの表示と追加
    表示画面ではコメントは一部しか表示しないが、コメント画面では全てのコメントを表示する。
    """
    form_class = CommentForm
    template_name = "wikis/comments/comments.html"
    mode = "show"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['page_dirs'] = self.request.page_dirs

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # コンテンツ
        context["main_contents"] = markdown_tools.get_contents(self.request.wiki_id, self.request.page_dirs)

        # コメント
        context["comments"] = comment_tool.get_comments_hierarchy(self.request.wiki_id, self.request.page_dirs)

        return context

    def form_valid(self, form):
        # コメントの追記
        form.put()

        return super().form_valid(form)

    def get_success_url(self):
        form = super().get_form()

        argzz = [form.data["wiki_id"]]
        argzz.extend(file_name_tools.to_page_dirs(form.data["page_name"]))

        return reverse('wikis.comments:comment', args=argzz) + "#comment"


def get_comments(request, wiki_id):
    if request.method == 'GET':
        page_name = request.GET.get('page_name')

        if not wiki_id or not page_name:
            return HttpResponse("")

        context = {}
        context["wiki_id"] = wiki_id

        context["comments"] = comment_tool.get_comments_short(wiki_id, page_name)
        context["form"] = {
            "page_name": {
                "value": page_name
            }
        }

        argzz = [wiki_id]
        argzz.extend(file_name_tools.to_page_dirs(page_name))
        context["comment_url"] = reverse('wikis.comments:comment', args=argzz)

        return render(request, 'wikis/comments/show_comments.html', context)

    return HttpResponse("")
