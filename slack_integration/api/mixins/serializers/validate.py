class ValidateSubsCallbackUrlMixin:
    def validate(self, attrs):
        request_method = self.context['request'].method

        callback_url = attrs.get('callback_url')

        if callback_url == '':
            attrs[self.subs_field_name] = False
        if callback_url is None:
            if request_method == 'POST':
                attrs[self.subs_field_name] = False
            elif (request_method in ['PUT', 'PATCH'] and not
            self.instance.callback_url):
                attrs[self.subs_field_name] = False

        return attrs
