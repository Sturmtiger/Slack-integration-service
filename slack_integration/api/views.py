from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PostMessageSerializer

from .slack_message_constructor import SlackMessageConstructor
from .slack_connector import WebClient
from slack_integration.models import SlackApplication


class PostMessageView(APIView):
    def post(self, request):
        serializer = PostMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.data)
        app_obj = SlackApplication.objects.get(
            name=serializer.validated_data['app_name'])
        slack_web_client = WebClient(token=app_obj.bot_user_oauth_access_token)

        message_constructor = SlackMessageConstructor(
            **serializer.validated_data)
        message = message_constructor.get_message_payload()

        slack_response = slack_web_client.chat_postMessage(**message)
        print(dir(slack_response))
        print(slack_response.status_code)

        return Response(slack_response.data,
                        status=slack_response.status_code)
