class UsernameAlreadyExists(Exception):
    pass


class BadRequest(Exception):
    pass


class NotFound(Exception):
    pass


class AuthenticationRequired(Exception):
    pass


class NoActiveEndpoint(Exception):
    pass