

class ShirtsioError(Exception):
    def __init__(self, message=None, http_body=None, http_status=None, json_body=None):
        super(ShirtsioError, self).__init__(message)
        self.http_body = http_body and http_body.decode('utf-8')
        self.http_status = http_status
        self.json_body = json_body


class APIError(ShirtsioError):
    pass


class APIConnectionError(ShirtsioError):
    pass


class InvalidRequestError(ShirtsioError):
    def __init__(self, message, http_body=None, http_status=None, json_body=None):
        super(InvalidRequestError, self).__init__(message, http_body, http_status, json_body)


class AuthenticationError(ShirtsioError):
    pass