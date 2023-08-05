import odesk


def get_odesk_client(request, **attrs):
    """Construct an oDesk client.

    *Parameters:*
      :attrs:   keyword arguments that will be
                attached to the ``client.auth`` as attributes
                (``request_token``, etc.)
    """
    client_kwargs = {
        'oauth_access_token': attrs.pop('oauth_access_token', None),
        'oauth_access_token_secret': attrs.pop(
            'oauth_access_token_secret', None)

    }

    settings = request.registry.settings
    client = odesk.Client(settings['odesk.api.key'],
                          settings['odesk.api.secret'], **client_kwargs)

    for key, value in attrs.items():
        setattr(client.auth, key, value)

    return client
