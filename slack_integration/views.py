from django.http import HttpResponseRedirect
from django.views import generic
from django.shortcuts import get_object_or_404
from .models import SlackApplication, Template


class AppListView(generic.ListView):
    model = SlackApplication
    template_name = 'slack_integration/app_list.html'
    context_object_name = 'applications'


class AppDetailView(generic.DetailView):
    model = SlackApplication
    template_name = 'slack_integration/app_detail.html'
    context_object_name = 'app'


class AppRegistrationView(generic.CreateView):
    model = SlackApplication
    fields = ('name', 'signing_secret', 'bot_user_oauth_access_token')
    template_name = 'slack_integration/app_registration.html'

    def get_context_data(self, **kwargs):
        print(self.get_form(), 'GET')
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', '/')
        return context

    def get_success_url(self):
        next_url = self.request.GET.get('next', '/')
        return next_url


class CreateTemplateView(generic.CreateView):
    model = Template
    fields = ('name', 'channel_name', 'text')
    template_name = 'slack_integration/template_create.html'

    def form_valid(self, form):
        application_obj = get_object_or_404(SlackApplication,
                                            pk=self.kwargs['app_pk'])
        self.object = form.save(commit=False)
        self.object.application = application_obj
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', '/')
        return context

    def get_success_url(self):
        next_url = self.request.GET.get('next', '/')
        return next_url
