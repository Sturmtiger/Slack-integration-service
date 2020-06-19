from django.forms import BaseModelFormSet, ValidationError


class BaseButtonFormSet(BaseModelFormSet):
    def clean(self):
        checked_buttons_data = []

        for form in self.forms:
            print(form.cleaned_data)
            if form.cleaned_data == {}:
                continue

            button_data = form.cleaned_data
            button_data.pop('id')

            for button in checked_buttons_data:
                for field, value in button_data.items():
                    if button[field] == value:
                        raise ValidationError(
                            'Buttons must have different data. '
                            'Field "%s" is duplicated.' % field)

            checked_buttons_data.append(form.cleaned_data)
