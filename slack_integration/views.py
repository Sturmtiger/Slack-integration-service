from django.forms import modelformset_factory, inlineformset_factory
from django.http import HttpResponseRedirect
from django.views import generic
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import SlackApplication, Template, ActionsBlock, Button
from .formsets import BaseButtonFormSet


class AppListView(generic.ListView):
    model = SlackApplication
    template_name = 'slack_integration/list/app.html'
    context_object_name = 'applications'


class AppDetailView(generic.DetailView):
    model = SlackApplication
    template_name = 'slack_integration/detail/app.html'
    context_object_name = 'app'


class CreateAppView(generic.CreateView):
    model = SlackApplication
    fields = ('name', 'signing_secret', 'bot_user_oauth_access_token')
    template_name = 'slack_integration/create/app.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', '/')
        return context

    def get_success_url(self):
        next_url = self.request.GET.get('next', '/')
        return next_url


class UpdateAppView(generic.UpdateView):
    model = SlackApplication
    fields = ('name', 'signing_secret', 'bot_user_oauth_access_token')
    template_name = 'slack_integration/update/app.html'

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
    template_name = 'slack_integration/create/template.html'

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
    template_name = 'slack_integration/detail/template.html'
    context_object_name = 'template'


class UpdateTemplateView(generic.UpdateView):
    model = Template
    fields = ('channel_name', 'name', 'message_text', 'fallback_text')
    template_name = 'slack_integration/update/template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', '/')

        return context

    def get_success_url(self):
        next_url = self.request.GET.get('next', '/')
        return next_url


class CreateActionsBlockView(generic.CreateView):
    """
    Creates an ActionsBlock object
    and at least 1 button(by formset) related with it.
    """
    model = ActionsBlock
    fields = ('block_id',)
    template_name = 'slack_integration/create/actions_block.html'
    formset_class = modelformset_factory(model=Button,
                                         formset=BaseButtonFormSet,
                                         fields=('action_id', 'text'),
                                         min_num=1,
                                         validate_min=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'formset' not in context:
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
            # save button object if form is not empty (has changed)
            if button_form.has_changed():
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


class ActionsBlockDetailView(generic.DetailView):
    model = ActionsBlock
    template_name = 'slack_integration/detail/actions_block.html'
    context_object_name = 'actions_block'


class UpdateActionsBlockView(generic.UpdateView):
    model = ActionsBlock
    fields = ('block_id',)
    template_name = 'slack_integration/update/actions_block.html'
    formset_class = inlineformset_factory(ActionsBlock, Button,
                                          fields=('action_id', 'text'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'formset' not in context:
            context['formset'] = self.formset_class(instance=self.object)

        context['next'] = self.request.GET.get('next', '/')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = self.get_form()
        formset = self.formset_class(request.POST, instance=self.object)

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    @transaction.atomic
    def form_valid(self, form, formset):
        self.object = form.save()

        formset.save()
        # formset processing code must be here

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form,
                                                             formset=formset))

    def get_success_url(self):
        next_url = self.request.GET.get('next', '/')
        return next_url
