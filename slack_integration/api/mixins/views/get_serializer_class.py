class GetSerializerClassListMixin:
    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializers_dict['list']

        return self.serializer_class