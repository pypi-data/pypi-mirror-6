class APIError(Exception):
    "Kirrupt TV API base Exception."
    pass


class WrongCredentials(APIError):
    pass
