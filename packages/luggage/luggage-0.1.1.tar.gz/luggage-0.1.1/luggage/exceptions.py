class ContainerDoesNotExistException(Exception):
    pass


class ObjectDoesNotExistException(Exception):
    @classmethod
    def construct(cls, container, object):
        return cls('Object {0} does not exist in container {1}'.format(
            container, object
        ))


class InvalidCredentialsException(Exception):
    pass


class LuggageException(Exception):
    @classmethod
    def from_respone(cls, response):
        return cls('Unexpected HTTP response - '
                                'status code: {0}, content: "{1}"'.format(
            response.status_code, response.text
        ))