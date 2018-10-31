from django.views.generic import *
from wikis.mixins import *
from wikis.maintenances.forms import WikiConfForm, PageConfForm
from wikis.maintenances.mixins import *
from django.urls import reverse
from django.contrib import messages


# Create your views here.
class WikiMaintenanceView(ManagerRequiredMixin, ModeMixin, FormView):
    """
    表示画面
    """
    form_class = WikiConfForm
    template_name = "wikis/maintenances/wiki.html"
    mode = "wikimnt"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['wiki_id'] = self.request.wiki_id

        return kwargs

    def form_valid(self, form):
        # ページ新規作成
        form.put()

        return super().form_valid(form)

    def get_success_url(self):
        form = super().get_form()

        messages.add_message(self.request, messages.SUCCESS, '保存しました。')
        argzz = [form.data["wiki_id"]]

        return reverse('wikis.maintenances:index', args=argzz)


class PageMaintenanceView(ManagerRequiredMixin, PageMixin, FormView):
    """
    表示画面
    """
    form_class = PageConfForm
    template_name = "wikis/maintenances/page.html"
    mode = "pagemnt"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['wiki_id'] = self.request.wiki_id
        kwargs['page_dirs'] = self.request.page_dirs

        return kwargs

    def form_valid(self, form):
        # ページ新規作成
        form.put()

        return super().form_valid(form)

    def get_success_url(self):
        form = super().get_form()

        messages.add_message(self.request, messages.SUCCESS, '保存しました。')
        argzz = [form.data["wiki_id"]]
        argzz.extend(file_name_tools.to_page_dirs(form.data["page_name"]))

        return reverse('wikis.maintenances:maintenance', args=argzz)
