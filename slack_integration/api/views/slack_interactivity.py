from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny


class InteractivityProcessingView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        Receives payload of interactions with shortcuts, modals,
        or interactive components from Slack.

        More info:
        https://api.slack.com/apps/A014KJFJ7KR/interactive-messages
        """
        # in progress
        print('INTERACTIVITY')
        print(request.data['payload'])
        return Response(status=200)
