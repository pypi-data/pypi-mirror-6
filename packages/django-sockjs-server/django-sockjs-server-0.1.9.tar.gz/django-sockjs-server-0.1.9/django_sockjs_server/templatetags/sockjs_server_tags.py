from random import choice
from django import template
from django_sockjs_server.lib.config import SockJSSereverSettings
from django_sockjs_server.lib.token import Token

register = template.Library()

@register.simple_tag(name='sockjs_auth_token')
def sockjs_auth_token(channel_name, unq_id=None):
    token = Token()
    if unq_id:
        return token.get_secret_data(channel_name+str(unq_id))
    return token.get_secret_data(channel_name)


@register.simple_tag(name='sockjs_server_url')
def sockjs_server_url():
    config = SockJSSereverSettings()
    return choice(config.sockjs_url)