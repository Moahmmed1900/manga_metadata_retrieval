class KomgaExceptions(Exception):
    """Base class for Komga exceptions."""
    def __init__(self, message) -> None:
        super().__init__(f"Komga: {message}")

class KomgaLoginFailed(KomgaExceptions):
    """Raise when authentication with komga fails"""

    def __init__(self, message) -> None:
        super().__init__(message)

class KomgaUnauthorized(KomgaExceptions):
    """Raise when the user is unauthorized to do the specified action"""

    def __init__(self, message) -> None:
        super().__init__(message)

class KomgaForbidden(KomgaExceptions):
    """Raise when the user is forbidden to do the specified action"""

    def __init__(self, message) -> None:
        super().__init__(message)

class KomgaBadRequest(KomgaExceptions):
    """Raise when the API request is bad or missing some parameters"""

    def __init__(self, message) -> None:
        super().__init__(message)