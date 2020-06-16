from slack import WebClient


def slack_connection_singleton(connection_class):
    instances = dict()

    def wrapper(*args, **kwargs):
        nonlocal instances
        token = kwargs['token']

        if token not in instances:
            instances[token] = connection_class(*args, **kwargs)
        return instances[token]

    return wrapper


WebClient = slack_connection_singleton(WebClient)
