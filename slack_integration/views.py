from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.views import generic
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import SlackApplication, Template, ActionsBlock, Button


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
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', '/')
        return context

    def get_success_url(self):
        next_url = self.request.GET.get('next', '/')
        return next_url


class CreateTemplateView(generic.CreateView):
    model = Template
    fields = ('channel_name', 'name', 'message_text', 'fallback_text')
    template_name = 'slack_integration/template_create.html'

    def form_valid(self, form):
        application_obj = get_object_or_404(SlackApplication,
                                            pk=self.kwargs['app_pk'])
        self.object = form.save(commit=False)
        self.object.application = application_obj
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        form = super().get_form(form_class)
        form.fields['name'].label = 'Template name'
        form.fields['channel_name'].widget.attrs = {'placeholder': 'channel'}
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', '/')
        return context

    def get_success_url(self):
        next_url = self.request.GET.get('next', '/')
        return next_url


class TemplateDetailView(generic.DetailView):
    model = Template
    template_name = 'slack_integration/template_detail.html'
    context_object_name = 'template'


class CreateActionsBlockView(generic.CreateView):
    model = ActionsBlock
    fields = ('block_id',)
    template_name = 'slack_integration/actions_block_create.html'
    formset_class = modelformset_factory(Button,
                                         fields=('action_id', 'text'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'formset' not in kwargs:
            context['formset'] = self.formset_class(
                queryset=Button.objects.none())

        context['next'] = self.request.GET.get('next', '/')
        return context

    def post(self, request, *args, **kwargs):
        self.object = None

        form = self.get_form()
        formset = self.formset_class(request.POST)

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    @transaction.atomic
    def form_valid(self, form, formset):
        template = get_object_or_404(Template,
                                     pk=self.kwargs['template_pk'])
        self.object = form.save(commit=False)
        self.object.template = template
        self.object.save()

        formset.save(commit=False)
        for button_form in formset:
            button_obj = button_form.save(commit=False)
            button_obj.actions_block = self.object
            button_obj.save()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form,
                                                             formset=formset))

    def get_success_url(self):
        next_url = self.request.GET.get('next', '/')
        return next_url
