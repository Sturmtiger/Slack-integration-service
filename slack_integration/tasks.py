from slack import WebClient

from slack_integration_service.celery import app
from slack_integration.models import SlackApplication
from slack_integration.api.slack_message_constructors \
    import PostSlackMessageConstructor


@app.task
def post_message(app_name, template_name):
    token = SlackApplication.objects.get(
                name=app_name).bot_user_oauth_access_token

    slack_web_client = WebClient(token=token)

    message_constructor = PostSlackMessageConstructor(
                            app_name=app_name,
                            template_name=template_name)
    message = message_constructor.get_message_payload()

    response = slack_web_client.chat_postMessage(**message)

    return response.status_code
