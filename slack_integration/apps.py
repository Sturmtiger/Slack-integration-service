from django.apps import AppConfig


class SlackIntegrationConfig(AppConfig):
    name = 'slack_integration'

    def ready(self):
        import slack_integration.signals
