from django.forms import BaseModelFormSet, ValidationError


class BaseButtonFormSet(BaseModelFormSet):
    def clean(self):
        buttons = []

        for form in self.forms:
            if form.cleaned_data == {}:
                continue

            for button in buttons:
                for field, value in form.cleaned_data.items():
                    if button[field] == value:
                        raise ValidationError(
                            'Buttons must have different data. '
                            'Field "%s" is duplicated.' % field)

            buttons.append(form.cleaned_data)
