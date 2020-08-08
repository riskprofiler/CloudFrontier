from functools import wraps


def cors_headers(handler_or_origin=None, origin=None, credentials=False):
    """
    Automatically injects ``Access-Control-Allow-Origin`` headers to http
    responses. Also optionally adds ``Access-Control-Allow-Credentials: True``
    if called with ``credentials=True``

    Usage::
        >>> @cors_headers
        ... def hello(example, context):
        ...     return {'body': 'foobar'}
        >>> hello({}, object())
        {'body': 'foobar', 'headers': {'Access-Control-Allow-Origin': '*'}}
        >>> # or with custom domain
        >>> @cors_headers(origin='https://example.com', credentials=True)
        ... def hello_custom_origin(example, context):
        ...     return {'body': 'foobar'}
        >>> hello_custom_origin({}, object())
        {'body': 'foobar', 'headers': {'Access-Control-Allow-Origin': 'https://example.com', 'Access-Control-Allow-Credentials': True}}
    """
    if isinstance(handler_or_origin, str) and origin is not None:
        raise TypeError(
            "You cannot include any positional arguments when using"
            " the `origin` keyword argument"
        )
    if isinstance(handler_or_origin, str) or origin is not None:

        def wrapper_wrapper(handler):
            @wraps(handler)
            def wrapper(event, context):
                response = handler(event, context)
                if response is None:
                    response = {}
                headers = response.setdefault("headers", {})
                if origin is not None:
                    headers["Access-Control-Allow-Origin"] = origin
                else:
                    headers["Access-Control-Allow-Origin"] = handler_or_origin
                if credentials:
                    headers["Access-Control-Allow-Credentials"] = True
                return response

            return wrapper

        return wrapper_wrapper
    elif handler_or_origin is None:
        return cors_headers("*", credentials=credentials)
    else:
        return cors_headers("*")(handler_or_origin)