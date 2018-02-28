
class KuberlabClientException(Exception):
    """Base Exception for Kuberlab client

    To correctly use this class, inherit from it and define
    a 'message' and 'code' properties.
    """
    message = "An unknown exception occurred"
    code = "UNKNOWN_EXCEPTION"

    def __str__(self):
        return self.message

    def __init__(self, message=message):
        self.message = message
        super(KuberlabClientException, self).__init__(
            '%s: %s' % (self.code, self.message))


class TimeoutError(KuberlabClientException):
    message = "TimeoutError occurred"
    code = "TIMEOUT_ERROR"

    def __init__(self, message=None):
        if message:
            self.message = message


class IllegalArgumentException(KuberlabClientException):
    message = "IllegalArgumentException occurred"
    code = "ILLEGAL_ARGUMENT_EXCEPTION"

    def __init__(self, message=None):
        if message:
            self.message = message
