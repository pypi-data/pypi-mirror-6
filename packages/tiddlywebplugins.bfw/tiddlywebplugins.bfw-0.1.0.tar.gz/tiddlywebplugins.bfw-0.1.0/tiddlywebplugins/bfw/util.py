from httpexceptor import HTTP415


def ensure_form_submission(fn):
    """
    decorator to ensure the request was a form submission
    """

    def wrapper(environ, start_response):
        content_type = environ.get('CONTENT_TYPE', '')
        if not content_type.startswith('application/x-www-form-urlencoded'):
            raise HTTP415('unsupported content type')

        return fn(environ, start_response)

    return wrapper


class Link(object):

    def __init__(self, uri, label, active=False):
        self.uri = uri
        self.label = label
        self.active = active
