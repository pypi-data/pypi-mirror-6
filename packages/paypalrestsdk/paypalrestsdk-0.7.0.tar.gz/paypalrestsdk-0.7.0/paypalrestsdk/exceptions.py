
class ConnectionError(Exception):
    def __init__(self, response, content=None, message=None):
        self.response = response
        self.content = content
        self.message = message

    def __str__(self):
        message = "Failed."
        if hasattr(self.response, 'status'):
            message = message + "  Response status = %s." % (self.response.status)
        if hasattr(self.response, 'reason'):
            message = message + "  Response message = %s." % (self.response.reason)
        return message


class TimeoutError(ConnectionError):
    """Raised when a Timeout::Error occurs.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class SSLError(ConnectionError):
    """Raised when a OpenSSL::SSL::SSLError occurs
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Redirection(ConnectionError):
    """3xx Redirection
    """
    def __str__(self):
        message = super(Redirection, self).__str__()
        if self.response.get('Location'):
            message = "%s => %s" % (message, self.response.get('Location'))
        return message

class MissingParam(TypeError):
    pass

class MissingConfig(Exception):
    pass

class ClientError(ConnectionError):
    """4xx Client Error
    """
    pass

class BadRequest(ClientError):
    """400 Bad Request
    """
    pass
 
class UnauthorizedAccess(ClientError):
    """401 Unauthorized
    """
    pass

class ForbiddenAccess(ClientError):
    """403 Forbidden
    """
    pass

class ResourceNotFound(ClientError):
    """404 Not Found
    """
    pass
 
class ResourceConflict(ClientError):
    """409 Conflict
    """
    pass

class ResourceGone(ClientError):
    """410 Gone
    """
    pass

class ResourceInvalid(ClientError):
    """422 Invalid
    """
    pass

class ServerError(ConnectionError):
    """5xx Server Error
    """
    pass
 
class MethodNotAllowed(ClientError):
    """405 Method Not Allowed
    """

    def allowed_methods(self):
        return self.response['Allow']
