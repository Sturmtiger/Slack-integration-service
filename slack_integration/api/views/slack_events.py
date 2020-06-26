from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny


class SlackEventsView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        # in progress
        data = request.data
        print('EVENT')
        print(request.data)
        return Response(status=200, data=data)
