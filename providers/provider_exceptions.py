class ProviderExceptions(Exception):
    """Base class for Providers exceptions."""
    def __init__(self, message, provider_name) -> None:
        super().__init__(f"{provider_name}: {message}")

class MangaNotFoundError(ProviderExceptions):
    """Raise when the manga was not found or got multiple manga when using the id_token."""

    def __init__(self, message, provider_name) -> None:
        super().__init__(message, provider_name)